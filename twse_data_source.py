"""
台灣證券交易所(TWSE)數據源
使用官方API，無需Token，免費使用

API文檔：
- 三大法人買賣超：https://www.twse.com.tw/rwd/zh/fund/T86
- 融資融券餘額：https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN
- 個股日成交資料：https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class TWSEDataSource:
    """
    台灣證券交易所數據源

    特點：
    - 官方數據，最準確
    - 無需Token
    - 免費使用
    - 即時更新
    """

    def __init__(self):
        """初始化TWSE數據源"""
        self.base_url = "https://www.twse.com.tw"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        print("✅ TWSE數據源已初始化（無需Token）")

    def _make_request(self, url: str, params: Dict = None, retry: int = 3) -> Optional[Dict]:
        """
        發送HTTP請求

        參數:
            url: API URL
            params: 查詢參數
            retry: 重試次數

        返回:
            JSON數據
        """
        for attempt in range(retry):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()

                # 檢查TWSE API特有的錯誤
                if 'stat' in data and data['stat'] == 'OK':
                    return data
                elif 'stat' in data and data['stat'] != 'OK':
                    print(f"⚠️ TWSE API返回錯誤: {data.get('stat')}")
                    return None
                else:
                    # 某些API沒有stat字段
                    return data

            except requests.exceptions.RequestException as e:
                print(f"⚠️ 請求失敗 (第{attempt+1}次): {e}")
                if attempt < retry - 1:
                    time.sleep(2)  # 等待2秒後重試

        return None

    def get_stock_day_data(self,
                          stock_no: str,
                          year_month: str) -> Optional[pd.DataFrame]:
        """
        獲取個股日成交資料

        API: https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY

        參數:
            stock_no: 股票代號（如 '2330'）
            year_month: 年月（如 '202511' 表示2025年11月）

        返回:
            DataFrame包含：日期、成交股數、成交金額、開盤價、最高價、最低價、收盤價、漲跌價差、成交筆數
        """
        url = f"{self.base_url}/rwd/zh/afterTrading/STOCK_DAY"
        params = {
            'date': year_month,
            'stockNo': stock_no,
            'response': 'json'
        }

        data = self._make_request(url, params)

        if not data or 'data' not in data:
            return None

        try:
            # 轉換為DataFrame
            df = pd.DataFrame(data['data'], columns=data['fields'])

            # 清理數據
            df.columns = ['date', 'volume', 'turnover', 'open', 'high', 'low', 'close',
                         'change', 'transactions']

            # 移除逗號並轉換數值
            for col in ['volume', 'turnover', 'open', 'high', 'low', 'close', 'transactions']:
                df[col] = df[col].str.replace(',', '').replace('--', '0')
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # 處理日期（從 '113/11/21' 轉為 '2024-11-21'）
            df['date'] = df['date'].apply(lambda x: self._convert_roc_date(x))
            df['date'] = pd.to_datetime(df['date'])

            # 排序
            df = df.sort_values('date').reset_index(drop=True)

            return df

        except Exception as e:
            print(f"❌ 解析股票日資料失敗: {e}")
            return None

    def get_stock_historical_data(self,
                                  stock_no: str,
                                  start_date: str,
                                  end_date: str = None) -> Optional[pd.DataFrame]:
        """
        獲取個股歷史資料（多個月）

        參數:
            stock_no: 股票代號
            start_date: 開始日期（格式：'2023-01-01'）
            end_date: 結束日期（格式：'2024-12-31'，默認為今天）

        返回:
            合併的歷史數據DataFrame
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        # 生成所有需要的年月
        dates = pd.date_range(start=start, end=end, freq='MS')  # MS = Month Start
        year_months = [d.strftime('%Y%m') for d in dates]

        all_data = []

        print(f"📥 開始下載 {stock_no} 的歷史資料（{len(year_months)}個月）...")

        for i, ym in enumerate(year_months, 1):
            print(f"  [{i}/{len(year_months)}] 下載 {ym}...", end=" ")

            df = self.get_stock_day_data(stock_no, ym)

            if df is not None and len(df) > 0:
                all_data.append(df)
                print(f"✅ {len(df)}筆")
            else:
                print("⚠️ 無數據")

            # 避免請求太快
            if i < len(year_months):
                time.sleep(3)  # TWSE建議間隔3秒

        if not all_data:
            print(f"❌ 無法獲取 {stock_no} 的任何數據")
            return None

        # 合併所有數據
        combined = pd.concat(all_data, ignore_index=True)

        # 過濾日期範圍
        combined = combined[(combined['date'] >= start) & (combined['date'] <= end)]

        print(f"✅ 共獲取 {len(combined)} 筆歷史資料")

        return combined

    def get_institutional_investors(self,
                                   date: str,
                                   stock_no: str = None) -> Optional[pd.DataFrame]:
        """
        獲取三大法人買賣超

        API: https://www.twse.com.tw/rwd/zh/fund/T86

        參數:
            date: 日期（格式：'20251121' 或 '2025-11-21'）
            stock_no: 股票代號（可選，None表示全市場）

        返回:
            DataFrame包含：外資、投信、自營商的買賣超
        """
        # 標準化日期格式
        date_str = date.replace('-', '')

        url = f"{self.base_url}/rwd/zh/fund/T86"
        params = {
            'date': date_str,
            'selectType': 'ALLBUT0999',  # 全部（不含權證等）
            'response': 'json'
        }

        data = self._make_request(url, params)

        if not data or 'data' not in data:
            return None

        try:
            # 轉換為DataFrame
            df = pd.DataFrame(data['data'], columns=data['fields'])

            # 如果指定股票代號，過濾
            if stock_no:
                df = df[df['證券代號'] == stock_no]

            # 重命名欄位
            df = df.rename(columns={
                '證券代號': 'stock_no',
                '證券名稱': 'stock_name',
                '外陸資買進股數(不含外資自營商)': 'foreign_buy',
                '外陸資賣出股數(不含外資自營商)': 'foreign_sell',
                '外陸資買賣超股數(不含外資自營商)': 'foreign_net',
                '投信買進股數': 'trust_buy',
                '投信賣出股數': 'trust_sell',
                '投信買賣超股數': 'trust_net',
                '自營商買賣超股數': 'dealer_net',
                '三大法人買賣超股數': 'total_net'
            })

            # 清理數值（移除逗號）
            numeric_cols = ['foreign_buy', 'foreign_sell', 'foreign_net',
                          'trust_buy', 'trust_sell', 'trust_net',
                          'dealer_net', 'total_net']

            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].str.replace(',', '').replace('--', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 加入日期
            df['date'] = pd.to_datetime(date_str, format='%Y%m%d')

            return df

        except Exception as e:
            print(f"❌ 解析法人資料失敗: {e}")
            return None

    def get_institutional_investors_range(self,
                                         stock_no: str,
                                         start_date: str,
                                         end_date: str = None,
                                         lookback_days: int = 30) -> Optional[pd.DataFrame]:
        """
        獲取指定期間的三大法人買賣超

        參數:
            stock_no: 股票代號
            start_date: 開始日期
            end_date: 結束日期（默認今天）
            lookback_days: 回溯天數（如果沒有指定日期範圍）

        返回:
            包含多日法人數據的DataFrame
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        if start_date is None:
            end = pd.to_datetime(end_date)
            start = end - timedelta(days=lookback_days)
            start_date = start.strftime('%Y-%m-%d')

        # 生成日期範圍（只包含交易日，週末會自動跳過）
        dates = pd.bdate_range(start=start_date, end=end_date)

        all_data = []

        print(f"📥 獲取 {stock_no} 的法人資料（{len(dates)}個交易日）...")

        for i, date in enumerate(dates, 1):
            date_str = date.strftime('%Y%m%d')

            if i % 5 == 0:
                print(f"  進度: {i}/{len(dates)}", end="\r")

            df = self.get_institutional_investors(date_str, stock_no)

            if df is not None and len(df) > 0:
                all_data.append(df)

            # 避免請求太快
            time.sleep(5)  # TWSE建議間隔5秒

        if not all_data:
            print(f"⚠️ 無法獲取 {stock_no} 的法人數據")
            return None

        # 合併所有數據
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.sort_values('date').reset_index(drop=True)

        print(f"\n✅ 共獲取 {len(combined)} 筆法人資料")

        return combined

    def get_margin_trading(self,
                          date: str,
                          stock_no: str = None) -> Optional[pd.DataFrame]:
        """
        獲取融資融券餘額

        API: https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN

        參數:
            date: 日期（格式：'20251121' 或 '2025-11-21'）
            stock_no: 股票代號（可選）

        返回:
            DataFrame包含：融資、融券餘額等
        """
        # 標準化日期格式
        date_str = date.replace('-', '')

        url = f"{self.base_url}/rwd/zh/marginTrading/MI_MARGN"
        params = {
            'date': date_str,
            'selectType': 'ALL',
            'response': 'json'
        }

        data = self._make_request(url, params)

        if not data or 'data' not in data:
            return None

        try:
            # TWSE的融資融券API有多個table，我們需要主要的那個
            # 通常在data的第一個元素
            if isinstance(data['data'], list) and len(data['data']) > 0:
                df = pd.DataFrame(data['data'], columns=data['fields'])
            else:
                return None

            # 如果指定股票代號，過濾
            if stock_no:
                df = df[df['股票代號'] == stock_no]

            # 重命名欄位
            df = df.rename(columns={
                '股票代號': 'stock_no',
                '股票名稱': 'stock_name',
                '融資買進': 'margin_buy',
                '融資賣出': 'margin_sell',
                '融資現金償還': 'margin_cash_repay',
                '融資前日餘額': 'margin_prev_balance',
                '融資今日餘額': 'margin_balance',
                '融資限額': 'margin_limit',
                '融券買進': 'short_buy',
                '融券賣出': 'short_sell',
                '融券現券償還': 'short_stock_repay',
                '融券前日餘額': 'short_prev_balance',
                '融券今日餘額': 'short_balance',
                '融券限額': 'short_limit',
                '資券互抵': 'offset'
            })

            # 清理數值
            numeric_cols = ['margin_buy', 'margin_sell', 'margin_cash_repay',
                          'margin_prev_balance', 'margin_balance', 'margin_limit',
                          'short_buy', 'short_sell', 'short_stock_repay',
                          'short_prev_balance', 'short_balance', 'short_limit', 'offset']

            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].str.replace(',', '').replace('--', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 計算融資使用率、券資比等
            df['margin_usage_rate'] = (df['margin_balance'] / df['margin_limit'] * 100).fillna(0)
            df['short_margin_ratio'] = (df['short_balance'] / (df['margin_balance'] + 1) * 100).fillna(0)

            # 加入日期
            df['date'] = pd.to_datetime(date_str, format='%Y%m%d')

            return df

        except Exception as e:
            print(f"❌ 解析融資融券資料失敗: {e}")
            return None

    def get_margin_trading_range(self,
                                stock_no: str,
                                lookback_days: int = 30) -> Optional[pd.DataFrame]:
        """
        獲取指定期間的融資融券資料

        參數:
            stock_no: 股票代號
            lookback_days: 回溯天數

        返回:
            包含多日融資融券的DataFrame
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        # 生成日期範圍
        dates = pd.bdate_range(start=start_date, end=end_date)

        all_data = []

        print(f"📥 獲取 {stock_no} 的融資融券資料（{len(dates)}個交易日）...")

        for i, date in enumerate(dates, 1):
            date_str = date.strftime('%Y%m%d')

            if i % 5 == 0:
                print(f"  進度: {i}/{len(dates)}", end="\r")

            df = self.get_margin_trading(date_str, stock_no)

            if df is not None and len(df) > 0:
                all_data.append(df)

            # 避免請求太快
            time.sleep(5)  # TWSE建議間隔5秒

        if not all_data:
            print(f"⚠️ 無法獲取 {stock_no} 的融資融券數據")
            return None

        # 合併所有數據
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.sort_values('date').reset_index(drop=True)

        print(f"\n✅ 共獲取 {len(combined)} 筆融資融券資料")

        return combined

    def _convert_roc_date(self, roc_date: str) -> str:
        """
        轉換民國年為西元年

        參數:
            roc_date: 民國年日期（如 '113/11/21'）

        返回:
            西元年日期（如 '2024-11-21'）
        """
        try:
            parts = roc_date.split('/')
            year = int(parts[0]) + 1911  # 民國年轉西元年
            month = parts[1].zfill(2)
            day = parts[2].zfill(2)
            return f"{year}-{month}-{day}"
        except:
            return roc_date


# ========== 使用示例 ==========

def example_twse_usage():
    """示例：使用TWSE API獲取數據"""
    print("\n" + "="*80)
    print("示例：TWSE官方API使用")
    print("="*80)

    twse = TWSEDataSource()

    # 1. 獲取個股歷史資料
    print("\n【1. 獲取台積電(2330)近3個月歷史資料】")
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    df_price = twse.get_stock_historical_data('2330', start_date)

    if df_price is not None:
        print(f"\n最新5筆資料:")
        print(df_price[['date', 'open', 'high', 'low', 'close', 'volume']].tail())

    # 2. 獲取三大法人買賣超
    print("\n【2. 獲取今日三大法人買賣超（台積電）】")
    today = datetime.now().strftime('%Y%m%d')
    df_inst = twse.get_institutional_investors(today, '2330')

    if df_inst is not None:
        print(f"\n法人資料:")
        print(df_inst[['stock_name', 'foreign_net', 'trust_net', 'dealer_net', 'total_net']])

    # 3. 獲取融資融券
    print("\n【3. 獲取今日融資融券（台積電）】")
    df_margin = twse.get_margin_trading(today, '2330')

    if df_margin is not None:
        print(f"\n融資融券資料:")
        print(df_margin[['stock_name', 'margin_balance', 'short_balance',
                        'margin_usage_rate', 'short_margin_ratio']])

    print("\n" + "="*80)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          TWSE官方數據源 - 無需Token，免費使用                 ║
    ║               Taiwan Stock Exchange Data Source               ║
    ╚════════════════════════════════════════════════════════════════╝

    功能:
    1. 📊 個股日成交資料 - 價格、成交量、成交筆數
    2. 👥 三大法人買賣超 - 外資、投信、自營商
    3. 💰 融資融券餘額 - 融資率、券資比

    優勢:
    ✅ 官方數據，最準確
    ✅ 無需Token，免費使用
    ✅ 即時更新
    ✅ 無請求次數限制（建議間隔3-5秒）

    注意事項:
    ⚠️ 請遵守TWSE使用條款
    ⚠️ 建議請求間隔3-5秒
    ⚠️ 週末及國定假日無數據
    """)

    example_twse_usage()
