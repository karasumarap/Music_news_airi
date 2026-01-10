"""
セッション管理システム
ニュースから動画アップロードまでのプロセスを追跡する
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """セッション情報を保持するデータクラス"""
    session_id: str
    created_at: str
    status: str  # lyrics_generated | music_uploaded | video_generated | youtube_uploaded
    news_title: str
    news_source: str
    news_date: str
    evaluation_score: Optional[int] = None
    is_suitable: Optional[bool] = None
    
    # ファイルパス（セッションディレクトリからの相対パス）
    structured_news_file: str = "structured_news.json"
    lyrics_file: str = "lyrics.txt"
    music_file: Optional[str] = None
    thumbnail_file: Optional[str] = None
    video_file: Optional[str] = None
    youtube_info_file: Optional[str] = None
    
    # YouTube情報
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    youtube_uploaded_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """辞書から復元"""
        return cls(**data)


class SessionManager:
    """セッション管理クラス"""
    
    def __init__(self, base_dir: str = "output/sessions"):
        """
        初期化
        
        Args:
            base_dir: セッションを保存するベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 セッションディレクトリ: {self.base_dir}")
    
    def create_session(
        self,
        news_title: str,
        news_source: str,
        news_date: str,
        evaluation_score: Optional[int] = None,
        is_suitable: Optional[bool] = None
    ) -> Session:
        """
        新しいセッションを作成
        
        Args:
            news_title: ニュースタイトル
            news_source: ニュースソース
            news_date: ニュース日付
            evaluation_score: 評価スコア
            is_suitable: 音楽化に適しているか
            
        Returns:
            Session: 作成されたセッション
        """
        # セッションIDを生成（タイムスタンプ）
        now = datetime.now()
        session_id = now.strftime("%Y%m%d_%H%M%S")
        
        # セッションディレクトリを作成
        session_dir = self.base_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # セッション情報を作成
        session = Session(
            session_id=session_id,
            created_at=now.isoformat(),
            status="created",
            news_title=news_title,
            news_source=news_source,
            news_date=news_date,
            evaluation_score=evaluation_score,
            is_suitable=is_suitable
        )
        
        # メタデータを保存
        self._save_metadata(session)
        
        logger.info(f"✅ セッション作成: {session_id}")
        logger.info(f"   ディレクトリ: {session_dir}")
        
        return session
    
    def load_session(self, session_id: str) -> Session:
        """
        既存のセッションを読み込み
        
        Args:
            session_id: セッションID
            
        Returns:
            Session: 読み込まれたセッション
            
        Raises:
            FileNotFoundError: セッションが存在しない
        """
        metadata_path = self.get_session_dir(session_id) / "metadata.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(
                f"❌ セッション {session_id} が見つかりません: {metadata_path}"
            )
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        session = Session.from_dict(data)
        logger.info(f"✅ セッション読み込み: {session_id}")
        
        return session
    
    def update_session(
        self,
        session_id: str,
        status: Optional[str] = None,
        **kwargs
    ) -> Session:
        """
        セッション情報を更新
        
        Args:
            session_id: セッションID
            status: 新しいステータス
            **kwargs: 更新する他のフィールド
            
        Returns:
            Session: 更新されたセッション
        """
        session = self.load_session(session_id)
        
        # ステータスを更新
        if status:
            session.status = status
            logger.info(f"🔄 ステータス更新: {session_id} → {status}")
        
        # その他のフィールドを更新
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
                logger.info(f"🔄 {key} 更新: {value}")
        
        # メタデータを保存
        self._save_metadata(session)
        
        return session
    
    def list_sessions(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Session]:
        """
        セッション一覧を取得
        
        Args:
            status: フィルタリングするステータス（Noneの場合は全て）
            limit: 取得する最大数（Noneの場合は全て）
            
        Returns:
            List[Session]: セッションのリスト（新しい順）
        """
        sessions = []
        
        # セッションディレクトリを走査
        for session_dir in sorted(self.base_dir.iterdir(), reverse=True):
            if not session_dir.is_dir():
                continue
            
            metadata_path = session_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            
            try:
                session = self.load_session(session_dir.name)
                
                # ステータスでフィルタリング
                if status and session.status != status:
                    continue
                
                sessions.append(session)
                
                # 制限に達したら終了
                if limit and len(sessions) >= limit:
                    break
                    
            except Exception as e:
                logger.warning(f"⚠️ セッション読み込みエラー: {session_dir.name} - {e}")
                continue
        
        return sessions
    
    def get_session_dir(self, session_id: str) -> Path:
        """
        セッションディレクトリのパスを取得
        
        Args:
            session_id: セッションID
            
        Returns:
            Path: セッションディレクトリのパス
        """
        return self.base_dir / session_id
    
    def get_file_path(self, session_id: str, filename: str) -> Path:
        """
        セッション内のファイルパスを取得
        
        Args:
            session_id: セッションID
            filename: ファイル名
            
        Returns:
            Path: ファイルの絶対パス
        """
        return self.get_session_dir(session_id) / filename
    
    def check_file_exists(self, session_id: str, filename: str) -> bool:
        """
        ファイルが存在するか確認
        
        Args:
            session_id: セッションID
            filename: ファイル名
            
        Returns:
            bool: ファイルが存在するか
        """
        return self.get_file_path(session_id, filename).exists()
    
    def _save_metadata(self, session: Session):
        """
        メタデータをJSONファイルに保存
        
        Args:
            session: セッション
        """
        metadata_path = self.get_session_dir(session.session_id) / "metadata.json"
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.debug(f"💾 メタデータ保存: {metadata_path}")


