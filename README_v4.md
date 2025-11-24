# 🚀 台股預測系統 v4.0 - 全面升級版

## 📊 系統概述

這是一個整合**多因子分析**、**AI輿情**、**總體經濟**的智能選股系統，支援**美股**和**台股**雙市場分析。

### 🎯 核心特色

- ✅ **五大維度分析**：技術面 + 市場面 + 籌碼面 + 總體經濟 + AI輿情
- ✅ **雙市場支援**：美股 (yfinance) + 台股 (FinMind)
- ✅ **AI驅動**：情緒分析、新聞熱度、市場情緒
- ✅ **實時指標**：VIX、美元指數、公債殖利率
- ✅ **美觀UI**：現代化Web介面，響應式設計

---

## 🆕 v4.0 新增功能

### 1️⃣ 總體經濟分析模組 (macro_economic_analyzer.py)

**整合全球宏觀指標，評估市場環境**

#### 功能亮點：
- 📊 **VIX恐慌指數** - 市場情緒溫度計
  - < 15: 極度平靜（可能過度樂觀）
  - 15-20: 正常低波動
  - 20-30: 正常波動
  - 30-40: 市場恐慌
  - \> 40: 極度恐慌（逆向機會）

- 💵 **美元指數 (DXY)** - 資金流向指標
  - 強勢美元 → 對新興市場負面
  - 弱勢美元 → 資金流向風險資產

- 📈 **10年期公債殖利率** - 利率環境
  - 快速上升 → 股市負面
  - 下降 → 資金尋求更高收益

#### 權重配置：
```yaml
VIX: 40%        # 最直接影響
美元指數: 30%
公債殖利率: 30%
```

#### 使用範例：
```python
from macro_economic_analyzer import MacroEconomicAnalyzer

analyzer = MacroEconomicAnalyzer()
macro_result = analyzer.calculate_macro_score(lookback_days=30)

print(f"總體經濟評分: {macro_result['macro_total_score']:.1f}/10")
print(f"市場環境: {macro_result['macro_environment']}")
```

---

### 2️⃣ AI輿情分析模組 (sentiment_analyzer.py)

**使用自然語言處理分析新聞情緒與市場熱度**

#### 功能亮點：
- 📰 **新聞獲取** - 自動抓取股票相關新聞 (NewsAPI)
- 🤖 **AI情緒分析** - VADER情緒分析引擎
- 🔥 **熱度評分** - 基於新聞數量的市場關注度
- 📊 **趨勢分析** - 正面/負面/中性比例

#### 評分標準：
```
新聞數量 ≥ 50  → 熱度 10分
新聞數量 ≥ 30  → 熱度 8分
新聞數量 ≥ 20  → 熱度 7分
新聞數量 ≥ 10  → 熱度 5分
```

#### 使用範例：
```python
from sentiment_analyzer import SentimentAnalyzer

# 需要NewsAPI密鑰（免費註冊：https://newsapi.org）
analyzer = SentimentAnalyzer(newsapi_key='你的密鑰')

# 分析AAPL的輿情
result = analyzer.calculate_sentiment_score(
    symbol='AAPL',
    company_name='Apple',
    days_back=7
)

print(f"輿情評分: {result['combined_score']:.1f}/10")
print(f"情緒環境: {result['environment']}")
print(f"新聞數量: {result['news_count']}")
```

---

### 3️⃣ 成交量與流動性指標 (前端顯示)

**在Web介面新增成交量分析，幫助判斷流動性**

#### 新增指標：
- 📊 **平均成交量** - 近20日平均
- 📈 **相對成交量** - 當日成交量 ÷ 平均成交量
  - \> 1.5x: 放量（正面信號）
  - < 0.5x: 縮量（觀望氣氛）
- 💧 **流動性評級** - 極高/高/中等/低/極低

#### 前端顯示：
```javascript
// 自動格式化成交量
formatVolume(1500000000)  // → "1.50B"
formatVolume(50000000)     // → "50.00M"
formatVolume(250000)       // → "250.00K"

// 動態顏色標示
相對成交量 > 1.5x → 綠色（放量）
流動性低 → 紅色警示
```

---

## 📐 多因子權重架構

### v4.0 權重分配（總和 = 100%）

```
┌─────────────────────────────────────────────┐
│  技術面：35%  (從 40% 調整)                   │
│    ├─ KD指標: 15%                            │
│    ├─ OBV: 10%                               │
│    ├─ MA均線: 10%                            │
│    └─ RSI/MACD: 各2.5%                       │
├─────────────────────────────────────────────┤
│  市場面：25%  (從 30% 調整)                   │
│    ├─ 投信買賣超: 12%                         │
│    ├─ 外資買賣超: 10%                         │
│    └─ 自營商+共識: 3%                         │
├─────────────────────────────────────────────┤
│  籌碼面：25%  (從 30% 調整)                   │
│    ├─ 融資使用率: 12%                         │
│    ├─ 主力進出: 10%                           │
│    └─ 券資比+當沖: 3%                         │
├─────────────────────────────────────────────┤
│  總體經濟：15%  (NEW!)                        │
│    ├─ VIX恐慌指數: 6%                         │
│    ├─ 美元指數: 4.5%                          │
│    └─ 公債殖利率: 4.5%                        │
└─────────────────────────────────────────────┘
```

