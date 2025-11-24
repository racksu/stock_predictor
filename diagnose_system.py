"""
系統診斷工具
檢查所有依賴和配置是否正確
"""

import sys
import os

print("=" * 80)
print("台股預測系統 - 系統診斷工具")
print("=" * 80)

# 1. 檢查 Python 版本
print("\n【1. Python 版本】")
print(f"Python 版本: {sys.version}")
print(f"Python 路徑: {sys.executable}")

# 2. 檢查必要的套件
print("\n【2. 檢查必要套件】")
required_packages = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'flask': 'flask',
    'flask_cors': 'flask-cors',
    'yfinance': 'yfinance',
    'scipy': 'scipy',
    'sklearn': 'scikit-learn',
    'requests': 'requests'
}

missing_packages = []
installed_packages = {}

for module_name, package_name in required_packages.items():
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        installed_packages[package_name] = version
        print(f"✅ {package_name:20} {version}")
    except ImportError:
        missing_packages.append(package_name)
        print(f"❌ {package_name:20} 未安裝")

# 3. 檢查可選套件
print("\n【3. 檢查可選套件（v4.0 新功能）】")
optional_packages = {
    'newsapi': 'newsapi-python',
    'vaderSentiment': 'vaderSentiment',
    'ta': 'ta'
}

for module_name, package_name in optional_packages.items():
    try:
        __import__(module_name)
        print(f"✅ {package_name:20} 已安裝")
    except ImportError:
        print(f"⚠️ {package_name:20} 未安裝（可選，部分功能可能不可用）")

# 4. 檢查核心模組
print("\n【4. 檢查核心模組】")
core_modules = [
    'stock_data_source_abc',
    'stock_data_source_us',
    'stock_data_source_tw',
    'unified_stock_data_manager',
    'smart_stock_picker_v2_1',
    'smart_stock_picker_enhanced_v3'
]

for module_name in core_modules:
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
    except ImportError as e:
        print(f"❌ {module_name} - {str(e)}")

# 5. 檢查 HTML 文件
print("\n【5. 檢查前端 HTML 文件】")
html_files = [
    'stock_picker_web_v5_enhanced.html',
    'stock_picker_web_v4_enhanced.html'
]

for html_file in html_files:
    if os.path.exists(html_file):
        size = os.path.getsize(html_file) / 1024
        print(f"✅ {html_file} ({size:.1f} KB)")
    else:
        print(f"❌ {html_file} 不存在")

# 6. 檢查數據目錄
print("\n【6. 檢查數據目錄】")
data_dirs = ['./stock_data', './stock_data/daily', './stock_data/metadata']
for data_dir in data_dirs:
    if os.path.exists(data_dir):
        print(f"✅ {data_dir} 存在")
    else:
        print(f"⚠️ {data_dir} 不存在（將在首次運行時創建）")

# 7. 測試數據下載功能
print("\n【7. 測試數據下載功能】")
if not missing_packages:
    try:
        from unified_stock_data_manager import UnifiedStockDataManager

        print("正在初始化 UnifiedStockDataManager...")
        manager = UnifiedStockDataManager(data_dir='./stock_data_test')
        print("✅ UnifiedStockDataManager 初始化成功")

        print("\n測試下載美股數據（AAPL）...")
        df_us = manager.download_stock_data('AAPL', period='5d')
        if df_us is not None and len(df_us) >= 3:
            print(f"✅ 美股下載成功：{len(df_us)} 筆數據")
        else:
            print(f"❌ 美股下載失敗（獲取到 {len(df_us) if df_us is not None else 0} 筆數據）")

        print("\n測試下載台股數據（2330）...")
        df_tw = manager.download_stock_data('2330', period='5d')
        if df_tw is not None and len(df_tw) >= 3:
            print(f"✅ 台股下載成功：{len(df_tw)} 筆數據")
        else:
            print(f"❌ 台股下載失敗（獲取到 {len(df_tw) if df_tw is not None else 0} 筆數據，可能是非交易日）")

        # 清理測試目錄
        import shutil
        if os.path.exists('./stock_data_test'):
            shutil.rmtree('./stock_data_test')
            print("\n已清理測試數據")

    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️ 跳過測試（缺少必要套件）")

# 總結
print("\n" + "=" * 80)
print("診斷總結")
print("=" * 80)

if missing_packages:
    print(f"\n❌ 缺少 {len(missing_packages)} 個必要套件:")
    for pkg in missing_packages:
        print(f"   - {pkg}")
    print(f"\n請執行以下命令安裝:")
    print(f"   pip install {' '.join(missing_packages)}")
else:
    print("\n✅ 所有必要套件已安裝")

print("\n如果所有檢查都通過，您可以運行:")
print("   python web_server_enhanced_v3.1.py")
print("\n然後在瀏覽器打開: http://localhost:5000")

print("\n" + "=" * 80)
