"""
股票資料源抽象基礎類別 (Abstract Base Class)
所有市場的資料源都必須繼承並實作這個類別

設計目標:
1. 將「通用邏輯」(如下載、快取)與「市場特定邏輯」(如代碼轉換)分離
2. 使系統可輕鬆擴展到其他市場(台股、港股、A股等)
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime


class StockDataSource(ABC):
    """
    抽象基礎類別:定義所有股票資料源必須實作的介面
    
    子類別必須實作:
    - format_symbol(): 將原始股票代碼轉換為該市場的標準格式
    - get_market_symbols(): 獲取該市場的股票清單
    - download_raw_data(): 從資料源下載原始數據
    """
    
    def __init__(self, market_name: str):
        """
        初始化資料源
        
        參數:
            market_name: 市場名稱(如 'US', 'TW', 'HK')
        """
        self.market_name = market_name
    
    @abstractmethod
    def format_symbol(self, symbol: str) -> str:
        """
        格式化股票代碼為該市場的標準格式
        
        參數:
            symbol: 原始股票代碼
            
        返回:
            標準化後的代碼
            
        範例:
            美股: 'AAPL' → 'AAPL' (不變)
            台股: '2330' → '2330.TW'
            港股: '0700' → '0700.HK'
        """
        pass
    
    @abstractmethod
    def get_market_symbols(self, category: str = 'all') -> List[str]:
        """
        獲取該市場的股票代碼清單
        
        參數:
            category: 股票類別(如 'index', 'popular', 'all')
            
        返回:
            股票代碼列表
            
        範例:
            美股: ['AAPL', 'MSFT', 'GOOGL', ...]
            台股: ['2330', '2317', '2454', ...]
        """
        pass
    
    @abstractmethod
    def download_raw_data(self, symbol: str, period: str = '1y', 
                          interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        從資料源下載原始股票數據
        
        參數:
            symbol: 股票代碼(已經過 format_symbol() 處理)
            period: 時間範圍('1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            interval: 數據間隔('1d', '1wk', '1mo')
            
        返回:
            DataFrame 或 None(下載失敗時)
            
        DataFrame 必須包含以下欄位(標準化命名):
            - date (DatetimeIndex)
            - open (float)
            - high (float)
            - low (float)
            - close (float)
            - volume (int)
        """
        pass
    
    @abstractmethod
    def get_stock_info(self, symbol: str) -> Dict:
        """
        獲取股票基本資訊
        
        參數:
            symbol: 股票代碼
            
        返回:
            包含股票資訊的字典,至少包含:
            {
                'symbol': str,           # 原始代碼
                'name': str,             # 股票名稱
                'market': str,           # 市場名稱
                'currency': str,         # 貨幣(如 'USD', 'TWD')
                'exchange': str,         # 交易所
                'available': bool,       # 是否可用
                'error': str (optional)  # 錯誤訊息
            }
        """
        pass
    
    # ========== 通用方法 (所有子類別共用) ==========
    
    # 檔案: stock_data_source_abc.py

    def validate_dataframe(self, df: pd.DataFrame, symbol: str) -> bool:
        """
        驗證 DataFrame 是否符合標準格式
        
        這是通用邏輯,所有市場都適用
        """
        # 修正：將 'date' 加入必要欄位
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        # 檢查必要欄位
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ {symbol}: 缺少欄位 {missing_columns}")
            return False
        
        # 檢查數據量
        if len(df) < 50:
            print(f"⚠️ {symbol}: 數據不足 ({len(df)} 筆,建議至少 50 筆)")
            return False
        
        # 檢查缺失值
        if df[required_columns].isnull().any().any():
            print(f"⚠️ {symbol}: 發現缺失值")
            return False
        
        return True
    
    # 檔案: stock_data_source_abc.py

    def standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        標準化 DataFrame 格式(統一欄位名稱、數據類型)
        
        這是通用邏輯,所有市場都適用
        """
        # 1. 先重置索引
        # 如果索引不是 RangeIndex (例如是 DatetimeIndex)，則重置
        # 這會將 yfinance 的 'Date' 索引變為一個 'Date' (大寫D) 欄位
        if not isinstance(df.index, pd.RangeIndex):
            df = df.reset_index()
        
        # 2. 再將所有欄位名稱轉為小寫
        # 'Date' -> 'date', 'Open' -> 'open'
        df.columns = [col.lower() for col in df.columns]
        
        # 3. 統一日期欄位名稱 (以防萬一 'date' 欄位名稱是 'index' 或 'datetime')
        if 'date' not in df.columns:
            date_columns = ['datetime', 'timestamp', 'index']
            for col in date_columns:
                if col in df.columns:
                    df = df.rename(columns={col: 'date'})
                    break
        
        # 4. 確保日期是 datetime 類型
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # 5. 只保留必要欄位
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        available_columns = [col for col in required_columns if col in df.columns]
        
        # 檢查 'date' 是否真的存在
        if 'date' not in available_columns:
            print(f"❌ 標準化失敗：找不到 'date' 欄位。可用欄位: {list(df.columns)}")
            # 返回一個空的 DataFrame 或 None
            return pd.DataFrame(columns=required_columns)

        df = df[available_columns]
        
        return df
    
    def download_stock_data(self, symbol: str, period: str = '1y', 
                           interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        完整的下載流程(格式化 → 下載 → 驗證 → 標準化)
        
        這是通用邏輯,整合了抽象方法和通用方法
        """
        try:
            # 1. 格式化股票代碼
            formatted_symbol = self.format_symbol(symbol)
            
            # 2. 下載原始數據(由子類別實作)
            df = self.download_raw_data(formatted_symbol, period, interval)
            
            if df is None or df.empty:
                print(f"⚠️ {symbol}: 無數據")
                return None
            
            # 3. 標準化格式
            df = self.standardize_dataframe(df)
            
            # 4. 驗證數據
            if not self.validate_dataframe(df, symbol):
                return None
            
            print(f"✅ {symbol}: 下載成功 ({len(df)} 筆)")
            return df
            
        except Exception as e:
            print(f"❌ {symbol}: 下載失敗 - {str(e)}")
            return None
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(market={self.market_name})>"


# ========== 工廠函式 ==========

def get_data_source(symbol: str) -> StockDataSource:
    """
    工廠函式:根據股票代碼自動選擇合適的資料源
    
    判斷邏輯:
    - 純數字(如 '2330') 或包含 '.TW' → 台股
    - 否則 → 美股
    
    參數:
        symbol: 股票代碼
        
    返回:
        對應的 StockDataSource 實例
        
    範例:
        source = get_data_source('2330')     # 返回 TWStockSource
        source = get_data_source('AAPL')     # 返回 USStockSource
    """
    # 判斷是否為台股
    if symbol.replace('.', '').replace('-', '').isdigit() or '.TW' in symbol.upper():
        from stock_data_source_tw import TWStockSource
        return TWStockSource()
    
    # 預設為美股
    from stock_data_source_us import USStockSource
    return USStockSource()
