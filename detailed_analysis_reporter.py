"""
Detailed Analysis Reporter for Taiwan Stock Prediction System v5.0

This module provides comprehensive reasoning and explanations for every score
in the five-dimensional analysis system (Technical, Market, Chips, Macro, Sentiment).

Author: Taiwan Stock Prediction System
Version: 5.0
Date: 2025-11-26
"""

import json
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import numpy as np


class DetailedAnalysisReporter:
    """
    Comprehensive report generator that provides detailed reasoning for every score
    in the five-dimensional analysis system.
    """

    def __init__(self):
        """Initialize the detailed analysis reporter."""
        self.report_sections = []
        self.strengths = []
        self.weaknesses = []
        self.risk_warnings = []

        # Weight allocation for five-dimensional analysis
        self.weights = {
            'technical': 0.30,    # 30% - Technical indicators
            'market': 0.20,       # 20% - Institutional investor activity
            'chips': 0.20,        # 20% - Margin trading and chips distribution
            'macro': 0.15,        # 15% - Macro economic indicators
            'sentiment': 0.15     # 15% - News sentiment analysis
        }

    def generate_comprehensive_report(self, stock_code: str, stock_data: Dict[str, Any],
                                     analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis report with detailed reasoning.

        Args:
            stock_code: Stock symbol (e.g., '2330')
            stock_data: Historical stock data and indicators
            analysis_results: Analysis results from all dimensions

        Returns:
            Dictionary containing comprehensive report with detailed explanations
        """
        self.report_sections = []
        self.strengths = []
        self.weaknesses = []
        self.risk_warnings = []

        # Generate analysis for each dimension
        technical_analysis = self._generate_technical_analysis(stock_data, analysis_results.get('technical', {}))
        market_analysis = self._generate_market_analysis(stock_data, analysis_results.get('market', {}))
        chips_analysis = self._generate_chips_analysis(stock_data, analysis_results.get('chips', {}))
        macro_analysis = self._generate_macro_analysis(analysis_results.get('macro', {}))
        sentiment_analysis = self._generate_sentiment_analysis(analysis_results.get('sentiment', {}))

        # Calculate overall score
        overall_score = self._calculate_overall_score(analysis_results)

        # Generate investment recommendation
        recommendation = self._generate_recommendation(overall_score, analysis_results)

        # Compile comprehensive report
        report = {
            'stock_code': stock_code,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': overall_score,
            'recommendation': recommendation,
            'dimension_scores': {
                'technical': analysis_results.get('technical', {}).get('score', 0),
                'market': analysis_results.get('market', {}).get('score', 0),
                'chips': analysis_results.get('chips', {}).get('score', 0),
                'macro': analysis_results.get('macro', {}).get('score', 0),
                'sentiment': analysis_results.get('sentiment', {}).get('score', 0)
            },
            'detailed_analysis': {
                'technical': technical_analysis,
                'market': market_analysis,
                'chips': chips_analysis,
                'macro': macro_analysis,
                'sentiment': sentiment_analysis
            },
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'risk_warnings': self.risk_warnings
        }

        return report

    def _generate_technical_analysis(self, stock_data: Dict[str, Any],
                                     technical_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed technical analysis with reasoning for each indicator.

        Technical indicators analyzed:
        - KD Indicator (Stochastic Oscillator)
        - OBV (On-Balance Volume)
        - Moving Averages (MA5, MA10, MA20, MA60)
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
        """
        analysis = {
            'score': technical_results.get('score', 0),
            'indicators': {}
        }

        # KD Indicator Analysis
        kd_analysis = self._analyze_kd_indicator(stock_data)
        analysis['indicators']['kd'] = kd_analysis

        # OBV Analysis
        obv_analysis = self._analyze_obv_indicator(stock_data)
        analysis['indicators']['obv'] = obv_analysis

        # Moving Average Analysis
        ma_analysis = self._analyze_moving_averages(stock_data)
        analysis['indicators']['moving_averages'] = ma_analysis

        # RSI Analysis
        rsi_analysis = self._analyze_rsi_indicator(stock_data)
        analysis['indicators']['rsi'] = rsi_analysis

        # MACD Analysis
        macd_analysis = self._analyze_macd_indicator(stock_data)
        analysis['indicators']['macd'] = macd_analysis

        # Generate summary
        analysis['summary'] = self._generate_technical_summary(analysis['indicators'])

        return analysis

    def _analyze_kd_indicator(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze KD (Stochastic Oscillator) indicator with detailed reasoning.

        KD Indicator Rules:
        - K > 80: Overbought (bearish signal)
        - K < 20: Oversold (bullish signal)
        - K cross above D: Golden cross (bullish)
        - K cross below D: Death cross (bearish)
        """
        kd_data = stock_data.get('kd', {})
        k_value = kd_data.get('k', 50)
        d_value = kd_data.get('d', 50)

        reasoning = []
        signal = "neutral"
        score = 50

        # Analyze K value level
        if k_value > 80:
            reasoning.append(f"K value at {k_value:.2f} is in overbought territory (>80), suggesting potential price correction.")
            score -= 20
            signal = "bearish"
            self.risk_warnings.append("KD indicator shows overbought condition - price may face resistance")
        elif k_value < 20:
            reasoning.append(f"K value at {k_value:.2f} is in oversold territory (<20), suggesting potential price rebound.")
            score += 20
            signal = "bullish"
            self.strengths.append("KD indicator shows oversold condition - good entry opportunity")
        else:
            reasoning.append(f"K value at {k_value:.2f} is in neutral range (20-80), indicating balanced momentum.")

        # Analyze K and D crossover
        k_d_diff = k_value - d_value
        if k_d_diff > 0 and k_value < 80:
            reasoning.append(f"K line ({k_value:.2f}) is above D line ({d_value:.2f}), showing bullish momentum.")
            score += 15
            if signal != "bearish":
                signal = "bullish"
                self.strengths.append("KD golden cross detected - bullish signal")
        elif k_d_diff < 0 and k_value > 20:
            reasoning.append(f"K line ({k_value:.2f}) is below D line ({d_value:.2f}), showing bearish momentum.")
            score -= 15
            if signal != "bullish":
                signal = "bearish"
                self.weaknesses.append("KD death cross detected - bearish signal")

        # Check for extreme divergence
        if abs(k_d_diff) > 20:
            reasoning.append(f"Large divergence between K and D ({abs(k_d_diff):.2f}) suggests strong directional momentum.")

        return {
            'k_value': k_value,
            'd_value': d_value,
            'signal': signal,
            'score': max(0, min(100, score)),
            'reasoning': reasoning
        }

    def _analyze_obv_indicator(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze OBV (On-Balance Volume) indicator with detailed reasoning.

        OBV Analysis Rules:
        - Rising OBV with rising price: Strong bullish confirmation
        - Falling OBV with falling price: Strong bearish confirmation
        - Rising OBV with falling price: Bullish divergence (accumulation)
        - Falling OBV with rising price: Bearish divergence (distribution)
        """
        obv_data = stock_data.get('obv', {})
        current_obv = obv_data.get('current', 0)
        obv_trend = obv_data.get('trend', 'neutral')
        obv_change = obv_data.get('change_pct', 0)

        price_data = stock_data.get('price', {})
        price_trend = price_data.get('trend', 'neutral')

        reasoning = []
        signal = "neutral"
        score = 50

        # Analyze OBV trend
        if obv_trend == 'rising':
            reasoning.append(f"OBV is in an uptrend (change: {obv_change:+.2f}%), indicating accumulation by investors.")
            score += 15

            if price_trend == 'rising':
                reasoning.append("OBV rising with price confirms strong buying pressure - bullish confirmation.")
                score += 20
                signal = "bullish"
                self.strengths.append("OBV and price both rising - strong bullish confirmation")
            elif price_trend == 'falling':
                reasoning.append("OBV rising while price falls suggests smart money accumulation - bullish divergence.")
                score += 10
                signal = "bullish"
                self.strengths.append("Bullish divergence detected - OBV rising while price falling")

        elif obv_trend == 'falling':
            reasoning.append(f"OBV is in a downtrend (change: {obv_change:+.2f}%), indicating distribution by investors.")
            score -= 15

            if price_trend == 'falling':
                reasoning.append("OBV falling with price confirms strong selling pressure - bearish confirmation.")
                score -= 20
                signal = "bearish"
                self.weaknesses.append("OBV and price both falling - strong bearish confirmation")
            elif price_trend == 'rising':
                reasoning.append("OBV falling while price rises suggests weak rally - bearish divergence.")
                score -= 10
                signal = "bearish"
                self.risk_warnings.append("Bearish divergence detected - OBV falling while price rising")

        else:
            reasoning.append(f"OBV shows sideways movement (change: {obv_change:+.2f}%), indicating balanced volume.")

        # Analyze magnitude of OBV change
        if abs(obv_change) > 10:
            reasoning.append(f"Significant OBV change ({abs(obv_change):.2f}%) indicates strong conviction in current direction.")
        elif abs(obv_change) < 2:
            reasoning.append("Minimal OBV change suggests low conviction and potential consolidation phase.")

        return {
            'current_obv': current_obv,
            'trend': obv_trend,
            'change_pct': obv_change,
            'signal': signal,
            'score': max(0, min(100, score)),
            'reasoning': reasoning
        }

    def _analyze_moving_averages(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Moving Averages with detailed reasoning.

        MA Analysis Rules:
        - Price above all MAs: Strong uptrend
        - Price below all MAs: Strong downtrend
        - Golden cross (short MA crosses above long MA): Bullish
        - Death cross (short MA crosses below long MA): Bearish
        - MA alignment (MA5 > MA10 > MA20 > MA60): Strong uptrend
        """
        ma_data = stock_data.get('moving_averages', {})
        current_price = stock_data.get('price', {}).get('current', 0)

        ma5 = ma_data.get('ma5', 0)
        ma10 = ma_data.get('ma10', 0)
        ma20 = ma_data.get('ma20', 0)
        ma60 = ma_data.get('ma60', 0)

        reasoning = []
        signal = "neutral"
        score = 50

        # Analyze price position relative to MAs
        above_ma_count = 0
        if current_price > ma5:
            above_ma_count += 1
        if current_price > ma10:
            above_ma_count += 1
        if current_price > ma20:
            above_ma_count += 1
        if current_price > ma60:
            above_ma_count += 1

        if above_ma_count == 4:
            reasoning.append(f"Price ({current_price:.2f}) is above all moving averages - strong uptrend.")
            score += 25
            signal = "bullish"
            self.strengths.append("Price above all moving averages - strong bullish trend")
        elif above_ma_count == 0:
            reasoning.append(f"Price ({current_price:.2f}) is below all moving averages - strong downtrend.")
            score -= 25
            signal = "bearish"
            self.weaknesses.append("Price below all moving averages - strong bearish trend")
        elif above_ma_count >= 2:
            reasoning.append(f"Price is above {above_ma_count} out of 4 moving averages - moderate uptrend.")
            score += 10
        else:
            reasoning.append(f"Price is above {above_ma_count} out of 4 moving averages - moderate downtrend.")
            score -= 10

        # Analyze MA alignment
        if ma5 > ma10 > ma20 > ma60:
            reasoning.append("Moving averages are in perfect bullish alignment (MA5 > MA10 > MA20 > MA60).")
            score += 20
            signal = "bullish"
            self.strengths.append("Perfect bullish MA alignment detected")
        elif ma5 < ma10 < ma20 < ma60:
            reasoning.append("Moving averages are in perfect bearish alignment (MA5 < MA10 < MA20 < MA60).")
            score -= 20
            signal = "bearish"
            self.weaknesses.append("Perfect bearish MA alignment detected")

        # Analyze short-term crossovers
        if ma5 > ma10 and ma10 > ma20:
            reasoning.append("Short-term golden cross pattern (MA5 > MA10 > MA20) suggests bullish momentum.")
            if signal != "bearish":
                signal = "bullish"
        elif ma5 < ma10 and ma10 < ma20:
            reasoning.append("Short-term death cross pattern (MA5 < MA10 < MA20) suggests bearish momentum.")
            if signal != "bullish":
                signal = "bearish"

        # Calculate distance from MA20 (important support/resistance)
        if ma20 > 0:
            ma20_distance = ((current_price - ma20) / ma20) * 100
            if abs(ma20_distance) > 10:
                reasoning.append(f"Price is {abs(ma20_distance):.2f}% {'above' if ma20_distance > 0 else 'below'} MA20 - significant deviation.")
                if abs(ma20_distance) > 15:
                    self.risk_warnings.append(f"Price is {abs(ma20_distance):.2f}% from MA20 - potential mean reversion risk")

        return {
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'ma60': ma60,
            'current_price': current_price,
            'above_ma_count': above_ma_count,
            'signal': signal,
            'score': max(0, min(100, score)),
            'reasoning': reasoning
        }

    def _analyze_rsi_indicator(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze RSI (Relative Strength Index) with detailed reasoning.

        RSI Analysis Rules:
        - RSI > 70: Overbought (potential reversal)
        - RSI < 30: Oversold (potential reversal)
        - RSI 40-60: Neutral zone
        - RSI divergence: Important reversal signal
        """
        rsi_data = stock_data.get('rsi', {})
        current_rsi = rsi_data.get('current', 50)
        rsi_trend = rsi_data.get('trend', 'neutral')

        reasoning = []
        signal = "neutral"
        score = 50

        # Analyze RSI level
        if current_rsi > 70:
            reasoning.append(f"RSI at {current_rsi:.2f} is in overbought territory (>70), suggesting overheated conditions.")
            score -= 20
            signal = "bearish"
            self.risk_warnings.append(f"RSI overbought at {current_rsi:.2f} - potential correction ahead")

            if current_rsi > 80:
                reasoning.append(f"Extremely overbought RSI (>80) indicates very high reversal risk.")
                score -= 10

        elif current_rsi < 30:
            reasoning.append(f"RSI at {current_rsi:.2f} is in oversold territory (<30), suggesting potential rebound.")
            score += 20
            signal = "bullish"
            self.strengths.append(f"RSI oversold at {current_rsi:.2f} - good entry opportunity")

            if current_rsi < 20:
                reasoning.append(f"Extremely oversold RSI (<20) indicates strong rebound potential.")
                score += 10

        elif 40 <= current_rsi <= 60:
            reasoning.append(f"RSI at {current_rsi:.2f} is in neutral zone (40-60), indicating balanced momentum.")

        else:
            if current_rsi > 60:
                reasoning.append(f"RSI at {current_rsi:.2f} shows bullish momentum but not yet overbought.")
                score += 10
                signal = "bullish"
            else:
                reasoning.append(f"RSI at {current_rsi:.2f} shows bearish momentum but not yet oversold.")
                score -= 10
                signal = "bearish"

        # Analyze RSI trend
        if rsi_trend == 'rising':
            reasoning.append("RSI is trending upward, indicating strengthening momentum.")
            if signal != "bearish":
                score += 5
        elif rsi_trend == 'falling':
            reasoning.append("RSI is trending downward, indicating weakening momentum.")
            if signal != "bullish":
                score -= 5

        return {
            'current_rsi': current_rsi,
            'trend': rsi_trend,
            'signal': signal,
            'score': max(0, min(100, score)),
            'reasoning': reasoning
        }

    def _analyze_macd_indicator(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze MACD (Moving Average Convergence Divergence) with detailed reasoning.

        MACD Analysis Rules:
        - MACD > Signal: Bullish
        - MACD < Signal: Bearish
        - MACD crosses above Signal: Golden cross (buy signal)
        - MACD crosses below Signal: Death cross (sell signal)
        - Histogram expanding: Strengthening momentum
        """
        macd_data = stock_data.get('macd', {})
        macd_line = macd_data.get('macd', 0)
        signal_line = macd_data.get('signal', 0)
        histogram = macd_data.get('histogram', 0)

        reasoning = []
        signal = "neutral"
        score = 50

        # Analyze MACD position relative to signal line
        if macd_line > signal_line:
            reasoning.append(f"MACD ({macd_line:.2f}) is above signal line ({signal_line:.2f}) - bullish configuration.")
            score += 15
            signal = "bullish"

            if histogram > 0 and macd_data.get('histogram_expanding', False):
                reasoning.append("MACD histogram is positive and expanding - strengthening bullish momentum.")
                score += 10
                self.strengths.append("MACD shows strong bullish momentum with expanding histogram")

        elif macd_line < signal_line:
            reasoning.append(f"MACD ({macd_line:.2f}) is below signal line ({signal_line:.2f}) - bearish configuration.")
            score -= 15
            signal = "bearish"

            if histogram < 0 and macd_data.get('histogram_expanding', False):
                reasoning.append("MACD histogram is negative and expanding - strengthening bearish momentum.")
                score -= 10
                self.weaknesses.append("MACD shows strong bearish momentum with expanding histogram")

        # Analyze histogram magnitude
        if abs(histogram) < 0.5:
            reasoning.append("Small MACD histogram suggests weak momentum and potential consolidation.")
        elif abs(histogram) > 2:
            reasoning.append(f"Large MACD histogram ({abs(histogram):.2f}) indicates strong directional momentum.")

        # Check for centerline crossover
        if macd_line > 0:
            reasoning.append("MACD is above zero line - longer-term bullish trend.")
            if signal != "bearish":
                score += 5
        elif macd_line < 0:
            reasoning.append("MACD is below zero line - longer-term bearish trend.")
            if signal != "bullish":
                score -= 5

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram,
            'signal': signal,
            'score': max(0, min(100, score)),
            'reasoning': reasoning
        }

    def _generate_technical_summary(self, indicators: Dict[str, Any]) -> str:
        """Generate a comprehensive technical analysis summary."""
        signals = [ind['signal'] for ind in indicators.values()]
        bullish_count = signals.count('bullish')
        bearish_count = signals.count('bearish')

        if bullish_count > bearish_count + 1:
            return f"Technical indicators show strong bullish consensus ({bullish_count}/5 bullish signals). The stock demonstrates positive momentum across multiple timeframes."
        elif bearish_count > bullish_count + 1:
            return f"Technical indicators show strong bearish consensus ({bearish_count}/5 bearish signals). The stock demonstrates negative momentum across multiple timeframes."
        else:
            return "Technical indicators show mixed signals with no clear directional consensus. This suggests a consolidation phase or transitional period."

    def _generate_market_analysis(self, stock_data: Dict[str, Any],
                                  market_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed market analysis focused on institutional investor activity.

        Market Analysis Components:
        - Foreign institutional investors net buying/selling
        - Investment trust net buying/selling
        - Dealer proprietary trading activity
        - Three major institutional investors combined flow
        """
        analysis = {
            'score': market_results.get('score', 0),
            'institutional_activity': {}
        }

        reasoning = []
        signal = "neutral"
        score = 50

        # Analyze foreign institutional investors
        foreign_data = stock_data.get('foreign_investors', {})
        foreign_net = foreign_data.get('net_buy', 0)
        foreign_trend = foreign_data.get('trend', 'neutral')

        if foreign_net > 0:
            reasoning.append(f"Foreign institutional investors net bought {foreign_net:,.0f} shares, showing international confidence.")
            score += 15
            signal = "bullish"
            if foreign_net > 1000000:  # Large amount
                self.strengths.append(f"Significant foreign institutional buying: {foreign_net:,.0f} shares")
                score += 10
        elif foreign_net < 0:
            reasoning.append(f"Foreign institutional investors net sold {abs(foreign_net):,.0f} shares, indicating caution.")
            score -= 15
            signal = "bearish"
            if abs(foreign_net) > 1000000:  # Large amount
                self.weaknesses.append(f"Significant foreign institutional selling: {abs(foreign_net):,.0f} shares")
                score -= 10

        # Analyze investment trust
        trust_data = stock_data.get('investment_trust', {})
        trust_net = trust_data.get('net_buy', 0)

        if trust_net > 0:
            reasoning.append(f"Investment trusts net bought {trust_net:,.0f} shares, showing domestic institutional support.")
            score += 10
            if signal != "bearish":
                signal = "bullish"
        elif trust_net < 0:
            reasoning.append(f"Investment trusts net sold {abs(trust_net):,.0f} shares, showing domestic institutional weakness.")
            score -= 10
            if signal != "bullish":
                signal = "bearish"

        # Analyze dealer activity
        dealer_data = stock_data.get('dealer_proprietary', {})
        dealer_net = dealer_data.get('net_buy', 0)

        if dealer_net > 0:
            reasoning.append(f"Dealers net bought {dealer_net:,.0f} shares (proprietary trading), indicating positive outlook.")
            score += 5
        elif dealer_net < 0:
            reasoning.append(f"Dealers net sold {abs(dealer_net):,.0f} shares (proprietary trading), indicating negative outlook.")
            score -= 5

        # Combined institutional analysis
        total_institutional_net = foreign_net + trust_net + dealer_net
        if abs(total_institutional_net) > 0:
            reasoning.append(f"Combined institutional net flow: {total_institutional_net:+,.0f} shares.")
            if total_institutional_net > 0:
                self.strengths.append("Positive combined institutional money flow indicates strong buying support")
            else:
                self.weaknesses.append("Negative combined institutional money flow indicates selling pressure")

        analysis['institutional_activity'] = {
            'foreign_net': foreign_net,
            'trust_net': trust_net,
            'dealer_net': dealer_net,
            'total_net': total_institutional_net,
            'signal': signal,
            'score': max(0, min(100, score)),
            'reasoning': reasoning
        }

        analysis['summary'] = self._generate_market_summary(total_institutional_net, signal)

        return analysis

    def _generate_market_summary(self, total_net: float, signal: str) -> str:
        """Generate market analysis summary."""
        if total_net > 1000000:
            return f"Strong institutional buying with net inflow of {total_net:,.0f} shares. Major players show high confidence in this stock."
        elif total_net < -1000000:
            return f"Strong institutional selling with net outflow of {abs(total_net):,.0f} shares. Major players are reducing exposure."
        elif total_net > 0:
            return f"Moderate institutional buying with net inflow of {total_net:,.0f} shares. Cautiously positive institutional sentiment."
        elif total_net < 0:
            return f"Moderate institutional selling with net outflow of {abs(total_net):,.0f} shares. Cautiously negative institutional sentiment."
        else:
            return "Balanced institutional trading activity with no significant directional bias."

    def _generate_chips_analysis(self, stock_data: Dict[str, Any],
                                 chips_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed chips analysis focused on margin trading and distribution.

        Chips Analysis Components:
        - Margin purchase (融資) trend
        - Short selling (融券) trend
        - Margin ratio and changes
        - Chips concentration
        """
        analysis = {
            'score': chips_results.get('score', 0),
            'margin_trading': {}
        }

        reasoning = []
        signal = "neutral"
        score = 50

        # Analyze margin purchase (融資)
        margin_purchase_data = stock_data.get('margin_purchase', {})
        margin_purchase_change = margin_purchase_data.get('change', 0)
        margin_purchase_balance = margin_purchase_data.get('balance', 0)

        if margin_purchase_change > 0:
            reasoning.append(f"Margin purchase increased by {margin_purchase_change:,.0f} shares, showing leveraged buying interest.")
            score += 10
            signal = "bullish"

            if margin_purchase_change > 500000:
                self.strengths.append("Significant increase in margin purchase indicates strong retail bullish sentiment")
                score += 10
        elif margin_purchase_change < 0:
            reasoning.append(f"Margin purchase decreased by {abs(margin_purchase_change):,.0f} shares, showing deleveraging or reduced interest.")
            score -= 10
            signal = "bearish"

            if abs(margin_purchase_change) > 500000:
                self.weaknesses.append("Significant decrease in margin purchase indicates weakening retail sentiment")
                score -= 10

        # Analyze short selling (融券)
        short_selling_data = stock_data.get('short_selling', {})
        short_selling_change = short_selling_data.get('change', 0)
        short_selling_balance = short_selling_data.get('balance', 0)

        if short_selling_change > 0:
            reasoning.append(f"Short selling increased by {short_selling_change:,.0f} shares, indicating increased bearish bets.")
            score -= 10
            if signal != "bullish":
                signal = "bearish"
        elif short_selling_change < 0:
            reasoning.append(f"Short selling decreased by {abs(short_selling_change):,.0f} shares (short covering), potentially bullish.")
            score += 10
            if signal != "bearish":
                signal = "bullish"
                if abs(short_selling_change) > 100000:
                    self.strengths.append("Significant short covering detected - potential short squeeze catalyst")

        # Analyze margin ratio
        margin_ratio = margin_purchase_data.get('ratio', 0)
        if margin_ratio > 40:
            reasoning.append(f"High margin ratio ({margin_ratio:.1f}%) indicates heavy leverage - increased volatility risk.")
            score -= 15
            self.risk_warnings.append(f"High margin ratio ({margin_ratio:.1f}%) increases forced selling risk during corrections")
        elif margin_ratio > 30:
            reasoning.append(f"Moderate margin ratio ({margin_ratio:.1f}%) suggests balanced leverage usage.")
        else:
            reasoning.append(f"Low margin ratio ({margin_ratio:.1f}%) indicates conservative positioning - lower volatility risk.")
            score += 5

        # Analyze chips concentration
        chips_concentration = stock_data.get('chips_concentration', {})
        concentration_score = chips_concentration.get('score', 50)

        if concentration_score > 70:
            reasoning.append("High chips concentration indicates strong hands holding - positive for stability.")
            score += 10
            self.strengths.append("Chips concentrated in strong hands - reduces selling pressure")
        elif concentration_score < 30:
            reasoning.append("Low chips concentration indicates dispersed ownership - higher volatility potential.")
            score -= 5

        analysis['margin_trading'] = {
            'margin_purchase_change': margin_purchase_change,
            'short_selling_change': short_selling_change,
            'margin_ratio': margin_ratio,
            'concentration_score': concentration_score,
            'signal': signal,
            'score': max(0, min(100, score)),
            'reasoning': reasoning
        }

        analysis['summary'] = self._generate_chips_summary(margin_purchase_change, short_selling_change, margin_ratio)

        return analysis

    def _generate_chips_summary(self, margin_change: float, short_change: float, margin_ratio: float) -> str:
        """Generate chips analysis summary."""
        if margin_change > 0 and short_change < 0:
            return "Strong bullish chips pattern: increasing margin purchase with short covering indicates strong buying momentum."
        elif margin_change < 0 and short_change > 0:
            return "Strong bearish chips pattern: decreasing margin purchase with increasing shorts indicates strong selling momentum."
        elif margin_ratio > 40:
            return f"High leverage warning: margin ratio at {margin_ratio:.1f}% increases forced selling risk during price declines."
        else:
            return "Neutral chips distribution with no clear directional bias in margin trading activity."

    def _generate_macro_analysis(self, macro_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed macro analysis focused on key economic indicators.

        Macro Analysis Components:
        - VIX (Volatility Index) - Fear gauge
        - US Dollar Index - Currency strength
        - US Treasury Yield - Interest rate outlook
        - Global market sentiment
        """
        analysis = {
            'score': macro_results.get('score', 0),
            'indicators': {}
        }

        reasoning = []
        signal = "neutral"
        score = 50

        # Analyze VIX
        vix_data = macro_results.get('vix', {})
        vix_level = vix_data.get('level', 20)
        vix_change = vix_data.get('change', 0)

        if vix_level < 15:
            reasoning.append(f"VIX at {vix_level:.2f} indicates low market fear and complacent sentiment.")
            score += 15
            signal = "bullish"
            self.strengths.append("Low VIX indicates stable market environment")
        elif vix_level > 30:
            reasoning.append(f"VIX at {vix_level:.2f} indicates elevated market fear and risk-off sentiment.")
            score -= 20
            signal = "bearish"
            self.risk_warnings.append(f"Elevated VIX ({vix_level:.2f}) indicates high market stress")
        else:
            reasoning.append(f"VIX at {vix_level:.2f} shows normal market volatility expectations.")

        if vix_change > 10:
            reasoning.append(f"VIX surged {vix_change:.2f}% - rapid increase in fear and uncertainty.")
            score -= 10
            self.risk_warnings.append("Rapidly rising VIX suggests increasing market stress")
        elif vix_change < -10:
            reasoning.append(f"VIX dropped {abs(vix_change):.2f}% - decreasing fear and improving sentiment.")
            score += 10

        # Analyze US Dollar Index
        dollar_data = macro_results.get('dollar_index', {})
        dollar_level = dollar_data.get('level', 100)
        dollar_trend = dollar_data.get('trend', 'neutral')

        if dollar_trend == 'strengthening':
            reasoning.append(f"US Dollar strengthening (level: {dollar_level:.2f}) typically pressures emerging market assets.")
            score -= 10
            if signal != "bullish":
                signal = "bearish"
            self.weaknesses.append("Strengthening US Dollar creates headwinds for Taiwan stocks")
        elif dollar_trend == 'weakening':
            reasoning.append(f"US Dollar weakening (level: {dollar_level:.2f}) typically supports emerging market assets.")
            score += 10
            if signal != "bearish":
                signal = "bullish"
            self.strengths.append("Weakening US Dollar provides tailwinds for Taiwan stocks")

        # Analyze US Treasury Yield
        treasury_data = macro_results.get('treasury_yield', {})
        yield_level = treasury_data.get('level', 4.0)
        yield_change = treasury_data.get('change', 0)

        if yield_level > 5.0:
            reasoning.append(f"10-year Treasury yield at {yield_level:.2f}% indicates tight monetary conditions.")
            score -= 15
            self.risk_warnings.append("High Treasury yields compete with equity returns")
        elif yield_level < 3.0:
            reasoning.append(f"10-year Treasury yield at {yield_level:.2f}% indicates accommodative conditions.")
            score += 10

        if yield_change > 0.2:
            reasoning.append(f"Treasury yield rising sharply (+{yield_change:.2f}%) pressures equity valuations.")
            score -= 10
        elif yield_change < -0.2:
            reasoning.append(f"Treasury yield falling sharply ({yield_change:.2f}%) supports equity valuations.")
            score += 10

        analysis['indicators'] = {
            'vix': {
                'level': vix_level,
                'change': vix_change
            },
            'dollar_index': {
                'level': dollar_level,
                'trend': dollar_trend
            },
            'treasury_yield': {
                'level': yield_level,
                'change': yield_change
            },
            'signal': signal,
            'score': max(0, min(100, score)),
            'reasoning': reasoning
        }

        analysis['summary'] = self._generate_macro_summary(vix_level, dollar_trend, yield_level)

        return analysis

    def _generate_macro_summary(self, vix: float, dollar_trend: str, yield_level: float) -> str:
        """Generate macro analysis summary."""
        conditions = []
        if vix < 15:
            conditions.append("low volatility")
        elif vix > 30:
            conditions.append("high volatility")

        if dollar_trend == 'weakening':
            conditions.append("weak dollar")
        elif dollar_trend == 'strengthening':
            conditions.append("strong dollar")

        if yield_level < 3.0:
            conditions.append("low rates")
        elif yield_level > 5.0:
            conditions.append("high rates")

        if len(conditions) > 0:
            return f"Macro environment characterized by {', '.join(conditions)}. Overall conditions are {'supportive' if vix < 20 and dollar_trend != 'strengthening' else 'challenging'} for Taiwan equities."
        else:
            return "Neutral macro environment with no extreme conditions in key indicators."

    def _generate_sentiment_analysis(self, sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed sentiment analysis from news and social media.

        Sentiment Analysis Components:
        - News sentiment score (from NewsAPI)
        - Sentiment trend over time
        - Key themes and topics
        - Sentiment consistency
        """
        analysis = {
            'score': sentiment_results.get('score', 0),
            'news_sentiment': {}
        }

        reasoning = []
        signal = "neutral"
        score = 50

        # Analyze overall sentiment score
        sentiment_score = sentiment_results.get('sentiment_score', 0)
        article_count = sentiment_results.get('article_count', 0)

        if article_count == 0:
            reasoning.append("No recent news articles found - insufficient data for sentiment analysis.")
            analysis['news_sentiment'] = {
                'sentiment_score': 0,
                'article_count': 0,
                'signal': 'neutral',
                'score': 50,
                'reasoning': reasoning
            }
            analysis['summary'] = "Insufficient news data for sentiment analysis."
            return analysis

        if sentiment_score > 0.3:
            reasoning.append(f"Positive news sentiment (score: {sentiment_score:.2f}) based on {article_count} recent articles.")
            score += 20
            signal = "bullish"
            self.strengths.append(f"Positive media coverage with sentiment score of {sentiment_score:.2f}")
        elif sentiment_score < -0.3:
            reasoning.append(f"Negative news sentiment (score: {sentiment_score:.2f}) based on {article_count} recent articles.")
            score -= 20
            signal = "bearish"
            self.weaknesses.append(f"Negative media coverage with sentiment score of {sentiment_score:.2f}")
        else:
            reasoning.append(f"Neutral news sentiment (score: {sentiment_score:.2f}) based on {article_count} recent articles.")

        # Analyze sentiment trend
        sentiment_trend = sentiment_results.get('trend', 'stable')
        if sentiment_trend == 'improving':
            reasoning.append("News sentiment is improving over time - positive momentum in public perception.")
            score += 10
            if signal != "bearish":
                signal = "bullish"
        elif sentiment_trend == 'deteriorating':
            reasoning.append("News sentiment is deteriorating over time - negative momentum in public perception.")
            score -= 10
            if signal != "bullish":
                signal = "bearish"

        # Analyze sentiment consistency
        sentiment_variance = sentiment_results.get('variance', 0)
        if sentiment_variance < 0.2:
            reasoning.append("High sentiment consistency across news sources indicates clear market consensus.")
        else:
            reasoning.append("Mixed sentiment across news sources indicates divided market opinion.")
            self.risk_warnings.append("Divided news sentiment suggests unclear market narrative")

        # Analyze key themes
        key_themes = sentiment_results.get('key_themes', [])
        if key_themes:
            themes_str = ", ".join(key_themes[:3])
            reasoning.append(f"Key news themes: {themes_str}")

        analysis['news_sentiment'] = {
            'sentiment_score': sentiment_score,
            'article_count': article_count,
            'trend': sentiment_trend,
            'key_themes': key_themes,
            'signal': signal,
            'score': max(0, min(100, score)),
            'reasoning': reasoning
        }

        analysis['summary'] = self._generate_sentiment_summary(sentiment_score, article_count, sentiment_trend)

        return analysis

    def _generate_sentiment_summary(self, sentiment_score: float, article_count: int, trend: str) -> str:
        """Generate sentiment analysis summary."""
        if article_count == 0:
            return "No recent news coverage found for sentiment analysis."

        sentiment_desc = "positive" if sentiment_score > 0.3 else "negative" if sentiment_score < -0.3 else "neutral"
        trend_desc = f" and {trend}" if trend != 'stable' else ""

        return f"Based on {article_count} recent articles, news sentiment is {sentiment_desc} (score: {sentiment_score:.2f}){trend_desc}. Media coverage provides {sentiment_desc} narrative for the stock."

    def _calculate_overall_score(self, analysis_results: Dict[str, Any]) -> float:
        """
        Calculate weighted overall score from all dimensions.

        Score = (Technical * 0.30) + (Market * 0.20) + (Chips * 0.20) +
                (Macro * 0.15) + (Sentiment * 0.15)
        """
        technical_score = analysis_results.get('technical', {}).get('score', 0)
        market_score = analysis_results.get('market', {}).get('score', 0)
        chips_score = analysis_results.get('chips', {}).get('score', 0)
        macro_score = analysis_results.get('macro', {}).get('score', 0)
        sentiment_score = analysis_results.get('sentiment', {}).get('score', 0)

        overall_score = (
            technical_score * self.weights['technical'] +
            market_score * self.weights['market'] +
            chips_score * self.weights['chips'] +
            macro_score * self.weights['macro'] +
            sentiment_score * self.weights['sentiment']
        )

        return round(overall_score, 2)

    def _generate_recommendation(self, overall_score: float,
                                 analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate investment recommendation based on overall score and analysis.

        Score Ranges:
        - 75-100: Strong Buy
        - 60-74: Buy
        - 45-59: Hold
        - 30-44: Sell
        - 0-29: Strong Sell
        """
        if overall_score >= 75:
            action = "Strong Buy"
            confidence = "High"
            reasoning = "Multiple dimensions show strong bullish signals with minimal downside risks."
        elif overall_score >= 60:
            action = "Buy"
            confidence = "Moderate"
            reasoning = "Majority of indicators show bullish signals, suggesting favorable risk/reward."
        elif overall_score >= 45:
            action = "Hold"
            confidence = "Low"
            reasoning = "Mixed signals across dimensions suggest waiting for clearer direction."
        elif overall_score >= 30:
            action = "Sell"
            confidence = "Moderate"
            reasoning = "Majority of indicators show bearish signals, suggesting unfavorable risk/reward."
        else:
            action = "Strong Sell"
            confidence = "High"
            reasoning = "Multiple dimensions show strong bearish signals with significant downside risks."

        return {
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'score': overall_score
        }

    def format_report_as_text(self, report: Dict[str, Any]) -> str:
        """
        Format the comprehensive report as readable text.

        Args:
            report: Dictionary containing comprehensive analysis report

        Returns:
            Formatted text report
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"TAIWAN STOCK PREDICTION SYSTEM - DETAILED ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Stock Code: {report['stock_code']}")
        lines.append(f"Analysis Date: {report['analysis_date']}")
        lines.append(f"Overall Score: {report['overall_score']:.2f}/100")
        lines.append("")

        # Recommendation
        rec = report['recommendation']
        lines.append("-" * 80)
        lines.append(f"INVESTMENT RECOMMENDATION: {rec['action']}")
        lines.append(f"Confidence Level: {rec['confidence']}")
        lines.append(f"Reasoning: {rec['reasoning']}")
        lines.append("-" * 80)
        lines.append("")

        # Dimension scores
        lines.append("FIVE-DIMENSIONAL ANALYSIS SCORES:")
        scores = report['dimension_scores']
        lines.append(f"  1. Technical Analysis:    {scores['technical']:.2f}/100 (Weight: 30%)")
        lines.append(f"  2. Market Analysis:       {scores['market']:.2f}/100 (Weight: 20%)")
        lines.append(f"  3. Chips Analysis:        {scores['chips']:.2f}/100 (Weight: 20%)")
        lines.append(f"  4. Macro Analysis:        {scores['macro']:.2f}/100 (Weight: 15%)")
        lines.append(f"  5. Sentiment Analysis:    {scores['sentiment']:.2f}/100 (Weight: 15%)")
        lines.append("")

        # Detailed analysis sections
        detailed = report['detailed_analysis']

        # Technical Analysis
        lines.append("=" * 80)
        lines.append("1. TECHNICAL ANALYSIS")
        lines.append("=" * 80)
        tech = detailed['technical']
        for indicator_name, indicator_data in tech['indicators'].items():
            lines.append(f"\n{indicator_name.upper().replace('_', ' ')}:")
            lines.append(f"  Signal: {indicator_data['signal'].upper()}")
            lines.append(f"  Score: {indicator_data['score']:.2f}/100")
            lines.append("  Reasoning:")
            for reason in indicator_data['reasoning']:
                lines.append(f"    - {reason}")
        lines.append(f"\nSummary: {tech['summary']}")
        lines.append("")

        # Market Analysis
        lines.append("=" * 80)
        lines.append("2. MARKET ANALYSIS (Institutional Investors)")
        lines.append("=" * 80)
        market = detailed['market']
        inst = market['institutional_activity']
        lines.append(f"Signal: {inst['signal'].upper()}")
        lines.append(f"Score: {inst['score']:.2f}/100")
        lines.append("Reasoning:")
        for reason in inst['reasoning']:
            lines.append(f"  - {reason}")
        lines.append(f"\nSummary: {market['summary']}")
        lines.append("")

        # Chips Analysis
        lines.append("=" * 80)
        lines.append("3. CHIPS ANALYSIS (Margin Trading)")
        lines.append("=" * 80)
        chips = detailed['chips']
        margin = chips['margin_trading']
        lines.append(f"Signal: {margin['signal'].upper()}")
        lines.append(f"Score: {margin['score']:.2f}/100")
        lines.append("Reasoning:")
        for reason in margin['reasoning']:
            lines.append(f"  - {reason}")
        lines.append(f"\nSummary: {chips['summary']}")
        lines.append("")

        # Macro Analysis
        lines.append("=" * 80)
        lines.append("4. MACRO ANALYSIS")
        lines.append("=" * 80)
        macro = detailed['macro']
        indicators = macro['indicators']
        lines.append(f"Signal: {indicators['signal'].upper()}")
        lines.append(f"Score: {indicators['score']:.2f}/100")
        lines.append("Reasoning:")
        for reason in indicators['reasoning']:
            lines.append(f"  - {reason}")
        lines.append(f"\nSummary: {macro['summary']}")
        lines.append("")

        # Sentiment Analysis
        lines.append("=" * 80)
        lines.append("5. SENTIMENT ANALYSIS")
        lines.append("=" * 80)
        sentiment = detailed['sentiment']
        news = sentiment['news_sentiment']
        lines.append(f"Signal: {news['signal'].upper()}")
        lines.append(f"Score: {news['score']:.2f}/100")
        lines.append("Reasoning:")
        for reason in news['reasoning']:
            lines.append(f"  - {reason}")
        lines.append(f"\nSummary: {sentiment['summary']}")
        lines.append("")

        # Strengths, Weaknesses, Risks
        lines.append("=" * 80)
        lines.append("INVESTMENT CONSIDERATIONS")
        lines.append("=" * 80)

        if report['strengths']:
            lines.append("\nSTRENGTHS:")
            for i, strength in enumerate(report['strengths'], 1):
                lines.append(f"  {i}. {strength}")

        if report['weaknesses']:
            lines.append("\nWEAKNESSES:")
            for i, weakness in enumerate(report['weaknesses'], 1):
                lines.append(f"  {i}. {weakness}")

        if report['risk_warnings']:
            lines.append("\nRISK WARNINGS:")
            for i, risk in enumerate(report['risk_warnings'], 1):
                lines.append(f"  {i}. {risk}")

        lines.append("")
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)

        return "\n".join(lines)

    def save_report_to_file(self, report: Dict[str, Any], filename: str) -> None:
        """
        Save the detailed report to a file.

        Args:
            report: Dictionary containing comprehensive analysis report
            filename: Path to save the report
        """
        # Save as JSON
        json_filename = filename.replace('.txt', '.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # Save as formatted text
        text_report = self.format_report_as_text(report)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_report)


# Example usage function
def example_usage():
    """Example of how to use the DetailedAnalysisReporter."""

    # Sample data structure (would come from actual analysis)
    sample_stock_data = {
        'kd': {'k': 75.5, 'd': 68.2},
        'obv': {'current': 15000000, 'trend': 'rising', 'change_pct': 5.2},
        'price': {'current': 585.0, 'trend': 'rising'},
        'moving_averages': {'ma5': 580, 'ma10': 575, 'ma20': 570, 'ma60': 560},
        'rsi': {'current': 65.5, 'trend': 'rising'},
        'macd': {'macd': 2.5, 'signal': 1.8, 'histogram': 0.7},
        'foreign_investors': {'net_buy': 1500000, 'trend': 'buying'},
        'investment_trust': {'net_buy': 500000},
        'dealer_proprietary': {'net_buy': 200000},
        'margin_purchase': {'change': 800000, 'balance': 5000000, 'ratio': 35.5},
        'short_selling': {'change': -150000, 'balance': 500000},
        'chips_concentration': {'score': 75}
    }

    sample_analysis_results = {
        'technical': {'score': 72},
        'market': {'score': 68},
        'chips': {'score': 65},
        'macro': {
            'score': 58,
            'vix': {'level': 18.5, 'change': -2.5},
            'dollar_index': {'level': 103.5, 'trend': 'weakening'},
            'treasury_yield': {'level': 4.2, 'change': -0.1}
        },
        'sentiment': {
            'score': 70,
            'sentiment_score': 0.45,
            'article_count': 25,
            'trend': 'improving',
            'variance': 0.15,
            'key_themes': ['Strong earnings', 'AI growth', 'Market leadership']
        }
    }

    # Create reporter and generate report
    reporter = DetailedAnalysisReporter()
    report = reporter.generate_comprehensive_report('2330', sample_stock_data, sample_analysis_results)

    # Print formatted report
    text_report = reporter.format_report_as_text(report)
    print(text_report)

    # Save to file
    reporter.save_report_to_file(report, 'analysis_report_2330.txt')


if __name__ == '__main__':
    example_usage()
