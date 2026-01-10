"""
音楽ニュースAI - 設定ファイル
キャラクター設定、パス設定、評価基準などを一元管理
"""

import os
from pathlib import Path


class Config:
    """プロジェクト全体の設定"""
    
    # プロジェクトルートディレクトリ
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # ディレクトリパス
    INPUT_DIR = PROJECT_ROOT / "input"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    
    # ===== キャラクター設定 =====
    CHARACTER_NAME = "あいり"
    CHARACTER_AGE = 16
    CHARACTER_PERSONA = "妹アイドル"
    
    # ===== ニュース評価設定 =====
    # スコアがこの閾値以上なら音楽化に適している
    MIN_SCORE_THRESHOLD = 70
    
    # 評価項目の重み
    EVALUATION_WEIGHTS = {
        "social_importance": 0.3,    # 社会的重要度
        "youth_relevance": 0.25,     # 若年層への関連性
        "information_certainty": 0.25,  # 情報の確実性
        "sensationalism": 0.2,       # センセーショナル度（低いほど良い）
    }
    
    # ===== 歌詞生成設定 =====
    MAX_LYRICS_LINES = 50  # 最大行数
    MIN_LYRICS_LINES = 25  # 最小行数
    
    # セクション別の行数の目安
    SECTION_LENGTHS = {
        "intro": (0, 2),
        "verse": (4, 8),
        "pre_chorus": (4, 6),
        "chorus": (6, 8),
        "bridge": (4, 6),
        "outro": (0, 2),
    }
    
    # 禁止表現リスト
    FORBIDDEN_EXPRESSIONS = [
        "ヤバい", "終わった", "最悪",
        "絶対", "間違いなく", "確実に",
        "すべき", "しなければならない",
    ]
    
    # 推奨表現リスト
    RECOMMENDED_EXPRESSIONS = [
        "かもしれない", "だと思うの", "一緒に考えよう",
        "どうしたらいいんだろう", "きっと", "もしかしたら",
    ]
    
    # ===== ログ設定 =====
    LOG_LEVEL = "INFO"
    
    @classmethod
    def ensure_directories(cls):
        """必要なディレクトリを作成する"""
        cls.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