### 可選整合（未來擴展）
```
AI輿情分析：可作為輔助參考
  ├─ 新聞情緒: 70%
  └─ 熱度評分: 30%
```

---

## 🛠️ 系統安裝

### 環境需求
- Python 3.8+
- pip套件管理工具

### 1. 安裝基礎套件

```bash
# 核心分析套件
pip install pandas numpy yfinance

# Web伺服器
pip install flask flask-cors

# 總體經濟分析（可選）
pip install yfinance  # VIX、DXY數據

# AI輿情分析（可選但推薦）
pip install newsapi-python vaderSentiment
```

### 2. 配置API密鑰（可選）

#### NewsAPI（新聞分析）
1. 前往 https://newsapi.org 免費註冊
2. 獲取API密鑰
3. 在程式中使用：
```python
from sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer(newsapi_key='你的密鑰')
```

#### FinMind（台股法人數據）
1. 前往 https://finmindtrade.com 註冊
2. 獲取API Token
3. 在 `config_enhanced.yaml` 中配置：
```yaml
api:
  finmind_token: "你的Token"
```

---

## 🚀 快速開始

### 方法1：命令列分析

```python
from smart_stock_picker_enhanced_v3 import EnhancedStockPicker
from unified_stock_data_manager import UnifiedStockDataManager

# 初始化
picker = EnhancedStockPicker()
manager = UnifiedStockDataManager()

# 下載數據
price_data = manager.download_stock_data('2330', period='2y')

# 執行分析（包含總體經濟）
result = picker.analyze_stock_enhanced(
    symbol='2330',
    price_data=price_data,
    use_macro=True  # 啟用總體經濟分析
)

# 顯示結果
print(f"綜合評分: {result['enhanced_score']:.1f}/100")
print(f"操作建議: {result['enhanced_recommendation']}")
```

### 方法2：Web介面（推薦）

```bash
# 啟動伺服器
python web_server_enhanced_v3.1.py

# 瀏覽器開啟
http://localhost:5000
```

#### Web功能：
- 📥 下載數據：支援單股、批量、預設清單
- 📊 單股分析：完整五維度分析
- 🔍 智能篩選：多條件篩選優質標的
- 💾 本地管理：查看已下載股票

---

## 📊 分析報告解讀

### 綜合評分 (0-100分)

| 分數範圍 | 信號 | 建議操作 |
|---------|------|----------|
| 80-100 | 強烈看多 | 積極進場，倉位50-70% |
| 60-79  | 看多 | 謹慎進場，倉位30-50% |
| 40-59  | 中性 | 觀望或輕倉 |
| 20-39  | 看空 | 減倉至10-30% |
| 0-19   | 強烈看空 | 空手或避險 |

### 詳細評分明細

#### 技術面 (35分)
- **KD指標**: 低檔金叉 → 最強買入信號
- **OBV**: 上升趨勢 → 資金流入
- **MA**: 多頭排列 → 趨勢向上

#### 市場面 (25分)
- **投信**: 連續買超5天 → 看多
- **外資**: 買超支撐 → 強力支撐

#### 籌碼面 (25分)
- **融資**: 使用率 < 30% → 接近底部
- **主力**: 三線向上 → 主力控盤

#### 總體經濟 (15分)
- **VIX < 20**: 市場平靜
- **美元弱勢**: 資金流向股市
- **殖利率下降**: 有利股市

---

## 🔧 進階配置

### 自訂權重

編輯 `config_enhanced.yaml`:

```yaml
weights:
  technical: 0.35  # 技術面
  market: 0.25     # 市場面
  chips: 0.25      # 籌碼面
  macro: 0.15      # 總體經濟
```

### 調整指標參數

```yaml
indicators:
  kd:
    n: 9           # RSV週期
    m1: 3          # K值平滑
    m2: 3          # D值平滑
    oversold: 20   # 超賣
    overbought: 80 # 超買
```

---

## 📁 檔案結構

```
台股預測系統/
├── 📄 核心分析模組
│   ├── smart_stock_picker_enhanced_v3.py    # 主選股引擎（已整合總經）
│   ├── macro_economic_analyzer.py           # 總體經濟分析（NEW!）
│   ├── sentiment_analyzer.py                # AI輿情分析（NEW!）
│   ├── unified_stock_data_manager.py        # 數據管理器
│   ├── taiwan_stock_database.py             # 台股數據庫
│   └── stock_data_source_*.py               # 數據源（美股/台股）
│
├── 🌐 Web介面
│   ├── web_server_enhanced_v3.1.py          # Flask伺服器
│   └── stock_picker_web_v5_enhanced.html    # 前端（新增成交量顯示）
│
├── ⚙️ 配置與文檔
│   ├── config_enhanced.yaml                 # 系統配置（已更新權重）
│   ├── README_v4.md                         # 本文檔
│   └── usage_examples_enhanced.py           # 使用範例
│
└── 💾 數據目錄（自動創建）
    ├── stock_data/                          # 價格數據
    ├── stock_data_cache/                    # 快取
    └── analysis_results/                    # 分析結果
```

