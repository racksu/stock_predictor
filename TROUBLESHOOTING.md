# 🔧 故障排除指南

## 問題：下載台股/美股時出現錯誤

### 步驟 1：運行系統診斷

首先運行診斷腳本來檢查系統配置：

```cmd
python diagnose_system.py
```

這個腳本會檢查：
- ✅ Python 版本
- ✅ 所有必要的套件
- ✅ 核心模組是否可以導入
- ✅ HTML 文件是否存在
- ✅ 實際測試下載美股和台股

### 步驟 2：查看診斷結果

#### 如果看到 "❌ 缺少必要套件"

執行以下命令安裝缺失的套件：

```cmd
pip install -r requirements.txt
```

或者根據診斷結果手動安裝缺失的套件：

```cmd
pip install pandas numpy flask flask-cors yfinance scipy scikit-learn
```

安裝完成後，**重新運行診斷腳本**確認。

#### 如果看到 "❌ 核心模組導入失敗"

這表示某些 Python 文件可能缺失或損壞。請確認以下文件存在：
- `stock_data_source_abc.py`
- `stock_data_source_us.py`
- `stock_data_source_tw.py`
- `unified_stock_data_manager.py`
- `smart_stock_picker_v2_1.py`
- `smart_stock_picker_enhanced_v3.py`

#### 如果看到 "❌ HTML 文件不存在"

請確認至少有以下一個文件存在：
- `stock_picker_web_v5_enhanced.html` (推薦)
- `stock_picker_web_v4_enhanced.html`

---

### 步驟 3：啟動 Web 服務器

確認診斷通過後，啟動服務器：

```cmd
python web_server_enhanced_v3.1.py
```

您應該看到類似以下的輸出：

```
✅ 基礎模組載入成功
✅ 增強版模組載入成功
✅ 基礎系統初始化成功
✅ 增強版系統初始化成功

╔════════════════════════════════════════════════════════════════╗
║          多市場智能選股系統 v4.0 Enhanced                    ║
║          Multi-Market Stock Picker Web Server                ║
╚════════════════════════════════════════════════════════════════╝

🌐 Web 介面: http://localhost:5000
```

**重要**：檢查是否有以下警告：
- ⚠️ 如果看到 "無法導入基礎模組"：需要安裝更多依賴
- ⚠️ 如果看到 "系統初始化失敗"：檢查依賴套件版本

---

### 步驟 4：測試 API 是否正常

**保持服務器運行**，打開新的命令提示符窗口，運行測試腳本：

```cmd
python test_api.py
```

這個腳本會測試：
1. ✅ 服務器健康檢查
2. ✅ 下載單支美股 (AAPL)
3. ✅ 下載單支台股 (2330)
4. ✅ 查看本地股票列表

**查看測試結果：**

#### 成功的輸出：

```
【測試 1】健康檢查
狀態碼: 200
✅ 服務器運行正常

【測試 2】下載單支美股 (AAPL)
狀態碼: 200
✅ 成功下載 AAPL
   數據詳情:
   - symbol: AAPL
   - market: US
   - rows: 5
   ...

【測試 3】下載單支台股 (2330)
狀態碼: 200
✅ 成功下載 2330
   數據詳情:
   - symbol: 2330
   - market: TW
   - rows: 5
   ...
```

#### 失敗的輸出及解決方案：

**1. 無法連接到服務器**
```
❌ 無法連接到服務器
請先運行: python web_server_enhanced_v3.1.py
```
**解決方案**：確保 Web 服務器正在運行

**2. 狀態碼 500**
```
狀態碼: 500
❌ 系統未初始化
```
**解決方案**：
- 檢查服務器啟動時是否有錯誤訊息
- 確認所有依賴套件已正確安裝
- 重新運行診斷腳本

**3. 狀態碼 404**
```
狀態碼: 404
❌ 找不到 API 端點
```
**解決方案**：
- 確認使用的是最新版本的 `web_server_enhanced_v3.1.py`
- 檢查 API 路由是否正確（應該有 `/api/download`）

