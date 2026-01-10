"""
セッション一覧表示スクリプト
全セッションの状態を表示する
"""

import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.session_manager import SessionManager, format_session_info, get_next_step_message

# ロガーの設定
logging.basicConfig(
    level=logging.WARNING,  # INFOログを抑制
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """バナーを表示する"""
    banner = """
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║      音楽ニュースAI - あいり              ║
    ║      セッション一覧                       ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """メイン処理"""
    print_banner()
    
    try:
        # セッション管理を初期化
        session_manager = SessionManager()
        
        # 全セッションを取得
        sessions = session_manager.list_sessions()
        
        if not sessions:
            print("📭 セッションがありません")
            print("\nセッションを作成するには:")
            print("python scripts/part1_generate_lyrics.py input/news/YYYYMMDD_news.json")
            return
        
        print(f"\n📊 セッション数: {len(sessions)}\n")
        print("=" * 80)
        
        for i, session in enumerate(sessions, 1):
            print(f"\n[{i}] {format_session_info(session)}")
            
            # 次のステップメッセージ（簡略版）
            if session.status == "lyrics_generated":
                print(f"\n   💡 次のステップ: music.mp3 を配置")
                print(f"      → output/sessions/{session.session_id}/music.mp3")
            elif session.status == "music_uploaded":
                print(f"\n   💡 次のステップ: python scripts/part2_upload_video.py {session.session_id}")
            elif session.status == "youtube_uploaded":
                print(f"\n   ✅ 完了")
            
            print("\n" + "-" * 80)
        
        print("\n")
        
    except Exception as e:
        logger.error(f"❌ エラーが発生しました: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
