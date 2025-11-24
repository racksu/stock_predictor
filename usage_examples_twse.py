"""
使用TWSE官方API的完整範例
替代FinMind，無需Token

示範如何使用TWSE API進行完整的股票分析
"""

import pandas as pd
from datetime import datetime, timedelta
from twse_data_source import TWSEDataSource
from smart_stock_picker_enhanced_v3 import (
    EnhancedStockPicker,
    EnhancedStockAnalyzer,
    MarketAnalyzer,
    ChipsAnalyzer,
    print_enhanced_analysis_report
)


class TWSTockDataFetcher:
    """
    台股數據獲取器（使用TWSE API）
    替代FinMind，無Token限制
    """

    def __init__(self):
        """初始化數據獲取器"""
        self.twse = TWSEDataSource()
        print("✅ 台股數據獲取器已初始化（TWSE官方API）")

    def get_price_data(self,
                      stock_no: str,
                      start_date: str = None,
                      lookback_days: int = 365) -> pd.DataFrame:
        """
        獲取股票價格數據

        參數:
            stock_no: 股票代號（如 '2330'）
            start_date: 開始日期（格式：'2023-01-01'）
            lookback_days: 回溯天數（默認365天）

        返回:
            標準化的價格DataFrame
        """
        if start_date is None:
            end_date = datetime.now()
            start_date = (end_date - timedelta(days=lookback_days)).strftime('%Y-%m-%d')

        print(f"\n📥 獲取 {stock_no} 的價格數據...")

        df = self.twse.get_stock_historical_data(stock_no, start_date)

        if df is None or len(df) == 0:
            print(f"❌ 無法獲取 {stock_no} 的價格數據")
            return None

        # 標準化欄位名稱（與系統其他部分一致）
        df = df.rename(columns={
            'volume': 'Volume',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close'
        })

        # 確保日期格式
        df['date'] = pd.to_datetime(df['date'])

        print(f"✅ 成功獲取 {len(df)} 筆價格數據")
        print(f"   日期範圍: {df['date'].min()} 至 {df['date'].max()}")

        return df

    def get_institutional_data(self,
                              stock_no: str,
                              lookback_days: int = 30) -> pd.DataFrame:
        """
        獲取三大法人買賣超數據

        參數:
            stock_no: 股票代號
            lookback_days: 回溯天數

        返回:
            法人數據DataFrame
        """
        print(f"\n📥 獲取 {stock_no} 的三大法人數據...")

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')

        df = self.twse.get_institutional_investors_range(
            stock_no, start_date, end_date, lookback_days
        )

        if df is None or len(df) == 0:
            print(f"⚠️ 無法獲取 {stock_no} 的法人數據")
            return None

        print(f"✅ 成功獲取 {len(df)} 筆法人數據")

        return df

    def get_margin_data(self,
                       stock_no: str,
                       lookback_days: int = 30) -> pd.DataFrame:
        """
        獲取融資融券數據

        參數:
            stock_no: 股票代號
            lookback_days: 回溯天數

        返回:
            融資融券DataFrame
        """
        print(f"\n📥 獲取 {stock_no} 的融資融券數據...")

        df = self.twse.get_margin_trading_range(stock_no, lookback_days)

        if df is None or len(df) == 0:
            print(f"⚠️ 無法獲取 {stock_no} 的融資融券數據")
            return None

        # 添加變化百分比
        if len(df) > 1:
            df['margin_change_pct'] = df['margin_balance'].pct_change() * 100

        print(f"✅ 成功獲取 {len(df)} 筆融資融券數據")

        return df


# ========== 完整分析範例 ==========

def example_full_analysis():
    """
    範例1：完整的台股分析（使用TWSE API）
    """
    print("\n" + "="*80)
    print("範例1：完整台股分析 - 台積電(2330)")
    print("使用TWSE官方API，無需FinMind Token")
    print("="*80)

    # 1. 初始化
    fetcher = TWSTockDataFetcher()
    picker = EnhancedStockPicker()

    stock_no = '2330'  # 台積電

    # 2. 獲取價格數據（2年）
    price_data = fetcher.get_price_data(stock_no, lookback_days=730)

    if price_data is None:
        print("❌ 無法獲取價格數據，結束分析")
        return

    # 3. 獲取法人數據（30天）
    institutional_data = fetcher.get_institutional_data(stock_no, lookback_days=30)

    # 4. 獲取融資融券數據（30天）
    margin_data = fetcher.get_margin_data(stock_no, lookback_days=30)

    # 5. 執行完整分析
    print(f"\n🔍 開始分析 {stock_no}...")

    analysis = picker.analyze_stock_enhanced(
        symbol=stock_no,
        price_data=price_data,
        institutional_data=institutional_data,
        margin_data=margin_data,
        use_macro=True  # 啟用總體經濟分析
    )

    # 6. 顯示結果
    if 'error' in analysis:
        print(f"❌ 分析失敗: {analysis['error']}")
    else:
        print_enhanced_analysis_report(analysis)