**4. 下載失敗但狀態碼 200**
```
狀態碼: 200
❌ 無法下載 XXX 的數據
```
**解決方案**：
- 可能是網絡問題或 yfinance 服務暫時不可用
- 嘗試使用 VPN 或稍後再試
- 檢查防火牆設置

---

### 步驟 5：使用 Web 前端測試

如果 API 測試通過，在瀏覽器中打開：

```
http://localhost:5000
```

1. 點擊 "📥 下載數據" 標籤
2. 嘗試下載：
   - 美股：輸入 `AAPL` 或 `MSFT`
   - 台股：輸入 `2330` 或 `2317`
3. 查看結果

**如果仍然失敗**：
- 按 `F12` 打開瀏覽器開發者工具
- 查看 "Console" 標籤中的錯誤訊息
- 查看 "Network" 標籤中的請求詳情

---

## 常見錯誤及解決方案

### 錯誤 1: ModuleNotFoundError: No module named 'xxx'

**原因**：缺少 Python 套件

**解決方案**：
```cmd
pip install xxx
```

或安裝所有依賴：
```cmd
pip install -r requirements.txt
```

---

### 錯誤 2: 系統未初始化 (500 錯誤)

**原因**：`UnifiedStockDataManager` 初始化失敗

**可能的子原因**：
1. 缺少依賴套件（pandas、yfinance 等）
2. 某些核心模組導入失敗

**解決方案**：
1. 運行診斷腳本檢查
2. 重新安裝依賴：`pip install -r requirements.txt`
3. 檢查服務器啟動時的錯誤訊息

---

### 錯誤 3: 下載台股失敗，但美股成功

**原因**：
1. 台股代碼格式錯誤
2. 今天是非交易日（週末/假日）
3. yfinance 台股數據暫時不可用

**解決方案**：
1. 確認使用純數字代碼（如 `2330`，不要加 `.TW`）
2. 檢查今天是否為交易日
3. 嘗試使用 TWSE 官方 API（見 `usage_examples_twse.py`）

---

### 錯誤 4: CORS 錯誤

**瀏覽器 Console 顯示**：
```
Access to fetch at 'http://localhost:5000/api/...' has been blocked by CORS policy
```

**解決方案**：
確認 `web_server_enhanced_v3.1.py` 中有：
```python
from flask_cors import CORS
CORS(app)
```

如果沒有，需要安裝：
```cmd
pip install flask-cors
```

---

### 錯誤 5: 權限錯誤 (Permission Denied)

**原因**：無法創建數據目錄或寫入文件

**解決方案**：
1. 檢查當前目錄的寫入權限
2. 以管理員身份運行命令提示符
3. 或更改數據目錄位置

---

## 進階診斷

### 查看服務器詳細日誌

修改 `web_server_enhanced_v3.1.py` 最後一行：

```python
# 從這個：
app.run(debug=True, host='0.0.0.0', port=5000)

# 改為：
app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
```

這樣可以看到更詳細的錯誤訊息。

### 手動測試數據下載

在 Python 交互式環境中測試：

```python
from unified_stock_data_manager import UnifiedStockDataManager

manager = UnifiedStockDataManager(data_dir='./stock_data')

# 測試美股
df_us = manager.download_stock_data('AAPL', period='5d')
print(f"美股: {len(df_us) if df_us is not None else '失敗'}")

# 測試台股
df_tw = manager.download_stock_data('2330', period='5d')
print(f"台股: {len(df_tw) if df_tw is not None else '失敗'}")
```

---

## 需要更多幫助？

如果以上步驟都無法解決問題，請提供以下信息：

1. **Python 版本**：
   ```cmd
   python --version
   ```

2. **已安裝套件列表**：
   ```cmd
   pip list > packages.txt
   ```

3. **診斷腳本輸出**：
   ```cmd
   python diagnose_system.py > diagnosis.txt
   ```

4. **API 測試輸出**：
   ```cmd
   python test_api.py > api_test.txt
   ```

5. **服務器完整錯誤訊息**（從命令提示符複製）

6. **瀏覽器 Console 錯誤訊息**（F12 開發者工具）

有了這些信息，可以更準確地診斷和解決問題！
