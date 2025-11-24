# 回測系統使用說明

## 📖 簡介

這是一個完整的股票策略回測系統,用於驗證你的選股策略在歷史數據上的實際表現。

### 為什麼需要回測?

- ✅ **驗證策略有效性**: 在真實交易前,用歷史數據測試策略
- ✅ **優化參數**: 找出最佳的停損、停利、倉位等參數
- ✅ **風險評估**: 了解策略的最大回撤和風險
- ✅ **建立信心**: 看到實際績效數據,更有信心執行策略

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install pandas numpy matplotlib
```

### 2. 執行回測範例

```bash
python backtesting_examples.py
```

選擇你想要的範例:
- **範例1**: 基本回測 - 單一股票 (台積電)
- **範例2**: 參數比較 - 測試不同倉位大小
- **範例3**: 多檔股票回測
- **範例4**: 停損停利參數優化

## 📊 功能特色

### 1. 真實交易模擬

回測系統模擬真實交易環境,包含:

- **手續費**: 0.1425% (券商手續費)
- **證交稅**: 0.3% (賣出時)
- **滑價**: 0.1% (買賣價差)

### 2. 風險管理

- **停損機制**: 自動停損,控制單筆虧損
- **停利機制**: 達到目標價自動獲利了結
- **倉位控制**: 設定單次建倉比例
- **動態評估**: 定期重新評估持倉,評分轉差時出場

### 3. 績效指標

計算多項專業績效指標:

| 指標 | 說明 |
|------|------|
| **總報酬率** | 整體獲利百分比 |
| **勝率** | 獲利交易次數 / 總交易次數 |
| **Sharpe比率** | 風險調整後報酬,越高越好 |
| **最大回撤** | 最大虧損幅度 |
| **獲利因子** | 總獲利 / 總虧損,>1表示獲利 |
| **平均持有天數** | 平均每筆交易持有時間 |

## 💡 使用範例

### 範例 1: 基本回測

```python
from backtesting_engine import BacktestingEngine
from unified_stock_data_manager import UnifiedStockDataManager

# 1. 載入數據
manager = UnifiedStockDataManager(data_dir='./stock_data')
df = manager.load_stock_data('2330')  # 台積電

# 2. 創建回測引擎
engine = BacktestingEngine(
    initial_capital=1000000,   # 100萬初始資金
    commission_rate=0.001425,  # 手續費
    tax_rate=0.003,            # 證交稅
    slippage=0.001             # 滑價
)

# 3. 執行回測
results = engine.run_backtest(
    df=df,
    strategy='enhanced',      # 使用增強版策略
    position_size=0.3,        # 30% 倉位
    stop_loss=-0.08,          # -8% 停損
    take_profit=0.15,         # 15% 停利
    rebalance_days=5          # 每5天重新評估
)

# 4. 查看績效報告
engine.print_performance_report()

# 5. 導出結果
engine.export_results('backtest_2330.csv')
```

### 範例 2: 參數優化

測試不同的停損停利組合,找出最佳參數:

```python
stop_losses = [-0.05, -0.08, -0.10]
take_profits = [0.10, 0.15, 0.20]

best_sharpe = -999
best_params = None