def example_batch_analysis():
    """
    範例2：批量分析多支台股
    """
    print("\n" + "="*80)
    print("範例2：批量分析台股熱門股票")
    print("="*80)

    fetcher = TWSTockDataFetcher()
    picker = EnhancedStockPicker()

    # 台股熱門股票清單
    stocks = {
        '2330': '台積電',
        '2317': '鴻海',
        '2454': '聯發科',
        '2881': '富邦金',
        '2882': '國泰金'
    }

    results = []

    for stock_no, stock_name in stocks.items():
        print(f"\n{'='*60}")
        print(f"分析: {stock_no} {stock_name}")
        print(f"{'='*60}")

        try:
            # 獲取價格數據（1年）
            price_data = fetcher.get_price_data(stock_no, lookback_days=365)

            if price_data is None or len(price_data) < 200:
                print(f"⚠️ {stock_no} 數據不足，跳過")
                continue

            # 執行分析（不包含法人和融資融券以加快速度）
            analysis = picker.analyze_stock_enhanced(
                symbol=stock_no,
                price_data=price_data,
                use_macro=False  # 批量分析時關閉總經（避免重複請求）
            )

            if 'error' not in analysis:
                results.append({
                    'stock_no': stock_no,
                    'stock_name': stock_name,
                    'score': analysis.get('enhanced_score', 0),
                    'signal': analysis.get('enhanced_signal', 'N/A'),
                    'current_price': analysis.get('current_price', 0),
                    'target_price': analysis.get('target_price', 0),
                    'expected_return': analysis.get('expected_return', 0),
                    'risk_reward_ratio': analysis.get('risk_reward_ratio', 0)
                })

                print(f"✅ 評分: {analysis.get('enhanced_score', 0):.1f}/100")
                print(f"   信號: {analysis.get('enhanced_signal', 'N/A')}")
                print(f"   預期報酬: {analysis.get('expected_return', 0):.1%}")

        except Exception as e:
            print(f"❌ 分析 {stock_no} 時發生錯誤: {e}")

    # 顯示匯總結果
    if results:
        print(f"\n{'='*80}")
        print("匯總結果（按評分排序）")
        print(f"{'='*80}")

        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('score', ascending=False)

        print("\n")
        print(df_results.to_string(index=False))

        print(f"\n🏆 最佳標的: {df_results.iloc[0]['stock_no']} {df_results.iloc[0]['stock_name']}")
        print(f"   評分: {df_results.iloc[0]['score']:.1f}/100")
        print(f"   預期報酬: {df_results.iloc[0]['expected_return']:.1%}")


def example_realtime_monitoring():
    """
    範例3：即時監控三大法人動向
    """
    print("\n" + "="*80)
    print("範例3：即時監控三大法人買賣超")
    print("="*80)

    twse = TWSEDataSource()

    # 監控的股票清單
    watch_list = ['2330', '2317', '2454', '2881', '2882']

    today = datetime.now().strftime('%Y%m%d')

    print(f"\n📅 日期: {today}")
    print(f"📊 監控標的: {len(watch_list)} 支\n")

    results = []

    for stock_no in watch_list:
        df_inst = twse.get_institutional_investors(today, stock_no)

        if df_inst is not None and len(df_inst) > 0:
            row = df_inst.iloc[0]
            results.append({
                '代號': stock_no,
                '名稱': row['stock_name'],
                '外資': f"{row['foreign_net']:,}",
                '投信': f"{row['trust_net']:,}",
                '自營': f"{row['dealer_net']:,}",
                '合計': f"{row['total_net']:,}"
            })

    if results:
        df_summary = pd.DataFrame(results)
        print(df_summary.to_string(index=False))

        # 分析趨勢
        print(f"\n📈 趨勢分析:")
        for result in results:
            total = int(result['合計'].replace(',', ''))
            if total > 1000:
                print(f"   🔹 {result['代號']} {result['名稱']}: 三大法人買超 {result['合計']} 張 ✅")
            elif total < -1000:
                print(f"   🔹 {result['代號']} {result['名稱']}: 三大法人賣超 {result['合計']} 張 ⚠️")


