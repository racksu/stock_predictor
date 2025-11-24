# 🔄 從 FinMind 遷移到 TWSE 官方 API

## 📋 遷移說明

由於 FinMind 有 Token 限制，我們提供了完整的 TWSE（台灣證券交易所）官方 API 解決方案，**完全免費、無需 Token**！

---

## ✨ TWSE API 優勢

| 特性 | FinMind | TWSE 官方 API |
|------|---------|---------------|
| **Token 需求** | ✅ 需要註冊取得 | ❌ 無需 Token |
| **請求限制** | 300次/小時（免費版） | 無限制（建議間隔3-5秒） |
| **數據準確性** | 高 | 最高（官方來源） |
| **數據延遲** | 較低 | 最低 |
| **使用成本** | 免費版有限 | 完全免費 |
| **穩定性** | 依賴第三方 | 官方保證 |

---

## 🚀 快速開始

### 1. 使用新的 TWSE 數據源

```python
from twse_data_source import TWSEDataSource
from usage_examples_twse import TWSTockDataFetcher

# 初始化（無需 Token！）
twse = TWSEDataSource()
fetcher = TWSTockDataFetcher()
```

### 2. 獲取價格數據

**舊方式（FinMind）：**
```python
from FinMind.data import DataLoader

api = DataLoader()
api.login_by_token(api_token='你的Token')
df = api.taiwan_stock_daily(stock_id='2330', start_date='2023-01-01')
```

**新方式（TWSE）：**
```python
from usage_examples_twse import TWSTockDataFetcher

fetcher = TWSTockDataFetcher()
df = fetcher.get_price_data('2330', start_date='2023-01-01')
```

✅ **無需 Token，更簡單！**

---

### 3. 獲取三大法人數據

**舊方式（FinMind）：**
```python
df_inst = api.taiwan_stock_institutional_investors(
    stock_id='2330',
    start_date='2024-01-01'
)
```

**新方式（TWSE）：**
```python
df_inst = fetcher.get_institutional_data('2330', lookback_days=30)
```

✅ **直接指定天數，更直觀！**

---

### 4. 獲取融資融券數據

**舊方式（FinMind）：**
```python
df_margin = api.taiwan_stock_margin_purchase_short_sale(
    stock_id='2330',
    start_date='2024-01-01'
)
```

**新方式（TWSE）：**
```python
df_margin = fetcher.get_margin_data('2330', lookback_days=30)
```

✅ **自動計算融資使用率、券資比！**

---

## 📊 完整分析範例

### 使用 TWSE API 進行完整分析

```python
from usage_examples_twse import TWSTockDataFetcher
from smart_stock_picker_enhanced_v3 import EnhancedStockPicker

# 1. 初始化
fetcher = TWSTockDataFetcher()
picker = EnhancedStockPicker()

# 2. 獲取所有需要的數據
stock_no = '2330'

price_data = fetcher.get_price_data(stock_no, lookback_days=730)  # 2年
institutional_data = fetcher.get_institutional_data(stock_no, lookback_days=30)
margin_data = fetcher.get_margin_data(stock_no, lookback_days=30)

# 3. 執行完整分析
analysis = picker.analyze_stock_enhanced(
    symbol=stock_no,
    price_data=price_data,
    institutional_data=institutional_data,
    margin_data=margin_data,
    use_macro=True  # 啟用總體經濟分析
)

# 4. 顯示結果
from smart_stock_picker_enhanced_v3 import print_enhanced_analysis_report
print_enhanced_analysis_report(analysis)
```

---

## 🔍 API 對照表

### 價格數據

| 數據項目 | FinMind 欄位 | TWSE 欄位 |
|---------|-------------|-----------|
| 日期 | date | date |
| 開盤價 | open | Open |
| 最高價 | max | High |
| 最低價 | min | Low |
| 收盤價 | close | Close |
| 成交量 | Trading_Volume | Volume |

### 三大法人

| 數據項目 | FinMind 欄位 | TWSE 欄位 |
|---------|-------------|-----------|
| 外資買超 | Foreign_Investor_Net_Buy_Sell | foreign_net |
| 投信買超 | Investment_Trust_Net_Buy_Sell | trust_net |
| 自營商買超 | Dealer_Net_Buy_Sell | dealer_net |

### 融資融券