for stop_loss in stop_losses:
    for take_profit in take_profits:
        engine = BacktestingEngine(initial_capital=1000000)
        results = engine.run_backtest(
            df=df,
            strategy='enhanced',
            position_size=0.3,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        sharpe = results['metrics']['sharpe_ratio']
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = (stop_loss, take_profit)

print(f"最佳參數: 停損={best_params[0]*100:.0f}%, 停利={best_params[1]*100:.0f}%")
```

### 範例 3: 多檔股票回測

批量測試多支股票:

```python
symbols = ['2330', '2317', '2454', '3008', '2308']
results = {}

for symbol in symbols:
    df = manager.load_stock_data(symbol)
    engine = BacktestingEngine(initial_capital=1000000)
    result = engine.run_backtest(df=df, strategy='enhanced')
    results[symbol] = result

# 比較各股票表現
for symbol, result in results.items():
    print(f"{symbol}: 總報酬 {result['total_return']*100:+.2f}%")
```

## 📈 績效報告範例

```
================================================================================
績效報告 (Performance Report)
================================================================================

【總體表現】
  初始資金: $1,000,000
  最終淨值: $1,156,000
  總報酬率: +15.60%
  最大回撤: 12.50%
  Sharpe比率: 1.85

【交易統計】
  總交易次數: 12
  獲利次數: 9
  虧損次數: 3
  勝率: 75.00%
  平均持有天數: 18.5天

【獲利分析】
  平均獲利: $13,000 (+6.50%)
  最大單筆獲利: $45,000
  最大單筆虧損: $-18,000
  總獲利: $234,000
  總虧損: $78,000
  獲利因子: 3.00

【交易明細】
進場日期      出場日期      進場價   出場價   報酬率      持有天  原因
--------------------------------------------------------------------------------
2023-01-15   2023-02-03   $450.00  $485.00   +7.78%      19天   停利 (+7.78%)
2023-02-20   2023-02-28   $470.00  $458.00   -2.55%       8天   評分轉差 (18.5分)
...
================================================================================
```

## 🎯 策略邏輯

回測系統使用你的選股策略進行交易決策:

### 買入條件

1. **技術面評分 >= 25分** (滿分40)
2. **KD指標良好 >= 8分** (滿分15)
3. **有足夠資金** (根據倉位比例計算)

### 賣出條件

1. **觸發停損**: 虧損達到設定比例 (如-8%)
2. **觸發停利**: 獲利達到設定比例 (如+15%)
3. **評分轉差**: 重新評估時技術評分 < 20分
4. **回測結束**: 強制平倉

### 資金管理

- 每次建倉使用固定比例的可用資金 (如30%)
- 台股以1000股(1張)為交易單位
- 同時只持有一檔股票 (單一持倉)
- 計入所有交易成本 (手續費、稅、滑價)

## 📁 輸出檔案

執行回測後會產生以下檔案:

### 1. 交易記錄 CSV
檔名: `backtest_2330.csv`

包含所有交易的詳細記錄:
- 進場/出場日期
- 進場/出場價格
- 股數
- 獲利金額和百分比
- 持有天數
- 出場原因

### 2. 資金曲線 CSV
檔名: `backtest_2330_equity.csv`

每日的資金變化:
- 日期
- 淨值
- 可用資金
- 持倉市值

### 3. 資金曲線圖
檔名: `equity_curve.png`

視覺化顯示資金隨時間的變化趨勢

## ⚙️ 參數說明

### BacktestingEngine 參數

```python
BacktestingEngine(
    initial_capital=1000000,   # 初始資金 (預設100萬)
    commission_rate=0.001425,  # 手續費率 (預設0.1425%)
    tax_rate=0.003,            # 證交稅率 (預設0.3%)
    slippage=0.001             # 滑價率 (預設0.1%)
)
```

### run_backtest 參數

```python
engine.run_backtest(
    df=df,                    # 歷史數據 DataFrame
    strategy='enhanced',      # 策略: 'basic' 或 'enhanced'
    position_size=0.3,        # 單次倉位 (0.1 = 10%, 0.3 = 30%)
    stop_loss=-0.08,          # 停損比例 (-0.08 = -8%)
    take_profit=0.15,         # 停利比例 (0.15 = 15%)
    rebalance_days=5          # 重新評估天數 (5 = 每5天)
)
```

## 📝 注意事項

### ⚠️ 重要提醒

1. **歷史表現不代表未來**
   - 回測結果僅供參考
   - 市場環境會改變
   - 實際交易可能有其他風險

2. **過度優化風險**
   - 不要過度調整參數以符合歷史數據
   - 這可能導致「過擬合」
   - 在未來市場表現不佳

3. **數據品質**
   - 確保使用高品質的歷史數據
   - 檢查數據是否有缺失或錯誤
   - 建議至少使用2年的數據

4. **交易成本**
   - 系統已包含手續費、稅、滑價
   - 實際成本可能因券商而異
   - 高頻交易會產生更多成本

5. **心理因素**
   - 回測無法模擬真實交易的心理壓力
   - 實際執行時需要紀律
   - 建議先用小資金實測

## 🔧 進階功能

### 1. 自定義策略

你可以修改 `backtesting_engine.py` 來實現自己的策略邏輯:

```python
# 在 run_backtest 方法中修改買入條件
if tech_score >= 30 and kd_score >= 10:  # 更嚴格的條件
    # 執行買入
    ...
```

### 2. 多策略比較

使用 `ComparisonBacktest` 類別比較不同策略:

```python
from backtesting_engine import ComparisonBacktest

comparison = ComparisonBacktest(df)
results = comparison.compare_strategies(
    strategies=['basic', 'enhanced'],
    initial_capital=1000000
)
```

### 3. 整合其他指標

在策略評估中加入更多因子:
- 法人買賣超 (需要 FinMind API)
- 籌碼面數據
- 總體經濟指標

## 📞 問題與支援

如果遇到問題:

1. 檢查是否安裝所有依賴套件
2. 確認數據檔案存在且完整
3. 查看錯誤訊息和追蹤堆疊
4. 參考 `backtesting_examples.py` 中的範例

## 🎓 學習資源

建議閱讀:
- 《交易系統與方法》- Perry Kaufman
- 《Python金融大數據分析》- Yves Hilpisch
- Quantopian Research (線上回測平台)

---

**祝你回測順利!** 🚀📈

記住:好的策略需要經過充分的回測驗證,但最終還是要在實戰中證明自己!
