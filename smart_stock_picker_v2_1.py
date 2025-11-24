"""
智能選股系統 v2.1 (Smart Stock Picker)
基礎版股票分析引擎

功能:
1. 技術指標計算
2. 價格預測
3. 股票分析和評分
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class StockAnalyzer:
    """股票分析器 - 計算技術指標"""

    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        計算基礎技術指標

        參數:
            df: 包含 OHLCV 數據的 DataFrame

        返回:
            添加了技術指標的 DataFrame
        """
        df = df.copy()

        # 確保欄位名稱統一
        if 'Close' in df.columns and 'close' not in df.columns:
            df['close'] = df['Close']
        if 'High' in df.columns and 'high' not in df.columns:
            df['high'] = df['High']
        if 'Low' in df.columns and 'low' not in df.columns:
            df['low'] = df['Low']
        if 'Open' in df.columns and 'open' not in df.columns:
            df['open'] = df['Open']
        if 'Volume' in df.columns and 'volume' not in df.columns:
            df['volume'] = df['Volume']

        # 移動平均線
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()

        # 指數移動平均線
        df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()

        # MACD
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal']

        # RSI (14日)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))

        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(window=14).mean()

        # 布林通道
        df['BB_Middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

        # 成交量移動平均
        df['Volume_MA'] = df['volume'].rolling(window=20).mean()

        return df

    @staticmethod
    def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信號

        參數:
            df: 包含技術指標的 DataFrame

        返回:
            添加了信號的 DataFrame
        """
        df = df.copy()

        # 初始化信號
        df['signal'] = 0

        # 趨勢信號
        df.loc[df['MA5'] > df['MA20'], 'trend_signal'] = 1
        df.loc[df['MA5'] < df['MA20'], 'trend_signal'] = -1

        # MACD 信號
        df.loc[df['MACD'] > df['Signal'], 'macd_signal'] = 1
        df.loc[df['MACD'] < df['Signal'], 'macd_signal'] = -1

        # RSI 信號
        df.loc[df['RSI'] < 30, 'rsi_signal'] = 1  # 超賣
        df.loc[df['RSI'] > 70, 'rsi_signal'] = -1  # 超買

        # 綜合信號
        signal_cols = ['trend_signal', 'macd_signal', 'rsi_signal']
        df['signal'] = df[signal_cols].fillna(0).mean(axis=1)

        return df


class PricePredictor:
    """價格預測器"""

    @staticmethod
    def predict_price(df: pd.DataFrame, days_ahead: int = 30) -> Dict:
        """
        預測未來價格

        參數:
            df: 歷史數據 DataFrame
            days_ahead: 預測天數

        返回:
            預測結果字典
        """
        if len(df) < 60:
            return {
                'error': '數據不足，無法預測',
                'target_price': None,
                'expected_return': None
            }

        # 使用簡單的線性回歸預測
        recent_data = df.tail(60).copy()
        recent_data['day_num'] = range(len(recent_data))

        # 計算趨勢
        x = recent_data['day_num'].values
        y = recent_data['close'].values

        # 線性回歸係數
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        intercept = coeffs[1]

        # 預測未來價格
        future_day = len(recent_data) + days_ahead
        target_price = slope * future_day + intercept

        # 當前價格
        current_price = df['close'].iloc[-1]

        # 預期報酬率
        expected_return = (target_price - current_price) / current_price

        # 波動性調整
        volatility = df['close'].pct_change().std()
        confidence = max(0, 1 - (volatility * 10))  # 波動越大，信心越低

        return {
            'target_price': float(target_price),
            'current_price': float(current_price),
            'expected_return': float(expected_return),
            'confidence': float(confidence),
            'trend_slope': float(slope),
            'volatility': float(volatility)
        }


class SmartStockPicker:
    """智能選股器 - 主要分析引擎"""

    def __init__(self):
        """初始化選股器"""
        self.analyzer = StockAnalyzer()
        self.predictor = PricePredictor()

    def analyze_stock(self, symbol: str, df: pd.DataFrame,
                     strategy: str = 'moderate') -> Dict:
        """
        分析單支股票

        參數:
            symbol: 股票代碼
            df: 股票數據 DataFrame
            strategy: 策略類型 ('aggressive', 'moderate', 'conservative')

        返回:
            分析結果字典
        """
        try:
            # 數據驗證
            if df is None or len(df) < 200:
                return {'error': '數據不足，需要至少 200 筆歷史數據'}

            # 計算技術指標
            df = self.analyzer.calculate_indicators(df)
            df = self.analyzer.generate_signals(df)

            # 獲取最新數據
            latest = df.iloc[-1]

            # 價格預測
            prediction = self.predictor.predict_price(df, days_ahead=30)

            # 技術分析評分
            tech_score = self._calculate_technical_score(df, latest)

            # 趨勢強度
            trend_strength = self._calculate_trend_strength(df)

            # 生成信號
            signal, confidence = self._generate_signal(
                tech_score, trend_strength, prediction, strategy
            )

            # 計算支撐和壓力位
            support, resistance = self._calculate_support_resistance(df)

            # 風險評估
            risk_level, risk_score = self._assess_risk(df, latest)

            # 計算風險報酬比
            expected_return = prediction.get('expected_return', 0)
            if risk_score > 0 and expected_return > 0:
                risk_reward_ratio = (expected_return * 100) / risk_score
            else:
                risk_reward_ratio = 0

            # 整合結果
            analysis = {
                'symbol': symbol,
                'current_price': float(latest['close']),
                'signal': signal,
                'confidence': float(confidence),
                'score': float(tech_score),
                'trend_strength': float(trend_strength),
                'target_price': prediction.get('target_price'),
                'expected_return': prediction.get('expected_return'),
                'support_price': float(support),
                'resistance_price': float(resistance),
                'risk_level': risk_level,
                'risk_score': float(risk_score),
                'risk_reward_ratio': float(risk_reward_ratio),
                'technical_indicators': {
                    'MA5': float(latest['MA5']),
                    'MA20': float(latest['MA20']),
                    'MA60': float(latest['MA60']),
                    'RSI': float(latest['RSI']),
                    'MACD': float(latest['MACD']),
                    'Volume': float(latest['volume']),
                    'Volume_MA': float(latest['Volume_MA'])
                },
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'strategy': strategy
            }

            return analysis

        except Exception as e:
            return {'error': f'分析失敗: {str(e)}'}

    def _calculate_technical_score(self, df: pd.DataFrame,
                                   latest: pd.Series) -> float:
        """計算技術分析評分 (0-100)"""
        score = 0

        # 趨勢分數 (0-30)
        if latest['MA5'] > latest['MA20'] > latest['MA60']:
            score += 30
        elif latest['MA5'] > latest['MA20']:
            score += 20
        elif latest['MA5'] > latest['MA60']:
            score += 10

        # MACD 分數 (0-20)
        if latest['MACD'] > latest['Signal'] and latest['MACD'] > 0:
            score += 20
        elif latest['MACD'] > latest['Signal']:
            score += 10

        # RSI 分數 (0-20)
        rsi = latest['RSI']
        if 40 <= rsi <= 60:
            score += 20
        elif 30 <= rsi <= 70:
            score += 15
        elif rsi < 30:
            score += 10  # 超賣，有反彈機會

        # 成交量分數 (0-15)
        if latest['volume'] > latest['Volume_MA'] * 1.5:
            score += 15
        elif latest['volume'] > latest['Volume_MA']:
            score += 10

        # 布林通道分數 (0-15)
        if 'BB_Lower' in latest and 'BB_Upper' in latest:
            bb_position = (latest['close'] - latest['BB_Lower']) / \
                         (latest['BB_Upper'] - latest['BB_Lower'] + 1e-10)
            if 0.3 <= bb_position <= 0.7:
                score += 15
            elif 0.2 <= bb_position <= 0.8:
                score += 10

        return min(100, max(0, score))

    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """計算趨勢強度 (-1 到 1)"""
        recent = df.tail(20)

        # 價格趨勢
        price_trend = (recent['close'].iloc[-1] - recent['close'].iloc[0]) / \
                     (recent['close'].iloc[0] + 1e-10)

        # MA 排列
        latest = df.iloc[-1]
        ma_alignment = 0
        if latest['MA5'] > latest['MA20'] > latest['MA60']:
            ma_alignment = 1
        elif latest['MA5'] < latest['MA20'] < latest['MA60']:
            ma_alignment = -1

        # 綜合趨勢強度
        trend = (price_trend * 0.6 + ma_alignment * 0.4)
        return max(-1, min(1, trend))

    def _generate_signal(self, tech_score: float, trend_strength: float,
                        prediction: Dict, strategy: str) -> Tuple[str, float]:
        """生成交易信號"""
        # 策略閾值
        thresholds = {
            'aggressive': {'buy': 60, 'sell': 40},
            'moderate': {'buy': 70, 'sell': 30},
            'conservative': {'buy': 80, 'sell': 20}
        }

        threshold = thresholds.get(strategy, thresholds['moderate'])

        # 綜合評分
        combined_score = tech_score * 0.7 + (trend_strength + 1) * 50 * 0.3

        # 生成信號
        if combined_score >= threshold['buy']:
            if trend_strength > 0.3:
                return '強力買入', 0.9
            else:
                return '買入', 0.7
        elif combined_score <= threshold['sell']:
            if trend_strength < -0.3:
                return '強力賣出', 0.9
            else:
                return '賣出', 0.7
        else:
            return '持有', 0.5

    def _calculate_support_resistance(self, df: pd.DataFrame) -> Tuple[float, float]:
        """計算支撐位和壓力位"""
        recent = df.tail(60)

        # 支撐位：最近60天的最低點
        support = recent['low'].min()

        # 壓力位：最近60天的最高點
        resistance = recent['high'].max()

        return support, resistance

    def _assess_risk(self, df: pd.DataFrame,
                    latest: pd.Series) -> Tuple[str, float]:
        """評估風險等級"""
        # 波動率
        returns = df['close'].pct_change()
        volatility = returns.std()

        # ATR 相對值
        atr_pct = latest['ATR'] / latest['close']

        # 綜合風險評分 (0-100)
        risk_score = (volatility * 100 * 0.6 + atr_pct * 100 * 0.4)

        # 風險等級
        if risk_score < 20:
            risk_level = '低風險'
        elif risk_score < 40:
            risk_level = '中低風險'
        elif risk_score < 60:
            risk_level = '中等風險'
        elif risk_score < 80:
            risk_level = '中高風險'
        else:
            risk_level = '高風險'

        return risk_level, risk_score

    def screen_stocks(self, stocks_data: Dict[str, pd.DataFrame],
                     filters: Dict = None) -> pd.DataFrame:
        """
        批量篩選股票

        參數:
            stocks_data: {symbol: DataFrame} 字典
            filters: 篩選條件

        返回:
            篩選結果 DataFrame
        """
        results = []

        for symbol, df in stocks_data.items():
            analysis = self.analyze_stock(symbol, df)

            if 'error' not in analysis:
                results.append({
                    'symbol': symbol,
                    'score': analysis['score'],
                    'signal': analysis['signal'],
                    'current_price': analysis['current_price'],
                    'target_price': analysis['target_price'],
                    'expected_return': analysis['expected_return'],
                    'trend_strength': analysis['trend_strength'],
                    'risk_level': analysis['risk_level']
                })

        df_results = pd.DataFrame(results)

        # 應用篩選條件
        if filters and not df_results.empty:
            if 'min_score' in filters:
                df_results = df_results[df_results['score'] >= filters['min_score']]
            if 'min_return' in filters:
                df_results = df_results[df_results['expected_return'] >= filters['min_return']]
            if 'signal' in filters:
                df_results = df_results[df_results['signal'].isin(filters['signal'])]

        return df_results.sort_values('score', ascending=False)


# ========== 測試代碼 ==========

if __name__ == "__main__":
    print("="*80)
    print("智能選股系統 v2.1 - 測試")
    print("="*80)

    print("\n✅ 所有類已成功定義:")
    print("  - StockAnalyzer")
    print("  - PricePredictor")
    print("  - SmartStockPicker")

    print("\n這是基礎版分析引擎，可以被增強版繼承和擴展。")
    print("="*80)
