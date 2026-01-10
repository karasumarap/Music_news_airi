"""
Part 2: 動画生成からYouTubeアップロードまで
入力: セッションID（music.mp3が配置済み）
出力: YouTube動画URL
"""

import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.session_manager import SessionManager, format_session_info
from src.thumbnail_generator import generate_thumbnail
from src.video_generator import generate_video
from src.youtube_uploader import YouTubeUploader
from src.utils import load_json, save_json

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """バナーを表示する"""
    banner = """
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║      音楽ニュースAI - あいり              ║
    ║      Part 2: 動画生成 & YouTubeアップロード║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """メイン処理"""
    print_banner()
    
    # コマンドライン引数をチェック
    if len(sys.argv) < 2:
        print("使い方: python scripts/part2_upload_video.py <セッションID>")
        print("例: python scripts/part2_upload_video.py 20260110_143052")
        print("\nセッション一覧を表示:")
        print("python scripts/list_sessions.py")
        sys.exit(1)
    
    session_id = sys.argv[1]
    
    try:
        # セッション管理を初期化
        session_manager = SessionManager()
        
        # セッションを読み込み
        logger.info(f"📂 セッション読み込み: {session_id}")
        session = session_manager.load_session(session_id)
        
        print("\n" + format_session_info(session))
        print()
        
        # music.mp3 の存在確認
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("ステップ1: 音楽ファイル確認")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        music_file = session_manager.get_file_path(session_id, "music.mp3")
        
        if not music_file.exists():
            logger.error(f"❌ 音楽ファイルが見つかりません: {music_file}")
            logger.error("音楽ファイルを以下に配置してください:")
            logger.error(f"   {music_file}")
            sys.exit(1)
        
        logger.info(f"✅ 音楽ファイル確認: music.mp3")
        logger.info(f"   ファイルサイズ: {music_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        # セッション更新
        if session.status == "lyrics_generated":
            session = session_manager.update_session(
                session_id,
                status="music_uploaded",
                music_file="music.mp3"
            )
        
        # セッションディレクトリと構造化データの取得
        session_dir = session_manager.get_session_dir(session_id)
        structured_file = session_dir / "structured_news.json"
        structured_data = load_json(str(structured_file))
        
        # ステップ2: サムネイル生成
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("ステップ2: サムネイル生成")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        try:
            thumbnail_file = session_dir / "thumbnail.jpg"
            news_title = structured_data['news']['title']
            news_date = structured_data['news']['date']
            
            generate_thumbnail(
                title=news_title,
                subtitle=news_date,
                output_path=str(thumbnail_file)
            )
            
            logger.info(f"✅ サムネイル生成完了: {thumbnail_file.name}")
            
            # セッション更新
            session = session_manager.update_session(
                session_id,
                thumbnail_file="thumbnail.jpg"
            )
        except Exception as e:
            logger.error(f"❌ サムネイル生成エラー: {e}")
            logger.info("デフォルトサムネイルなしで続行します")
            thumbnail_file = None
        
        # ステップ3: 動画生成
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("ステップ3: 動画生成")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        try:
            video_file = session_dir / "video.mp4"
            
            if not thumbnail_file or not thumbnail_file.exists():
                logger.error("❌ サムネイルファイルが見つかりません")
                sys.exit(1)
            
            generate_video(
                audio_path=str(music_file),
                image_path=str(thumbnail_file),
                output_path=str(video_file)
            )
            
            logger.info(f"✅ 動画生成完了: {video_file.name}")
            
            # セッション更新
            session = session_manager.update_session(
                session_id,
                status="video_generated",
                video_file="video.mp4"
            )
        except Exception as e:
            logger.error(f"❌ 動画生成エラー: {e}")
            sys.exit(1)
        
        # ステップ4: YouTubeアップロード
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("ステップ4: YouTubeアップロード（通常動画）")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        try:
            # YouTubeアップローダーを初期化
            uploader = YouTubeUploader()
            
            # 認証
            if not uploader.authenticate():
                logger.error("❌ YouTube認証に失敗しました")
                logger.error("設定方法: docs/07_youtube_setup.md を参照")
                sys.exit(1)
            
            # 動画タイトルと説明を生成
            news_title = structured_data['news']['title']
            news_date = structured_data['news']['date']
            
            video_title = f"【音楽ニュース】{news_title}"
            
            # 歌詞を読み込み
            lyrics_file = session_dir / "lyrics.txt"
            with open(lyrics_file, 'r', encoding='utf-8') as f:
                lyrics = f.read()
            
            # 4構造の情報を含めた説明文を作成
            fact_summary = structured_data['structure']['fact']['summary']
            meaning_summary = structured_data['structure']['meaning']['summary']
            
            video_description = f"""【音楽ニュースAI - あいり】
{news_date}