---

## 🎓 使用範例

### 範例1：完整分析（含總經+輿情）

```python
from smart_stock_picker_enhanced_v3 import EnhancedStockPicker
from macro_economic_analyzer import MacroEconomicAnalyzer
from sentiment_analyzer import SentimentAnalyzer
from unified_stock_data_manager import UnifiedStockDataManager

# 初始化
picker = EnhancedStockPicker()
macro_analyzer = MacroEconomicAnalyzer()
sentiment_analyzer = SentimentAnalyzer(newsapi_key='你的密鑰')
manager = UnifiedStockDataManager()

# 1. 獲取總體經濟環境
macro_score = macro_analyzer.calculate_macro_score()
print(f"總體環境: {macro_score['macro_environment']}")

# 2. 分析輿情
sentiment = sentiment_analyzer.calculate_sentiment_score('AAPL', 'Apple')
print(f"輿情評分: {sentiment['combined_score']:.1f}/10")

# 3. 股票分析
price_data = manager.download_stock_data('AAPL')
result = picker.analyze_stock_enhanced(
    symbol='AAPL',
    price_data=price_data,
    use_macro=True
)

print(f"綜合評分: {result['enhanced_score']:.1f}/100")
```

### 範例2：批量篩選優質股票

```python
# 下載多支股票
symbols = ['2330', '2317', '2454', '2881', '2882']
stocks_data = {}

for symbol in symbols:
    df = manager.download_stock_data(symbol)
    if df is not None:
        stocks_data[symbol] = df

# 設定篩選條件
filters = {
    'min_score': 60,           # 最低評分60
    'min_expected_return': 0.1, # 最低報酬10%
    'min_risk_reward': 2.0     # 風險報酬比≥2
}

# 執行篩選
results = picker.screen_stocks(stocks_data, filters)
print(f"找到 {len(results)} 支符合條件的股票")
print(results[['symbol', 'total_score', 'expected_return']])
```

---

## ⚠️ 重要聲明

### 風險警示
1. **本系統僅供參考**，不構成投資建議
2. **過去績效不代表未來**，請自行評估風險
3. **投資有風險**，請謹慎操作
4. **建議搭配其他分析工具**綜合判斷

### 數據準確性
- 技術指標：基於歷史價格計算
- 法人數據：來自公開資訊（可能延遲1-2天）
- 總體經濟：實時獲取（需網路連接）
- AI輿情：依賴新聞API（有數量限制）

### 使用建議
1. ✅ 作為**輔助工具**，結合基本面分析
2. ✅ 設定**停損點**，控制風險
3. ✅ 分散投資，不要單押一支股票
4. ✅ 定期檢視持股，適時調整

---

## 🤝 技術支援

### 常見問題

**Q: NewsAPI 免費版有限制嗎？**
A: 免費版每日100次請求，足夠個人使用。

**Q: FinMind Token 如何獲取？**
A: 前往 https://finmindtrade.com 註冊即可免費獲得。

**Q: 總體經濟數據多久更新一次？**
A: VIX、美元、殖利率每次分析時實時獲取。

**Q: 為何某些股票分析失敗？**
A: 可能是數據不足（<200筆）或網路問題。

### 錯誤排查

```python
# 檢查系統健康
import sys
print(f"Python版本: {sys.version}")

# 檢查必要套件
try:
    import pandas, numpy, yfinance, flask
    print("✅ 基礎套件正常")
except ImportError as e:
    print(f"❌ 缺少套件: {e}")

# 檢查可選套件
try:
    from newsapi import NewsApiClient
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    print("✅ AI分析套件正常")
except ImportError:
    print("⚠️ AI分析套件未安裝（功能受限）")
```

---

## 🎉 更新日誌

### v4.0 (2025-01-23)
- ✨ **新增**：總體經濟分析模組（VIX、美元、利率）
- ✨ **新增**：AI輿情分析模組（新聞情緒+熱度）
- ✨ **新增**：前端成交量與流動性指標顯示
- 🔧 **調整**：多因子權重架構（技35%、市25%、籌25%、總經15%）
- 📚 **新增**：完整使用說明文檔

### v3.0
- 整合台股波段預測框架
- 加入KD+OBV優化指標
- 三大法人、融資融券分析

### v2.1
- 支援美股+台股雙市場
- Web介面優化

---

## 📞 聯繫方式

- 📧 Email: 系統管理員
- 💬 Issues: GitHub Issues
- 📖 文檔: README.md

---

## 📜 授權

本專案僅供學習和研究使用，請勿用於商業用途。

---

**🎯 祝你投資順利！記得理性投資，風險自負！** 🚀

