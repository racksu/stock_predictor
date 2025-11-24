"""
多市場智能選股系統 - Web 伺服器 v3.1 Enhanced
整合增強版台股波段預測功能

新功能：
✅ 支援美股 + 台股
✅ 整合增強版分析（KD+OBV+法人+籌碼）
✅ 雙版本分析（基礎版 + 增強版）
✅ 優化的錯誤處理
✅ 進度追蹤功能
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

# 添加路徑
current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)

# 導入核心模組
try:
    from unified_stock_data_manager import UnifiedStockDataManager
    from smart_stock_picker_v2_1 import SmartStockPicker
    CORE_MODULES_AVAILABLE = True
    print("✅ 基礎模組載入成功")
except ImportError as e:
    print(f"⚠️ 警告：無法導入基礎模組 - {e}")
    CORE_MODULES_AVAILABLE = False

# 導入增強版模組
try:
    from smart_stock_picker_enhanced_v3 import EnhancedStockPicker
    from usage_examples_enhanced import TaiwanStockDataFetcher
    ENHANCED_MODULES_AVAILABLE = True
    print("✅ 增強版模組載入成功")
except ImportError as e:
    print(f"⚠️ 警告：無法導入增強版模組 - {e}")
    ENHANCED_MODULES_AVAILABLE = False

# 導入回測模組
try:
    from backtesting_engine import BacktestingEngine
    BACKTEST_AVAILABLE = True
    print("✅ 回測模組載入成功")
except ImportError as e:
    print(f"⚠️ 警告：無法導入回測模組 - {e}")
    BACKTEST_AVAILABLE = False

# ====================================
# Flask 應用初始化
# ====================================

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 初始化系統
picker = None
enhanced_picker = None
manager = None
enhanced_fetcher = None

if CORE_MODULES_AVAILABLE:
    try:
        picker = SmartStockPicker()
        manager = UnifiedStockDataManager(data_dir='./stock_data')
        print("✅ 基礎系統初始化成功")
    except Exception as e:
        print(f"❌ 基礎系統初始化失敗：{e}")

if ENHANCED_MODULES_AVAILABLE:
    try:
        enhanced_picker = EnhancedStockPicker()
        enhanced_fetcher = TaiwanStockDataFetcher()
        print("✅ 增強版系統初始化成功")
    except Exception as e:
        print(f"❌ 增強版系統初始化失敗：{e}")

# ====================================
# 輔助函數
# ====================================

def convert_to_json_serializable(obj):
    """將 numpy/pandas 資料型態轉換為 JSON 可序列化的型態"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif pd.isna(obj):
        return None
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    else:
        return obj

def format_response(success: bool, message: str, data: Optional[Dict] = None) -> Dict:
    """格式化 API 回應"""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    if data:
        response['data'] = convert_to_json_serializable(data)
    return response

def _determine_action_smart(score: float, expected_return: float,
                           risk_reward_ratio: float, signal: str) -> str:
    """
    智能判斷操作建議（綜合方案）

    結合技術評分、預期報酬率和風險報酬比進行綜合判斷

    參數:
        score: 技術評分 (0-100)
        expected_return: 預期報酬率 (-1.0 to 1.0)
        risk_reward_ratio: 風險報酬比 (0+)
        signal: 技術信號（買入/賣出/持有）

    返回:
        action: 'BUY' / 'HOLD' / 'SELL'
    """

    # 1. 強力買入條件（三個條件都要滿足）
    if (score >= 70 and
        expected_return >= 0.08 and  # 預期報酬 >= 8%
        risk_reward_ratio >= 2.0):   # 風險報酬比 >= 2
        return 'BUY'

    # 2. 買入條件（三個條件中滿足兩個即可）
    buy_conditions = sum([
        score >= 60,
        expected_return >= 0.05,  # 預期報酬 >= 5%
        risk_reward_ratio >= 1.5
    ])

    if buy_conditions >= 2:
        return 'BUY'

    # 3. 賣出條件（任一條件滿足即可）
    if (score < 40 or
        expected_return < -0.05 or  # 預期虧損 >= 5%
        '強力賣出' in signal):
        return 'SELL'

    # 4. 謹慎持有（技術轉弱且預期為負）
    if score < 50 and expected_return < 0:
        return 'HOLD'

    # 5. 其他情況：持有
    return 'HOLD'

