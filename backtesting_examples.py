"""
回測系統使用範例
示範如何使用回測引擎驗證策略表現

使用方式：
python backtesting_examples.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sys
import os

# 添加當前目錄到路徑
sys.path.append(os.path.dirname(__file__))

from backtesting_engine import BacktestingEngine, ComparisonBacktest
from unified_stock_data_manager import UnifiedStockDataManager


def example_1_basic_backtest():
    """範例1: 基本回測 - 單一股票"""
    print("\n" + "="*80)
    print("範例1: 基本回測 - 台積電 (2330)")
    print("="*80 + "\n")

    # 1. 載入數據
    manager = UnifiedStockDataManager(data_dir='./stock_data')

    # 嘗試載入本地數據
    df = manager.load_stock_data('2330')

    if df is None or len(df) < 200:
        print("本地無數據，開始下載...")
        df = manager.download_stock_data('2330', period='2y')

    if df is None:
        print("❌ 無法獲取數據")
        return

    print(f"數據期間: {df['date'].iloc[0]} ~ {df['date'].iloc[-1]}")
    print(f"數據筆數: {len(df)}")

    # 2. 執行回測
    engine = BacktestingEngine(
        initial_capital=1000000,   # 100萬初始資金
        commission_rate=0.001425,  # 0.1425% 手續費
        tax_rate=0.003,            # 0.3% 證交稅
        slippage=0.001             # 0.1% 滑價
    )

    results = engine.run_backtest(
        df=df,
        strategy='enhanced',      # 使用增強版策略
        position_size=0.3,        # 30% 倉位
        stop_loss=-0.08,          # -8% 停損
        take_profit=0.15,         # 15% 停利
        rebalance_days=5          # 每5天重新評估
    )

    # 3. 顯示績效報告
    engine.print_performance_report()

    # 4. 導出結果
    engine.export_results('backtest_2330.csv')

    # 5. 繪製資金曲線
    plot_equity_curve(engine.equity_curve, '2330 回測資金曲線')

    return results


def example_2_compare_parameters():
    """範例2: 參數比較 - 測試不同倉位大小"""
    print("\n" + "="*80)
    print("範例2: 參數比較 - 不同倉位大小")
    print("="*80 + "\n")

    # 載入數據
    manager = UnifiedStockDataManager(data_dir='./stock_data')
    df = manager.load_stock_data('2330')

    if df is None:
        df = manager.download_stock_data('2330', period='2y')

    if df is None:
        print("❌ 無法獲取數據")
        return

    # 測試不同的倉位大小
    position_sizes = [0.2, 0.3, 0.5, 0.7]
    results_comparison = {}

    for pos_size in position_sizes:
        print(f"\n測試倉位: {pos_size*100:.0f}%")
        print("-" * 50)

        engine = BacktestingEngine(initial_capital=1000000)
        results = engine.run_backtest(
            df=df,
            strategy='enhanced',
            position_size=pos_size,
            stop_loss=-0.08,
            take_profit=0.15
        )

        results_comparison[f'{pos_size*100:.0f}%'] = {
            'total_return': results['total_return'],
            'win_rate': results['metrics']['win_rate'],
            'max_drawdown': results['metrics']['max_drawdown'],
            'sharpe_ratio': results['metrics']['sharpe_ratio'],
            'total_trades': results['metrics']['total_trades']
        }

    # 比較結果
    print(f"\n{'='*80}")
    print("參數比較結果")
    print(f"{'='*80}\n")

    print(f"{'倉位':<10} {'總報酬':<12} {'勝率':<10} {'交易次數':<10} "
          f"{'Sharpe':<10} {'最大回撤':<10}")
    print("-" * 80)

    for pos, metrics in results_comparison.items():
        print(f"{pos:<10} "
              f"{metrics['total_return']*100:>+10.2f}% "
              f"{metrics['win_rate']*100:>8.1f}% "
              f"{metrics['total_trades']:>8} "
              f"{metrics['sharpe_ratio']:>8.2f} "
              f"{metrics['max_drawdown']*100:>8.2f}%")

    print(f"\n{'='*80}\n")

    return results_comparison


def example_3_multiple_stocks():
    """範例3: 多檔股票回測"""
    print("\n" + "="*80)
    print("範例3: 多檔股票回測")
    print("="*80 + "\n")

    # 要測試的股票列表
    symbols = ['2330', '2317', '2454', '3008', '2308']
    manager = UnifiedStockDataManager(data_dir='./stock_data')

    all_results = {}

    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"回測股票: {symbol}")
        print(f"{'='*60}")

        # 載入數據
        df = manager.load_stock_data(symbol)
        if df is None or len(df) < 200:
            print(f"下載 {symbol} 數據...")
            df = manager.download_stock_data(symbol, period='2y')

        if df is None or len(df) < 200:
            print(f"⚠️ {symbol} 數據不足，跳過")
            continue

        # 執行回測
        engine = BacktestingEngine(initial_capital=1000000)
        results = engine.run_backtest(
            df=df,
            strategy='enhanced',
            position_size=0.3,
            stop_loss=-0.08,
            take_profit=0.15
        )

        all_results[symbol] = {
            'total_return': results['total_return'],
            'win_rate': results['metrics']['win_rate'],
            'sharpe_ratio': results['metrics']['sharpe_ratio'],
            'max_drawdown': results['metrics']['max_drawdown'],
            'total_trades': results['metrics']['total_trades']
        }

    # 綜合比較
    print(f"\n{'='*80}")
    print("多檔股票回測結果比較")
    print(f"{'='*80}\n")

    print(f"{'股票':<10} {'總報酬':<12} {'勝率':<10} {'交易次數':<10} "
          f"{'Sharpe':<10} {'最大回撤':<10}")
    print("-" * 80)

    for symbol, metrics in all_results.items():
        print(f"{symbol:<10} "
              f"{metrics['total_return']*100:>+10.2f}% "
              f"{metrics['win_rate']*100:>8.1f}% "
              f"{metrics['total_trades']:>8} "
              f"{metrics['sharpe_ratio']:>8.2f} "
              f"{metrics['max_drawdown']*100:>8.2f}%")

    # 計算平均表現
    avg_return = np.mean([m['total_return'] for m in all_results.values()])
    avg_win_rate = np.mean([m['win_rate'] for m in all_results.values()])
    avg_sharpe = np.mean([m['sharpe_ratio'] for m in all_results.values()])

    print("-" * 80)
    print(f"{'平均':<10} "
          f"{avg_return*100:>+10.2f}% "
          f"{avg_win_rate*100:>8.1f}% "
          f"{'N/A':<8} "
          f"{avg_sharpe:>8.2f} "
          f"{'N/A':<8}")

    print(f"\n{'='*80}\n")

    return all_results


def example_4_stop_loss_optimization():
    """範例4: 停損停利參數優化"""
    print("\n" + "="*80)
    print("範例4: 停損停利參數優化")
    print("="*80 + "\n")

    # 載入數據
    manager = UnifiedStockDataManager(data_dir='./stock_data')
    df = manager.load_stock_data('2330')

    if df is None:
        df = manager.download_stock_data('2330', period='2y')

    if df is None:
        print("❌ 無法獲取數據")
        return

    # 測試不同的停損停利組合
    stop_losses = [-0.05, -0.08, -0.10]
    take_profits = [0.10, 0.15, 0.20]

    best_result = None
    best_params = None
    best_sharpe = -999

    results_grid = []

    for stop_loss in stop_losses:
        for take_profit in take_profits:
            print(f"\n測試參數: 停損={stop_loss*100:.0f}%, 停利={take_profit*100:.0f}%")

            engine = BacktestingEngine(initial_capital=1000000)
            results = engine.run_backtest(
                df=df,
                strategy='enhanced',
                position_size=0.3,
                stop_loss=stop_loss,
                take_profit=take_profit,
                rebalance_days=5
            )

            sharpe = results['metrics']['sharpe_ratio']

            results_grid.append({
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'total_return': results['total_return'],
                'win_rate': results['metrics']['win_rate'],
                'sharpe_ratio': sharpe,
                'max_drawdown': results['metrics']['max_drawdown'],
                'total_trades': results['metrics']['total_trades']
            })

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_result = results
                best_params = (stop_loss, take_profit)

    # 顯示結果
    print(f"\n{'='*80}")
    print("停損停利參數優化結果")
    print(f"{'='*80}\n")

    print(f"{'停損':<10} {'停利':<10} {'總報酬':<12} {'勝率':<10} "
          f"{'Sharpe':<10} {'回撤':<10} {'交易':<10}")
    print("-" * 80)

    for r in results_grid:
        marker = " ⭐" if (r['stop_loss'], r['take_profit']) == best_params else ""
        print(f"{r['stop_loss']*100:>8.0f}% "
              f"{r['take_profit']*100:>8.0f}% "
              f"{r['total_return']*100:>+10.2f}% "
              f"{r['win_rate']*100:>8.1f}% "
              f"{r['sharpe_ratio']:>8.2f} "
              f"{r['max_drawdown']*100:>8.2f}% "
              f"{r['total_trades']:>6}{marker}")

    print(f"\n最佳參數: 停損={best_params[0]*100:.0f}%, 停利={best_params[1]*100:.0f}%")
    print(f"最佳Sharpe比率: {best_sharpe:.2f}")
    print(f"\n{'='*80}\n")

    return results_grid


def plot_equity_curve(equity_curve: list, title: str = '資金曲線'):
    """繪製資金曲線"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib import font_manager
        import platform

        # 設定中文字體
        if platform.system() == 'Windows':
            plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
        else:
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        dates = [e['date'] for e in equity_curve]
        equity = [e['equity'] for e in equity_curve]

        plt.figure(figsize=(12, 6))
        plt.plot(dates, equity, linewidth=2, label='淨值')
        plt.axhline(y=equity[0], color='r', linestyle='--', alpha=0.5, label='初始資金')

        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('淨值 (元)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)

        # 格式化日期軸
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gcf().autofmt_xdate()

        plt.tight_layout()
        plt.savefig('equity_curve.png', dpi=300, bbox_inches='tight')
        print(f"✅ 資金曲線已保存到: equity_curve.png")

        # plt.show()  # 取消註解以顯示圖表

    except ImportError:
        print("⚠️ matplotlib 未安裝，無法繪製圖表")
        print("   請執行: pip install matplotlib")
    except Exception as e:
        print(f"⚠️ 繪圖錯誤: {e}")


def main():
    """主程式"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║              回測系統使用範例                                  ║
    ║              Backtesting Examples                             ║
    ╚════════════════════════════════════════════════════════════════╝

    請選擇範例：
    1. 基本回測 - 單一股票 (台積電 2330)
    2. 參數比較 - 不同倉位大小
    3. 多檔股票回測
    4. 停損停利參數優化
    5. 執行全部範例

    0. 退出
    """)

    while True:
        try:
            choice = input("\n請輸入選項 (0-5): ").strip()

            if choice == '0':
                print("👋 再見！")
                break
            elif choice == '1':
                example_1_basic_backtest()
            elif choice == '2':
                example_2_compare_parameters()
            elif choice == '3':
                example_3_multiple_stocks()
            elif choice == '4':
                example_4_stop_loss_optimization()
            elif choice == '5':
                print("\n執行全部範例...\n")
                example_1_basic_backtest()
                example_2_compare_parameters()
                example_3_multiple_stocks()
                example_4_stop_loss_optimization()
                print("\n✅ 全部範例執行完畢！")
                break
            else:
                print("❌ 無效的選項，請重新輸入")

        except KeyboardInterrupt:
            print("\n\n👋 程式已中斷")
            break
        except Exception as e:
            print(f"\n❌ 錯誤: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
