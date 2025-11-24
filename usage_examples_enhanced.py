"""
增强版智能选股系统使用示例
演示如何整合FinMind API数据进行台股波段预测

依赖套件：
pip install FinMind pandas numpy yfinance

FinMind注册：https://finmindtrade.com/
免费版限制：300次/小时
注册会员：600次/小时
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# 导入增强版分析器
from smart_stock_picker_enhanced_v3 import (
    EnhancedStockPicker,
    print_enhanced_analysis_report
)


class TaiwanStockDataFetcher:
    """
    台股数据获取器
    整合FinMind API和yfinance
    """
    
    def __init__(self, finmind_token: str = None):
        """
        初始化数据获取器
        
        参数:
            finmind_token: FinMind API Token (可选，注册后获得更高请求限制)
        """
        try:
            from FinMind.data import DataLoader
            self.api = DataLoader()
            
            if finmind_token:
                self.api.login_by_token(api_token=finmind_token)
                print("✅ FinMind API 已登录（会员模式）")
            else:
                print("⚠️ 使用FinMind免费模式（300次/小时限制）")
        except ImportError:
            print("❌ 请先安装FinMind: pip install FinMind")
            self.api = None
    
    def get_price_data(self, stock_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取股价数据
        
        参数:
            stock_id: 股票代码（如 '2330'）
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        """
        if self.api is None:
            return self._get_price_from_yfinance(stock_id, start_date, end_date)
        
        try:
            # 设置默认日期
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # 从FinMind获取数据
            df = self.api.taiwan_stock_daily(
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is None or len(df) == 0:
                print(f"⚠️ FinMind无数据，尝试使用yfinance")
                return self._get_price_from_yfinance(stock_id, start_date, end_date)
            
            # 标准化列名
            df = df.rename(columns={
                'date': 'date',
                'open': 'open',
                'max': 'high',
                'min': 'low',
                'close': 'close',
                'Trading_Volume': 'volume'
            })
            
            # 确保日期格式
            df['date'] = pd.to_datetime(df['date'])
            
            # 选择需要的列
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            
            print(f"✅ 成功从FinMind获取 {stock_id} 股价数据 ({len(df)} 笔)")
            return df
            
        except Exception as e:
            print(f"❌ FinMind获取失败: {e}")
            return self._get_price_from_yfinance(stock_id, start_date, end_date)
    
    def _get_price_from_yfinance(self, stock_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """备用方案：从yfinance获取数据"""
        try:
            import yfinance as yf
            
            # 台股需要加.TW后缀
            symbol = f"{stock_id}.TW"
            
            # 下载数据
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if df is None or len(df) == 0:
                print(f"❌ yfinance也无法获取 {stock_id} 数据")
                return None
            
            # 重置索引
            df = df.reset_index()
            
            # 标准化列名
            df.columns = [col.lower() for col in df.columns]
            df = df.rename(columns={'adj close': 'adj_close'})
            
            # 选择需要的列
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            
            print(f"✅ 从yfinance获取 {stock_id} 数据 ({len(df)} 笔)")
            return df
            
        except Exception as e:
            print(f"❌ yfinance获取失败: {e}")
            return None
    
    def get_institutional_data(self, stock_id: str, start_date: str = None, lookback_days: int = 30) -> pd.DataFrame:
        """
        获取三大法人买卖超数据
        
        参数:
            stock_id: 股票代码
            start_date: 开始日期（如果为None，则往前推lookback_days天）
            lookback_days: 回溯天数
        """
        if self.api is None:
            print("⚠️ 需要FinMind API才能获取法人数据")
            return None
        
        try:
            # 设置日期范围
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 获取数据
            df = self.api.taiwan_stock_institutional_investors(
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is None or len(df) == 0:
                print(f"⚠️ {stock_id} 无法人数据")
                return None
            
            # 计算净买超
            df['foreign_net'] = df['buy'] - df['sell']  # 外资
            df['trust_net'] = 0  # 投信（需要额外处理）
            df['dealer_net'] = 0  # 自营商（需要额外处理）
            
            # 注意：FinMind的法人数据结构可能需要调整
            # 这里提供基本框架，实际使用时需根据API返回调整
            
            print(f"✅ 成功获取 {stock_id} 法人数据 ({len(df)} 笔)")
            return df
            
        except Exception as e:
            print(f"❌ 获取法人数据失败: {e}")
            return None
    
    def get_margin_data(self, stock_id: str, start_date: str = None, lookback_days: int = 30) -> pd.DataFrame:
        """
        获取融资融券数据
        
        参数:
            stock_id: 股票代码
            start_date: 开始日期
            lookback_days: 回溯天数
        """
        if self.api is None:
            print("⚠️ 需要FinMind API才能获取融资融券数据")
            return None
        
        try:
            # 设置日期范围
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 获取数据
            df = self.api.taiwan_stock_margin_purchase_short_sale(
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is None or len(df) == 0:
                print(f"⚠️ {stock_id} 无融资融券数据")
                return None
            
            # 计算指标
            df['margin_usage_rate'] = (
                df['MarginPurchaseTodayBalance'] / 
                (df['MarginPurchaseLimit'] + 1) * 100
            )
            
            df['short_margin_ratio'] = (
                df['ShortSaleTodayBalance'] / 
                (df['MarginPurchaseTodayBalance'] + 1) * 100
            )
            
            df['margin_change_pct'] = (
                df['MarginPurchaseTodayBalance'].pct_change() * 100
            )
            
            # 当冲比例（如果有数据）
            df['day_trade_ratio'] = 0  # 需要额外获取
            
            print(f"✅ 成功获取 {stock_id} 融资融券数据 ({len(df)} 笔)")
            return df
            
        except Exception as e:
            print(f"❌ 获取融资融券数据失败: {e}")
            return None


# ========== 使用示例 ==========

def example_1_basic_analysis():
    """示例1: 基础分析（仅使用价格数据）"""
    print("\n" + "="*80)
    print("示例1: 基础技术分析（仅价格数据）")
    print("="*80)
    
    # 初始化数据获取器（不需要token）
    fetcher = TaiwanStockDataFetcher()
    
    # 获取台积电数据
    stock_id = '2330'
    print(f"\n正在分析 {stock_id} (台积电)...")
    
    price_data = fetcher.get_price_data(
        stock_id=stock_id,
        start_date='2023-01-01'
    )
    
    if price_data is None:
        print("❌ 无法获取数据")
        return
    
    # 创建增强版分析器
    picker = EnhancedStockPicker()
    
    # 分析股票（仅技术面）
    analysis = picker.analyze_stock_enhanced(
        symbol=stock_id,
        price_data=price_data,
        institutional_data=None,  # 不使用法人数据
        margin_data=None          # 不使用融资融券数据
    )
    
    # 打印报告
    print_enhanced_analysis_report(analysis)


def example_2_full_analysis_with_finmind():
    """示例2: 完整分析（整合FinMind法人和融资融券数据）"""
    print("\n" + "="*80)
    print("示例2: 完整多因子分析（需要FinMind API）")
    print("="*80)
    
    # 初始化数据获取器（可选：输入你的token）
    finmind_token = None  # 在这里输入你的FinMind token
    fetcher = TaiwanStockDataFetcher(finmind_token=finmind_token)
    
    if fetcher.api is None:
        print("⚠️ 跳过完整分析示例（需要FinMind）")
        return
    
    # 分析多支股票
    stock_list = ['2330', '2454', '2317']  # 台积电、联发科、鸿海
    
    for stock_id in stock_list:
        print(f"\n{'='*80}")
        print(f"正在分析 {stock_id}...")
        print(f"{'='*80}")
        
        # 1. 获取价格数据
        price_data = fetcher.get_price_data(stock_id, start_date='2023-01-01')
        
        if price_data is None:
            print(f"❌ {stock_id} 无价格数据，跳过")
            continue
        
        # 2. 获取法人数据
        institutional_data = fetcher.get_institutional_data(stock_id, lookback_days=30)
        
        # 3. 获取融资融券数据
        margin_data = fetcher.get_margin_data(stock_id, lookback_days=30)
        
        # 4. 执行完整分析
        picker = EnhancedStockPicker()
        analysis = picker.analyze_stock_enhanced(
            symbol=stock_id,
            price_data=price_data,
            institutional_data=institutional_data,
            margin_data=margin_data
        )
        
        # 5. 打印报告
        print_enhanced_analysis_report(analysis)
        
        # 延迟避免API请求过快
        time.sleep(1)


def example_3_batch_screening():
    """示例3: 批量筛选优质股票"""
    print("\n" + "="*80)
    print("示例3: 批量筛选台股（半导体类股）")
    print("="*80)
    
    # 半导体龙头股票
    semiconductor_stocks = [
        '2330',  # 台积电
        '2454',  # 联发科
        '2303',  # 联电
        '3034',  # 联咏
        '2379',  # 瑞昱
    ]
    
    fetcher = TaiwanStockDataFetcher()
    picker = EnhancedStockPicker()
    
    results = []
    
    for stock_id in semiconductor_stocks:
        print(f"\n分析 {stock_id}...", end=" ")
        
        # 获取数据
        price_data = fetcher.get_price_data(stock_id, start_date='2023-01-01')
        
        if price_data is None:
            print("❌ 无数据")
            continue
        
        # 分析
        analysis = picker.analyze_stock_enhanced(
            symbol=stock_id,
            price_data=price_data
        )
        
        if 'error' in analysis:
            print(f"❌ {analysis['error']}")
            continue
        
        # 收集结果
        results.append({
            'Stock_ID': stock_id,
            'Score': analysis.get('enhanced_score', analysis.get('total_score', 0)),
            'Signal': analysis.get('enhanced_signal', 'neutral'),
            'Current_Price': analysis.get('current_price', 0),
            'Target_Price': analysis.get('target_price', 0),
            'Expected_Return': analysis.get('expected_return', 0),
            'Risk_Reward': analysis.get('risk_reward_ratio', 0)
        })
        
        print("✅")
        time.sleep(0.5)
    
    # 显示筛选结果
    if results:
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('Score', ascending=False)
        
        print("\n" + "="*80)
        print("筛选结果（按评分排序）")
        print("="*80)
        print(df_results.to_string(index=False))
        
        # 显示前三名的详细分析
        print("\n" + "="*80)
        print("前三名详细分析")
        print("="*80)
        
        for stock_id in df_results['Stock_ID'].head(3):
            price_data = fetcher.get_price_data(stock_id, start_date='2023-01-01')
            analysis = picker.analyze_stock_enhanced(stock_id, price_data)
            print_enhanced_analysis_report(analysis)
            print("\n")
    else:
        print("❌ 无有效筛选结果")


def example_4_compare_strategies():
    """示例4: 比较原版与增强版策略"""
    print("\n" + "="*80)
    print("示例4: 策略比较（原版 vs 增强版）")
    print("="*80)
    
    fetcher = TaiwanStockDataFetcher()
    picker = EnhancedStockPicker()
    
    stock_id = '2330'
    print(f"\n分析 {stock_id} (台积电)")
    
    price_data = fetcher.get_price_data(stock_id, start_date='2023-01-01')
    
    if price_data is None:
        print("❌ 无法获取数据")
        return
    
    # 原版分析
    print("\n【原版分析】")
    print("-"*80)
    base_analysis = picker.analyze_stock(stock_id, price_data, 'moderate')
    print(f"总分: {base_analysis.get('total_score', 0):.1f}/100")
    print(f"评级: {base_analysis.get('rating', 'N/A')}")
    print(f"动作: {base_analysis.get('action', 'N/A')}")
    
    # 增强版分析
    print("\n【增强版分析】")
    print("-"*80)
    enhanced_analysis = picker.analyze_stock_enhanced(stock_id, price_data)
    print(f"总分: {enhanced_analysis.get('enhanced_score', 0):.1f}/100")
    print(f"信号: {enhanced_analysis.get('enhanced_signal', 'N/A')}")
    print(f"建议: {enhanced_analysis.get('enhanced_recommendation', 'N/A')}")
    
    if 'score_breakdown' in enhanced_analysis:
        print(f"\n评分细节:")
        breakdown = enhanced_analysis['score_breakdown']
        print(f"  技术面: {breakdown['technical']:.1f}/40")
        print(f"  市场面: {breakdown['market']:.1f}/30")
        print(f"  筹码面: {breakdown['chips']:.1f}/30")


# ========== 主程序 ==========

def main():
    """主程序 - 运行所有示例"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          增强版智能选股系统 - 使用示例                        ║
    ║     Enhanced Stock Picker Usage Examples                     ║
    ╚════════════════════════════════════════════════════════════════╝
    
    示例说明：
    1. 基础分析 - 仅使用价格数据（不需要FinMind）
    2. 完整分析 - 整合法人和融资融券数据（需要FinMind）
    3. 批量筛选 - 筛选半导体类股
    4. 策略比较 - 比较原版与增强版
    
    注意事项：
    - 示例1不需要任何API token
    - 示例2-4需要FinMind账号（免费版即可）
    - FinMind注册：https://finmindtrade.com/
    """)
    
    # 选择要运行的示例
    print("\n可用示例:")
    print("1. 基础分析（推荐，无需API）")
    print("2. 完整分析（需要FinMind）")
    print("3. 批量筛选")
    print("4. 策略比较")
    print("0. 运行所有示例")
    
    choice = input("\n请选择 (0-4): ").strip()
    
    try:
        if choice == '1':
            example_1_basic_analysis()
        elif choice == '2':
            example_2_full_analysis_with_finmind()
        elif choice == '3':
            example_3_batch_screening()
        elif choice == '4':
            example_4_compare_strategies()
        elif choice == '0':
            example_1_basic_analysis()
            input("\n按Enter继续...")
            example_3_batch_screening()
            input("\n按Enter继续...")
            example_4_compare_strategies()
            print("\n⚠️ 跳过示例2（需要手动配置FinMind token）")
        else:
            print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
