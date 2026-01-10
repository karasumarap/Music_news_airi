"""
音楽ニュースAI - プロンプト生成モジュール
Suno AI用の音楽生成プロンプトを構築する
"""

import logging
from typing import Dict, Any

from .config import Config

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Suno AI用プロンプトを生成するクラス"""
    
    def __init__(self):
        self.config = Config()
    
    def build_prompt(self, structured_news: Dict[str, Any], lyrics: str) -> Dict[str, Any]:
        """
        構造化ニュースと歌詞から、Suno AI用のプロンプトを生成する
        
        Args:
            structured_news: 4構造化されたニュースデータ
            lyrics: 生成された歌詞
            
        Returns:
            Suno APIリクエスト用のパラメータ
        """
        logger.info("🎹 Suno AI用プロンプトを生成します")
        
        # ニュースのトーンを判定
        tone = self._determine_tone(structured_news)
        
        # 音楽スタイルを決定
        style = self._determine_style(structured_news, tone)
        
        # メタデータを生成
        title = self._generate_title(structured_news)
        
        # Suno API用のパラメータを構築
        prompt_params = {
            "title": title,
            "lyrics": lyrics,
            "style": style,
            "instrumental": False,  # 歌詞あり
            "model": "chirp-v3-5",  # 最新モデル
            "wait_audio": True,     # 音楽生成完了まで待機
        }
        
        logger.info(f"✅ スタイル: {style}")
        logger.info(f"✅ タイトル: {title}")
        
        return prompt_params
    
    def _determine_tone(self, structured_news: Dict[str, Any]) -> str:
        """
        ニュースのトーン（感情的な雰囲気）を判定する
        
        Returns:
            "positive", "negative", "neutral", "hopeful"
        """
        impact = structured_news.get("impact", {})
        positive = impact.get("positive", [])
        negative = impact.get("negative", [])
        
        # ポジティブとネガティブのバランスで判定
        if len(positive) > len(negative):
            return "hopeful"  # 希望的
        elif len(negative) > len(positive):
            return "hopeful"  # ネガティブでも希望を残す（妹キャラの特性）
        else:
            return "hopeful"  # デフォルトは希望的
    
    def _determine_style(self, structured_news: Dict[str, Any], tone: str) -> str:
        """
        ニュースの内容とトーンから音楽スタイルを決定する
        
        Args:
            structured_news: 構造化ニュース
            tone: トーン
            
        Returns:
            Suno AI用のスタイル記述
        """
        # 基本スタイル: J-Pop、女性ボーカル、妹キャラ
        base_style = "J-Pop, female vocals, kawaii, idol"
        
        # トーンに応じてスタイルを調整
        if tone == "hopeful":
            mood_style = "uplifting, hopeful, bright, energetic"
        elif tone == "positive":
            mood_style = "cheerful, happy, optimistic, bright"
        elif tone == "negative":
            mood_style = "emotional, thoughtful, gentle, supportive"
        else:
            mood_style = "balanced, thoughtful, moderate tempo"
        
        # カテゴリ別の追加要素
        category = structured_news.get("original_news", {}).get("category", "")
        
        if "環境" in category or "エネルギー" in category:
            theme_style = "futuristic, electronic elements"
        elif "経済" in category:
            theme_style = "dynamic, rhythmic"
        elif "教育" in category:
            theme_style = "inspiring, warm"
        elif "技術" in category:
            theme_style = "modern, tech-inspired"
        else:
            theme_style = "contemporary"
        
        # 全体を組み合わせ
        full_style = f"{base_style}, {mood_style}, {theme_style}"
        
        return full_style
    
    def _generate_title(self, structured_news: Dict[str, Any]) -> str:
        """
        楽曲タイトルを生成する
        
        Args:
            structured_news: 構造化ニュース
            
        Returns:
            楽曲タイトル
        """
        original_title = structured_news.get("original_news", {}).get("title", "")
        date = structured_news.get("original_news", {}).get("date", "")
        
        # 短いタイトルに変換
        # 例: "日本政府、再生可能エネルギー目標を40%に引き上げ" 
        #  -> "再生可能エネルギー40%へ"
        
        if "再生可能エネルギー" in original_title and "40%" in original_title:
            short_title = "再生可能エネルギー40%へ"
        else:
            # 一般的な短縮（最初の20文字）
            short_title = original_title[:20]
            if len(original_title) > 20:
                short_title += "..."
        
        # 日付を追加
        if date:
            title = f"{short_title} ({date})"
        else:
            title = short_title
        
        return title


# 便利関数
def build_music_prompt(structured_news: Dict[str, Any], lyrics: str) -> Dict[str, Any]:
    """
    Suno AI用プロンプトを生成する（便利関数）
    
    Args:
        structured_news: 4構造化されたニュースデータ
        lyrics: 生成された歌詞
        
    Returns:
        Suno APIリクエスト用のパラメータ
    """
    builder = PromptBuilder()
    return builder.build_prompt(structured_news, lyrics)
