#!/usr/bin/env python3
"""
既存セッションでASS字幕付き動画を生成するテストスクリプト
"""

import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.subtitle_generator import SubtitleGenerator
from src.video_generator import VideoGenerator

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    session_id = "20260110_075447"
    session_dir = project_root / "output" / "sessions" / session_id
    
    logger.info(f"=" * 60)
    logger.info(f"ASS字幕付き動画生成テスト")
    logger.info(f"セッション: {session_id}")
    logger.info(f"=" * 60)
    
    # ファイルパスを設定
    music_file = session_dir / "music.mp3"
    thumbnail_file = session_dir / "thumbnail.jpg"
    lyrics_file = session_dir / "lyrics.txt"
    
    # ファイル存在確認
    if not music_file.exists():
        logger.error(f"音楽ファイルが見つかりません: {music_file}")
        sys.exit(1)
    
    if not thumbnail_file.exists():
        logger.error(f"サムネイルが見つかりません: {thumbnail_file}")
        sys.exit(1)
        
    if not lyrics_file.exists():
        logger.error(f"歌詞ファイルが見つかりません: {lyrics_file}")
        sys.exit(1)
    
    logger.info(f"✅ ファイル確認完了")
    
    # ステップ1: 歌詞を読み込み
    logger.info(f"\n" + "=" * 60)
    logger.info(f"ステップ1: 歌詞を読み込み")
    logger.info(f"=" * 60)
    
    with open(lyrics_file, 'r', encoding='utf-8') as f:
        lyrics = f.read()
    
    logger.info(f"✅ 歌詞読み込み完了: {len(lyrics)}文字")
    
    # ステップ2: 音声の長さを取得
    logger.info(f"\n" + "=" * 60)
    logger.info(f"ステップ2: 音声の長さを取得")
    logger.info(f"=" * 60)
    
    video_gen = VideoGenerator()
    duration = video_gen.get_audio_duration(str(music_file))
    logger.info(f"✅ 音楽の長さ: {duration:.1f}秒")
    
    # ステップ3: ASS字幕を生成
    logger.info(f"\n" + "=" * 60)
    logger.info(f"ステップ3: ASS字幕を生成")
    logger.info(f"=" * 60)
    
    subtitle_gen = SubtitleGenerator()
    ass_file = session_dir / "subtitles_new.ass"
    
    subtitle_gen.generate_ass(
        lyrics=lyrics,
        output_path=str(ass_file),
        duration=duration,
        chars_per_second=12.0,
        # リッチスタイル設定
        font_name="Noto Sans CJK JP Bold",
        font_size=56,
        primary_color="&H00FFFFFF",      # 白
        secondary_color="&H0000FFFF",    # 黄色（カラオケ用）
        outline_color="&H00000000",      # 黒
        back_color="&HA0000000",         # 半透明黒
        outline=4.0,
        shadow=2.5,
        bold=True,
        alignment=2,
        margin_v=50,
        fade_in=0.4,
        fade_out=0.4
    )
    
    logger.info(f"✅ ASS字幕生成完了: {ass_file.name}")
    logger.info(f"   ファイルサイズ: {ass_file.stat().st_size} bytes")
    
    # ステップ4: ASS字幕付き動画を生成
    logger.info(f"\n" + "=" * 60)
    logger.info(f"ステップ4: ASS字幕付き動画を生成")
    logger.info(f"=" * 60)
    
    video_with_subs = session_dir / "video_with_ass_subtitles.mp4"
    
    video_gen.generate_with_subtitles(
        audio_path=str(music_file),
        image_path=str(thumbnail_file),
        subtitle_path=str(ass_file),
        output_path=str(video_with_subs)
    )
    
    logger.info(f"✅ ASS字幕付き動画生成完了: {video_with_subs.name}")
    logger.info(f"   ファイルサイズ: {video_with_subs.stat().st_size / 1024 / 1024:.2f} MB")
    
    # 完了
    logger.info(f"\n" + "=" * 60)
    logger.info(f"🎉 完了！")
    logger.info(f"=" * 60)
    
    print(f"\n生成されたファイル:")
    print(f"  📝 ASS字幕: {ass_file}")
    print(f"  🎬 動画: {video_with_subs}")
    print(f"\n比較:")
    
    old_video = session_dir / "video.mp4"
    if old_video.exists():
        print(f"  旧動画（字幕なし）: {old_video.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"  新動画（ASS字幕付き）: {video_with_subs.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