{fact_summary}

{meaning_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 歌詞

{lyrics}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 音楽ニュースAI
ニュースを音楽にして、未来を一緒に考えよう

#音楽ニュース #AI #ニュース #あいり
"""
            
            # 通常動画をアップロード
            result = uploader.upload(
                video_path=str(video_file),
                title=video_title,
                description=video_description,
                tags=["音楽ニュース", "AI", "ニュース", "あいり", news_title[:30]],
                privacy_status="public",
                thumbnail_path=str(thumbnail_file) if thumbnail_file and thumbnail_file.exists() else None
            )
            
            if result:
                logger.info(f"✅ YouTubeアップロード完了")
                logger.info(f"   Video ID: {result['video_id']}")
                logger.info(f"   URL: {result['url']}")
                
                # YouTube情報をJSONで保存
                youtube_info_file = session_dir / "youtube_info.json"
                save_json(str(youtube_info_file), result)
                
                # セッション更新
                session = session_manager.update_session(
                    session_id,
                    status="youtube_uploaded",
                    youtube_info_file="youtube_info.json",
                    youtube_video_id=result['video_id'],
                    youtube_url=result['url']
                )
            else:
                logger.error("❌ YouTubeアップロードに失敗しました")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"❌ YouTubeアップロードエラー: {e}", exc_info=True)
            sys.exit(1)
        
        # ステップ5: YouTubeショート生成とアップロード
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("ステップ5: YouTubeショート生成＆アップロード")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        try:
            from src.video_generator import VideoGenerator
            
            # ショートディレクトリを作成
            shorts_dir = session_dir / "shorts"
            shorts_dir.mkdir(exist_ok=True)
            
            # VideoGeneratorを初期化
            video_gen = VideoGenerator()
            
            # 音声の長さを確認
            duration = video_gen.get_audio_duration(str(music_file))
            logger.info(f"🎵 音楽の長さ: {duration:.1f}秒")
            
            if duration > 30:
                logger.info("📹 30秒以上のため、複数のショート動画を生成します")
                
                # YouTubeショート動画を生成（30秒ごとに分割）
                short_videos = video_gen.generate_shorts(
                    audio_path=str(music_file),
                    image_path=str(thumbnail_file),
                    output_dir=str(shorts_dir),
                    max_duration=30,  # 30秒以下
                    width=1080,       # 縦型
                    height=1920
                )
                
                logger.info(f"✅ ショート動画生成完了: {len(short_videos)}個")
                
                # ショートをアップロード
                short_title = f"【音楽ニュース】{news_title}"
                short_description = f"""【音楽ニュースAI - あいり】YouTubeショート版
{news_date}

{fact_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 音楽ニュースAI
ニュースを音楽にして、未来を一緒に考えよう

フル版はこちら: {result['url']}

#音楽ニュース #AI #ニュース #あいり #Shorts
"""
                
                shorts_results = uploader.upload_shorts(
                    video_paths=short_videos,
                    base_title=short_title,
                    base_description=short_description,
                    tags=["音楽ニュース", "AI", "ニュース", "あいり", "Shorts", news_title[:30]],
                    privacy_status="public",
                    thumbnail_path=str(thumbnail_file) if thumbnail_file and thumbnail_file.exists() else None
                )
                
                if shorts_results:
                    logger.info(f"✅ YouTubeショートアップロード完了: {len(shorts_results)}個")
                    
                    # ショート情報をJSONで保存
                    youtube_shorts_info_file = session_dir / "youtube_shorts_info.json"
                    save_json(str(youtube_shorts_info_file), shorts_results)
                    
                    # セッション更新
                    session = session_manager.update_session(
                        session_id,
                        status="shorts_uploaded",
                        youtube_shorts_info_file="youtube_shorts_info.json"
                    )
                else:
                    logger.warning("⚠️ YouTubeショートのアップロードに失敗しましたが、処理を続行します")
            else:
                logger.info(f"ℹ️ 音楽が30秒以下({duration:.1f}秒)のため、ショートは1個のみ生成します")
                
                # 1個だけショート動画を生成
                short_videos = video_gen.generate_shorts(
                    audio_path=str(music_file),
                    image_path=str(thumbnail_file),
                    output_dir=str(shorts_dir),
                    max_duration=60,  # 60秒以下（ショートの上限）
                    width=1080,
                    height=1920
                )
                
                logger.info(f"✅ ショート動画生成完了: {len(short_videos)}個")
                
                # ショートをアップロード
                short_title = f"【音楽ニュース】{news_title}"
                short_description = f"""【音楽ニュースAI - あいり】YouTubeショート版
{news_date}

{fact_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 音楽ニュースAI
ニュースを音楽にして、未来を一緒に考えよう

フル版はこちら: {result['url']}

#音楽ニュース #AI #ニュース #あいり #Shorts
"""
                
                shorts_results = uploader.upload_shorts(
                    video_paths=short_videos,
                    base_title=short_title,
                    base_description=short_description,
                    tags=["音楽ニュース", "AI", "ニュース", "あいり", "Shorts", news_title[:30]],
                    privacy_status="public",
                    thumbnail_path=str(thumbnail_file) if thumbnail_file and thumbnail_file.exists() else None
                )
                
                if shorts_results:
                    logger.info(f"✅ YouTubeショートアップロード完了: {len(shorts_results)}個")
                    
                    # ショート情報をJSONで保存
                    youtube_shorts_info_file = session_dir / "youtube_shorts_info.json"
                    save_json(str(youtube_shorts_info_file), shorts_results)
                    
                    # セッション更新
                    session = session_manager.update_session(
                        session_id,
                        status="shorts_uploaded",
                        youtube_shorts_info_file="youtube_shorts_info.json"
                    )
                else:
                    logger.warning("⚠️ YouTubeショートのアップロードに失敗しましたが、処理を続行します")
                
        except Exception as e:
            logger.error(f"❌ YouTubeショート生成エラー: {e}", exc_info=True)
            logger.warning("⚠️ ショート生成に失敗しましたが、処理を続行します")
        
        # 結果表示
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("✅ Part 2 完了！")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # ショート情報を含めた結果表示
        shorts_info_text = ""
        if 'youtube_shorts_info.json' in str(session_dir):
            youtube_shorts_info_file = session_dir / "youtube_shorts_info.json"
            if youtube_shorts_info_file.exists():
                shorts_data = load_json(str(youtube_shorts_info_file))
                shorts_info_text = f"\n\nYouTubeショート動画:\n"
                for i, short_info in enumerate(shorts_data, 1):
                    shorts_info_text += f"  Part {i}: {short_info['url']}\n"
        
        print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 完了！

YouTube動画情報:
  タイトル: {video_title}
  URL: {result['url']}
  公開設定: {result['privacy_status']}{shorts_info_text}

ファイル:
  動画: {video_file}
  サムネイル: {thumbnail_file}
  YouTube情報: {youtube_info_file}

セッション: {session_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        logger.error("セッション一覧を表示:")
        logger.error("python scripts/list_sessions.py")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ エラーが発生しました: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
