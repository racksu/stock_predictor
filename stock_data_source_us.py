"""
美股資料源 (US Stock Data Source)
繼承 StockDataSource 並實作美股特定邏輯

特點:
1. 使用 yfinance API
2. 支援 S&P 500、NASDAQ 100、道瓊斯指數
3. 處理美股特殊符號(如 BRK.B → BRK-B)
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from stock_data_source_abc import StockDataSource


class USStockSource(StockDataSource):
    """美股資料源實作"""
    
    def __init__(self):
        super().__init__(market_name='US')
    
    def format_symbol(self, symbol: str) -> str:
        """
        格式化美股代碼
        
        美股特殊處理:
        - 將 '.' 替換為 '-' (如 BRK.B → BRK-B)
        - 轉為大寫
        
        參數:
            symbol: 原始股票代碼
            
        返回:
            標準化後的美股代碼
        """
        # 轉大寫
        symbol = symbol.upper().strip()
        
        # 處理特殊符號(. → -)
        symbol = symbol.replace('.', '-')
        
        return symbol
    
    def get_market_symbols(self, category: str = 'popular') -> List[str]:
        """
        獲取美股股票清單
        
        參數:
            category: 類別
                - 'sp500': S&P 500 成分股
                - 'nasdaq100': NASDAQ 100 成分股
                - 'dow': 道瓊斯 30 成分股
                - 'popular': 熱門股票
                - 'all': 所有(sp500 + nasdaq100)
                
        返回:
            股票代碼列表
        """
        if category == 'sp500':
            return self._get_sp500_symbols()
        elif category == 'nasdaq100':
            return self._get_nasdaq100_symbols()
        elif category == 'dow':
            return self._get_dow_jones_symbols()
        elif category == 'popular':
            return self._get_popular_stocks()
        elif category == 'all':
            sp500 = self._get_sp500_symbols()
            nasdaq = self._get_nasdaq100_symbols()
            return list(set(sp500 + nasdaq))  # 去重
        else:
            print(f"⚠️ 未知類別 '{category}',返回熱門股票")
            return self._get_popular_stocks()
    
    def download_raw_data(self, symbol: str, period: str = '1y', 
                          interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        從 yfinance 下載美股數據
        
        參數:
            symbol: 股票代碼(已格式化)
            period: 時間範圍
            interval: 數據間隔
            
        返回:
            DataFrame 或 None
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return None
            
            return df
            
        except Exception as e:
            print(f"❌ yfinance 下載失敗: {str(e)}")
            return None
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        獲取美股基本資訊
        
        參數:
            symbol: 股票代碼
            
        返回:
            股票資訊字典
        """
        formatted_symbol = self.format_symbol(symbol)
        
        try:
            ticker = yf.Ticker(formatted_symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'formatted_symbol': formatted_symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'market': 'US',
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'NYSE/NASDAQ'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'available': True
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'formatted_symbol': formatted_symbol,
                'name': 'Unknown',
                'market': 'US',
                'available': False,
                'error': str(e)
            }
    
    # ========== 私有方法:獲取股票清單 ==========
    
    def _get_sp500_symbols(self) -> List[str]:
        """從 Wikipedia 獲取 S&P 500 成分股"""
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            df = tables[0]
            symbols = df['Symbol'].tolist()
            
            # 格式化符號
            symbols = [self.format_symbol(s) for s in symbols]
            
            print(f"✅ 成功獲取 {len(symbols)} 支 S&P 500 成分股")
            return symbols
        except Exception as e:
            print(f"❌ 獲取 S&P 500 列表失敗: {str(e)}")
            return self._get_popular_stocks()
    
    def _get_nasdaq100_symbols(self) -> List[str]:
        """從 Wikipedia 獲取 NASDAQ 100 成分股"""
        try:
            url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
            tables = pd.read_html(url)
            df = tables[4]
            symbols = df['Ticker'].tolist()
            
            print(f"✅ 成功獲取 {len(symbols)} 支 NASDAQ 100 成分股")
            return symbols
        except Exception as e:
            print(f"❌ 獲取 NASDAQ 100 列表失敗: {str(e)}")
            return []
    
    def _get_dow_jones_symbols(self) -> List[str]:
        """道瓊斯 30 成分股(硬編碼)"""
        dow_symbols = [
            'AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT'
        ]
        print(f"✅ 道瓊斯 30 成分股已載入")
        return dow_symbols
    
    def _get_popular_stocks(self) -> List[str]:
        """熱門美股列表(硬編碼)"""
        popular_stocks = [
            # 科技股
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD', 'INTC', 'CRM',
            'ORCL', 'ADBE', 'NFLX', 'AVGO', 'QCOM', 'TXN', 'AMAT', 'MU', 'LRCX', 'KLAC',
            
            # 金融股
            'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'SCHW', 'AXP', 'USB',
            
            # 醫療保健
            'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK', 'ABT', 'DHR', 'BMY', 'LLY',
            
            # 消費品
            'PG', 'KO', 'PEP', 'WMT', 'COST', 'NKE', 'MCD', 'SBUX', 'HD', 'LOW',
            
            # 能源
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'MPC', 'VLO', 'PSX', 'OXY',
            
            # 工業
            'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'EMR',
            
            # 通訊
            'T', 'VZ', 'TMUS', 'CMCSA', 'DIS', 'CHTR',
            
            # 公用事業
            'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC',
            
            # 房地產
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'SPG'
        ]
        
        print(f"✅ 已載入 {len(popular_stocks)} 支熱門美股")
        return popular_stocks


# ========== 測試程式碼 ==========

def test_us_stock_source():
    """測試美股資料源"""
    print("="*80)
    print("美股資料源測試 (USStockSource)")
    print("="*80)
    
    source = USStockSource()
    
    # 測試 1: 格式化股票代碼
    print("\n【測試 1】格式化股票代碼")
    print("-"*80)
    test_symbols = ['aapl', 'BRK.B', 'msft', 'googl']
    for symbol in test_symbols:
        formatted = source.format_symbol(symbol)
        print(f"{symbol:10} → {formatted}")
    
    # 測試 2: 獲取股票清單
    print("\n【測試 2】獲取股票清單")
    print("-"*80)
    dow_stocks = source.get_market_symbols('dow')
    print(f"道瓊斯 30: {len(dow_stocks)} 支")
    print(f"前 10 支: {dow_stocks[:10]}")
    
    # 測試 3: 下載股票數據
    print("\n【測試 3】下載股票數據")
    print("-"*80)
    test_stocks = ['AAPL', 'MSFT', 'TSLA']
    
    for symbol in test_stocks:
        print(f"\n正在測試 {symbol}...")
        
        # 獲取股票資訊
        info = source.get_stock_info(symbol)
        if info['available']:
            print(f"  名稱: {info['name']}")
            print(f"  交易所: {info['exchange']}")
            print(f"  產業: {info['sector']}")
        
        # 下載數據
        df = source.download_stock_data(symbol, period='3mo')
        if df is not None:
            print(f"  數據範圍: {df['date'].min()} 至 {df['date'].max()}")
            print(f"  數據筆數: {len(df)}")
            print(f"  最新價格: ${df['close'].iloc[-1]:.2f}")
    
    print("\n" + "="*80)
    print("✅ 測試完成")
    print("="*80)


if __name__ == "__main__":
    test_us_stock_source()
