"""
音楽ニュースAI - 音楽プロンプト生成モジュール
構造化されたニュースから、Suno AI用の音楽スタイルプロンプトを生成する
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MusicPromptGenerator:
    """音楽プロンプト生成クラス"""
    
    def generate_prompt(self, structured_news: Dict[str, Any], lyrics: str) -> str:
        """
        音楽スタイルのプロンプトを生成する
        
        Args:
            structured_news: 構造化されたニュース
            lyrics: 歌詞
            
        Returns:
            Suno AI用のプロンプト
        """
        logger.info("🎨 音楽スタイルのプロンプトを生成します")
        
        # ニュースのトーンを分析
        tone = self._analyze_tone(structured_news)
        
        # 基本スタイル
        base_style = "J-Pop, Female Vocal, Idol"
        
        # トーンに応じた追加要素
        if tone == "positive":
            mood = "uplifting, bright, hopeful"
            tempo = "upbeat"
        elif tone == "negative":
            mood = "reflective, emotional, gentle"
            tempo = "mid-tempo"
        else:  # neutral/complex
            mood = "thoughtful, balanced, sincere"
            tempo = "moderate"
        
        # プロンプトを組み立て
        prompt = f"{base_style}, {mood}, {tempo}, clear vocals, emotional delivery"
        
        logger.info(f"✅ プロンプト: {prompt}")
        
        return prompt
    
    def _analyze_tone(self, structured_news: Dict[str, Any]) -> str:
        """
        ニュースのトーンを分析する
        
        Returns:
            "positive", "negative", "neutral"のいずれか
        """
        impact = structured_news.get("impact", {})
        
        positive_count = len(impact.get("positive", []))
        negative_count = len(impact.get("negative", []))
        
        if positive_count > negative_count + 1:
            return "positive"
        elif negative_count > positive_count + 1:
            return "negative"
        else:
            return "neutral"
    
    def generate_title(self, structured_news: Dict[str, Any]) -> str:
        """
        曲のタイトルを生成する
        
        Args:
            structured_news: 構造化されたニュース
            
        Returns:
            曲のタイトル
        """
        original = structured_news.get("original_news", {})
        title = original.get("title", "未来のニュース")
        
        # タイトルが長すぎる場合は短縮
        if len(title) > 30:
            # キーワードを抽出して短いタイトルを作成
            fact = structured_news.get("fact", {})
            summary = fact.get("summary", title)
            
            # 簡易的に最初の文を使用
            short_title = summary.split("。")[0]
            if len(short_title) > 30:
                short_title = short_title[:27] + "..."
            
            return short_title
        
        return title


# 便利関数
def generate_music_prompt(structured_news: Dict[str, Any], lyrics: str) -> str:
    """
    音楽プロンプトを生成する（便利関数）
    
    Args:
        structured_news: 構造化されたニュース
        lyrics: 歌詞
        
    Returns:
        音楽プロンプト
    """
    generator = MusicPromptGenerator()
    return generator.generate_prompt(structured_news, lyrics)


def generate_music_title(structured_news: Dict[str, Any]) -> str:
    """
    曲のタイトルを生成する（便利関数）
    
    Args:
        structured_news: 構造化されたニュース
        
    Returns:
        曲のタイトル
    """
    generator = MusicPromptGenerator()
    return generator.generate_title(structured_news)
