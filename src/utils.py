"""
音楽ニュースAI - ユーティリティ
共通で使用する関数群
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict
from datetime import datetime


# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_json(file_path: str | Path) -> Dict[str, Any]:
    """
    JSONファイルを読み込む
    
    Args:
        file_path: ファイルパス
        
    Returns:
        読み込んだデータ
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ JSONファイルを読み込みました: {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"❌ ファイルが見つかりません: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON解析エラー: {e}")
        raise


def save_json(file_path: str | Path, data: Dict[str, Any], indent: int = 2) -> None:
    """
    データをJSONファイルとして保存する
    
    Args:
        file_path: 保存先のファイルパス
        data: 保存するデータ
        indent: インデント幅
    """
    try:
        # ディレクトリがなければ作成
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        logger.info(f"✅ JSONファイルを保存しました: {file_path}")
    except Exception as e:
        logger.error(f"❌ ファイル保存エラー: {e}")
        raise


def load_text(file_path: str | Path) -> str:
    """
    テキストファイルを読み込む
    
    Args:
        file_path: ファイルパス
        
    Returns:
        読み込んだテキスト
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        logger.info(f"✅ テキストファイルを読み込みました: {file_path}")
        return text
    except FileNotFoundError:
        logger.error(f"❌ ファイルが見つかりません: {file_path}")
        raise


def save_text(file_path: str | Path, text: str) -> None:
    """
    テキストをファイルとして保存する
    
    Args:
        file_path: 保存先のファイルパス
        text: 保存するテキスト
    """
    try:
        # ディレクトリがなければ作成
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.info(f"✅ テキストファイルを保存しました: {file_path}")
    except Exception as e:
        logger.error(f"❌ ファイル保存エラー: {e}")
        raise


def get_timestamp() -> str:
    """
    現在のタイムスタンプを取得する
    
    Returns:
        ISO形式のタイムスタンプ
    """
    return datetime.now().isoformat()


def validate_news_data(news: Dict[str, Any]) -> bool:
    """
    ニュースデータの形式を検証する
    
    Args:
        news: ニュースデータ
        
    Returns:
        有効ならTrue、無効ならFalse
    """
    required_keys = ["title", "content", "source", "date"]
    
    for key in required_keys:
        if key not in news:
            logger.error(f"❌ 必須キー '{key}' がありません")
            return False
    
    if not news["title"] or not news["content"]:
        logger.error("❌ タイトルまたは本文が空です")
        return False
    
    return True
