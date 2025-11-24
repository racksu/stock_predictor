"""
增强版智能选股系统 (Enhanced Smart Stock Picker)
整合台股波段预测多因子框架

新增功能：
1. 台股优化技术指标 - KD(9,3,3) + OBV + 10日MA
2. 市场面分析 - 三大法人买卖超
3. 筹码面分析 - 融资融券、主力进出
4. 总体经济分析 - VIX、美元、利率等宏观指标 (NEW!)
5. 多因子整合 - 技术35% + 市场25% + 筹码25% + 总经15%

基于学术研究：
- KD+OBV组合策略成功率79% (Springer 2018)
- 投信买卖超表现最优 (豹投资统计)
- 融资使用率作为散户情绪指标
- 总体经济环境对股市影响显著 (学术共识)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 导入原有的基础类
from smart_stock_picker_v2_1 import StockAnalyzer as BaseStockAnalyzer
from smart_stock_picker_v2_1 import PricePredictor, SmartStockPicker

# 导入总体经济分析器
try:
    from macro_economic_analyzer import MacroEconomicAnalyzer
    MACRO_AVAILABLE = True
except ImportError:
    MACRO_AVAILABLE = False
    print("⚠️ 总体经济分析模块未找到，将跳过宏观分析")


class EnhancedStockAnalyzer(BaseStockAnalyzer):
    """增强版股票分析器 - 增加台股优化指标"""
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标（包含台股优化版）"""
        # 先调用基础指标计算
        df = BaseStockAnalyzer.calculate_indicators(df)
        
        # === 新增：台股优化指标 ===
        
        # 1. KD指标 (9,3,3) - 台股最有效
        df = EnhancedStockAnalyzer._calculate_kd(df, n=9, m1=3, m2=3)
        
        # 2. OBV (On-Balance Volume) - 必配指标
        df = EnhancedStockAnalyzer._calculate_obv(df)
        
        # 3. 10日MA - 台股最优
        df['MA10'] = df['close'].rolling(window=10).mean()
        
        # 4. 布林通道 - 用于辅助判断
        df = EnhancedStockAnalyzer._calculate_bollinger_bands(df)
        
        # 5. 主力进出指标 (基于OBV优化)
        df = EnhancedStockAnalyzer._calculate_main_force_indicator(df)
        
        return df
    
    @staticmethod
    def _calculate_kd(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """
        计算KD指标
        
        参数:
            n: RSV周期 (台股优化值: 9)
            m1: K值平滑周期 (台股优化值: 3)
            m2: D值平滑周期 (台股优化值: 3)
        """
        # 计算RSV (Raw Stochastic Value)
        low_n = df['low'].rolling(window=n).min()
        high_n = df['high'].rolling(window=n).max()
        
        df['RSV'] = 100 * (df['close'] - low_n) / (high_n - low_n + 1e-10)
        
        # 计算K值 (使用EMA平滑)
        df['K'] = df['RSV'].ewm(span=m1, adjust=False).mean()
        
        # 计算D值
        df['D'] = df['K'].ewm(span=m2, adjust=False).mean()
        
        # 计算J值 (可选，用于极值判断)
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        return df
    
    @staticmethod
    def _calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算OBV (On-Balance Volume)
        
        OBV是台股预测中唯一能普遍提升所有策略表现的指标
        """
        obv = [0]
        
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        
        df['OBV'] = obv
        
        # OBV趋势 (5日、10日)
        df['OBV_MA5'] = df['OBV'].rolling(window=5).mean()
        df['OBV_MA10'] = df['OBV'].rolling(window=10).mean()
        
        return df
    
    @staticmethod
    def _calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """计算布林通道"""
        df['BB_Middle'] = df['close'].rolling(window=period).mean()
        rolling_std = df['close'].rolling(window=period).std()
        df['BB_Upper'] = df['BB_Middle'] + (rolling_std * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (rolling_std * std_dev)
        
        # 计算%B指标 (价格在通道中的位置)
        df['BB_percent'] = (df['close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'] + 1e-10)
        
        return df
    
    @staticmethod
    def _calculate_main_force_indicator(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算主力进出指标 (ZLJC)
        基于OBV优化改造
        """
        # 短期线 (5日)
        df['MFI_Short'] = df['OBV'].ewm(span=5, adjust=False).mean()
        
        # 中期线 (10日)
        df['MFI_Medium'] = df['OBV'].ewm(span=10, adjust=False).mean()
        
        # 长期线 (20日)
        df['MFI_Long'] = df['OBV'].ewm(span=20, adjust=False).mean()
        
        return df
    
    @staticmethod
    def calculate_taiwan_optimized_score(df: pd.DataFrame, index: int) -> Dict:
        """
        计算台股优化评分
        
        权重分配：
        - 技术面: 40%
          - KD指标: 15%
          - OBV: 10%
          - MA10: 10%
          - RSI: 2.5%
          - MACD: 2.5%
        
        返回技术面评分（满分40分）
        """
        row = df.iloc[index]
        
        scores = {
            'kd_score': 0,        # KD指标分数 (0-15)
            'obv_score': 0,       # OBV分数 (0-10)
            'ma_score': 0,        # MA分数 (0-10)
            'rsi_score': 0,       # RSI分数 (0-2.5)
            'macd_score': 0,      # MACD分数 (0-2.5)
            'technical_total': 0  # 技术面总分 (0-40)
        }
        
        # 1. KD指标评分 (15分) - 权重最高
        if pd.notna(row['K']) and pd.notna(row['D']):
            k_value = row['K']
            d_value = row['D']
            
            # 金叉买入信号
            if index > 0:
                k_prev = df.iloc[index-1]['K']
                d_prev = df.iloc[index-1]['D']
                
                # 低档金叉 (K<20 且 K上穿D)
                if k_value < 20 and k_value > d_value and k_prev <= d_prev:
                    scores['kd_score'] += 15  # 最强买入信号
                # 一般金叉 (K<50 且 K上穿D)
                elif k_value < 50 and k_value > d_value and k_prev <= d_prev:
                    scores['kd_score'] += 12
                # 高档死叉 (K>80 且 K下穿D)
                elif k_value > 80 and k_value < d_value and k_prev >= d_prev:
                    scores['kd_score'] -= 10  # 卖出信号
                # 一般死叉
                elif k_value > 50 and k_value < d_value and k_prev >= d_prev:
                    scores['kd_score'] -= 5
                # K>D 且未超买
                elif k_value > d_value and k_value < 70:
                    scores['kd_score'] += 8
                # K<D
                elif k_value < d_value:
                    scores['kd_score'] += 2
            
            # 超买超卖修正
            if k_value > 80:
                scores['kd_score'] -= 3  # 超买警示
            elif k_value < 20:
                scores['kd_score'] += 3  # 超卖反弹机会
        
        # 2. OBV评分 (10分) - 资金流向确认
        if pd.notna(row['OBV']) and pd.notna(row['OBV_MA5']) and pd.notna(row['OBV_MA10']):
            # OBV上升趋势
            if row['OBV'] > row['OBV_MA5'] > row['OBV_MA10']:
                scores['obv_score'] += 10  # 强势资金流入
            elif row['OBV'] > row['OBV_MA5']:
                scores['obv_score'] += 6   # 短期资金流入
            elif row['OBV'] < row['OBV_MA5'] < row['OBV_MA10']:
                scores['obv_score'] -= 5   # 资金流出
            
            # 价量背离检查
            if index > 5:
                price_trend = (df['close'].iloc[index] - df['close'].iloc[index-5]) / df['close'].iloc[index-5]
                obv_trend = (df['OBV'].iloc[index] - df['OBV'].iloc[index-5]) / (abs(df['OBV'].iloc[index-5]) + 1)
                
                # 价涨量缩 (负面信号)
                if price_trend > 0.02 and obv_trend < 0:
                    scores['obv_score'] -= 3
                # 价跌量增 (可能筑底)
                elif price_trend < -0.02 and obv_trend > 0:
                    scores['obv_score'] += 2
        
        # 3. MA评分 (10分) - 10日MA为主
        if pd.notna(row['MA10']) and pd.notna(row['MA20']) and pd.notna(row['MA60']):
            # 多头排列
            if row['close'] > row['MA10'] > row['MA20'] > row['MA60']:
                scores['ma_score'] += 10
            elif row['close'] > row['MA10'] > row['MA20']:
                scores['ma_score'] += 7
            elif row['close'] > row['MA10']:
                scores['ma_score'] += 4
            # 空头排列
            elif row['close'] < row['MA10'] < row['MA20'] < row['MA60']:
                scores['ma_score'] -= 5
            elif row['close'] < row['MA10']:
                scores['ma_score'] -= 2
            
            # 距离10日MA的位置
            distance_from_ma10 = (row['close'] - row['MA10']) / row['MA10']
            if -0.03 < distance_from_ma10 < 0.03:
                scores['ma_score'] += 2  # 靠近MA，支撑/压力明确
        
        # 4. RSI评分 (2.5分) - 仅辅助
        if pd.notna(row['RSI']):
            if 40 < row['RSI'] < 60:
                scores['rsi_score'] += 2.5  # 健康区间
            elif 30 < row['RSI'] < 40:
                scores['rsi_score'] += 1.5  # 接近超卖
            elif row['RSI'] <= 30:
                scores['rsi_score'] += 1.0  # 超卖，可能反弹
            elif 60 < row['RSI'] < 70:
                scores['rsi_score'] += 1.0  # 强势
            elif row['RSI'] >= 70:
                scores['rsi_score'] -= 1.0  # 超买警示
        
        # 5. MACD评分 (2.5分) - 仅辅助
        if pd.notna(row['MACD']) and pd.notna(row['MACD_signal']):
            if row['MACD'] > row['MACD_signal'] and row['MACD'] > 0:
                scores['macd_score'] += 2.5
            elif row['MACD'] > row['MACD_signal']:
                scores['macd_score'] += 1.5
            elif row['MACD'] < row['MACD_signal']:
                scores['macd_score'] -= 1.0
        
        # 计算技术面总分
        scores['technical_total'] = (
            scores['kd_score'] + 
            scores['obv_score'] + 
            scores['ma_score'] + 
            scores['rsi_score'] + 
            scores['macd_score']
        )
        
        return scores


class MarketAnalyzer:
    """
    市场面分析器
    分析三大法人（外资、投信、自营商）买卖超
    
    数据来源: FinMind API - taiwan_stock_institutional_investors
    """
    
    @staticmethod
    def calculate_institutional_score(institutional_data: pd.DataFrame, 
                                     lookback_days: int = 10) -> Dict:
        """
        计算法人面评分
        
        权重分配：
        - 外资买卖超: 10%
        - 投信买卖超: 12% (表现最优)
        - 自营商买卖超: 5%
        - 三大法人共识: 3%
        
        返回市场面评分（满分30分）
        """
        scores = {
            'foreign_score': 0,      # 外资分数 (0-10)
            'trust_score': 0,        # 投信分数 (0-12)
            'dealer_score': 0,       # 自营商分数 (0-5)
            'consensus_score': 0,    # 共识分数 (0-3)
            'market_total': 0        # 市场面总分 (0-30)
        }
        
        if institutional_data is None or len(institutional_data) < lookback_days:
            return scores
        
        recent_data = institutional_data.tail(lookback_days)
        
        # 1. 外资分析 (10分)
        foreign_net = recent_data['foreign_net'].sum()  # 累计净买超
        foreign_consecutive = MarketAnalyzer._count_consecutive_days(recent_data['foreign_net'])
        
        if foreign_consecutive >= 5 and foreign_net > 0:
            scores['foreign_score'] += 10  # 连续买超5天以上
        elif foreign_consecutive >= 3 and foreign_net > 0:
            scores['foreign_score'] += 7
        elif foreign_net > 0:
            scores['foreign_score'] += 4
        elif foreign_consecutive <= -5 and foreign_net < 0:
            scores['foreign_score'] -= 5  # 连续卖超
        elif foreign_net < 0:
            scores['foreign_score'] -= 2
        
        # 2. 投信分析 (12分) - 权重最高
        trust_net = recent_data['trust_net'].sum()
        trust_consecutive = MarketAnalyzer._count_consecutive_days(recent_data['trust_net'])
        
        # 投信是台股三大法人中表现最优
        if trust_consecutive >= 5 and trust_net > 0:
            scores['trust_score'] += 12  # 最强信号
        elif trust_consecutive >= 3 and trust_net > 0:
            scores['trust_score'] += 9
        elif trust_net > 0:
            scores['trust_score'] += 5
        elif trust_consecutive <= -5 and trust_net < 0:
            scores['trust_score'] -= 6
        elif trust_net < 0:
            scores['trust_score'] -= 3
        
        # 3. 自营商分析 (5分)
        dealer_net = recent_data['dealer_net'].sum()
        
        if dealer_net > 0:
            scores['dealer_score'] += 5
        elif dealer_net < 0:
            scores['dealer_score'] -= 2
        
        # 4. 三大法人共识 (3分)
        latest = recent_data.iloc[-1]
        all_buy = (latest['foreign_net'] > 0 and 
                   latest['trust_net'] > 0 and 
                   latest['dealer_net'] > 0)
        all_sell = (latest['foreign_net'] < 0 and 
                    latest['trust_net'] < 0 and 
                    latest['dealer_net'] < 0)
        
        if all_buy:
            scores['consensus_score'] += 3  # 三大法人同步买超
        elif all_sell:
            scores['consensus_score'] -= 3  # 三大法人同步卖超
        
        # 计算市场面总分
        scores['market_total'] = (
            scores['foreign_score'] + 
            scores['trust_score'] + 
            scores['dealer_score'] + 
            scores['consensus_score']
        )
        
        return scores
    
    @staticmethod
    def _count_consecutive_days(series: pd.Series) -> int:
        """计算连续买超/卖超天数"""
        if len(series) == 0:
            return 0
        
        count = 0
        last_value = series.iloc[-1]
        
        if last_value == 0:
            return 0
        
        direction = 1 if last_value > 0 else -1
        
        for value in reversed(series.values):
            if (direction > 0 and value > 0) or (direction < 0 and value < 0):
                count += 1
            else:
                break
        
        return count * direction


class ChipsAnalyzer:
    """
    筹码面分析器
    分析融资融券、主力进出、当冲比例
    
    数据来源: FinMind API - taiwan_stock_margin_purchase_short_sale
    """
    
    @staticmethod
    def calculate_chips_score(margin_data: pd.DataFrame, 
                             price_data: pd.DataFrame,
                             lookback_days: int = 10) -> Dict:
        """
        计算筹码面评分
        
        权重分配：
        - 融资使用率: 12%
        - 主力进出: 10%
        - 券资比: 5%
        - 当冲比例: 3%
        
        返回筹码面评分（满分30分）
        """
        scores = {
            'margin_usage_score': 0,   # 融资使用率分数 (0-12)
            'main_force_score': 0,     # 主力进出分数 (0-10)
            'short_ratio_score': 0,    # 券资比分数 (0-5)
            'day_trade_score': 0,      # 当冲分数 (0-3)
            'chips_total': 0           # 筹码面总分 (0-30)
        }
        
        if margin_data is None or len(margin_data) < lookback_days:
            return scores
        
        recent_margin = margin_data.tail(lookback_days)
        latest_margin = recent_margin.iloc[-1]
        
        # 1. 融资使用率评分 (12分) - 散户情绪温度计
        margin_usage = latest_margin.get('margin_usage_rate', 50)
        
        if margin_usage < 30:
            scores['margin_usage_score'] += 12  # 低档，散户不积极，可能接近底部
        elif 30 <= margin_usage < 45:
            scores['margin_usage_score'] += 8   # 健康区间
        elif 45 <= margin_usage < 60:
            scores['margin_usage_score'] += 4   # 正常
        elif 60 <= margin_usage < 70:
            scores['margin_usage_score'] += 0   # 偏高
        elif 70 <= margin_usage < 80:
            scores['margin_usage_score'] -= 4   # 需注意风险
        else:  # >= 80
            scores['margin_usage_score'] -= 8   # 散户过度乐观，顶部信号
        
        # 融资变化趋势
        if len(recent_margin) >= 5:
            margin_change = latest_margin.get('margin_change_pct', 0)
            
            # 融资大幅减少 (底部信号)
            if margin_change < -5:
                scores['margin_usage_score'] += 3
            # 融资快速增加 (警示信号)
            elif margin_change > 10:
                scores['margin_usage_score'] -= 3
        
        # 2. 主力进出评分 (10分)
        # 基于价格数据中的主力指标
        if price_data is not None and len(price_data) >= lookback_days:
            recent_price = price_data.tail(lookback_days)
            
            if 'MFI_Short' in recent_price.columns:
                latest_price = recent_price.iloc[-1]
                
                # 三线向上发散
                if (latest_price['MFI_Short'] > latest_price['MFI_Medium'] > 
                    latest_price['MFI_Long']):
                    scores['main_force_score'] += 10  # 主力有效控盘
                # 短线远离中长线
                elif (latest_price['MFI_Short'] > latest_price['MFI_Medium']):
                    scores['main_force_score'] += 6
                # 死亡交叉
                elif (latest_price['MFI_Short'] < latest_price['MFI_Medium'] < 
                      latest_price['MFI_Long']):
                    scores['main_force_score'] -= 6  # 主力出货
        
        # 3. 券资比评分 (5分)
        short_ratio = latest_margin.get('short_margin_ratio', 10)
        
        if short_ratio < 10:
            scores['short_ratio_score'] += 5    # 看多力量强
        elif 10 <= short_ratio < 15:
            scores['short_ratio_score'] += 3    # 正常
        elif 15 <= short_ratio < 20:
            scores['short_ratio_score'] += 0    # 正常偏高
        else:  # >= 20
            scores['short_ratio_score'] -= 2    # 看空力量强
        
        # 4. 当冲比例评分 (3分)
        day_trade_ratio = latest_margin.get('day_trade_ratio', 10)
        
        if day_trade_ratio < 5:
            scores['day_trade_score'] += 3      # 市场冷清，可能底部
        elif 5 <= day_trade_ratio < 15:
            scores['day_trade_score'] += 2      # 正常
        elif 15 <= day_trade_ratio < 20:
            scores['day_trade_score'] -= 1      # 投机氛围浓厚
        else:  # >= 20
            scores['day_trade_score'] -= 3      # 市场过热
        
        # 计算筹码面总分
        scores['chips_total'] = (
            scores['margin_usage_score'] + 
            scores['main_force_score'] + 
            scores['short_ratio_score'] + 
            scores['day_trade_score']
        )
        
        return scores


class SignalIntegrator:
    """
    信号整合引擎
    整合技术面、市场面、筹码面、总体经济面的多维度信号
    """

    def __init__(self, weights: Dict = None):
        """
        初始化整合器

        默认权重（优化版，加入总体经济）：
        - 技术面: 35% (从40%调整)
        - 市场面: 25% (从30%调整)
        - 筹码面: 25% (从30%调整)
        - 总体经济: 15% (新增!)
        """
        self.weights = weights or {
            'technical': 0.35,
            'market': 0.25,
            'chips': 0.25,
            'macro': 0.15
        }
    
    def integrate_signals(self,
                         technical_score: Dict,
                         market_score: Dict = None,
                         chips_score: Dict = None,
                         macro_score: Dict = None) -> Dict:
        """
        整合多维度信号

        返回：
        - score: 综合评分 (-1 到 1)
        - score_100: 0-100分制
        - signal: 信号类型
        - strength: 信号强度
        - recommendation: 操作建议
        """
        # 获取各维度总分
        tech_total = technical_score.get('technical_total', 0)  # 满分35 (调整后)
        market_total = market_score.get('market_total', 0) if market_score else 0  # 满分25
        chips_total = chips_score.get('chips_total', 0) if chips_score else 0  # 满分25
        macro_total = macro_score.get('macro_total_score', 0) if macro_score else 5  # 满分10，默认中性5分

        # 调整技术面、市场面、筹码面的满分以匹配新权重
        # 技术面：从40分调整为35分
        tech_adjusted = tech_total * (35 / 40)
        # 市场面：从30分调整为25分
        market_adjusted = market_total * (25 / 30) if market_score else 0
        # 筹码面：从30分调整为25分
        chips_adjusted = chips_total * (25 / 30) if chips_score else 0

        # 标准化到 -1 到 1 范围
        tech_normalized = tech_adjusted / 17.5 - 1    # 35分 -> [-1, 1]
        market_normalized = market_adjusted / 12.5 - 1  # 25分 -> [-1, 1]
        chips_normalized = chips_adjusted / 12.5 - 1   # 25分 -> [-1, 1]
        macro_normalized = macro_total / 5 - 1        # 10分 -> [-1, 1]

        # 加权综合评分
        integrated_score = (
            tech_normalized * self.weights['technical'] +
            market_normalized * self.weights['market'] +
            chips_normalized * self.weights['chips'] +
            macro_normalized * self.weights['macro']
        )

        # 转换为0-100分
        score_100 = (integrated_score + 1) * 50

        # 生成信号和强度
        signal, strength = self._generate_signal(score_100)

        # 生成操作建议
        recommendation = self._generate_recommendation(signal, score_100)

        return {
            'score': integrated_score,
            'score_100': score_100,
            'signal': signal,
            'strength': strength,
            'recommendation': recommendation,
            'breakdown': {
                'technical': tech_adjusted,
                'market': market_adjusted,
                'chips': chips_adjusted,
                'macro': macro_total
            }
        }
    
    def _generate_signal(self, score_100: float) -> Tuple[str, str]:
        """根据分数生成信号类型和强度"""
        if score_100 >= 80:
            return 'strong_buy', 'very_high'
        elif score_100 >= 60:
            return 'buy', 'high'
        elif score_100 >= 40:
            return 'neutral', 'medium'
        elif score_100 >= 20:
            return 'sell', 'low'
        else:
            return 'strong_sell', 'very_low'
    
    def _generate_recommendation(self, signal: str, score: float) -> str:
        """生成操作建议"""
        recommendations = {
            'strong_buy': f'强烈看多（{score:.1f}分），建议积极进场，仓位50-70%',
            'buy': f'看多（{score:.1f}分），建议谨慎进场，仓位30-50%',
            'neutral': f'中性（{score:.1f}分），建议观望或轻仓',
            'sell': f'看空（{score:.1f}分），建议减仓至10-30%',
            'strong_sell': f'强烈看空（{score:.1f}分），建议空手或避险'
        }
        
        return recommendations.get(signal, f'无明确建议（{score:.1f}分）')


class EnhancedStockPicker(SmartStockPicker):
    """
    增强版智能选股器
    整合台股波段预测的多因子框架 + 总体经济分析
    """

    def __init__(self):
        super().__init__()
        self.signal_integrator = SignalIntegrator()
        self.enhanced_analyzer = EnhancedStockAnalyzer()

        # 初始化总体经济分析器
        if MACRO_AVAILABLE:
            self.macro_analyzer = MacroEconomicAnalyzer()
            print("✅ 总体经济分析器已启用")
        else:
            self.macro_analyzer = None
            print("⚠️ 总体经济分析器未启用")
    
    def analyze_stock_enhanced(self,
                              symbol: str,
                              price_data: pd.DataFrame,
                              institutional_data: pd.DataFrame = None,
                              margin_data: pd.DataFrame = None,
                              use_macro: bool = True,
                              strategy: str = 'moderate') -> Dict:
        """
        增强版股票分析

        整合：
        1. 技术面 (35%) - 包含台股优化指标
        2. 市场面 (25%) - 法人买卖超
        3. 筹码面 (25%) - 融资融券
        4. 总体经济 (15%) - VIX、美元、利率 (NEW!)

        返回完整的分析结果
        """
        try:
            # 1. 计算增强版技术指标
            df = self.enhanced_analyzer.calculate_indicators(price_data.copy())

            if len(df) < 50:
                return {'error': '数据不足，至少需要50笔交易数据'}

            # 2. 计算台股优化技术评分
            tech_score = self.enhanced_analyzer.calculate_taiwan_optimized_score(df, -1)

            # 3. 计算市场面评分（如果有数据）
            market_score = None
            if institutional_data is not None and len(institutional_data) > 0:
                market_score = MarketAnalyzer.calculate_institutional_score(
                    institutional_data, lookback_days=10
                )

            # 4. 计算筹码面评分（如果有数据）
            chips_score = None
            if margin_data is not None and len(margin_data) > 0:
                chips_score = ChipsAnalyzer.calculate_chips_score(
                    margin_data, df, lookback_days=10
                )

            # 5. 计算总体经济评分（新增！）
            macro_score = None
            if use_macro and self.macro_analyzer is not None:
                try:
                    print(f"\n🌍 获取总体经济数据...")
                    macro_score = self.macro_analyzer.calculate_macro_score(lookback_days=30)
                except Exception as e:
                    print(f"⚠️ 总体经济分析失败: {e}，将使用默认值")
                    macro_score = None

            # 6. 整合信号
            integrated = self.signal_integrator.integrate_signals(
                tech_score, market_score, chips_score, macro_score
            )
            
            # 7. 获取基础分析（使用原有方法）
            base_analysis = super().analyze_stock(symbol, price_data, strategy)

            # 8. 合并结果
            enhanced_analysis = {
                **base_analysis,
                'enhanced_score': integrated['score_100'],
                'enhanced_signal': integrated['signal'],
                'enhanced_recommendation': integrated['recommendation'],
                'score_breakdown': integrated['breakdown'],
                'technical_details': tech_score,
                'market_details': market_score,
                'chips_details': chips_score,
                'macro_details': macro_score  # 新增！总体经济详情
            }

            # 9. 生成增强版操作建议（包含总体经济）
            enhanced_analysis['key_points'] = self._generate_enhanced_key_points(
                tech_score, market_score, chips_score, macro_score, df.iloc[-1]
            )
            
            return enhanced_analysis
            
        except Exception as e:
            return {'error': f'分析失败: {str(e)}'}
    
    def _generate_enhanced_key_points(self,
                                     tech_score: Dict,
                                     market_score: Dict,
                                     chips_score: Dict,
                                     macro_score: Dict,
                                     latest_row: pd.Series) -> List[str]:
        """生成增强版关键观察点（包含总体经济）"""
        points = []

        # 技术面关键点
        if pd.notna(latest_row.get('K')):
            k_value = latest_row['K']
            d_value = latest_row['D']

            if k_value < 20:
                points.append(f"🔹 KD指标处于超卖区 (K={k_value:.1f})，可能出现反弹")
            elif k_value > 80:
                points.append(f"🔹 KD指标处于超买区 (K={k_value:.1f})，注意回调风险")

            if k_value > d_value:
                points.append(f"🔹 KD金叉，多头讯号")
            else:
                points.append(f"🔹 KD死叉，空头讯号")

        # OBV趋势
        if pd.notna(latest_row.get('OBV')):
            obv = latest_row['OBV']
            obv_ma5 = latest_row.get('OBV_MA5', obv)

            if obv > obv_ma5:
                points.append("🔹 OBV上升，资金持续流入")
            else:
                points.append("🔹 OBV下降，资金流出")

        # 市场面关键点
        if market_score:
            trust_score = market_score.get('trust_score', 0)
            foreign_score = market_score.get('foreign_score', 0)

            if trust_score >= 9:
                points.append("🔹 投信连续大幅买超，强力看多信号")
            elif trust_score <= -6:
                points.append("🔹 投信连续卖超，注意风险")

            if foreign_score >= 7:
                points.append("🔹 外资连续买超，支撑强劲")
            elif foreign_score <= -5:
                points.append("🔹 外资连续卖超，承压明显")

        # 筹码面关键点
        if chips_score:
            margin_score = chips_score.get('margin_usage_score', 0)

            if margin_score >= 10:
                points.append("🔹 融资使用率低，散户不积极，可能接近底部")
            elif margin_score <= -6:
                points.append("🔹 融资使用率高，散户过度乐观，注意顶部风险")

        # 总体经济面关键点（新增！）
        if macro_score and self.macro_analyzer:
            macro_points = self.macro_analyzer.generate_macro_report(macro_score)
            points.extend(macro_points)

        return points


# ========== 工具函数 ==========

def print_enhanced_analysis_report(analysis: Dict):
    """打印增强版分析报告（包含总体经济）"""
    print("\n" + "="*80)
    print(f"📊 {analysis['symbol']} - 多因子智能选股报告 v4.0")
    print("="*80)

    # 基本信息
    print(f"\n【基本信息】")
    print(f"当前价格: ${analysis['current_price']:.2f}")
    print(f"数据日期: {analysis.get('data_date', 'N/A')}")

    # 增强版评分
    if 'enhanced_score' in analysis:
        print(f"\n【多因子综合评分】")
        print(f"总分: {analysis['enhanced_score']:.1f}/100")
        print(f"信号: {analysis['enhanced_signal']}")
        print(f"建议: {analysis['enhanced_recommendation']}")

        if 'score_breakdown' in analysis:
            breakdown = analysis['score_breakdown']
            print(f"\n评分明细 (v4.0):")
            print(f"  技术面: {breakdown['technical']:.1f}/35 (权重35%)")
            print(f"  市场面: {breakdown['market']:.1f}/25 (权重25%)")
            print(f"  筹码面: {breakdown['chips']:.1f}/25 (权重25%)")
            print(f"  总体经济: {breakdown['macro']:.1f}/10 (权重15%) ← NEW!")
    
    # 技术细节
    if 'technical_details' in analysis:
        print(f"\n【技术面细节】")
        tech = analysis['technical_details']
        print(f"  KD指标分数: {tech['kd_score']:.1f}/15")
        print(f"  OBV分数: {tech['obv_score']:.1f}/10")
        print(f"  MA分数: {tech['ma_score']:.1f}/10")
        print(f"  RSI分数: {tech['rsi_score']:.2f}/2.5")
        print(f"  MACD分数: {tech['macd_score']:.2f}/2.5")
    
    # 市场面细节
    if 'market_details' in analysis and analysis['market_details']:
        print(f"\n【市场面细节】")
        market = analysis['market_details']
        print(f"  外资分数: {market['foreign_score']:.1f}/10")
        print(f"  投信分数: {market['trust_score']:.1f}/12")
        print(f"  自营商分数: {market['dealer_score']:.1f}/5")
        print(f"  共识分数: {market['consensus_score']:.1f}/3")
    
    # 筹码面细节
    if 'chips_details' in analysis and analysis['chips_details']:
        print(f"\n【筹码面细节】")
        chips = analysis['chips_details']
        print(f"  融资使用率分数: {chips['margin_usage_score']:.1f}/12")
        print(f"  主力进出分数: {chips['main_force_score']:.1f}/10")
        print(f"  券资比分数: {chips['short_ratio_score']:.1f}/5")
        print(f"  当冲比例分数: {chips['day_trade_score']:.1f}/3")

    # 总体经济面细节（新增！）
    if 'macro_details' in analysis and analysis['macro_details']:
        print(f"\n【总体经济面细节】← NEW!")
        macro = analysis['macro_details']
        print(f"  综合评分: {macro['macro_total_score']:.1f}/10")
        print(f"  市场环境: {macro['macro_environment']}")
        print(f"  分析日期: {macro['analysis_date']}")

        # VIX详情
        if 'vix_analysis' in macro:
            vix = macro['vix_analysis']
            if vix['current_vix'] > 0:
                print(f"\n  🔸 VIX恐慌指数:")
                print(f"     当前值: {vix['current_vix']:.2f}")
                print(f"     市场情绪: {vix['market_sentiment']}")
                print(f"     风险等级: {vix['risk_level']}")
                print(f"     趋势: {vix['vix_trend']}")
                print(f"     评分: {vix['vix_score']:.1f}/10")

        # 美元指数详情
        if 'dollar_analysis' in macro:
            dxy = macro['dollar_analysis']
            if dxy['current_dxy'] > 0:
                print(f"\n  🔸 美元指数DXY:")
                print(f"     当前值: {dxy['current_dxy']:.2f}")
                print(f"     美元强度: {dxy['dollar_strength']}")
                print(f"     趋势: {dxy['dxy_trend']}")
                print(f"     对股市影响: {dxy['impact_on_stocks']}")
                print(f"     评分: {dxy['dxy_score']:.1f}/10")

        # 殖利率详情
        if 'yield_analysis' in macro:
            yld = macro['yield_analysis']
            if yld['current_yield'] > 0:
                print(f"\n  🔸 10年期公债殖利率:")
                print(f"     当前值: {yld['current_yield']:.2f}%")
                print(f"     趋势: {yld['yield_trend']}")
                print(f"     对股市影响: {yld['impact_on_stocks']}")
                print(f"     评分: {yld['yield_score']:.1f}/10")

    # 价格预测
    print(f"\n【价格预测】")
    print(f"目标价格: ${analysis['target_price']:.2f}")
    print(f"预期报酬: {analysis['expected_return']:.1%}")
    print(f"风险报酬比: {analysis['risk_reward_ratio']:.2f}")
    print(f"预计时间: {analysis['timeframe_days']}天")
    
    # 关键观察点
    print(f"\n【关键观察点】")
    for point in analysis.get('key_points', []):
        print(f"  {point}")
    
    # 风险提示
    print(f"\n【风险提示】")
    for risk in analysis.get('risks', []):
        print(f"  ⚠ {risk}")
    
    # 操作建议
    print(f"\n【操作建议】")
    for suggestion in analysis.get('operation_suggestions', []):
        print(f"  • {suggestion}")
    
    print("\n" + "="*80)


# ========== 使用示例 ==========

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          增强版智能选股系统 v3.0 - 台股波段预测              ║
    ║     Enhanced Stock Picker with Multi-Factor Analysis         ║
    ╚════════════════════════════════════════════════════════════════╝
    
    新增功能：
    1. 🎯 台股优化技术指标 - KD(9,3,3) + OBV + 10日MA
    2. 📊 市场面分析 - 三大法人买卖超
    3. 💹 筹码面分析 - 融资融券、主力进出
    4. 🔄 多因子整合 - 技术40% + 市场30% + 筹码30%
    
    基于学术实证：
    - KD+OBV组合策略成功率79% (Springer 2018)
    - 投信买卖超表现最优 (台股实证)
    - 融资使用率作为散户情绪指标
    """)
    
    print("\n使用示例见 usage_examples_enhanced.py")