def format_session_info(session: Session) -> str:
    """
    セッション情報を人間が読みやすい形式にフォーマット
    
    Args:
        session: セッション
        
    Returns:
        str: フォーマットされた情報
    """
    status_emoji = {
        "created": "🆕",
        "lyrics_generated": "📝",
        "music_uploaded": "🎵",
        "video_generated": "🎬",
        "youtube_uploaded": "✅"
    }
    
    emoji = status_emoji.get(session.status, "❓")
    
    lines = [
        f"{emoji} セッション: {session.session_id}",
        f"   ステータス: {session.status}",
        f"   ニュース: {session.news_title}",
        f"   ソース: {session.news_source}",
        f"   日付: {session.news_date}",
    ]
    
    if session.evaluation_score:
        lines.append(f"   評価スコア: {session.evaluation_score}")
    
    if session.youtube_url:
        lines.append(f"   YouTube: {session.youtube_url}")
    
    return "\n".join(lines)


def get_next_step_message(session: Session) -> str:
    """
    次のステップのメッセージを取得
    
    Args:
        session: セッション
        
    Returns:
        str: 次のステップメッセージ
    """
    if session.status == "lyrics_generated":
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
次のステップ:
1. 以下の歌詞を確認してください:
   output/sessions/{session.session_id}/lyrics.txt

2. Suno AI で音楽を生成してください

3. 生成したmp3を以下に配置してください:
   output/sessions/{session.session_id}/music.mp3

4. 配置後、以下のコマンドで動画生成・YouTubeアップロード:
   python scripts/part2_upload_video.py {session.session_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    elif session.status == "music_uploaded":
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
次のステップ:
以下のコマンドで動画生成・YouTubeアップロード:
python scripts/part2_upload_video.py {session.session_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    elif session.status == "youtube_uploaded":
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 完了！
YouTube URL: {session.youtube_url}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    else:
        return ""


if __name__ == "__main__":
    # テスト用
    logging.basicConfig(level=logging.INFO)
    
    manager = SessionManager()
    
    # セッション作成テスト
    session = manager.create_session(
        news_title="再生可能エネルギー、2030年までに40%目標",
        news_source="環境省",
        news_date="2026-01-10",
        evaluation_score=85,
        is_suitable=True
    )
    
    print("\n" + format_session_info(session))
    print(get_next_step_message(session))
    
    # セッション更新テスト
    session = manager.update_session(
        session.session_id,
        status="lyrics_generated"
    )
    
    print("\n更新後:")
    print(format_session_info(session))
    
    # セッション一覧テスト
    print("\n全セッション:")
    for s in manager.list_sessions():
        print(format_session_info(s))
        print()