def example_margin_analysis():
    """
    範例4：融資融券深度分析
    """
    print("\n" + "="*80)
    print("範例4：融資融券深度分析")
    print("="*80)

    twse = TWSEDataSource()
    stock_no = '2330'

    # 獲取30天融資融券資料
    df_margin = twse.get_margin_trading_range(stock_no, lookback_days=30)

    if df_margin is None or len(df_margin) == 0:
        print(f"❌ 無法獲取融資融券數據")
        return

    print(f"\n📊 {stock_no} 融資融券分析\n")

    # 最新數據
    latest = df_margin.iloc[-1]

    print(f"【最新數據】({latest['date'].strftime('%Y-%m-%d')})")
    print(f"  融資餘額: {latest['margin_balance']:,.0f} 張")
    print(f"  融資使用率: {latest['margin_usage_rate']:.2f}%")
    print(f"  融券餘額: {latest['short_balance']:,.0f} 張")
    print(f"  券資比: {latest['short_margin_ratio']:.2f}%")

    # 趨勢分析
    if len(df_margin) >= 5:
        margin_5d_change = (latest['margin_balance'] - df_margin.iloc[-6]['margin_balance'])
        short_5d_change = (latest['short_balance'] - df_margin.iloc[-6]['short_balance'])

        print(f"\n【5日變化】")
        print(f"  融資增減: {margin_5d_change:+,.0f} 張 ({margin_5d_change/df_margin.iloc[-6]['margin_balance']*100:+.2f}%)")
        print(f"  融券增減: {short_5d_change:+,.0f} 張 ({short_5d_change/df_margin.iloc[-6]['short_balance']*100:+.2f}%)")

    # 解讀
    print(f"\n【解讀】")
    if latest['margin_usage_rate'] < 30:
        print("  ✅ 融資使用率低，散戶不積極，可能接近底部")
    elif latest['margin_usage_rate'] > 70:
        print("  ⚠️ 融資使用率高，散戶過度樂觀，注意頂部風險")
    else:
        print("  ➡️ 融資使用率正常")

    if latest['short_margin_ratio'] < 10:
        print("  ✅ 券資比低，看多力量強")
    elif latest['short_margin_ratio'] > 20:
        print("  ⚠️ 券資比高，看空力量強")
    else:
        print("  ➡️ 券資比正常")


# ========== 主程式 ==========

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║     使用TWSE官方API的台股分析範例                              ║
    ║              No Token Required - Free Forever                 ║
    ╚════════════════════════════════════════════════════════════════╝

    本範例展示如何使用TWSE官方API進行完整的台股分析，
    完全替代FinMind，無需Token，永久免費！

    包含範例：
    1. 完整分析（技術+法人+籌碼+總經）
    2. 批量分析多支股票
    3. 即時監控三大法人
    4. 融資融券深度分析

    注意事項：
    - 請遵守TWSE使用條款
    - 建議請求間隔3-5秒
    - 週末及國定假日無數據
    """)

    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("\n請選擇範例:")
        print("  1. 完整分析（台積電）")
        print("  2. 批量分析（熱門股票）")
        print("  3. 即時監控法人")
        print("  4. 融資融券分析")
        print("  0. 全部執行")

        mode = input("\n請輸入選項 (0-4): ").strip()

    if mode == '1':
        example_full_analysis()
    elif mode == '2':
        example_batch_analysis()
    elif mode == '3':
        example_realtime_monitoring()
    elif mode == '4':
        example_margin_analysis()
    elif mode == '0':
        example_full_analysis()
        input("\n按Enter繼續下一個範例...")
        example_batch_analysis()
        input("\n按Enter繼續下一個範例...")
        example_realtime_monitoring()
        input("\n按Enter繼續下一個範例...")
        example_margin_analysis()
    else:
        print("請選擇有效選項！")

    print("\n" + "="*80)
    print("✅ 範例執行完成！")
    print("="*80)