def _enhance_analysis_result(analysis: Dict, df: pd.DataFrame, symbol: str) -> Dict:
    """增強分析結果，添加前端需要的字段"""

    # 1. 添加公司名稱
    is_tw_stock = symbol.isdigit()
    if is_tw_stock:
        # 台股：嘗試獲取中文名稱
        try:
            from taiwan_stock_names import get_stock_name
            analysis['stock_name_chinese'] = get_stock_name(symbol)
            analysis['stock_name'] = get_stock_name(symbol)
        except:
            analysis['stock_name_chinese'] = symbol
            analysis['stock_name'] = symbol
        analysis['market'] = 'TW'
        analysis['market_display'] = '🇹🇼 台股'
    else:
        # 美股：使用代碼
        analysis['stock_name'] = symbol
        analysis['market'] = 'US'
        analysis['market_display'] = '🇺🇸 美股'

    # 2. 添加數據日期
    if 'date' in df.columns:
        latest_date = df['date'].iloc[-1]
        if isinstance(latest_date, pd.Timestamp):
            analysis['data_date'] = latest_date.strftime('%Y-%m-%d')
        else:
            analysis['data_date'] = str(latest_date)
    else:
        analysis['data_date'] = datetime.now().strftime('%Y-%m-%d')

    # 3. 計算目標達成時間
    if analysis.get('expected_return') and analysis.get('expected_return') != 0:
        # 基於歷史波動率估算時間
        returns = df['close'].pct_change().dropna()
        daily_return = returns.mean()
        if daily_return > 0:
            estimated_days = int(abs(analysis['expected_return']) / daily_return)
            estimated_days = max(7, min(estimated_days, 365))  # 限制在 7-365 天
        else:
            estimated_days = 30  # 默認30天

        estimated_date = (datetime.now() + timedelta(days=estimated_days)).strftime('%Y-%m-%d')

        analysis['target_timeframe'] = {
            'days': estimated_days,
            'estimated_date': estimated_date,
            'best_case_days': max(7, int(estimated_days * 0.7)),
            'likely_case_days': estimated_days,
            'worst_case_days': min(365, int(estimated_days * 1.5))
        }
    else:
        analysis['target_timeframe'] = {
            'days': 30,
            'estimated_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'best_case_days': 21,
            'likely_case_days': 30,
            'worst_case_days': 45
        }

    # 4. 計算成功機率（基於信心度和評分）
    confidence = analysis.get('confidence', 0.5)
    score = analysis.get('score', 50)
    probability = (confidence * 0.6 + (score / 100) * 0.4)
    analysis['probability'] = max(0.1, min(0.95, probability))

    # 5. 計算成交量數據
    if 'volume' in df.columns:
        latest_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].tail(20).mean()

        analysis['avg_volume'] = float(avg_volume)
        analysis['relative_volume'] = float(latest_volume / avg_volume) if avg_volume > 0 else 1.0

        # 流動性評級
        volume_score = 0
        if avg_volume > 10000000:  # 1000萬股以上
            volume_score = 5
        elif avg_volume > 5000000:
            volume_score = 4
        elif avg_volume > 1000000:
            volume_score = 3
        elif avg_volume > 500000:
            volume_score = 2
        else:
            volume_score = 1

        # 結合價格波動率
        volatility = df['close'].pct_change().std()
        if volatility < 0.02:
            liquidity_score = volume_score
        elif volatility < 0.03:
            liquidity_score = max(1, volume_score - 1)
        else:
            liquidity_score = max(1, volume_score - 2)

        liquidity_map = {5: '極高', 4: '高', 3: '中等', 2: '低', 1: '極低'}
        analysis['liquidity_rating'] = liquidity_map[liquidity_score]
    else:
        analysis['avg_volume'] = 0
        analysis['relative_volume'] = 1.0
        analysis['liquidity_rating'] = '未知'

    # 6. 生成分析摘要
    signal = analysis.get('signal', '持有')
    score = analysis.get('score', 50)
    expected_return = analysis.get('expected_return', 0)
    risk_level = analysis.get('risk_level', '中等風險')

    summary = f"根據技術分析，{symbol} 當前評分為 {score:.0f} 分，"
    if '買入' in signal:
        summary += f"呈現買入信號，預期報酬率約 {expected_return*100:+.2f}%。"
    elif '賣出' in signal:
        summary += f"呈現賣出信號，建議謹慎操作。"
    else:
        summary += f"建議持有觀望，等待更明確的信號。"

    summary += f" 風險等級為{risk_level}。"
    analysis['summary'] = summary

    # 7. 生成關鍵要點
    key_points = []

    # 技術指標要點
    tech = analysis.get('technical_indicators', {})
    ma5 = tech.get('MA5', 0)
    ma20 = tech.get('MA20', 0)
    rsi = tech.get('RSI', 50)

    if ma5 and ma20:
        if ma5 > ma20:
            key_points.append(f"✅ 短期均線(MA5: {ma5:.2f})在長期均線(MA20: {ma20:.2f})之上，趨勢向上")
        else:
            key_points.append(f"⚠️ 短期均線(MA5: {ma5:.2f})在長期均線(MA20: {ma20:.2f})之下，趨勢偏弱")

    if rsi:
        if rsi > 70:
            key_points.append(f"⚠️ RSI 指標 {rsi:.0f} 處於超買區，注意回調風險")
        elif rsi < 30:
            key_points.append(f"✅ RSI 指標 {rsi:.0f} 處於超賣區，可能出現反彈")
        else:
            key_points.append(f"✓ RSI 指標 {rsi:.0f} 處於正常區間")

    # 成交量要點
    if analysis.get('relative_volume', 0) > 1.5:
        key_points.append(f"📈 成交量放大 {analysis['relative_volume']:.1f} 倍，市場關注度提升")

    # 風險要點
    key_points.append(f"⚖️ 風險評估：{risk_level}")

    analysis['key_points'] = key_points

    # 8. 生成操作建議
    operation_suggestions = []

    if '強力買入' in signal:
        operation_suggestions.append(f"💰 建議分批建倉，目標價位 {analysis.get('target_price', 0):.2f}")
        operation_suggestions.append(f"🛡️ 建議止損價位 {analysis.get('support_price', 0):.2f}")
        operation_suggestions.append(f"⏰ 預計持有時間 {analysis['target_timeframe']['likely_case_days']} 天")
    elif '買入' in signal:
        operation_suggestions.append(f"💰 可考慮適量建倉，注意控制倉位")
        operation_suggestions.append(f"🛡️ 建議止損價位 {analysis.get('support_price', 0):.2f}")
    elif '賣出' in signal or '強力賣出' in signal:
        operation_suggestions.append(f"⚠️ 建議逐步減倉或觀望")
        operation_suggestions.append(f"📊 可等待價格回調至 {analysis.get('support_price', 0):.2f} 附近再考慮")
    else:
        operation_suggestions.append(f"👀 建議持有觀望，等待更明確的信號")
        operation_suggestions.append(f"📈 關注是否突破 {analysis.get('resistance_price', 0):.2f} 壓力位")

    analysis['operation_suggestions'] = operation_suggestions

    # 9. 生成風險提示
    risks = []

    if risk_level in ['高風險', '中高風險']:
        risks.append(f"⚠️ 該股票波動較大，屬於{risk_level}，請注意控制倉位")

    if analysis.get('liquidity_rating') in ['低', '極低']:
        risks.append(f"⚠️ 流動性評級為{analysis['liquidity_rating']}，可能存在買賣價差較大的風險")

    if expected_return < -0.05:
        risks.append(f"⚠️ 預期報酬率為負({expected_return*100:.2f}%)，下跌風險較高")

    risks.append(f"📊 本分析僅供參考，不構成投資建議，投資有風險，入市需謹慎")

    analysis['risks'] = risks

    # 10. 智能判斷操作建議（新邏輯：綜合判斷）
    action = _determine_action_smart(
        score=score,
        expected_return=expected_return,
        risk_reward_ratio=analysis.get('risk_reward_ratio', 0),
        signal=signal
    )
    analysis['action'] = action

    # 11. 根據評分和操作設定評級
    if score >= 80:
        analysis['rating'] = '優秀'
    elif score >= 70:
        analysis['rating'] = '良好'
    elif score >= 60:
        analysis['rating'] = '中上'
    elif score >= 50:
        analysis['rating'] = '中等'
    elif score >= 40:
        analysis['rating'] = '中下'
    else:
        analysis['rating'] = '偏弱'

    # 添加總分（與分數相同）
    analysis['total_score'] = score

    return analysis

