"""
統一股票資料管理器 (Unified Stock Data Manager)
整合美股和台股資料源,提供統一的介面

功能:
1. 自動判斷股票代碼所屬市場
2. 批量下載多市場股票
3. 本地數據快取和更新
4. 支援觀察清單管理
"""

import os
import json
import time
import pandas as pd
from typing import List, Dict, Optional, Union
from datetime import datetime

from stock_data_source_abc import StockDataSource, get_data_source
from stock_data_source_us import USStockSource
from stock_data_source_tw import TWStockSource


class UnifiedStockDataManager:
    """統一股票資料管理器"""
    
    def __init__(self, data_dir: str = './stock_data'):
        """
        初始化管理器
        
        參數:
            data_dir: 數據存儲目錄
        """
        self.data_dir = data_dir
        self.us_source = USStockSource()
        self.tw_source = TWStockSource()
        self.create_directories()
    
    def create_directories(self):
        """創建必要的目錄結構"""
        directories = [
            self.data_dir,
            f'{self.data_dir}/daily',
            f'{self.data_dir}/metadata',
            f'{self.data_dir}/watchlists'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        print(f"✅ 數據目錄創建完成: {self.data_dir}")
    
    def get_source_for_symbol(self, symbol: str) -> StockDataSource:
        """
        根據股票代碼自動選擇資料源
        
        參數:
            symbol: 股票代碼
            
        返回:
            對應的資料源實例
        """
        return get_data_source(symbol)
    
    def download_stock_data(self, symbol: str, period: str = '2y', 
                           interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        下載單支股票數據(自動判斷市場)
        
        參數:
            symbol: 股票代碼
            period: 時間範圍
            interval: 數據間隔
            
        返回:
            DataFrame 或 None
        """
        try:
            # 自動選擇資料源
            source = self.get_source_for_symbol(symbol)
            
            # 下載數據
            df = source.download_stock_data(symbol, period, interval)
            
            if df is None:
                return None
            
            # 數據質量檢查（只在獲取長期數據時警告）
            if period in ['2y', '5y', '10y', 'max'] and len(df) < 200:
                print(f"⚠️ {symbol}: 數據不足 ({len(df)} 筆,建議至少 200 筆)")
            elif len(df) > 0:
                print(f"✅ {symbol}: 成功獲取 {len(df)} 筆數據")
            
            # 保存到本地
            self.save_stock_data(symbol, df, source.market_name)
            
            return df
            
        except Exception as e:
            print(f"❌ {symbol}: 下載失敗 - {str(e)}")
            return None
    
    def batch_download(self, symbols: List[str], period: str = '2y',
                      delay: float = 0.5) -> Dict[str, pd.DataFrame]:
        """
        批量下載股票數據(支援多市場混合)
        
        參數:
            symbols: 股票代碼列表(可混合美股和台股)
            period: 時間範圍
            delay: 每次請求間隔(秒)
            
        返回:
            {symbol: DataFrame} 字典
        """
        print(f"\n開始批量下載 {len(symbols)} 支股票...")
        print(f"時間週期: {period}")
        print(f"=" * 80)
        
        results = {}
        success_count = 0
        fail_count = 0
        
        # 統計市場分佈
        us_symbols = []
        tw_symbols = []
        for symbol in symbols:
            source = self.get_source_for_symbol(symbol)
            if source.market_name == 'US':
                us_symbols.append(symbol)
            else:
                tw_symbols.append(symbol)
        
        print(f"📊 市場分佈: 美股 {len(us_symbols)} 支 | 台股 {len(tw_symbols)} 支\n")
        
        for i, symbol in enumerate(symbols, 1):
            source = self.get_source_for_symbol(symbol)
            market_flag = "🇺🇸" if source.market_name == 'US' else "🇹🇼"
            
            print(f"[{i}/{len(symbols)}] {market_flag} {symbol}...", end=" ")
            
            df = self.download_stock_data(symbol, period=period)
            
            if df is not None:
                results[symbol] = df
                success_count += 1
            else:
                fail_count += 1
            
            # 延遲避免請求過快
            if i < len(symbols):
                time.sleep(delay)
        
        print(f"\n" + "=" * 80)
        print(f"下載完成！")
        print(f"✅ 成功: {success_count} 支")
        print(f"❌ 失敗: {fail_count} 支")
        print(f"📊 成功率: {success_count/len(symbols)*100:.1f}%")
        
        return results
    
    def save_stock_data(self, symbol: str, df: pd.DataFrame, market: str):
        """
        保存股票數據到本地
        
        參數:
            symbol: 股票代碼
            df: 數據 DataFrame
            market: 市場名稱('US' 或 'TW')
        """
        # 保存數據文件
        filename = f"{self.data_dir}/daily/{symbol}.csv"
        df.to_csv(filename, index=False)
        
        # 保存元數據
        metadata = {
            'symbol': symbol,
            'market': market,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'rows': len(df),
            'start_date': df['date'].min().strftime('%Y-%m-%d'),
            'end_date': df['date'].max().strftime('%Y-%m-%d'),
            'columns': list(df.columns)
        }
        
        metadata_file = f"{self.data_dir}/metadata/{symbol}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def load_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        從本地載入股票數據
        
        參數:
            symbol: 股票代碼
            
        返回:
            DataFrame 或 None
        """
        filename = f"{self.data_dir}/daily/{symbol}.csv"
        
        try:
            df = pd.read_csv(filename)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            print(f"⚠️ {symbol}: 本地無數據,請先下載")
            return None
    
    def get_local_symbols(self) -> List[str]:
        """獲取本地已下載的股票列表"""
        daily_dir = f"{self.data_dir}/daily"
        
        if not os.path.exists(daily_dir):
            return []
        
        files = os.listdir(daily_dir)
        symbols = [f.replace('.csv', '') for f in files if f.endswith('.csv')]
        
        return sorted(symbols)
    
    def update_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        更新單支股票的數據
        
        參數:
            symbol: 股票代碼
            
        返回:
            更新後的 DataFrame
        """
        # 檢查本地是否有數據
        df_old = self.load_stock_data(symbol)
        
        if df_old is None:
            # 沒有本地數據,下載完整數據
            print(f"📥 {symbol}: 首次下載")
            return self.download_stock_data(symbol, period='2y')
        
        # 計算距離上次更新的天數
        last_date = df_old['date'].max()
        days_since_update = (pd.Timestamp.now() - last_date).days
        
        if days_since_update <= 1:
            print(f"✅ {symbol}: 數據已是最新")
            return df_old
        
        print(f"🔄 {symbol}: 更新數據(上次更新: {days_since_update} 天前)")
        
        # 下載最新數據
        df_new = self.download_stock_data(symbol, period='1mo')
        
        if df_new is None:
            return df_old
        
        # 合併數據
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=['date'], keep='last')
        df_combined = df_combined.sort_values('date').reset_index(drop=True)
        
        # 保存更新後的數據
        source = self.get_source_for_symbol(symbol)
        self.save_stock_data(symbol, df_combined, source.market_name)
        
        return df_combined
    
    def create_watchlist(self, name: str, symbols: List[str]):
        """
        創建觀察清單
        
        參數:
            name: 清單名稱
            symbols: 股票代碼列表
        """
        # 統計市場分佈
        market_count = {'US': 0, 'TW': 0}
        for symbol in symbols:
            source = self.get_source_for_symbol(symbol)
            market_count[source.market_name] += 1
        
        watchlist = {
            'name': name,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbols': symbols,
            'count': len(symbols),
            'market_distribution': market_count
        }
        
        filename = f"{self.data_dir}/watchlists/{name}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(watchlist, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 觀察清單 '{name}' 已創建")
        print(f"   總計: {len(symbols)} 支")
        print(f"   🇺🇸 美股: {market_count['US']} 支")
        print(f"   🇹🇼 台股: {market_count['TW']} 支")
    
    def load_watchlist(self, name: str) -> Optional[List[str]]:
        """
        載入觀察清單
        
        參數:
            name: 清單名稱
            
        返回:
            股票代碼列表
        """
        filename = f"{self.data_dir}/watchlists/{name}.json"
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                watchlist = json.load(f)
            return watchlist['symbols']
        except FileNotFoundError:
            print(f"⚠️ 觀察清單 '{name}' 不存在")
            return None
    
    def get_data_summary(self) -> pd.DataFrame:
        """獲取本地數據摘要"""
        symbols = self.get_local_symbols()
        
        if not symbols:
            print("⚠️ 本地無數據")
            return pd.DataFrame()
        
        summaries = []
        
        for symbol in symbols:
            metadata_file = f"{self.data_dir}/metadata/{symbol}.json"
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                summaries.append(metadata)
            except:
                continue
        
        if not summaries:
            return pd.DataFrame()
        
        df_summary = pd.DataFrame(summaries)
        df_summary = df_summary.sort_values(['market', 'symbol'])
        
        return df_summary
    
    def get_market_symbols(self, market: str, category: str = 'popular') -> List[str]:
        """
        獲取指定市場的股票清單
        
        參數:
            market: 'US' 或 'TW'
            category: 股票類別
            
        返回:
            股票代碼列表
        """
        if market.upper() == 'US':
            return self.us_source.get_market_symbols(category)
        elif market.upper() == 'TW':
            return self.tw_source.get_market_symbols(category)
        else:
            print(f"⚠️ 未知市場: {market}")
            return []


# ========== 使用範例 ==========

def example_mixed_download():
    """範例: 混合下載美股和台股"""
    print("\n" + "="*80)
    print("範例: 混合下載美股和台股")
    print("="*80)
    
    manager = UnifiedStockDataManager(data_dir='./unified_stock_data')
    
    # 混合的股票清單
    mixed_symbols = [
        # 美股
        'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA',
        # 台股
        '2330', '2317', '2454', '2881', '2882'
    ]
    
    # 批量下載
    results = manager.batch_download(mixed_symbols, period='1y', delay=0.5)
    
    print(f"\n成功下載 {len(results)} 支股票")
    
    # 創建混合觀察清單
    manager.create_watchlist('my_portfolio', mixed_symbols)


def example_market_specific():
    """範例: 分市場下載"""
    print("\n" + "="*80)
    print("範例: 分市場下載")
    print("="*80)
    
    manager = UnifiedStockDataManager(data_dir='./unified_stock_data')
    
    # 下載美股道瓊斯成分股
    print("\n【下載美股】")
    us_symbols = manager.get_market_symbols('US', 'dow')
    print(f"道瓊斯 30: {us_symbols[:5]}...")
    
    # 下載台股半導體類股
    print("\n【下載台股】")
    tw_symbols = manager.get_market_symbols('TW', 'semiconductor')
    print(f"半導體類股: {tw_symbols}")
    
    # 合併下載
    all_symbols = us_symbols[:5] + tw_symbols
    results = manager.batch_download(all_symbols, period='1y', delay=0.5)


def example_data_management():
    """範例: 數據管理"""
    print("\n" + "="*80)
    print("範例: 數據管理")
    print("="*80)
    
    manager = UnifiedStockDataManager(data_dir='./unified_stock_data')
    
    # 查看本地數據摘要
    summary = manager.get_data_summary()
    
    if not summary.empty:
        print("\n本地數據摘要:")
        print(summary[['symbol', 'market', 'rows', 'start_date', 'end_date']])
        
        print(f"\n統計:")
        print(f"總股票數: {len(summary)}")
        print(f"美股: {len(summary[summary['market']=='US'])} 支")
        print(f"台股: {len(summary[summary['market']=='TW'])} 支")
    
    # 更新所有本地股票
    print("\n更新本地數據...")
    local_symbols = manager.get_local_symbols()
    for symbol in local_symbols[:3]:  # 只更新前3支作為示範
        manager.update_stock_data(symbol)
        time.sleep(0.5)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          統一股票資料管理器 - Unified Stock Data Manager      ║
    ║                   支援美股 + 台股混合分析                       ║
    ╚════════════════════════════════════════════════════════════════╝
    
    功能:
    1. 🌐 自動判斷股票所屬市場(美股/台股)
    2. 📥 批量下載多市場股票
    3. 💾 本地數據快取和更新
    4. 📋 觀察清單管理
    5. 📊 統一的數據格式
    """)
    
    # 運行範例
    example_mixed_download()
    
    input("\n按 Enter 繼續下一個範例...")
    example_market_specific()
    
    input("\n按 Enter 繼續下一個範例...")
    example_data_management()
    
    print("\n" + "="*80)
    print("✅ 所有演示完成！")
    print("="*80)
