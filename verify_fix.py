"""
快速驗證修復腳本
檢查關鍵文件是否可以正常導入
"""

print("="*80)
print("快速驗證修復")
print("="*80)

# 1. 測試導入 smart_stock_picker_v2_1
print("\n【1】測試 smart_stock_picker_v2_1 導入...")
try:
    from smart_stock_picker_v2_1 import StockAnalyzer, PricePredictor, SmartStockPicker
    print("✅ smart_stock_picker_v2_1 導入成功")
    print(f"   - StockAnalyzer: {StockAnalyzer}")
    print(f"   - PricePredictor: {PricePredictor}")
    print(f"   - SmartStockPicker: {SmartStockPicker}")
except Exception as e:
    print(f"❌ 導入失敗: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 2. 測試導入 smart_stock_picker_enhanced_v3
print("\n【2】測試 smart_stock_picker_enhanced_v3 導入...")
try:
    from smart_stock_picker_enhanced_v3 import EnhancedStockPicker
    print("✅ smart_stock_picker_enhanced_v3 導入成功")
    print(f"   - EnhancedStockPicker: {EnhancedStockPicker}")
except Exception as e:
    print(f"❌ 導入失敗: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 3. 測試初始化
print("\n【3】測試初始化 EnhancedStockPicker...")
try:
    picker = EnhancedStockPicker()
    print("✅ EnhancedStockPicker 初始化成功")
except Exception as e:
    print(f"❌ 初始化失敗: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 4. 測試 UnifiedStockDataManager
print("\n【4】測試 UnifiedStockDataManager...")
try:
    from unified_stock_data_manager import UnifiedStockDataManager
    manager = UnifiedStockDataManager(data_dir='./test_verify')
    print("✅ UnifiedStockDataManager 初始化成功")

    # 清理測試目錄
    import shutil, os
    if os.path.exists('./test_verify'):
        shutil.rmtree('./test_verify')
except Exception as e:
    print(f"❌ 初始化失敗: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 5. 測試 Web 服務器核心模組導入
print("\n【5】測試 Web 服務器核心模組...")
try:
    from flask import Flask
    from flask_cors import CORS
    print("✅ Flask 和 CORS 導入成功")
except Exception as e:
    print(f"❌ 導入失敗: {e}")
    exit(1)

print("\n" + "="*80)
print("✅ 所有驗證通過！系統已修復")
print("="*80)
print("\n現在可以啟動 Web 服務器：")
print("   python web_server_enhanced_v3.1.py")
print("\n然後在瀏覽器打開：")
print("   http://localhost:5000")
print("="*80)
