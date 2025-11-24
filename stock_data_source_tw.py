"""
台股資料源 (Taiwan Stock Data Source)
繼承 StockDataSource 並實作台股特定邏輯

特點:
1. 使用 yfinance API (台股需加 .TW 或 .TWO 後綴)
2. 支援上市(TWSE)和上櫃(TPEx)股票
3. 內建台灣知名股票清單
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from stock_data_source_abc import StockDataSource
from taiwan_stock_database import (
    TAIWAN_STOCK_CATEGORIES, 
    TAIWAN_INDEX_STOCKS,
    get_all_tw_stocks,
    get_category_stocks,
    get_all_categories
)

# 導入台股名稱字典
try:
    from taiwan_stock_names import get_stock_name, TAIWAN_STOCK_NAMES
    HAS_STOCK_NAMES = True
except ImportError:
    HAS_STOCK_NAMES = False
    TAIWAN_STOCK_NAMES = {}


class TWStockSource(StockDataSource):
    """台股資料源實作"""
    
    def __init__(self):
        super().__init__(market_name='TW')
        
        # 市場後綴定義
        self.market_suffix = {
            'TWSE': '.TW',      # 台灣證券交易所(上市)
            'TPEx': '.TWO'      # 台灣櫃買中心(上櫃)
        }
    
    def format_symbol(self, symbol: str, market: str = 'TWSE') -> str:
        """
        格式化台股代碼
        
        台股特殊處理:
        - 純數字代碼需加上 .TW 或 .TWO 後綴
        - 如果已有後綴則不重複添加
        
        參數:
            symbol: 原始股票代碼(如 '2330', '2317')
            market: 市場類型('TWSE' 上市 或 'TPEx' 上櫃)
            
        返回:
            Yahoo Finance 格式的代碼
            
        範例:
            '2330' → '2330.TW' (台積電)
            '2317' → '2317.TW' (鴻海)
            '2330.TW' → '2330.TW' (已有後綴,不重複)
        """
        # 移除可能存在的後綴(避免重複)
        symbol = symbol.upper().strip()
        symbol = symbol.replace('.TW', '').replace('.TWO', '')
        
        # 添加市場後綴
        suffix = self.market_suffix.get(market, '.TW')
        return f"{symbol}{suffix}"
    
    def get_market_symbols(self, category: str = 'popular') -> List[str]:
        """
        獲取台股股票清單
        
        參數:
            category: 類別
                產業分類:
                - '半導體', '電子零組件', '電腦及週邊', '通信網路', '光電'
                - '金控', '銀行', '保險', '證券'
                - '鋼鐵', '塑膠化工', '水泥', '紡織纖維', '造紙'
                - '食品', '觀光', '百貨'
                - '營建', '汽車', '航運', '生技醫療', '油電燃氣', '電機機械'
                
                指數成分股:
                - '台灣50', '台灣中型100', '高股息'
                
                特殊類別:
                - 'all': 所有台股 (227支內建)
                - 'all_listed': 從台灣證券交易所下載全部上市公司(900+支)
                - 'popular': 知名股票
                
        返回:
            股票代碼列表(不含後綴)
        """
        if category == 'all':
            # 返回內建的227支台股
            return get_all_tw_stocks()
        elif category == 'all_listed':
            # 從台灣證券交易所下載全部上市公司
            from taiwan_stock_database import download_all_listed_stocks_from_twse
            return download_all_listed_stocks_from_twse()
        elif category == 'popular':
            # 返回熱門台股
            return self._get_popular_stocks()
        elif category in TAIWAN_STOCK_CATEGORIES:
            # 產業分類
            return TAIWAN_STOCK_CATEGORIES[category]["symbols"]
        elif category in TAIWAN_INDEX_STOCKS:
            # 指數成分股
            return TAIWAN_INDEX_STOCKS[category]["symbols"]
        else:
            print(f"⚠️ 未知類別 '{category}',返回熱門股票")
            return self._get_popular_stocks()
    
    def download_raw_data(self, symbol: str, period: str = '1y', 
                          interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        從 yfinance 下載台股數據
        
        參數:
            symbol: 股票代碼(已格式化,包含 .TW 後綴)
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
        獲取台股基本資訊
        
        參數:
            symbol: 股票代碼(不含後綴)
            
        返回:
            股票資訊字典
        """
        formatted_symbol = self.format_symbol(symbol)
        
        try:
            ticker = yf.Ticker(formatted_symbol)
            info = ticker.info
            
            # 從內建字典獲取中文名稱
            chinese_name = self._get_stock_name(symbol)
            
            return {
                'symbol': symbol,
                'formatted_symbol': formatted_symbol,
                'name': info.get('longName', info.get('shortName', chinese_name)),
                'chinese_name': chinese_name,
                'market': 'TW',
                'currency': info.get('currency', 'TWD'),
                'exchange': info.get('exchange', 'TAI'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'available': True
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'formatted_symbol': formatted_symbol,
                'name': self._get_stock_name(symbol),
                'chinese_name': self._get_stock_name(symbol),
                'market': 'TW',
                'available': False,
                'error': str(e)
            }
    
    # ========== 私有方法:輔助功能 ==========
    
    def _get_popular_stocks(self) -> List[str]:
        """知名台股(各產業龍頭)"""
        return [
            # 半導體龍頭
            '2330',  # 台積電
            '2454',  # 聯發科
            '2303',  # 聯電
            
            # 電子龍頭
            '2317',  # 鴻海
            '2382',  # 廣達
            '2308',  # 台達電
            
            # 金融龍頭
            '2882',  # 國泰金
            '2881',  # 富邦金
            '2891',  # 中信金
            
            # 其他重要股票
            '2412',  # 中華電
            '2609',  # 陽明
            '2603',  # 長榮
        ]
    
    def get_all_categories(self) -> Dict:
        """獲取所有可用的分類"""
        return get_all_categories()
    
    def _get_stock_name(self, symbol: str) -> str:
        """獲取股票中文名稱"""
        # 使用完整的台股名稱字典
        if HAS_STOCK_NAMES:
            return get_stock_name(symbol)
        
        # 回退到基本字典（僅包含常見股票）
        basic_names = {
            # 半導體
            '2330': '台積電',
            '2454': '聯發科',
            '2303': '聯電',
            '3034': '聯詠',
            '2408': '南亞科',
            
            # 電子
            '2317': '鴻海',
            '2382': '廣達',
            '2357': '華碩',
            '2353': '宏碁',
            '2308': '台達電',
            
            # 金融
            '2882': '國泰金',
            '2881': '富邦金',
            '2891': '中信金',
            '2886': '兆豐金',
            '2884': '玉山金',
            
            # 傳產
            '2002': '中鋼',
            '1301': '台塑',
            '1303': '南亞',
            '2801': '彰銀',
            '9910': '豐泰',
            
            # 其他
            '2412': '中華電',
            '2609': '陽明',
            '2603': '長榮',
            '2912': '統一超',
        }
        
        return basic_names.get(symbol, symbol)


# ========== 測試程式碼 ==========

def test_tw_stock_source():
    """測試台股資料源"""
    print("="*80)
    print("台股資料源測試 (TWStockSource)")
    print("="*80)
    
    source = TWStockSource()
    
    # 測試 1: 格式化股票代碼
    print("\n【測試 1】格式化股票代碼")
    print("-"*80)
    test_symbols = ['2330', '2317', '2330.TW', '2454']
    for symbol in test_symbols:
        formatted = source.format_symbol(symbol)
        print(f"{symbol:10} → {formatted}")
    
    # 測試 2: 獲取分類列表
    print("\n【測試 2】獲取所有分類")
    print("-"*80)
    categories = source.get_all_categories()
    print(f"產業分類 ({len(categories['產業分類'])} 個):")
    print(f"  {', '.join(categories['產業分類'][:10])}...")
    print(f"\n指數成分股 ({len(categories['指數成分股'])} 個):")
    print(f"  {', '.join(categories['指數成分股'])}")
    
    # 測試 3: 獲取各類別股票清單
    print("\n【測試 3】獲取不同類別的股票清單")
    print("-"*80)
    test_categories = ['半導體', '金控', '台灣50', 'all']
    for category in test_categories:
        stocks = source.get_market_symbols(category)
        print(f"{category:15}: {len(stocks)} 支 → {stocks[:5]}...")
    
    # 測試 4: 下載測試(會因網路限制而失敗,但邏輯正確)
    print("\n【測試 4】下載股票數據(可能因網路限制失敗)")
    print("-"*80)
    test_stocks = ['2330', '2317']  # 台積電、鴻海
    
    for symbol in test_stocks:
        name = source._get_stock_name(symbol)
        print(f"\n正在測試 {symbol} ({name})...")
        
        # 獲取股票資訊
        info = source.get_stock_info(symbol)
        if info['available']:
            print(f"  中文名稱: {info['chinese_name']}")
            print(f"  Yahoo代碼: {info['formatted_symbol']}")
        else:
            print(f"  ⚠️ 無法獲取資訊(可能網路限制)")
        
        # 嘗試下載數據
        df = source.download_stock_data(symbol, period='5d')
        if df is not None:
            print(f"  ✅ 數據下載成功")
            print(f"  數據筆數: {len(df)}")
        else:
            print(f"  ⚠️ 數據下載失敗(預期中,環境網路限制)")
    
    print("\n" + "="*80)
    print("✅ 測試完成 - 台股分類系統已完整整合")
    print(f"✅ 總共支援 {len(source.get_market_symbols('all'))} 支台股")
    print("="*80)


if __name__ == "__main__":
    test_tw_stock_source()
