"""
YouTubeショート生成のテストスクリプト
音声ファイルの長さをチェックして、ショート動画が正しく生成されるかテスト
"""

import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.video_generator import VideoGenerator

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_audio_duration(audio_path: str):
    """音声ファイルの長さをテスト"""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("音声ファイル長さテスト")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    generator = VideoGenerator()
    
    try:
        duration = generator.get_audio_duration(audio_path)
        logger.info(f"✅ 音声長さ: {duration:.2f}秒")
        
        # 30秒で分割した場合の推定
        import math
        num_shorts = math.ceil(duration / 30)
        logger.info(f"📊 予想されるショート数（30秒分割）: {num_shorts}個")
        
        for i in range(num_shorts):
            start = i * 30
            end = min((i + 1) * 30, duration)
            logger.info(f"   Part {i+1}: {start:.1f}秒 - {end:.1f}秒 ({end-start:.1f}秒)")
        
        return duration
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return None


def test_shorts_generation(audio_path: str, image_path: str, output_dir: str):
    """ショート動画生成のテスト"""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("ショート動画生成テスト")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    generator = VideoGenerator()
    
    try:
        # ショート動画を生成
        short_videos = generator.generate_shorts(
            audio_path=audio_path,
            image_path=image_path,
            output_dir=output_dir,
            max_duration=30,
            width=1080,
            height=1920
        )
        
        logger.info(f"✅ 生成完了: {len(short_videos)}個のショート動画")
        
        for i, video in enumerate(short_videos, 1):
            video_path = Path(video)
            size_mb = video_path.stat().st_size / 1024 / 1024
            logger.info(f"   Part {i}: {video_path.name} ({size_mb:.2f} MB)")
        
        return short_videos
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}", exc_info=True)
        return None


def main():
    """メイン処理"""
    print("""
╔════════════════════════════════════════════╗
║                                            ║
║   YouTubeショート生成テストスクリプト      ║
║                                            ║
╚════════════════════════════════════════════╝
""")
    
    if len(sys.argv) < 3:
        print("使い方: python scripts/test_shorts_generation.py <音声ファイル> <画像ファイル> [出力ディレクトリ]")
        print("例: python scripts/test_shorts_generation.py output/sessions/20260110_143052/music.mp3 output/sessions/20260110_143052/thumbnail.jpg test_shorts")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    image_path = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "test_shorts"
    
    # ファイル存在確認
    if not Path(audio_path).exists():
        logger.error(f"❌ 音声ファイルが見つかりません: {audio_path}")
        sys.exit(1)
    
    if not Path(image_path).exists():
        logger.error(f"❌ 画像ファイルが見つかりません: {image_path}")
        sys.exit(1)
    
    # テスト1: 音声の長さを確認
    duration = test_audio_duration(audio_path)
    
    if duration is None:
        sys.exit(1)
    
    print()
    
    # テスト2: ショート動画を生成
    short_videos = test_shorts_generation(audio_path, image_path, output_dir)
    
    if short_videos:
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("✅ テスト成功！")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n生成されたショート動画:\n")
        for video in short_videos:
            print(f"  - {video}")
    else:
        logger.error("❌ テスト失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
