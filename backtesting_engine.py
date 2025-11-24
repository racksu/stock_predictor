"""
回測系統 (Backtesting Engine)
用於驗證股票預測策略的實際表現

功能：
1. 歷史數據回測
2. 交易信號模擬
3. 資金管理
4. 績效指標計算
5. 風險分析
6. 可視化報告

作者：Enhanced Stock Picker Team
版本：v1.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 導入現有的選股系統
try:
    from smart_stock_picker_enhanced_v3 import EnhancedStockPicker, EnhancedStockAnalyzer
    from smart_stock_picker_v2_1 import SmartStockPicker
    PICKER_AVAILABLE = True
except ImportError:
    PICKER_AVAILABLE = False
    print("⚠️ 警告：無法導入選股系統，部分功能將不可用")


class BacktestingEngine:
    """
    回測引擎

    模擬真實交易場景，測試策略表現
    """

    def __init__(self,
                 initial_capital: float = 1000000,
                 commission_rate: float = 0.001425,  # 台股手續費 0.1425%
                 tax_rate: float = 0.003,             # 台股證交稅 0.3%
                 slippage: float = 0.001):            # 滑價 0.1%
        """
        初始化回測引擎

        參數:
            initial_capital: 初始資金 (預設100萬)
            commission_rate: 手續費率 (預設0.1425%)
            tax_rate: 證交稅率 (預設0.3%)
            slippage: 滑價率 (預設0.1%)
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.tax_rate = tax_rate
        self.slippage = slippage

        # 回測結果
        self.trades = []           # 交易記錄
        self.positions = []        # 持倉記錄
        self.equity_curve = []     # 資金曲線
        self.daily_returns = []    # 每日報酬率

        # 績效指標
        self.metrics = {}

    def calculate_trade_cost(self, price: float, shares: int, is_buy: bool) -> float:
        """
        計算交易成本

        參數:
            price: 股價
            shares: 股數
            is_buy: 是否為買入

        返回:
            total_cost: 總成本 (包含手續費和稅)
        """
        trade_value = price * shares

        # 手續費 (買賣都收)
        commission = trade_value * self.commission_rate
        commission = max(commission, 20)  # 最低20元

        # 證交稅 (只有賣出才收)
        tax = trade_value * self.tax_rate if not is_buy else 0

        # 滑價
        slippage_cost = trade_value * self.slippage

        return commission + tax + slippage_cost

    def run_backtest(self,
                    df: pd.DataFrame,
                    strategy: str = 'enhanced',
                    position_size: float = 0.3,
                    stop_loss: float = -0.08,
                    take_profit: float = 0.15,
                    rebalance_days: int = 5) -> Dict:
        """
        執行回測

        參數:
            df: 歷史數據 DataFrame (必須包含 OHLCV)
            strategy: 策略類型 ('basic' 或 'enhanced')
            position_size: 單次建倉比例 (預設30%)
            stop_loss: 停損比例 (預設-8%)
            take_profit: 停利比例 (預設15%)
            rebalance_days: 重新評估天數 (預設5天)

        返回:
            results: 回測結果字典
        """
        print(f"\n{'='*80}")
        print(f"開始回測 - {strategy.upper()} 策略")
        print(f"{'='*80}")
        print(f"初始資金: ${self.initial_capital:,.0f}")
        print(f"單次倉位: {position_size*100:.0f}%")
        print(f"停損: {stop_loss*100:.0f}%")
        print(f"停利: {take_profit*100:.0f}%")
        print(f"回測期間: {df['date'].iloc[0]} ~ {df['date'].iloc[-1]}")
        print(f"{'='*80}\n")

        # 初始化
        capital = self.initial_capital
        position = None  # 當前持倉 {entry_price, shares, entry_date, entry_index}
        self.trades = []
        self.positions = []
        self.equity_curve = []

        # 初始化分析器
        if strategy == 'enhanced' and PICKER_AVAILABLE:
            analyzer = EnhancedStockAnalyzer()
        else:
            analyzer = None

        # 計算技術指標
        if analyzer:
            df = analyzer.calculate_indicators(df.copy())

        # 逐日回測
        for i in range(60, len(df)):  # 從第60天開始,確保有足夠的歷史數據
            current_date = df['date'].iloc[i]
            current_price = df['close'].iloc[i]

            # 記錄當前淨值
            current_equity = capital
            if position:
                current_equity += position['shares'] * current_price
            self.equity_curve.append({
                'date': current_date,
                'equity': current_equity,
                'capital': capital,
                'position_value': current_equity - capital
            })

            # 如果有持倉,檢查停損/停利
            if position:
                entry_price = position['entry_price']
                return_pct = (current_price - entry_price) / entry_price
                days_held = i - position['entry_index']

                should_exit = False
                exit_reason = None

                # 檢查停損
                if return_pct <= stop_loss:
                    should_exit = True
                    exit_reason = f'停損 ({return_pct*100:.2f}%)'

                # 檢查停利
                elif return_pct >= take_profit:
                    should_exit = True
                    exit_reason = f'停利 ({return_pct*100:.2f}%)'

                # 檢查是否需要重新評估 (每N天)
                elif days_held % rebalance_days == 0 and days_held > 0:
                    # 重新計算評分
                    if analyzer:
                        score_dict = analyzer.calculate_taiwan_optimized_score(df, i)
                        tech_score = score_dict.get('technical_total', 0)

                        # 如果評分轉差 (低於30分),考慮出場
                        if tech_score < 20:
                            should_exit = True
                            exit_reason = f'評分轉差 ({tech_score:.1f}分)'

                # 執行賣出
                if should_exit:
                    sell_price = current_price
                    shares = position['shares']

                    # 計算交易成本
                    trade_cost = self.calculate_trade_cost(sell_price, shares, False)

                    # 計算收益
                    sell_value = sell_price * shares - trade_cost
                    capital += sell_value

                    profit = sell_value - (position['entry_price'] * shares + position['entry_cost'])
                    profit_pct = profit / (position['entry_price'] * shares + position['entry_cost'])

                    # 記錄交易
                    trade_record = {
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': sell_price,
                        'shares': shares,
                        'profit': profit,
                        'profit_pct': profit_pct,
                        'days_held': days_held,
                        'exit_reason': exit_reason
                    }
                    self.trades.append(trade_record)

                    print(f"[{current_date}] 賣出 @ ${sell_price:.2f} | "
                          f"報酬: {profit_pct*100:+.2f}% | "
                          f"持有: {days_held}天 | "
                          f"原因: {exit_reason} | "
                          f"淨值: ${current_equity:,.0f}")

                    position = None

            # 如果沒有持倉,檢查是否有買入信號
            if not position and analyzer:
                # 計算當前評分
                score_dict = analyzer.calculate_taiwan_optimized_score(df, i)
                tech_score = score_dict.get('technical_total', 0)
                kd_score = score_dict.get('kd_score', 0)

                # 買入條件:
                # 1. 技術面評分 >= 25分 (滿分40)
                # 2. KD指標良好 (>= 8分,滿分15)
                if tech_score >= 25 and kd_score >= 8:
                    # 計算買入股數
                    buy_value = capital * position_size
                    buy_price = current_price
                    shares = int(buy_value / (buy_price * 1000)) * 1000  # 台股以1000股為單位

                    if shares >= 1000:  # 至少買1張
                        # 計算交易成本
                        trade_cost = self.calculate_trade_cost(buy_price, shares, True)
                        total_cost = buy_price * shares + trade_cost

                        # 檢查資金是否足夠
                        if total_cost <= capital:
                            capital -= total_cost

                            # 記錄持倉
                            position = {
                                'entry_date': current_date,
                                'entry_price': buy_price,
                                'shares': shares,
                                'entry_cost': trade_cost,
                                'entry_index': i,
                                'entry_tech_score': tech_score
                            }

                            print(f"[{current_date}] 買入 @ ${buy_price:.2f} | "
                                  f"股數: {shares:,} | "
                                  f"評分: {tech_score:.1f} | "
                                  f"剩餘資金: ${capital:,.0f}")

        # 回測結束,如果還有持倉,強制平倉
        if position:
            final_price = df['close'].iloc[-1]
            final_date = df['date'].iloc[-1]
            shares = position['shares']

            trade_cost = self.calculate_trade_cost(final_price, shares, False)
            sell_value = final_price * shares - trade_cost
            capital += sell_value

            profit = sell_value - (position['entry_price'] * shares + position['entry_cost'])
            profit_pct = profit / (position['entry_price'] * shares + position['entry_cost'])

            trade_record = {
                'entry_date': position['entry_date'],
                'exit_date': final_date,
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'shares': shares,
                'profit': profit,
                'profit_pct': profit_pct,
                'days_held': len(df) - 1 - position['entry_index'],
                'exit_reason': '回測結束強制平倉'
            }
            self.trades.append(trade_record)

            print(f"[{final_date}] 回測結束平倉 @ ${final_price:.2f} | "
                  f"報酬: {profit_pct*100:+.2f}%")

        # 計算績效指標
        final_equity = capital
        self.metrics = self._calculate_metrics(df)

        print(f"\n{'='*80}")
        print(f"回測完成")
        print(f"{'='*80}")
        print(f"最終淨值: ${final_equity:,.0f}")
        print(f"總報酬: {(final_equity/self.initial_capital - 1)*100:+.2f}%")
        print(f"交易次數: {len(self.trades)}")
        print(f"{'='*80}\n")

        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': (final_equity / self.initial_capital - 1),
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'metrics': self.metrics
        }

    def _calculate_metrics(self, df: pd.DataFrame) -> Dict:
        """計算績效指標"""
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_profit_pct': 0,
                'max_profit': 0,
                'max_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'avg_holding_days': 0
            }

        # 基本統計
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['profit'] > 0]
        losing_trades = [t for t in self.trades if t['profit'] <= 0]

        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0

        # 獲利統計
        profits = [t['profit'] for t in self.trades]
        profit_pcts = [t['profit_pct'] for t in self.trades]

        avg_profit = np.mean(profits) if profits else 0
        avg_profit_pct = np.mean(profit_pcts) if profit_pcts else 0
        max_profit = max(profits) if profits else 0
        max_loss = min(profits) if profits else 0

        # 獲利因子
        total_gains = sum([t['profit'] for t in winning_trades])
        total_losses = abs(sum([t['profit'] for t in losing_trades]))
        profit_factor = total_gains / total_losses if total_losses > 0 else float('inf')

        # Sharpe Ratio
        if len(profit_pcts) > 1:
            sharpe_ratio = np.mean(profit_pcts) / np.std(profit_pcts) * np.sqrt(252)
        else:
            sharpe_ratio = 0

        # 最大回撤
        equity_curve = [e['equity'] for e in self.equity_curve]
        max_drawdown = self._calculate_max_drawdown(equity_curve)

        # 平均持有天數
        holding_days = [t['days_held'] for t in self.trades]
        avg_holding_days = np.mean(holding_days) if holding_days else 0

        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_profit_pct': avg_profit_pct,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'avg_holding_days': avg_holding_days,
            'total_gains': total_gains,
            'total_losses': total_losses
        }

    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """計算最大回撤"""
        if not equity_curve:
            return 0

        max_drawdown = 0
        peak = equity_curve[0]

        for equity in equity_curve:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown

    def print_performance_report(self):
        """打印績效報告"""
        if not self.metrics:
            print("⚠️ 尚未執行回測")
            return

        m = self.metrics

        print(f"\n{'='*80}")
        print(f"績效報告 (Performance Report)")
        print(f"{'='*80}\n")

        # 總體表現
        print(f"【總體表現】")
        print(f"  初始資金: ${self.initial_capital:,.0f}")
        final_equity = self.equity_curve[-1]['equity'] if self.equity_curve else self.initial_capital
        print(f"  最終淨值: ${final_equity:,.0f}")
        total_return = (final_equity / self.initial_capital - 1) * 100
        print(f"  總報酬率: {total_return:+.2f}%")
        print(f"  最大回撤: {m['max_drawdown']*100:.2f}%")
        print(f"  Sharpe比率: {m['sharpe_ratio']:.2f}")

        # 交易統計
        print(f"\n【交易統計】")
        print(f"  總交易次數: {m['total_trades']}")
        print(f"  獲利次數: {m['winning_trades']}")
        print(f"  虧損次數: {m['losing_trades']}")
        print(f"  勝率: {m['win_rate']*100:.2f}%")
        print(f"  平均持有天數: {m['avg_holding_days']:.1f}天")

        # 獲利分析
        print(f"\n【獲利分析】")
        print(f"  平均獲利: ${m['avg_profit']:,.0f} ({m['avg_profit_pct']*100:+.2f}%)")
        print(f"  最大單筆獲利: ${m['max_profit']:,.0f}")
        print(f"  最大單筆虧損: ${m['max_loss']:,.0f}")
        print(f"  總獲利: ${m['total_gains']:,.0f}")
        print(f"  總虧損: ${m['total_losses']:,.0f}")
        print(f"  獲利因子: {m['profit_factor']:.2f}")

        # 交易明細
        print(f"\n【交易明細】")
        print(f"{'進場日期':<12} {'出場日期':<12} {'進場價':<8} {'出場價':<8} "
              f"{'報酬率':<10} {'持有天':<8} {'原因':<20}")
        print(f"{'-'*80}")

        for trade in self.trades:
            print(f"{str(trade['entry_date']):<12} {str(trade['exit_date']):<12} "
                  f"${trade['entry_price']:<7.2f} ${trade['exit_price']:<7.2f} "
                  f"{trade['profit_pct']*100:>+8.2f}% "
                  f"{trade['days_held']:>6}天 "
                  f"{trade['exit_reason']:<20}")

        print(f"\n{'='*80}\n")

    def export_results(self, filename: str = 'backtest_results.csv'):
        """導出回測結果到CSV"""
        if not self.trades:
            print("⚠️ 無交易記錄可導出")
            return

        df_trades = pd.DataFrame(self.trades)
        df_trades.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 交易記錄已導出到: {filename}")

        # 導出資金曲線
        if self.equity_curve:
            df_equity = pd.DataFrame(self.equity_curve)
            equity_filename = filename.replace('.csv', '_equity.csv')
            df_equity.to_csv(equity_filename, index=False, encoding='utf-8-sig')
            print(f"✅ 資金曲線已導出到: {equity_filename}")


