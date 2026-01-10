"""
音楽ニュースAI - 音楽生成モジュール
Suno AIと連携して音楽を生成する
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logging.warning("⚠️ requests または python-dotenv がインストールされていません")

from .config import Config
from .prompt_builder import build_music_prompt

logger = logging.getLogger(__name__)


class MusicGenerator:
    """Suno AIを使って音楽を生成するクラス"""
    
    def __init__(self):
        self.config = Config()
        
        # 環境変数を読み込む
        load_dotenv() if DEPENDENCIES_AVAILABLE else None
        
        self.api_key = os.getenv("SUNO_API_KEY", "")
        self.enabled = os.getenv("MUSIC_GENERATION_ENABLED", "false").lower() == "true"
        self.model = os.getenv("SUNO_MODEL", "chirp-v3-5")
        
        # Suno API エンドポイント（非公式）
        # 注: Suno AIは公式APIを提供していない場合があります
        # 実際の実装では、Suno AIの利用規約を確認してください
        self.api_base = "https://api.suno.ai/v1"  # 例示用
        
    def generate(
        self,
        structured_news: Dict[str, Any],
        lyrics: str,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        音楽を生成する
        
        Args:
            structured_news: 4構造化されたニュースデータ
            lyrics: 歌詞
            output_dir: 出力ディレクトリ（デフォルトはconfig.OUTPUT_DIR）
            
        Returns:
            生成結果（ファイルパス、メタデータ等）
        """
        logger.info("🎵 音楽生成を開始します")
        
        if not DEPENDENCIES_AVAILABLE:
            logger.error("❌ 必要なパッケージがインストールされていません")
            logger.error("pip install -r requirements.txt を実行してください")
            return self._generate_mock_result(structured_news, lyrics, output_dir)
        
        if not self.enabled:
            logger.warning("⚠️ 音楽生成が無効になっています（モックモード）")
            logger.info("💡 実際に生成するには .env で MUSIC_GENERATION_ENABLED=true に設定してください")
            return self._generate_mock_result(structured_news, lyrics, output_dir)
        
        if not self.api_key:
            logger.error("❌ SUNO_API_KEY が設定されていません")
            logger.info("💡 .env ファイルにAPIキーを設定してください")
            return self._generate_mock_result(structured_news, lyrics, output_dir)
        
        # プロンプトを生成
        prompt_params = build_music_prompt(structured_news, lyrics)
        
        try:
            # Suno AIで音楽を生成
            result = self._call_suno_api(prompt_params)
            
            # 音楽ファイルをダウンロード
            if output_dir is None:
                output_dir = self.config.OUTPUT_DIR
            
            music_file = self._download_music(result, output_dir)
            
            logger.info(f"✅ 音楽生成が完了しました: {music_file}")
            
            return {
                "success": True,
                "music_file": str(music_file),
                "title": prompt_params["title"],
                "style": prompt_params["style"],
                "duration": result.get("duration", 0),
                "audio_url": result.get("audio_url", ""),
            }
            
        except Exception as e:
            logger.error(f"❌ 音楽生成エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "mock": True,
            }
    
    def _call_suno_api(self, prompt_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suno APIを呼び出す
        
        注意: これは例示的な実装です
        実際のSuno AIのAPIエンドポイントは異なる可能性があります
        """
        logger.info("📡 Suno AIにリクエストを送信します...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "title": prompt_params["title"],
            "prompt": prompt_params["lyrics"],
            "tags": prompt_params["style"],
            "model": prompt_params["model"],
            "instrumental": prompt_params["instrumental"],
            "wait_audio": prompt_params["wait_audio"],
        }
        
        # 生成リクエスト
        response = requests.post(
            f"{self.api_base}/generate",
            headers=headers,
            json=payload,
            timeout=300  # 5分
        )
        
        response.raise_for_status()
        result = response.json()
        
        # 生成完了を待つ
        if not prompt_params.get("wait_audio", False):
            generation_id = result.get("id")
            result = self._wait_for_completion(generation_id)
        
        return result
    
    def _wait_for_completion(self, generation_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """
        音楽生成の完了を待つ
        
        Args:
            generation_id: 生成ID
            max_wait: 最大待機時間（秒）
        """
        logger.info("⏳ 音楽生成を待機中...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(
                f"{self.api_base}/status/{generation_id}",
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            status = result.get("status")
            
            if status == "complete":
                logger.info("✅ 音楽生成が完了しました")
                return result
            elif status == "failed":
                raise Exception("音楽生成に失敗しました")
            
            time.sleep(5)  # 5秒ごとにポーリング
        
        raise TimeoutError("音楽生成のタイムアウト")
    
    def _download_music(self, result: Dict[str, Any], output_dir: Path) -> Path:
        """
        生成された音楽ファイルをダウンロードする
        
        Args:
            result: Suno APIのレスポンス
            output_dir: 出力ディレクトリ
            
        Returns:
            保存されたファイルパス
        """
        audio_url = result.get("audio_url")
        if not audio_url:
            raise ValueError("音楽ファイルのURLが見つかりません")
        
        logger.info("📥 音楽ファイルをダウンロードしています...")
        
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        
        # ファイル名を生成
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"music_{timestamp}.mp3"
        filepath = output_dir / filename
        
        # ファイルに保存
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"✅ ダウンロード完了: {filepath}")
        return filepath
    
    def _generate_mock_result(
        self,
        structured_news: Dict[str, Any],
        lyrics: str,
        output_dir: Optional[Path]
    ) -> Dict[str, Any]:
        """
        モック結果を生成する（実際のAPI呼び出しなし）
        """
        logger.info("🎭 モックモードで実行中（実際の音楽は生成されません）")
        
        # プロンプトだけは生成して表示
        prompt_params = build_music_prompt(structured_news, lyrics)
        
        logger.info("=" * 50)
        logger.info("📋 生成されるはずだった音楽の設定:")
        logger.info(f"  タイトル: {prompt_params['title']}")
        logger.info(f"  スタイル: {prompt_params['style']}")
        logger.info(f"  モデル: {prompt_params['model']}")
        logger.info("=" * 50)
        
        # モックファイルを作成
        if output_dir is None:
            output_dir = self.config.OUTPUT_DIR
        
        mock_file = output_dir / "music_mock.txt"
        with open(mock_file, "w", encoding="utf-8") as f:
            f.write("🎵 音楽ファイル（モック）\n\n")
            f.write("実際に音楽を生成するには:\n")
            f.write("1. pip install -r requirements.txt\n")
            f.write("2. .env ファイルに SUNO_API_KEY を設定\n")
            f.write("3. .env で MUSIC_GENERATION_ENABLED=true に設定\n\n")
            f.write(f"タイトル: {prompt_params['title']}\n")
            f.write(f"スタイル: {prompt_params['style']}\n\n")
            f.write("歌詞:\n")
            f.write(lyrics)
        
        return {
            "success": True,
            "mock": True,
            "music_file": str(mock_file),
            "title": prompt_params["title"],
            "style": prompt_params["style"],
            "message": "モックモード: 実際の音楽は生成されていません",
        }


# 便利関数
def generate_music(
    structured_news: Dict[str, Any],
    lyrics: str,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    音楽を生成する（便利関数）
    
    Args:
        structured_news: 4構造化されたニュースデータ
        lyrics: 歌詞
        output_dir: 出力ディレクトリ
        
    Returns:
        生成結果
    """
    generator = MusicGenerator()
    return generator.generate(structured_news, lyrics, output_dir)
