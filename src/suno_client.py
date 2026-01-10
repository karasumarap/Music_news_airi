"""
音楽ニュースAI - Suno AI連携モジュール
Suno AIを使って歌詞から音楽を生成する
"""

import os
import logging
import time
import json
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SunoAIClient:
    """Suno AI APIクライアント"""
    
    def __init__(self, api_key: Optional[str] = None, dev_mode: bool = True):
        """
        初期化
        
        Args:
            api_key: Suno AI APIキー
            dev_mode: 開発モード（Trueの場合はモック実装）
        """
        self.api_key = api_key
        self.dev_mode = dev_mode
        self.base_url = os.getenv("SUNO_BASE_URL", "https://api.sunoapi.com")
        
        if not dev_mode and not api_key:
            logger.warning("⚠️ Suno AI APIキーが設定されていません。開発モードで動作します。")
            self.dev_mode = True
        
        if not dev_mode:
            logger.info(f"🔑 Suno AI APIキー: {api_key[:8]}...{api_key[-4:]}")
            logger.info(f"🌐 ベースURL: {self.base_url}")
    
    def generate_music(
        self,
        lyrics: str,
        prompt: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        音楽を生成する
        
        Args:
            lyrics: 歌詞
            prompt: 音楽スタイルのプロンプト
            title: 曲のタイトル
            metadata: メタデータ
            
        Returns:
            生成結果（生成ID、URL等）
        """
        if self.dev_mode:
            return self._generate_music_mock(lyrics, prompt, title, metadata)
        else:
            return self._generate_music_api(lyrics, prompt, title, metadata)
    
    def _generate_music_api(
        self,
        lyrics: str,
        prompt: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Suno AI v4.5 APIを使って実際に音楽を生成する
        公式ドキュメント: https://docs.sunoapi.org/suno-api/generate-music
        
        正しいエンドポイント: /v1/music/generate (POST)
        """
        logger.info("🎵 Suno AI v4.5で音楽を生成します（API実装）")
        
        try:
            import requests
            
            # Suno AI v4.5 APIエンドポイント（公式ドキュメントに基づく修正版）
            endpoint = f"{self.base_url}/v1/music/generate"
            
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Suno AI v4.5のペイロード形式
            payload = {
                "title": title,
                "tags": prompt,  # 音楽スタイルはtagsとして指定
                "prompt": "",  # promptは空でよい（カスタムモード時）
                "mv": "chirp-v4-5",  # モデルバージョン
                "custom_mode": True,  # カスタムモード（歌詞を指定）
                "instrumental": False,
                "lyrics": lyrics
            }
            
            logger.info(f"📤 Suno AI v4.5にリクエストを送信します")
            logger.info(f"   エンドポイント: {endpoint}")
            logger.info(f"   タイトル: {title}")
            logger.info(f"   モデル: chirp-v4-5")
            logger.info(f"   タグ: {prompt[:50]}...")
            logger.info(f"   歌詞の長さ: {len(lyrics)} 文字")
            
            # APIリクエスト送信
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            
            # レスポンスログ
            logger.info(f"📥 レスポンスステータス: {response.status_code}")
            
            # エラーハンドリング
            if response.status_code == 400:
                logger.error("❌ リクエストエラー: パラメータが不正です")
                logger.error(f"   詳細: {response.text}")
                return {"success": False, "error": f"Bad request: {response.text}"}
            elif response.status_code == 401:
                logger.error("❌ 認証エラー: APIキーが無効です")
                logger.error(f"   APIキー: {self.api_key[:8]}...{self.api_key[-4:]}")
                return {"success": False, "error": "Invalid API key"}
            elif response.status_code == 402:
                logger.error("❌ クレジット不足: APIクレジットが足りません")
                return {"success": False, "error": "Insufficient credits"}
            elif response.status_code == 404:
                logger.error("❌ エンドポイントが見つかりません")
                logger.error(f"   URL: {endpoint}")
                logger.error(f"   正しいURLか確認してください")
                return {"success": False, "error": "Endpoint not found"}
            elif response.status_code == 405:
                logger.error("❌ メソッドが許可されていません")
                logger.error(f"   URL: {endpoint}")
                logger.error(f"   メソッド: POST")
                logger.error(f"   ヘッダー: {headers}")
                return {"success": False, "error": "Method not allowed"}
            elif response.status_code == 429:
                logger.error("❌ レート制限: APIリクエストが多すぎます")
                return {"success": False, "error": "Rate limit exceeded"}
            elif response.status_code >= 500:
                logger.error("❌ サーバーエラー: Suno AIサーバーでエラーが発生しました")
                logger.error(f"   詳細: {response.text}")
                return {"success": False, "error": f"Server error: {response.text}"}
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"📦 APIレスポンス: {result}")
            
            # レスポンスからデータを取得
            # 成功時のレスポンス形式を確認
            if isinstance(result, dict):
                # データがネストされている可能性を考慮
                data = result.get("data") or result
                
                if isinstance(data, list) and len(data) > 0:
                    clip = data[0]
                elif isinstance(data, dict):
                    clip = data
                else:
                    clip = result
            elif isinstance(result, list) and len(result) > 0:
                clip = result[0]
            else:
                logger.error("❌ 予期しないレスポンス形式")
                logger.error(f"   レスポンス: {result}")
                return {"success": False, "error": "Unexpected response format"}
            
            generation_id = clip.get("id") or clip.get("song_id") or clip.get("clip_id")
            
            if not generation_id:
                logger.error("❌ 生成IDが取得できませんでした")
                logger.error(f"   レスポンス: {clip}")
                return {"success": False, "error": "No generation ID returned"}
            
            logger.info(f"✅ 音楽生成リクエストが送信されました（ID: {generation_id}）")
            
            # 生成完了を待機
            audio_url = clip.get("audio_url") or clip.get("song_url")
            if not audio_url:
                logger.info("⏳ 音楽生成完了を待機しています（最大5分）...")
                audio_url = self._wait_for_generation(generation_id)
            
            return {
                "success": True,
                "generation_id": generation_id,
                "audio_url": audio_url,
                "video_url": clip.get("video_url"),
                "image_url": clip.get("image_url") or clip.get("image_large_url"),
                "title": title,
                "duration": clip.get("duration"),
                "status": clip.get("status", "completed"),
                "model": "chirp-v4-5"
            }
            
        except ImportError:
            logger.error("❌ requestsライブラリがインストールされていません")
            logger.info("💡 pip install requests を実行してください")
            return {"success": False, "error": "requests library not installed"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ 接続エラー: Suno AIサーバーに接続できません")
            logger.error(f"   URL: {self.base_url}")
            logger.error(f"   詳細: {e}")
            return {"success": False, "error": "Connection error"}
        except requests.exceptions.Timeout:
            logger.error("❌ タイムアウト: リクエストが時間内に完了しませんでした")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ Suno AI API エラー: {e}")
            logger.error(f"   エラータイプ: {type(e).__name__}")
            import traceback
            logger.error(f"   トレースバック:\n{traceback.format_exc()}")
            return {"success": False, "error": str(e)}
    
    def _generate_music_mock(
        self,
        lyrics: str,
        prompt: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        音楽生成のモック実装（開発・デモ用）
        """
        logger.info("🎵 音楽を生成します（モック実装）")
        logger.info(f"📝 タイトル: {title}")
        logger.info(f"🎨 スタイル: {prompt}")
        logger.info(f"📄 歌詞の長さ: {len(lyrics)} 文字")
        
        # モック：生成中をシミュレート
        logger.info("⏳ 音楽を生成中... (モック)")
        time.sleep(2)  # 実際の生成時間をシミュレート
        
        # モック結果
        mock_result = {
            "success": True,
            "generation_id": f"mock_{int(time.time())}",
            "audio_url": "https://example.com/mock_audio.mp3",
            "video_url": "https://example.com/mock_video.mp4",
            "title": title,
            "duration": 180,  # 3分
            "status": "completed",
            "note": "これはモック実装です。実際の音楽は生成されていません。",
            "dev_mode": True
        }
        
        logger.info("✅ 音楽の生成が完了しました（モック）")
        logger.info(f"🔗 モックURL: {mock_result['audio_url']}")
        
        return mock_result
    
    def download_audio(self, audio_url: str, output_path: str | Path) -> bool:
        """
        生成された音楽をダウンロードする
        
        Args:
            audio_url: 音楽ファイルのURL
            output_path: 保存先パス
            
        Returns:
            成功したらTrue
        """
        if self.dev_mode:
            logger.info(f"💾 音楽ファイルをダウンロードします（モック）: {output_path}")
            
            # モック：空ファイルを作成
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write("# Mock audio file\n")
                f.write(f"# URL: {audio_url}\n")
                f.write(f"# This is a mock file. Real audio is not downloaded in dev mode.\n")
            
            logger.info("✅ モックファイルを作成しました")
            return True
        
        try:
            import requests
            
            logger.info(f"📥 音楽ファイルをダウンロードします: {output_path}")
            
            response = requests.get(audio_url, stream=True, timeout=60)
            response.raise_for_status()
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info("✅ 音楽ファイルのダウンロードが完了しました")
            return True
            
        except ImportError:
            logger.error("❌ requestsライブラリがインストールされていません")
            return False
        except Exception as e:
            logger.error(f"❌ ダウンロードエラー: {e}")
            return False
    
    def _wait_for_generation(self, generation_id: str, max_wait: int = 300) -> Optional[str]:
        """
        音楽生成完了を待機する
        
        Args:
            generation_id: 生成ID
            max_wait: 最大待機時間（秒）
            
        Returns:
            audio_url（生成失敗時はNone）
        """
        try:
            import requests
            import time
            
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status = self.get_generation_status(generation_id)
                
                if status.get("error"):
                    logger.error(f"❌ ステータス確認エラー: {status['error']}")
                    return None
                
                current_status = status.get("status")
                audio_url = status.get("audio_url")
                
                if current_status == "completed" and audio_url:
                    logger.info("✅ 音楽生成が完了しました")
                    return audio_url
                elif current_status == "failed":
                    logger.error("❌ 音楽生成に失敗しました")
                    return None
                
                # 進捗表示
                progress = status.get("progress", 0)
                logger.info(f"⏳ 生成中... {progress}%")
                
                time.sleep(10)  # 10秒待機
            
            logger.warning("⚠️ 音楽生成がタイムアウトしました")
            return None
            
        except Exception as e:
            logger.error(f"❌ 待機中にエラーが発生しました: {e}")
            return None
    
    def get_generation_status(self, generation_id: str) -> Dict[str, Any]:
        """
        生成ステータスを確認する（公式ドキュメントに基づく）
        
        Args:
            generation_id: 生成ID
            
        Returns:
            ステータス情報
        """
        if self.dev_mode:
            return {
                "id": generation_id,
                "status": "completed",
                "progress": 100,
                "audio_url": "https://example.com/mock_audio.mp3",
                "dev_mode": True
            }
        
        try:
            import requests
            
            # Suno AI v4.5のステータス確認エンドポイント
            endpoint = f"{self.base_url}/api/get"
            
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # パラメータとしてIDを指定
            params = {
                "ids": generation_id
            }
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # レスポンスはリストで返される
            if isinstance(result, list) and len(result) > 0:
                clip = result[0]
                
                # ステータス情報を返す
                return {
                    "id": clip.get("id"),
                    "status": clip.get("status"),
                    "audio_url": clip.get("audio_url"),
                    "video_url": clip.get("video_url"),
                    "image_url": clip.get("image_url"),
                    "duration": clip.get("duration"),
                    "progress": 100 if clip.get("status") == "completed" else 50
                }
            else:
                return {"error": "Clip not found"}
            
        except Exception as e:
            logger.error(f"❌ ステータス確認エラー: {e}")
            return {"error": str(e)}


# 便利関数
def create_suno_client(dev_mode: Optional[bool] = None) -> SunoAIClient:
    """
    Suno AIクライアントを作成する
    
    Args:
        dev_mode: 開発モード（Noneの場合は環境変数から取得）
        
    Returns:
        SunoAIClientインスタンス
    """
    if dev_mode is None:
        dev_mode = os.getenv("DEV_MODE", "true").lower() == "true"
    
    api_key = os.getenv("SUNO_API_KEY")
    
    return SunoAIClient(api_key=api_key, dev_mode=dev_mode)
