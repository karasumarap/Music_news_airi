"""
YouTubeアップロードモジュール
YouTube Data API v3 を使用して動画をアップロードする
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict
import pickle

# 開発環境用: localhostでのOAuth 2.0を許可
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Google API クライアントライブラリ
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

logger = logging.getLogger(__name__)


class YouTubeUploader:
    """YouTubeアップロードクラス"""
    
    # OAuth 2.0 スコープ
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    # API サービス名とバージョン
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    
    def __init__(
        self,
        client_secret_file: str = "credentials/youtube_client_secret.json",
        token_file: str = "credentials/youtube_token.json"
    ):
        """
        初期化
        
        Args:
            client_secret_file: OAuth クライアントシークレットファイル
            token_file: 認証トークンファイル
        """
        if not GOOGLE_API_AVAILABLE:
            raise ImportError(
                "Google APIクライアントライブラリがインストールされていません。\n"
                "インストール方法:\n"
                "  pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2"
            )
        
        self.client_secret_file = Path(client_secret_file)
        self.token_file = Path(token_file)
        self.credentials = None
        self.youtube = None
        
        # 認証情報ディレクトリを作成
        self.client_secret_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("📺 YouTubeアップローダー初期化")
    
    def authenticate(self) -> bool:
        """
        認証を実行
        
        Returns:
            bool: 認証が成功した場合True
        """
        logger.info("🔑 YouTube認証を開始...")
        
        # クライアントシークレットファイルの確認
        if not self.client_secret_file.exists():
            logger.error(f"❌ クライアントシークレットファイルが見つかりません: {self.client_secret_file}")
            logger.error("設定方法: docs/07_youtube_setup.md を参照してください")
            return False
        
        # トークンファイルが存在する場合は読み込み
        if self.token_file.exists():
            logger.info("📄 既存の認証トークンを読み込み...")
            self.credentials = Credentials.from_authorized_user_file(
                str(self.token_file),
                self.SCOPES
            )
        
        # 認証情報が無効または存在しない場合
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                logger.info("🔄 認証トークンを更新...")
                try:
                    self.credentials.refresh(Request())
                except Exception as e:
                    logger.warning(f"⚠️ トークン更新失敗: {e}")
                    logger.info("🔑 再認証を実行...")
                    self.credentials = None
            
            if not self.credentials:
                logger.info("🌐 ブラウザで認証を実行...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.client_secret_file),
                    self.SCOPES,
                    redirect_uri='http://localhost:8080'
                )
                # 認証URLを生成
                auth_url, _ = flow.authorization_url(
                    prompt='consent',
                    access_type='offline'
                )
                
                print("\n" + "="*60)
                print("📺 YouTube認証が必要です")
                print("="*60)
                print("\n以下のURLをブラウザで開いて、認証を完了してください：")
                print(f"\n{auth_url}\n")
                print("※ アップロード先のYouTubeアカウントでログインしてください")
                print("\n認証後、ブラウザのアドレスバーに表示されるURL全体をコピーしてください。")
                print("（http://localhost:8080/?code=... で始まるURL）")
                print("="*60 + "\n")
                
                # ユーザーからリダイレクトURLを入力
                redirect_url = input("リダイレクトされたURL全体を貼り付けてください: ").strip()
                
                # トークンを取得
                flow.fetch_token(authorization_response=redirect_url)
                self.credentials = flow.credentials
            
            # トークンを保存
            logger.info("💾 認証トークンを保存...")
            with open(self.token_file, 'w') as token:
                token.write(self.credentials.to_json())
        
        # YouTube APIクライアントを構築
        try:
            self.youtube = build(
                self.API_SERVICE_NAME,
                self.API_VERSION,
                credentials=self.credentials
            )
            logger.info("✅ YouTube認証成功")
            return True
        except Exception as e:
            logger.error(f"❌ YouTube APIクライアント構築エラー: {e}")
            return False
    
    def upload(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[list] = None,
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "private",  # private, public, unlisted
        thumbnail_path: Optional[str] = None
    ) -> Optional[Dict]:
        """
        動画をアップロード
        
        Args:
            video_path: 動画ファイルパス
            title: 動画タイトル
            description: 動画説明
            tags: タグのリスト
            category_id: カテゴリID（22: People & Blogs, 24: Entertainment）
            privacy_status: 公開設定
            thumbnail_path: サムネイル画像パス（オプション）
            
        Returns:
            Dict: アップロード結果（video_id, url など）
        """
        if not self.youtube:
            logger.error("❌ 認証されていません。先に authenticate() を実行してください")
            return None
        
        video_path = Path(video_path)
        if not video_path.exists():
            logger.error(f"❌ 動画ファイルが見つかりません: {video_path}")
            return None
        
        logger.info(f"📤 動画アップロード開始: {title}")
        logger.info(f"   ファイル: {video_path.name}")
        logger.info(f"   サイズ: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        # タグのデフォルト設定
        if tags is None:
            tags = ["音楽ニュース", "AI", "ニュース", "あいり"]
        
        # リクエストボディを構築
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # メディアファイルをアップロード
        media = MediaFileUpload(
            str(video_path),
            chunksize=-1,  # -1 = 全体を一度にアップロード
            resumable=True
        )
        
        try:
            # アップロードリクエストを実行
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            logger.info("⏳ アップロード中...")
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"   進捗: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"✅ アップロード完了")
            logger.info(f"   Video ID: {video_id}")
            logger.info(f"   URL: {video_url}")
            
            # サムネイルをアップロード
            if thumbnail_path:
                thumbnail_path = Path(thumbnail_path)
                if thumbnail_path.exists():
                    logger.info("🖼️ サムネイルをアップロード...")
                    try:
                        self.youtube.thumbnails().set(
                            videoId=video_id,
                            media_body=MediaFileUpload(str(thumbnail_path))
                        ).execute()
                        logger.info("✅ サムネイルアップロード完了")
                    except HttpError as e:
                        logger.warning(f"⚠️ サムネイルアップロードエラー: {e}")
                else:
                    logger.warning(f"⚠️ サムネイルファイルが見つかりません: {thumbnail_path}")
            
            return {
                'video_id': video_id,
                'url': video_url,
                'title': title,
                'privacy_status': privacy_status
            }
            
        except HttpError as e:
            logger.error(f"❌ アップロードエラー: {e}")
            if e.resp.status == 403:
                logger.error("権限エラー: YouTube Data API v3 が有効になっているか確認してください")
            elif e.resp.status == 401:
                logger.error("認証エラー: 認証情報を再確認してください")
            return None
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}", exc_info=True)
            return None
    
    def get_channel_info(self) -> Optional[Dict]:
        """
        チャンネル情報を取得
        
        Returns:
            Dict: チャンネル情報
        """
        if not self.youtube:
            logger.error("❌ 認証されていません")
            return None
        
        try:
            request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                mine=True
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                logger.info(f"📺 チャンネル: {channel['snippet']['title']}")
                return channel
            else:
                logger.warning("⚠️ チャンネル情報が見つかりません")
                return None
                
        except HttpError as e:
            logger.error(f"❌ チャンネル情報取得エラー: {e}")
            return None


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    **kwargs
) -> Optional[Dict]:
    """
    YouTubeアップロードの便利関数
    
    Args:
        video_path: 動画ファイルパス
        title: 動画タイトル
        description: 動画説明
        **kwargs: その他のオプション
        
    Returns:
        Dict: アップロード結果
    """
    uploader = YouTubeUploader()
    
    if not uploader.authenticate():
        return None
    
    return uploader.upload(
        video_path=video_path,
        title=title,
        description=description,
        **kwargs
    )


if __name__ == "__main__":
    # テスト用
    logging.basicConfig(level=logging.INFO)
    
    print("📺 YouTubeアップロードモジュール")
    print("\n設定確認:")
    
    uploader = YouTubeUploader()
    
    if uploader.client_secret_file.exists():
        print(f"✅ クライアントシークレット: {uploader.client_secret_file}")
    else:
        print(f"❌ クライアントシークレットが見つかりません: {uploader.client_secret_file}")
        print("設定方法: docs/07_youtube_setup.md を参照")
    
    if uploader.token_file.exists():
        print(f"✅ 認証トークン: {uploader.token_file}")
    else:
        print(f"ℹ️ 認証トークン: 未認証（初回認証が必要）")
    
    print("\n使用方法:")
    print("  from src.youtube_uploader import upload_to_youtube")
    print("  upload_to_youtube(")
    print("      video_path='video.mp4',")
    print("      title='動画タイトル',")
    print("      description='動画説明',")
    print("      tags=['タグ1', 'タグ2'],")
    print("      privacy_status='private'")
    print("  )")
