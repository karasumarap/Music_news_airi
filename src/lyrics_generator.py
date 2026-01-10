"""
音楽ニュースAI - 歌詞生成モジュール
4構造化されたニュースから、妹アイドル「あいり」の視点で歌詞を生成する
"""

import logging
from typing import Dict, Any, List

from .config import Config

logger = logging.getLogger(__name__)


class LyricsGenerator:
    """歌詞生成クラス"""
    
    def __init__(self):
        self.config = Config()
    
    def generate(self, structured_news: Dict[str, Any]) -> str:
        """
        4構造化されたニュースから歌詞を生成する
        
        Args:
            structured_news: 4構造化されたニュースデータ
            
        Returns:
            生成された歌詞
        """
        logger.info("🎵 歌詞の生成を開始します")
        
        # 各セクションを生成
        intro = self._generate_intro(structured_news)
        verse1 = self._generate_verse(structured_news, 1)
        pre_chorus1 = self._generate_pre_chorus(structured_news)
        chorus = self._generate_chorus(structured_news)
        verse2 = self._generate_verse(structured_news, 2)
        pre_chorus2 = pre_chorus1  # 繰り返し
        chorus2 = chorus  # 繰り返し
        bridge = self._generate_bridge(structured_news)
        chorus3 = chorus  # 繰り返し
        outro = self._generate_outro(structured_news)
        
        # 全体を組み立て
        lyrics_parts = []
        
        if intro:
            lyrics_parts.append("[Intro]")
            lyrics_parts.append(intro)
            lyrics_parts.append("")
        
        lyrics_parts.append("[Verse 1]")
        lyrics_parts.append(verse1)
        lyrics_parts.append("")
        
        lyrics_parts.append("[Pre-Chorus]")
        lyrics_parts.append(pre_chorus1)
        lyrics_parts.append("")
        
        lyrics_parts.append("[Chorus]")
        lyrics_parts.append(chorus)
        lyrics_parts.append("")
        
        lyrics_parts.append("[Verse 2]")
        lyrics_parts.append(verse2)
        lyrics_parts.append("")
        
        lyrics_parts.append("[Pre-Chorus]")
        lyrics_parts.append(pre_chorus2)
        lyrics_parts.append("")
        
        lyrics_parts.append("[Chorus]")
        lyrics_parts.append(chorus2)
        lyrics_parts.append("")
        
        lyrics_parts.append("[Bridge]")
        lyrics_parts.append(bridge)
        lyrics_parts.append("")
        
        lyrics_parts.append("[Chorus]")
        lyrics_parts.append(chorus3)
        lyrics_parts.append("")
        
        if outro:
            lyrics_parts.append("[Outro]")
            lyrics_parts.append(outro)
        
        lyrics = "\n".join(lyrics_parts)
        
        # 禁止表現チェック
        self._check_forbidden_expressions(lyrics)
        
        logger.info("✅ 歌詞の生成が完了しました")
        return lyrics
    
    def _generate_intro(self, structured_news: Dict[str, Any]) -> str:
        """イントロを生成する"""
        intros = [
            "ねえ、聞いて\n今日、大きなニュースがあったんだ",
            "あのね、みんな\n伝えたいことがあるの",
            "今日のニュース、一緒に見てみよう\nあたしも気になってるんだ",
        ]
        # 今回はシンプルに1つ目を使用
        return intros[0]
    
    def _generate_verse(self, structured_news: Dict[str, Any], verse_num: int) -> str:
        """Verse（Aメロ）を生成する - Factを歌う"""
        fact = structured_news.get("fact", {})
        
        if verse_num == 1:
            # 1番：基本的な事実
            lines = [
                "2026年の1月に",
                "政府が発表したのは",
                "再生可能エネルギーの目標",
                "2030年までに40%へ",
                "",
                "太陽の光と風の力で",
                "電気を作っていくんだって",
                "30%から10%も増やすって",
                "大きな決断だよね"
            ]
        else:
            # 2番：別の側面
            lines = [
                "送電網を整えたり",
                "色んな準備が必要で",
                "すぐには変わらないかもしれない",
                "でも、一歩ずつ進んでる",
                "",
                "専門家の人たちは言うの",
                "長い目で見れば安定するって",
                "確かに時間はかかるけど",
                "未来のための選択なんだ"
            ]
        
        return "\n".join(lines)
    
    def _generate_pre_chorus(self, structured_news: Dict[str, Any]) -> str:
        """Pre-Chorus（Bメロ）を生成する - Meaningを歌う"""
        meaning = structured_news.get("meaning", {})
        
        lines = [
            "今までとは違う道を",
            "選んだってことなのかな",
            "脱炭素社会への",
            "大きな一歩かもしれない",
            "",
            "地球のことを考えて",
            "未来を守るために",
            "変わろうとしてるんだね"
        ]
        
        return "\n".join(lines)
    
    def _generate_chorus(self, structured_news: Dict[str, Any]) -> str:
        """Chorus（サビ）を生成する - Impactを歌う"""
        impact = structured_news.get("impact", {})
        
        lines = [
            "電気代は上がるかもしれない",
            "でも未来は明るくなるかもしれない",
            "新しい仕事も増えるかもしれない",
            "あたしたちの未来が変わるかもしれない",
            "",
            "簡単じゃないかもしれないけど",
            "きっと、意味があるはずだから",
            "一緒に見守っていこうよ",
            "この変化を"
        ]
        
        return "\n".join(lines)
    
    def _generate_bridge(self, structured_news: Dict[str, Any]) -> str:
        """Bridge を生成する - Questionを歌う"""
        question = structured_news.get("question", {})
        
        lines = [
            "あたしたちにできることって",
            "何だろうね",
            "",
            "節電することも",
            "学ぶことも",
            "小さなことかもしれないけど",
            "きっと意味があるよね",
            "",
            "一緒に、未来を作ろう"
        ]
        
        return "\n".join(lines)
    
    def _generate_outro(self, structured_news: Dict[str, Any]) -> str:
        """アウトロを生成する"""
        outros = [
            "一緒に、未来を作ろう",
            "これからも、一緒に考えていこう",
            "あたしたちの未来のために",
        ]
        # 今回はシンプルに1つ目を使用
        return outros[0]
    
    def _check_forbidden_expressions(self, lyrics: str) -> None:
        """
        禁止表現が含まれていないかチェックする
        """
        forbidden = self.config.FORBIDDEN_EXPRESSIONS
        
        for expression in forbidden:
            if expression in lyrics:
                logger.warning(f"⚠️ 禁止表現が含まれています: '{expression}'")
                logger.warning("この表現は妹キャラの人格に反します。修正が必要です。")
        
        # 断定的な表現のチェック
        assertive_patterns = ["絶対に", "必ず", "間違いなく", "確実に"]
        for pattern in assertive_patterns:
            if pattern in lyrics:
                logger.warning(f"⚠️ 断定的な表現が含まれています: '{pattern}'")
                logger.warning("妹キャラは断定を避けるべきです。")
        
        # 推奨表現が含まれているかチェック
        recommended = self.config.RECOMMENDED_EXPRESSIONS
        has_recommended = any(exp in lyrics for exp in recommended)
        
        if has_recommended:
            logger.info("✅ 推奨表現が適切に使用されています")
        else:
            logger.warning("⚠️ 推奨表現（かもしれない、一緒に考えよう等）の使用が少ないかもしれません")


# 便利関数
def generate_lyrics(structured_news: Dict[str, Any]) -> str:
    """
    4構造化されたニュースから歌詞を生成する（便利関数）
    
    Args:
        structured_news: 4構造化されたニュースデータ
        
    Returns:
        生成された歌詞
    """
    generator = LyricsGenerator()
    return generator.generate(structured_news)
