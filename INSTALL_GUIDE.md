# 🚀 安裝指南

## ❓ 系統未初始化錯誤的解決方案

如果您遇到 "系統未初始化" 錯誤（500 錯誤），請按照以下步驟操作：

---

## 📋 方案 1：在 Windows 命令提示符中運行

**推薦使用此方案**（因為您之前能看到 404 錯誤）

### 步驟 1：打開 Windows 命令提示符或 PowerShell

按 `Win + R`，輸入 `cmd` 或 `powershell`，按 Enter

### 步驟 2：切換到項目目錄

```cmd
cd C:\Users\rack\Desktop\台股預測系統
```

### 步驟 3：檢查 Python 是否安裝

```cmd
python --version
```

應該看到類似 `Python 3.x.x` 的輸出

### 步驟 4：安裝依賴套件（如果還沒安裝）

```cmd
pip install -r requirements.txt
```

或者手動安裝核心套件：

```cmd
pip install pandas numpy yfinance flask flask-cors scipy scikit-learn ta requests newsapi-python vaderSentiment
```

### 步驟 5：運行 Web 服務器

```cmd
python web_server_enhanced_v3.1.py
```

---

## 📋 方案 2：檢查 Python 環境

### 檢查已安裝的套件

```cmd
pip list
```

確認以下套件已安裝：
- ✅ pandas
- ✅ numpy
- ✅ flask
- ✅ flask-cors
- ✅ yfinance
- ✅ scipy
- ✅ scikit-learn

### 如果缺少套件

單獨安裝缺少的套件：

```cmd
pip install pandas
pip install flask flask-cors
pip install yfinance
```

---

## 📋 方案 3：使用虛擬環境（推薦）

### 創建虛擬環境

```cmd
cd C:\Users\rack\Desktop\台股預測系統
python -m venv venv
```

### 激活虛擬環境

**Windows 命令提示符：**
```cmd
venv\Scripts\activate
```

**Windows PowerShell：**
```powershell
venv\Scripts\Activate.ps1
```

如果 PowerShell 報錯，先執行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 安裝依賴

```cmd
pip install -r requirements.txt
```

### 運行服務器

```cmd
python web_server_enhanced_v3.1.py
```

---

## 🔧 常見問題

### Q1: 為什麼之前能運行，現在不行了？

**A:** 可能原因：
1. 您之前在不同的 Python 環境中運行
2. 某些依賴套件沒有正確安裝
3. Python 環境變量發生了變化

### Q2: pip 不是內部或外部命令

**A:** Python 沒有正確安裝或沒有加入環境變量。
- 重新安裝 Python，勾選 "Add Python to PATH"
- 或者使用完整路徑：`C:\Python3x\Scripts\pip.exe install ...`

### Q3: ModuleNotFoundError: No module named 'xxx'

**A:** 缺少某個 Python 套件，使用以下命令安裝：
```cmd
pip install xxx
```

### Q4: 在 WSL 中運行失敗

**A:** 建議在 **Windows 原生環境**中運行（不是 WSL），因為：
1. WSL 和 Windows 使用不同的 Python 環境
2. 文件路徑格式不同
3. 網絡配置可能不同

---

## ✅ 驗證安裝

安裝完成後，運行以下命令驗證：

```cmd
python -c "import pandas, flask, yfinance; print('✅ 所有核心依賴已安裝')"
```

如果看到 "✅ 所有核心依賴已安裝"，說明環境配置正確！

---

## 🚀 啟動服務器

環境配置完成後，運行：

```cmd
python web_server_enhanced_v3.1.py
```

應該看到：

```
╔════════════════════════════════════════════════════════════════╗
║          多市場智能選股系統 v4.0 Enhanced                    ║
║          Multi-Market Stock Picker Web Server                ║
╚════════════════════════════════════════════════════════════════╝

🌐 Web 介面: http://localhost:5000
```

然後在瀏覽器中打開 `http://localhost:5000`，即可使用系統！

---

## 📞 需要幫助？

如果仍然遇到問題，請提供以下信息：

1. Python 版本：`python --version`
2. 已安裝的套件：`pip list`
3. 錯誤訊息的完整輸出

這樣可以更準確地診斷問題！
