"""
音楽ニュースAI - ニュース評価・選別モジュール
ニュースを評価し、音楽化に適しているかを判定する
"""

import logging
from typing import Dict, Any

from .config import Config

logger = logging.getLogger(__name__)


class NewsEvaluator:
    """ニュース評価クラス"""
    
    def __init__(self):
        self.config = Config()
    
    def evaluate(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """
        ニュースを評価する
        
        Args:
            news: ニュースデータ
            
        Returns:
            評価結果
        """
        logger.info("📊 ニュースの評価を開始します")
        
        # 各項目を評価
        social_importance = self._evaluate_social_importance(news)
        youth_relevance = self._evaluate_youth_relevance(news)
        information_certainty = self._evaluate_information_certainty(news)
        sensationalism = self._evaluate_sensationalism(news)
        
        # 重み付けして総合スコアを計算
        weights = self.config.EVALUATION_WEIGHTS
        total_score = (
            social_importance * weights["social_importance"] +
            youth_relevance * weights["youth_relevance"] +
            information_certainty * weights["information_certainty"] +
            (100 - sensationalism) * weights["sensationalism"]  # センセーショナル度は低いほど良い
        )
        
        is_suitable = total_score >= self.config.MIN_SCORE_THRESHOLD
        
        result = {
            "is_suitable": is_suitable,
            "total_score": round(total_score, 2),
            "scores": {
                "social_importance": social_importance,
                "youth_relevance": youth_relevance,
                "information_certainty": information_certainty,
                "sensationalism": sensationalism,
            },
            "reason": self._generate_reason(is_suitable, total_score, {
                "social_importance": social_importance,
                "youth_relevance": youth_relevance,
                "information_certainty": information_certainty,
                "sensationalism": sensationalism,
            })
        }
        
        if is_suitable:
            logger.info(f"✅ このニュースは音楽化に適しています (スコア: {total_score:.2f})")
        else:
            logger.warning(f"⚠️ このニュースは音楽化に適していません (スコア: {total_score:.2f})")
        
        return result
    
    def _evaluate_social_importance(self, news: Dict[str, Any]) -> float:
        """
        社会的重要度を評価する（モック実装）
        
        実際のAPI実装では、ニュースの内容を分析して評価する
        """
        # モック実装：政府発表、環境、エネルギーなどは重要度が高い
        content = news.get("content", "").lower()
        title = news.get("title", "").lower()
        
        score = 50  # ベーススコア
        
        # キーワードベースの簡易評価
        important_keywords = [
            "政府", "発表", "法律", "制度", "政策",
            "環境", "エネルギー", "気候", "経済",
            "教育", "医療", "福祉", "雇用"
        ]
        
        for keyword in important_keywords:
            if keyword in content or keyword in title:
                score += 10
        
        return min(score, 100)
    
    def _evaluate_youth_relevance(self, news: Dict[str, Any]) -> float:
        """
        若年層への関連性を評価する（モック実装）
        """
        content = news.get("content", "").lower()
        title = news.get("title", "").lower()
        
        score = 50  # ベーススコア
        
        # 若年層に関連するキーワード
        youth_keywords = [
            "学生", "若者", "就職", "雇用", "教育",
            "未来", "世代", "子ども", "学校",
            "環境", "気候", "ネット", "デジタル"
        ]
        
        for keyword in youth_keywords:
            if keyword in content or keyword in title:
                score += 8
        
        return min(score, 100)
    
    def _evaluate_information_certainty(self, news: Dict[str, Any]) -> float:
        """
        情報の確実性を評価する（モック実装）
        """
        source = news.get("source", "").lower()
        content = news.get("content", "").lower()
        
        score = 50  # ベーススコア
        
        # 信頼できる情報源
        reliable_sources = [
            "公式発表", "政府", "省庁", "官邸",
            "発表した", "発表される", "公表"
        ]
        
        for keyword in reliable_sources:
            if keyword in source or keyword in content:
                score += 15
        
        # 不確定な表現があるとスコアダウン
        uncertain_expressions = [
            "噂", "〜らしい", "憶測", "未確認",
            "情報筋", "関係者によると"
        ]
        
        for expression in uncertain_expressions:
            if expression in content:
                score -= 20
        
        return max(min(score, 100), 0)
    
    def _evaluate_sensationalism(self, news: Dict[str, Any]) -> float:
        """
        センセーショナル度を評価する（低いほど良い）（モック実装）
        """
        content = news.get("content", "").lower()
        title = news.get("title", "").lower()
        
        score = 20  # ベーススコア（低めに設定）
        
        # センセーショナルな表現
        sensational_expressions = [
            "衝撃", "ヤバい", "終わった", "最悪",
            "大炎上", "批判殺到", "緊急", "速報",
            "!!!!", "!?", "まさか"
        ]
        
        for expression in sensational_expressions:
            if expression in content or expression in title:
                score += 20
        
        return min(score, 100)
    
    def _generate_reason(self, is_suitable: bool, total_score: float, scores: Dict[str, float]) -> str:
        """
        評価理由を生成する
        """
        if is_suitable:
            reasons = []
            if scores["social_importance"] >= 70:
                reasons.append("社会的影響が大きい")
            if scores["youth_relevance"] >= 70:
                reasons.append("若い世代に関連がある")
            if scores["information_certainty"] >= 70:
                reasons.append("情報の信頼性が高い")
            if scores["sensationalism"] <= 40:
                reasons.append("冷静な報道")
            
            if reasons:
                return "、".join(reasons) + "ため、音楽化に適しています"
            else:
                return "総合的に音楽化に適しています"
        else:
            reasons = []
            if scores["social_importance"] < 70:
                reasons.append("社会的影響が限定的")
            if scores["youth_relevance"] < 70:
                reasons.append("若い世代への関連性が低い")
            if scores["information_certainty"] < 70:
                reasons.append("情報の確実性に懸念")
            if scores["sensationalism"] > 60:
                reasons.append("センセーショナルな表現が多い")
            
            if reasons:
                return "、".join(reasons) + "ため、音楽化には適していません"
            else:
                return "総合スコアが閾値を下回っているため、音楽化には適していません"


# 便利関数
def evaluate_news(news: Dict[str, Any]) -> Dict[str, Any]:
    """
    ニュースを評価する（便利関数）
    
    Args:
        news: ニュースデータ
        
    Returns:
        評価結果
    """
    evaluator = NewsEvaluator()
    return evaluator.evaluate(news)