class ComparisonBacktest:
    """
    策略比較回測

    比較不同策略或參數設定的表現
    """

    def __init__(self, df: pd.DataFrame):
        """
        初始化

        參數:
            df: 歷史數據 DataFrame
        """
        self.df = df
        self.results = {}

    def compare_strategies(self,
                          strategies: List[str] = ['basic', 'enhanced'],
                          initial_capital: float = 1000000) -> Dict:
        """
        比較多個策略

        參數:
            strategies: 策略列表
            initial_capital: 初始資金

        返回:
            comparison: 比較結果
        """
        print(f"\n{'='*80}")
        print(f"策略比較回測")
        print(f"{'='*80}\n")

        for strategy in strategies:
            print(f"\n測試策略: {strategy}")
            engine = BacktestingEngine(initial_capital=initial_capital)
            results = engine.run_backtest(self.df, strategy=strategy)

            self.results[strategy] = {
                'results': results,
                'engine': engine
            }

        # 比較結果
        print(f"\n{'='*80}")
        print(f"策略比較結果")
        print(f"{'='*80}\n")

        print(f"{'策略':<15} {'總報酬':<12} {'勝率':<10} {'交易次數':<10} "
              f"{'Sharpe':<10} {'最大回撤':<10}")
        print(f"{'-'*80}")

        for strategy, data in self.results.items():
            r = data['results']
            m = r['metrics']
            print(f"{strategy:<15} "
                  f"{r['total_return']*100:>+10.2f}% "
                  f"{m['win_rate']*100:>8.1f}% "
                  f"{m['total_trades']:>8} "
                  f"{m['sharpe_ratio']:>8.2f} "
                  f"{m['max_drawdown']*100:>8.2f}%")

        print(f"\n{'='*80}\n")

        return self.results


# ========== 使用示例 ==========

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║              回測系統 v1.0 - Backtesting Engine              ║
    ║           驗證股票預測策略的實際表現                          ║
    ╚════════════════════════════════════════════════════════════════╝

    功能：
    1. 📈 歷史數據回測
    2. 💰 交易成本計算（手續費、稅、滑價）
    3. 🎯 停損停利機制
    4. 📊 績效指標分析
    5. 🔄 策略比較

    使用方式：
    見 backtesting_examples.py
    """)