| 數據項目 | FinMind 欄位 | TWSE 欄位 |
|---------|-------------|-----------|
| 融資餘額 | Margin_Balance | margin_balance |
| 融資限額 | Margin_Limit | margin_limit |
| 融券餘額 | Short_Balance | short_balance |
| 融資使用率 | - | margin_usage_rate（自動計算） |
| 券資比 | - | short_margin_ratio（自動計算） |

---

## ⚙️ 配置調整

### 更新 Web 服務器（可選）

如果你想在 Web 介面中使用 TWSE API，可以修改 `web_server_enhanced_v3.1.py`：

**原本：**
```python
from usage_examples_enhanced import TaiwanStockDataFetcher
```

**改為：**
```python
from usage_examples_twse import TWSTockDataFetcher as TaiwanStockDataFetcher
```

就這麼簡單！介面兼容，無需其他修改。

---

## 📝 使用範例腳本

我們提供了完整的範例腳本 `usage_examples_twse.py`，包含：

1. **完整分析**：技術面 + 法人 + 籌碼 + 總經
2. **批量分析**：分析多支股票並排序
3. **即時監控**：監控三大法人動向
4. **融資融券分析**：深度分析籌碼面

### 執行範例：

```bash
# 執行完整分析
python usage_examples_twse.py 1

# 批量分析
python usage_examples_twse.py 2

# 監控法人
python usage_examples_twse.py 3

# 融資融券分析
python usage_examples_twse.py 4

# 全部執行
python usage_examples_twse.py 0
```

---

## ⚠️ 注意事項

### 1. 請求間隔

TWSE API 建議請求間隔：
- **個股日資料**：3秒
- **三大法人**：5秒
- **融資融券**：5秒

**已內建延遲處理**，無需手動設置！

### 2. 交易日限制

- 週末及國定假日無數據
- 盤後約 15:30 更新當日數據
- 建議在交易日 16:00 後查詢

### 3. 數據格式

TWSE API 使用民國年（如 113/11/21），我們已自動轉換為西元年。

---

## 🆚 性能對比

### 獲取 2 年歷史數據（2330）

| 方法 | 請求次數 | 總時間 | Token消耗 |
|------|---------|--------|----------|
| **FinMind** | 1次 | ~2秒 | 1次 |
| **TWSE** | 24次 | ~72秒 | 0次 |

**結論**：
- FinMind 更快，但有 Token 限制
- TWSE 較慢，但**無限制、永久免費**

💡 **建議**：
- 歷史數據：第一次用 TWSE 下載並快取
- 日常更新：每天只需更新當日，很快
- 長期使用：TWSE 更穩定可靠

---

## 🔧 故障排除

### Q: 獲取數據失敗？

**可能原因**：
1. 非交易日（週末/假日）
2. 請求太快被暫時封鎖
3. 股票代號錯誤

**解決方案**：
```python
# 檢查是否為交易日
from datetime import datetime
import pandas as pd

today = datetime.now()
if today.weekday() >= 5:  # 週末
    print("⚠️ 今天是週末，無交易數據")

# 使用更長的延遲
twse = TWSEDataSource()
# 請求會自動處理延遲
```

### Q: 數據格式不對？

檢查欄位對照表，TWSE 使用標準化欄位名稱。

### Q: 如何提升速度？

```python
# 使用本地快取
from unified_stock_data_manager import UnifiedStockDataManager

manager = UnifiedStockDataManager()

# 第一次下載並快取
df = fetcher.get_price_data('2330', lookback_days=730)
manager.save_stock_data('2330', df, 'TW')

# 之後直接載入快取
df_cached = manager.load_stock_data('2330')
```

---

## 📚 延伸閱讀

### TWSE API 官方文檔
- 個股日成交：https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY
- 三大法人：https://www.twse.com.tw/rwd/zh/fund/T86
- 融資融券：https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN

### 相關檔案
- `twse_data_source.py` - TWSE API 封裝
- `usage_examples_twse.py` - 完整使用範例
- `README_v4.md` - 系統完整說明

---

## 🎉 總結

使用 TWSE 官方 API 的優勢：

✅ **無 Token 限制** - 永久免費
✅ **官方數據** - 最準確可靠
✅ **簡單易用** - 與原系統完全兼容
✅ **完整功能** - 支持所有分析需求

**立即開始使用 TWSE API，享受無限制的台股分析！** 🚀

---

**有任何問題？**

1. 查看 `usage_examples_twse.py` 中的範例
2. 閱讀 `README_v4.md` 完整文檔
3. 測試 `twse_data_source.py` 各項功能

祝你分析愉快！📈