# ====================================
# API 路由
# ====================================

@app.route('/')
def index():
    """首頁"""
    # 檢查 v5 版本是否存在
    if os.path.exists('stock_picker_web_v5_enhanced.html'):
        return send_file('stock_picker_web_v5_enhanced.html')
    else:
        return send_file('stock_picker_web_v4_enhanced.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查"""
    status = {
        'status': 'running',
        'version': 'v4.1',
        'core_modules': CORE_MODULES_AVAILABLE,
        'enhanced_modules': ENHANCED_MODULES_AVAILABLE,
        'backtest_module': BACKTEST_AVAILABLE,
        'features': {
            'basic_analysis': picker is not None,
            'enhanced_analysis': enhanced_picker is not None,
            'data_management': manager is not None,
            'backtesting': BACKTEST_AVAILABLE
        }
    }
    return jsonify(format_response(True, '系統運行正常', status))

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """基礎版股票分析（增強數據）"""
    try:
        if not picker or not manager:
            return jsonify(format_response(False, '系統未初始化')), 500

        data = request.json
        symbol = data.get('symbol', '').strip().upper()
        strategy = data.get('strategy', 'moderate')

        if not symbol:
            return jsonify(format_response(False, '請提供股票代碼')), 400

        print(f"\n📊 開始分析: {symbol} (基礎版)")

        # 下載數據
        df = manager.download_stock_data(symbol, period='2y')

        if df is None or len(df) < 200:
            return jsonify(format_response(False, f'無法獲取 {symbol} 的數據或數據不足')), 404

        # 執行分析
        analysis = picker.analyze_stock(symbol, df, strategy)

        if 'error' in analysis:
            return jsonify(format_response(False, analysis['error'])), 500

        # 增強分析結果，添加前端需要的字段
        analysis = _enhance_analysis_result(analysis, df, symbol)

        print(f"✅ 分析完成: {symbol}")
        return jsonify(format_response(True, '分析完成', analysis))

    except Exception as e:
        print(f"❌ 分析錯誤: {str(e)}")
        traceback.print_exc()
        return jsonify(format_response(False, f'分析失敗: {str(e)}')), 500

@app.route('/api/analyze_enhanced', methods=['POST'])
def analyze_stock_enhanced():
    """增強版股票分析（整合KD+OBV+法人+籌碼）"""
    try:
        if not enhanced_picker or not enhanced_fetcher:
            return jsonify(format_response(False, '增強版系統未初始化')), 500
        
        data = request.json
        symbol = data.get('symbol', '').strip().upper()
        use_finmind = data.get('use_finmind', False)  # 是否使用FinMind數據
        
        if not symbol:
            return jsonify(format_response(False, '請提供股票代碼')), 400
        
        print(f"\n📊 開始分析: {symbol} (增強版)")
        
        # 獲取價格數據
        price_data = enhanced_fetcher.get_price_data(symbol, start_date='2023-01-01')
        
        if price_data is None or len(price_data) < 200:
            return jsonify(format_response(False, f'無法獲取 {symbol} 的數據或數據不足')), 404
        
        # 獲取法人和籌碼數據（如果啟用）
        institutional_data = None
        margin_data = None
        
        if use_finmind:
            try:
                institutional_data = enhanced_fetcher.get_institutional_data(symbol, lookback_days=30)
                margin_data = enhanced_fetcher.get_margin_data(symbol, lookback_days=30)
                print(f"✅ 已獲取法人和籌碼數據")
            except Exception as e:
                print(f"⚠️ 無法獲取法人/籌碼數據: {e}")
        
        # 執行增強版分析
        analysis = enhanced_picker.analyze_stock_enhanced(
            symbol=symbol,
            price_data=price_data,
            institutional_data=institutional_data,
            margin_data=margin_data
        )
        
        if 'error' in analysis:
            return jsonify(format_response(False, analysis['error'])), 500
        
        print(f"✅ 增強版分析完成: {symbol}")
        return jsonify(format_response(True, '增強版分析完成', analysis))
        
    except Exception as e:
        print(f"❌ 增強版分析錯誤: {str(e)}")
        traceback.print_exc()
        return jsonify(format_response(False, f'增強版分析失敗: {str(e)}')), 500

@app.route('/api/screen', methods=['POST'])
def screen_stocks():
    """股票篩選"""
    try:
        if not picker or not manager:
            return jsonify(format_response(False, '系統未初始化')), 500

        data = request.json

        # 讀取所有篩選條件
        # 基本篩選
        market = data.get('market', 'all')
        min_score = data.get('min_score', 0)
        max_score = data.get('max_score', 100)
        action_filter = data.get('action_filter', 'all')

        # 價格與報酬
        min_price = data.get('min_price', 0)
        max_price = data.get('max_price', 9999)
        min_expected_return = data.get('min_expected_return', -1)
        max_expected_return = data.get('max_expected_return', 1)
        min_target_price = data.get('min_target_price', 0)
        max_target_price = data.get('max_target_price', 9999)

        # 風險與流動性
        min_risk_reward = data.get('min_risk_reward', 0)
        max_risk_reward = data.get('max_risk_reward', 10)
        min_relative_volume = data.get('min_relative_volume', 0)
        max_relative_volume = data.get('max_relative_volume', 10)
        liquidity_filter = data.get('liquidity_filter', 'all')

        # 時間與其他
        min_timeframe_days = data.get('min_timeframe_days', 0)
        max_timeframe_days = data.get('max_timeframe_days', 365)
        min_avg_volume = data.get('min_avg_volume', 0)
        max_avg_volume = data.get('max_avg_volume', 999999999)

        print(f"\n🔍 開始智能篩選")
        print(f"   市場: {market}")
        print(f"   評分範圍: {min_score}-{max_score}")
        print(f"   預期報酬範圍: {min_expected_return*100:.1f}%-{max_expected_return*100:.1f}%")
        print(f"   風險報酬比範圍: {min_risk_reward:.1f}-{max_risk_reward:.1f}")

        # 1. 獲取本地已下載的股票清單
        summary = manager.get_data_summary()

        if summary.empty:
            return jsonify(format_response(False, '本地無股票數據，請先下載股票數據')), 400

        # 2. 根據市場篩選
        if market == 'US':
            symbols = summary[summary['market'] == 'US']['symbol'].tolist()
        elif market == 'TW':
            symbols = summary[summary['market'] == 'TW']['symbol'].tolist()
        else:  # 'all'
            symbols = summary['symbol'].tolist()

        if not symbols:
            return jsonify(format_response(False, f'本地無{market}市場的股票數據')), 400

        print(f"   找到 {len(symbols)} 支本地股票")

        # 3. 載入股票數據
        stocks_data = {}
        for symbol in symbols:
            df = manager.load_stock_data(symbol)
            if df is not None and len(df) >= 200:
                stocks_data[symbol] = df

        print(f"   成功載入 {len(stocks_data)} 支股票數據")

        if not stocks_data:
            return jsonify(format_response(False, '沒有足夠的股票數據進行篩選')), 400

        # 4. 執行分析和篩選
        results = []
        analyzed_count = 0
        total = len(stocks_data)

        for i, (symbol, df) in enumerate(stocks_data.items(), 1):
            print(f"   [{i}/{total}] 分析 {symbol}...", end=" ")

            try:
                analysis = picker.analyze_stock(symbol, df, strategy='moderate')
                analyzed_count += 1

                if 'error' not in analysis:
                    # 增強分析結果（添加前端需要的字段）
                    analysis = _enhance_analysis_result(analysis, df, symbol)

                    # 提取所有需要檢查的字段
                    score = analysis.get('score', 0)
                    current_price = analysis.get('current_price', 0)
                    target_price = analysis.get('target_price', 0)
                    expected_return = analysis.get('expected_return', 0)
                    risk_reward_ratio = analysis.get('risk_reward_ratio', 0)
                    relative_volume = analysis.get('relative_volume', 0)
                    avg_volume = analysis.get('avg_volume', 0)
                    liquidity_rating = analysis.get('liquidity_rating', 'N/A')
                    action = analysis.get('action', 'HOLD')
                    timeframe_days = analysis.get('target_timeframe', {}).get('days', 30)

                    # 應用所有篩選條件（只應用前端發送的條件）
                    conditions_met = True
                    fail_reason = []

                    # 基本篩選
                    # 評分範圍（只在條件存在時檢查）
                    if 'min_score' in data or 'max_score' in data:
                        if not (min_score <= score <= max_score):
                            conditions_met = False
                            fail_reason.append(f"評分{score:.1f}不在範圍內")

                    # 操作建議（只在條件存在時檢查）
                    if 'action_filter' in data:
                        if action_filter != 'all' and action != action_filter:
                            conditions_met = False
                            fail_reason.append(f"操作建議{action}不符")

                    # 價格與報酬
                    # 現價範圍
                    if 'min_price' in data or 'max_price' in data:
                        if not (min_price <= current_price <= max_price):
                            conditions_met = False
                            fail_reason.append(f"現價{current_price:.2f}不在範圍內")

                    # 目標價範圍
                    if 'min_target_price' in data or 'max_target_price' in data:
                        if not (min_target_price <= target_price <= max_target_price):
                            conditions_met = False
                            fail_reason.append(f"目標價{target_price:.2f}不在範圍內")

                    # 預期報酬率
                    if 'min_expected_return' in data or 'max_expected_return' in data:
                        if not (min_expected_return <= expected_return <= max_expected_return):
                            conditions_met = False
                            fail_reason.append(f"預期報酬{expected_return*100:.1f}%不在範圍內")

                    # 風險與流動性
                    # 風險報酬比
                    if 'min_risk_reward' in data or 'max_risk_reward' in data:
                        if not (min_risk_reward <= risk_reward_ratio <= max_risk_reward):
                            conditions_met = False
                            fail_reason.append(f"風險報酬比{risk_reward_ratio:.2f}不在範圍內")

                    # 相對成交量
                    if 'min_relative_volume' in data or 'max_relative_volume' in data:
                        if not (min_relative_volume <= relative_volume <= max_relative_volume):
                            conditions_met = False
                            fail_reason.append(f"相對成交量{relative_volume:.2f}不在範圍內")

                    # 平均成交量
                    if 'min_avg_volume' in data or 'max_avg_volume' in data:
                        if not (min_avg_volume <= avg_volume <= max_avg_volume):
                            conditions_met = False
                            fail_reason.append(f"平均成交量不在範圍內")

                    # 流動性評級
                    if 'liquidity_filter' in data:
                        if liquidity_filter != 'all' and liquidity_rating != liquidity_filter:
                            conditions_met = False
                            fail_reason.append(f"流動性{liquidity_rating}不符")

                    # 時間
                    # 達成時間
                    if 'min_timeframe_days' in data or 'max_timeframe_days' in data:
                        if not (min_timeframe_days <= timeframe_days <= max_timeframe_days):
                            conditions_met = False
                            fail_reason.append(f"達成時間{timeframe_days}天不在範圍內")

                    # 如果符合所有條件，添加到結果
                    if conditions_met:
                        results.append({
                            'symbol': symbol,
                            'stock_name': analysis.get('stock_name', symbol),
                            'stock_name_chinese': analysis.get('stock_name_chinese', symbol),
                            'market': analysis.get('market', 'US' if not symbol.isdigit() else 'TW'),
                            'market_display': analysis.get('market_display', ''),
                            'score': score,
                            'total_score': score,
                            'signal': analysis.get('signal', ''),
                            'action': action,
                            'rating': analysis.get('rating', ''),
                            'current_price': current_price,
                            'target_price': target_price,
                            'support_price': analysis.get('support_price', 0),
                            'resistance_price': analysis.get('resistance_price', 0),
                            'expected_return': expected_return,
                            'risk_reward_ratio': risk_reward_ratio,
                            'avg_volume': avg_volume,
                            'relative_volume': relative_volume,
                            'liquidity_rating': liquidity_rating,
                            'trend_strength': analysis.get('trend_strength', 0),
                            'risk_level': analysis.get('risk_level', '未知'),
                            'data_date': analysis.get('data_date', 'N/A'),
                            'target_timeframe': analysis.get('target_timeframe', {}),
                            'timeframe_days': timeframe_days
                        })
                        print("✅ 符合")
                    else:
                        print(f"⚠️ 不符: {', '.join(fail_reason[:2])}")  # 只顯示前兩個原因
                else:
                    print("❌ 分析失敗")

            except Exception as e:
                print(f"❌ 錯誤: {e}")
                continue

        # 5. 按評分排序
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        print(f"\n✅ 篩選完成，找到 {len(results)} 支符合條件的股票（共分析 {analyzed_count} 支）")

        # 構建回應數據，包含前端需要的 total_matched 和 total_analyzed
        response_data = {
            'results': results,
            'total_matched': len(results),
            'total_analyzed': analyzed_count
        }

        if not results:
            return jsonify(format_response(True, '無符合條件的股票', response_data))

        return jsonify(format_response(True, f'找到 {len(results)} 支符合條件的股票', response_data))

    except Exception as e:
        print(f"❌ 篩選錯誤: {str(e)}")
        traceback.print_exc()
        return jsonify(format_response(False, f'篩選失敗: {str(e)}')), 500

@app.route('/api/get_symbols', methods=['GET'])
def get_symbols():
    """獲取可用的股票清單"""
    try:
        market = request.args.get('market', 'US')
        category = request.args.get('category', 'popular')
        
        if not manager:
            return jsonify(format_response(False, '系統未初始化')), 500
        
        symbols = manager.get_market_symbols(market, category)
        
        return jsonify(format_response(True, f'成功獲取 {len(symbols)} 支股票', {
            'market': market,
            'category': category,
            'symbols': symbols,
            'count': len(symbols)
        }))
        
    except Exception as e:
        print(f"❌ 獲取股票清單錯誤: {str(e)}")
        return jsonify(format_response(False, f'獲取失敗: {str(e)}')), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """獲取可用的分類"""
    try:
        market = request.args.get('market', 'TW')
        
        if market == 'TW':
            from taiwan_stock_database import get_all_categories
            categories = get_all_categories()
            
            return jsonify(format_response(True, '成功獲取分類', {
                'market': market,
                'categories': categories
            }))
        else:
            categories = {
                '指數': ['sp500', 'nasdaq100', 'dow'],
                '其他': ['popular', 'all']
            }
            return jsonify(format_response(True, '成功獲取分類', {
                'market': market,
                'categories': categories
            }))
        
    except Exception as e:
        print(f"❌ 獲取分類錯誤: {str(e)}")
        return jsonify(format_response(False, f'獲取失敗: {str(e)}')), 500

@app.route('/api/download', methods=['POST'])
def download_data():
    """下載股票數據"""
    try:
        if not manager:
            return jsonify(format_response(False, '系統未初始化')), 500

        data = request.json
        method = data.get('method', 'single')
        period = data.get('period', '2y')

        print(f"\n📥 開始下載數據 (方法: {method})")

        if method == 'single':
            # 下載單支股票
            symbol = data.get('symbol', '').strip().upper()
            if not symbol:
                return jsonify(format_response(False, '請提供股票代碼')), 400

            df = manager.download_stock_data(symbol, period=period)

            if df is None:
                return jsonify(format_response(False, f'無法下載 {symbol} 的數據')), 404

            result = {
                'symbol': symbol,
                'market': 'TW' if symbol.isdigit() else 'US',
                'rows': len(df),
                'start_date': df['date'].min().strftime('%Y-%m-%d'),
                'end_date': df['date'].max().strftime('%Y-%m-%d')
            }

            return jsonify(format_response(True, f'成功下載 {symbol}', result))

        elif method == 'multiple':
            # 下載多支股票
            symbols_str = data.get('symbols', '')
            symbols = [s.strip().upper() for s in symbols_str.split(',') if s.strip()]

            if not symbols:
                return jsonify(format_response(False, '請提供股票代碼')), 400

            success_count = 0
            failed_count = 0
            us_count = 0
            tw_count = 0

            for symbol in symbols:
                df = manager.download_stock_data(symbol, period=period)
                if df is not None:
                    success_count += 1
                    if symbol.isdigit():
                        tw_count += 1
                    else:
                        us_count += 1
                else:
                    failed_count += 1

            result = {
                'total': len(symbols),
                'success': success_count,
                'failed': failed_count,
                'us_stocks': us_count,
                'tw_stocks': tw_count
            }

            return jsonify(format_response(
                True,
                f'下載完成：成功 {success_count}/{len(symbols)}',
                result
            ))

        elif method == 'market_list':
            # 下載市場清單
            market = data.get('market', 'US')
            category = data.get('category', 'popular')

            # 獲取股票清單
            symbols = manager.get_market_symbols(market, category)

            if not symbols:
                return jsonify(format_response(False, f'無法獲取 {market}/{category} 的股票清單')), 404

            print(f"📊 準備下載 {len(symbols)} 支 {market} 股票...")

            success_count = 0
            failed_count = 0

            for i, symbol in enumerate(symbols, 1):
                print(f"  [{i}/{len(symbols)}] {symbol}...", end=" ")
                df = manager.download_stock_data(symbol, period=period)
                if df is not None:
                    success_count += 1
                    print("✅")
                else:
                    failed_count += 1
                    print("❌")

            result = {
                'market': market,
                'category': category,
                'total': len(symbols),
                'success': success_count,
                'failed': failed_count
            }

            return jsonify(format_response(
                True,
                f'批量下載完成：{success_count}/{len(symbols)} 成功',
                result
            ))

        else:
            return jsonify(format_response(False, f'未知的下載方法: {method}')), 400

    except Exception as e:
        print(f"❌ 下載錯誤: {str(e)}")
        traceback.print_exc()
        return jsonify(format_response(False, f'下載失敗: {str(e)}')), 500

@app.route('/api/local-stocks', methods=['GET'])
def get_local_stocks():
    """獲取本地已下載的股票列表"""
    try:
        if not manager:
            return jsonify(format_response(False, '系統未初始化')), 500

        summary = manager.get_data_summary()

        if summary.empty:
            return jsonify(format_response(True, '尚無本地股票數據', {
                'stocks': [],
                'total': 0,
                'us_count': 0,
                'tw_count': 0
            }))

        # 轉換為列表
        stocks = summary.to_dict('records')

        # 計算統計
        us_count = len(summary[summary['market'] == 'US'])
        tw_count = len(summary[summary['market'] == 'TW'])

        result = {
            'stocks': stocks,
            'total': len(stocks),
            'us_count': us_count,
            'tw_count': tw_count
        }

        return jsonify(format_response(True, f'找到 {len(stocks)} 支本地股票', result))

    except Exception as e:
        print(f"❌ 獲取本地股票錯誤: {str(e)}")
        traceback.print_exc()
        return jsonify(format_response(False, f'獲取失敗: {str(e)}')), 500

@app.route('/api/download_all_listed', methods=['POST'])
def download_all_listed():
    """下載台灣全部上市公司"""
    try:
        from taiwan_stock_database import download_all_listed_stocks_from_twse

        print("\n📥 開始下載台灣全部上市公司...")
        symbols = download_all_listed_stocks_from_twse()

        if symbols:
            return jsonify(format_response(True, f'成功下載 {len(symbols)} 支上市公司', {
                'symbols': symbols,
                'count': len(symbols)
            }))
        else:
            return jsonify(format_response(False, '下載失敗或無數據')), 500

    except Exception as e:
        print(f"❌ 下載錯誤: {str(e)}")
        traceback.print_exc()
        return jsonify(format_response(False, f'下載失敗: {str(e)}')), 500

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """執行回測"""
    try:
        if not BACKTEST_AVAILABLE or not manager:
            return jsonify(format_response(False, '回測系統未初始化')), 500

        data = request.json
        symbol = data.get('symbol', '').strip().upper()

        if not symbol:
            return jsonify(format_response(False, '請提供股票代碼')), 400

        # 回測參數
        initial_capital = data.get('initial_capital', 1000000)
        position_size = data.get('position_size', 0.3)
        stop_loss = data.get('stop_loss', -0.08)
        take_profit = data.get('take_profit', 0.15)
        rebalance_days = data.get('rebalance_days', 5)
        strategy = data.get('strategy', 'enhanced')

        print(f"\n📊 開始回測: {symbol}")
        print(f"   策略: {strategy}")
        print(f"   初始資金: ${initial_capital:,.0f}")
        print(f"   倉位: {position_size*100:.0f}%")

        # 載入數據
        df = manager.load_stock_data(symbol)
        if df is None or len(df) < 200:
            return jsonify(format_response(False, f'數據不足，需要至少200筆交易數據')), 400

        # 創建回測引擎
        engine = BacktestingEngine(
            initial_capital=initial_capital,
            commission_rate=0.001425,
            tax_rate=0.003,
            slippage=0.001
        )

        # 執行回測
        results = engine.run_backtest(
            df=df,
            strategy=strategy,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            rebalance_days=rebalance_days
        )

        # 格式化交易記錄
        trades_formatted = []
        for trade in results['trades']:
            trades_formatted.append({
                'entry_date': trade['entry_date'].strftime('%Y-%m-%d') if hasattr(trade['entry_date'], 'strftime') else str(trade['entry_date']),
                'exit_date': trade['exit_date'].strftime('%Y-%m-%d') if hasattr(trade['exit_date'], 'strftime') else str(trade['exit_date']),
                'entry_price': float(trade['entry_price']),
                'exit_price': float(trade['exit_price']),
                'shares': int(trade['shares']),
                'profit': float(trade['profit']),
                'profit_pct': float(trade['profit_pct']),
                'days_held': int(trade['days_held']),
                'exit_reason': trade['exit_reason']
            })

        # 格式化資金曲線
        equity_curve_formatted = []
        for eq in results['equity_curve'][-100:]:  # 只返回最後100個點
            equity_curve_formatted.append({
                'date': eq['date'].strftime('%Y-%m-%d') if hasattr(eq['date'], 'strftime') else str(eq['date']),
                'equity': float(eq['equity']),
                'capital': float(eq['capital']),
                'position_value': float(eq['position_value'])
            })

        # 構建回應
        response_data = {
            'symbol': symbol,
            'strategy': strategy,
            'parameters': {
                'initial_capital': initial_capital,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'rebalance_days': rebalance_days
            },
            'results': {
                'initial_capital': float(results['initial_capital']),
                'final_equity': float(results['final_equity']),
                'total_return': float(results['total_return']),
                'total_return_pct': float(results['total_return'] * 100)
            },
            'metrics': {
                'total_trades': results['metrics']['total_trades'],
                'winning_trades': results['metrics']['winning_trades'],
                'losing_trades': results['metrics']['losing_trades'],
                'win_rate': float(results['metrics']['win_rate']),
                'avg_profit': float(results['metrics']['avg_profit']),
                'avg_profit_pct': float(results['metrics']['avg_profit_pct']),
                'max_profit': float(results['metrics']['max_profit']),
                'max_loss': float(results['metrics']['max_loss']),
                'profit_factor': float(results['metrics']['profit_factor']),
                'sharpe_ratio': float(results['metrics']['sharpe_ratio']),
                'max_drawdown': float(results['metrics']['max_drawdown']),
                'avg_holding_days': float(results['metrics']['avg_holding_days'])
            },
            'trades': trades_formatted,
            'equity_curve': equity_curve_formatted,
            'data_period': {
                'start': df['date'].iloc[0].strftime('%Y-%m-%d'),
                'end': df['date'].iloc[-1].strftime('%Y-%m-%d'),
                'total_days': len(df)
            }
        }

        print(f"✅ 回測完成")
        print(f"   總報酬: {results['total_return']*100:+.2f}%")
        print(f"   交易次數: {results['metrics']['total_trades']}")
        print(f"   勝率: {results['metrics']['win_rate']*100:.1f}%")

        return jsonify(format_response(True, '回測完成', response_data))

    except Exception as e:
        print(f"❌ 回測錯誤: {str(e)}")
        traceback.print_exc()
        return jsonify(format_response(False, f'回測失敗: {str(e)}')), 500

@app.route('/api/backtest_compare', methods=['POST'])
def compare_parameters():
    """比較不同參數的回測結果"""
    try:
        if not BACKTEST_AVAILABLE or not manager:
            return jsonify(format_response(False, '回測系統未初始化')), 500

        data = request.json
        symbol = data.get('symbol', '').strip().upper()

        if not symbol:
            return jsonify(format_response(False, '請提供股票代碼')), 400

        # 載入數據
        df = manager.load_stock_data(symbol)
        if df is None or len(df) < 200:
            return jsonify(format_response(False, f'數據不足')), 400

        print(f"\n📊 開始參數比較回測: {symbol}")

        # 測試參數組合
        param_sets = data.get('param_sets', [
            {'position_size': 0.2, 'stop_loss': -0.05, 'take_profit': 0.10},
            {'position_size': 0.3, 'stop_loss': -0.08, 'take_profit': 0.15},
            {'position_size': 0.5, 'stop_loss': -0.10, 'take_profit': 0.20},
        ])

        results_comparison = []

        for idx, params in enumerate(param_sets):
            print(f"   測試參數組 {idx+1}/{len(param_sets)}: "
                  f"倉位{params['position_size']*100:.0f}%, "
                  f"停損{params['stop_loss']*100:.0f}%, "
                  f"停利{params['take_profit']*100:.0f}%")

            engine = BacktestingEngine(initial_capital=1000000)
            results = engine.run_backtest(
                df=df,
                strategy='enhanced',
                position_size=params['position_size'],
                stop_loss=params['stop_loss'],
                take_profit=params['take_profit']
            )

            results_comparison.append({
                'parameters': params,
                'total_return': float(results['total_return']),
                'win_rate': float(results['metrics']['win_rate']),
                'sharpe_ratio': float(results['metrics']['sharpe_ratio']),
                'max_drawdown': float(results['metrics']['max_drawdown']),
                'total_trades': results['metrics']['total_trades']
            })

        # 找出最佳參數
        best_result = max(results_comparison, key=lambda x: x['sharpe_ratio'])

        print(f"✅ 參數比較完成")
        print(f"   最佳Sharpe: {best_result['sharpe_ratio']:.2f}")

        return jsonify(format_response(True, '參數比較完成', {
            'symbol': symbol,
            'results': results_comparison,
            'best_parameters': best_result['parameters']
        }))

    except Exception as e:
        print(f"❌ 參數比較錯誤: {str(e)}")
        traceback.print_exc()
        return jsonify(format_response(False, f'參數比較失敗: {str(e)}')), 500

# ====================================
# 啟動服務器
# ====================================

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          多市場智能選股系統 v4.1 Enhanced                    ║
    ║          Multi-Market Stock Picker Web Server                ║
    ╚════════════════════════════════════════════════════════════════╝

    🌐 Web 介面: http://localhost:5000

    📡 API 端點：
    ✅ GET  /api/health              - 健康檢查
    ✅ POST /api/download            - 下載股票數據
    ✅ GET  /api/local-stocks        - 本地股票列表
    ✅ POST /api/analyze             - 基礎版分析
    ✅ POST /api/analyze_enhanced    - 增強版分析
    ✅ POST /api/screen              - 股票篩選
    ✅ GET  /api/get_symbols         - 獲取股票清單
    ✅ GET  /api/categories          - 獲取分類
    ✅ POST /api/download_all_listed - 下載全部上市公司
    ✅ POST /api/backtest            - 執行回測 (NEW!)
    ✅ POST /api/backtest_compare    - 參數比較回測 (NEW!)

    🎯 v4.1 新功能：
    • 📈 回測系統 - 驗證策略實際表現
    • 💰 交易成本計算 - 手續費、稅、滑價
    • 🎯 風險管理 - 停損停利機制
    • 📊 績效指標 - Sharpe比率、勝率、回撤
    • 🔧 參數優化 - 自動比較最佳參數
    • 總體經濟分析（VIX、美元、利率）
    • AI輿情分析（新聞情緒）
    • 成交量與流動性指標
    • TWSE官方API（無Token限制）
    """)

    # 檢查HTML文件是否存在
    html_file = 'stock_picker_web_v5_enhanced.html'
    if not os.path.exists(html_file):
        print(f"⚠️ 警告：找不到 {html_file}")
        print(f"   請確保該文件與此腳本在同一目錄")
        # 檢查是否有舊版本
        if os.path.exists('stock_picker_web_v4_enhanced.html'):
            print(f"   發現舊版本：stock_picker_web_v4_enhanced.html")
            print(f"   將使用舊版本（部分新功能可能不可用）")
            html_file = 'stock_picker_web_v4_enhanced.html'

    app.run(debug=True, host='0.0.0.0', port=5000)
