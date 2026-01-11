#!/usr/bin/env python3
"""
字幕付き動画生成のテストスクリプト
ダミーのmp3（70秒）と字幕付き動画を生成してテストする
"""

import sys
import logging
from pathlib import Path

# プロジェクトのルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.music_generator import MusicGenerator
from src.subtitle_generator import SubtitleGenerator
from src.video_generator import VideoGenerator
from src.thumbnail_generator import ThumbnailGenerator

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("🎬 字幕付き動画生成テスト")
    logger.info("=" * 60)
    
    # 出力ディレクトリ
    output_dir = project_root / "output" / "test_subtitles"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # サンプル歌詞
    sample_lyrics = """
今日のニュース、お届けします

朝の空気が冷たくて
街は静かに目覚める
新しいニュースが届く
世界は回り続ける

ニュースの時間だよ
聞いてみよう今日の出来事
ニュースの時間だよ
知ろう世界の動き

情報の海を泳いで
真実を探していく
変わりゆく世の中で
大切なことを見つける

ニュースの時間だよ
聞いてみよう今日の出来事
ニュースの時間だよ
知ろう世界の動き
"""
    
    # サンプルニュースデータ
    sample_news = {
        "category": "テクノロジー",
        "topics": [
            {"title": "新しいAI技術", "importance": 5},
        ]
    }
    
    try:
        # ステップ1: ダミーのmp3（70秒）を生成
        logger.info("\n" + "=" * 60)
        logger.info("ステップ1: ダミーのmp3を生成（70秒）")
        logger.info("=" * 60)
        
        music_generator = MusicGenerator()
        music_result = music_generator._generate_mock_result(
            structured_news=sample_news,
            lyrics=sample_lyrics,
            output_dir=output_dir
        )
        
        audio_path = music_result.get("music_file")
        logger.info(f"✅ 音楽ファイル: {audio_path}")
        
        # ステップ2: サムネイル画像を生成
        logger.info("\n" + "=" * 60)
        logger.info("ステップ2: サムネイル画像を生成")
        logger.info("=" * 60)
        
        thumbnail_generator = ThumbnailGenerator()
        thumbnail_path = thumbnail_generator.generate(
            title="今日のニュース",
            subtitle="AIニュース音楽",
            output_path=str(output_dir / "thumbnail.jpg")
        )
        logger.info(f"✅ サムネイル: {thumbnail_path}")
        
        # ステップ3: ASS字幕ファイルを生成（リッチスタイル）
        logger.info("\n" + "=" * 60)
        logger.info("ステップ3: ASS字幕ファイルを生成（リッチスタイル）")
        logger.info("=" * 60)
        
        subtitle_generator = SubtitleGenerator()
        
        # SRT字幕も生成（比較用）
        srt_path = subtitle_generator.generate_srt(
            lyrics=sample_lyrics,
            output_path=str(output_dir / "subtitles.srt"),
            duration=70.0,
            chars_per_second=12.0
        )
        logger.info(f"✅ SRT字幕ファイル: {srt_path}")
        
        # ASS字幕を生成（リッチスタイル）
        ass_path = subtitle_generator.generate_ass(
            lyrics=sample_lyrics,
            output_path=str(output_dir / "subtitles.ass"),
            duration=70.0,
            chars_per_second=12.0,
            # リッチスタイル設定
            font_name="Noto Sans CJK JP Bold",
            font_size=56,
            primary_color="&H00FFFFFF",      # 白
            secondary_color="&H0000FFFF",    # 黄色（カラオケ用）
            outline_color="&H00000000",      # 黒
            back_color="&HA0000000",         # 透明度40%の黒
            outline=4.0,
            shadow=2.5,
            bold=True,
            alignment=2,                      # 下中央
            margin_v=50,
            fade_in=0.4,
            fade_out=0.4
        )
        logger.info(f"✅ ASS字幕ファイル: {ass_path}")
        
        # 生成されたASSファイルの内容を表示
        logger.info("\n📝 ASS字幕ファイルのヘッダー:")
        with open(ass_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:30]):  # 最初の30行
                print(line.rstrip())
        
        # ステップ4: 字幕なし動画を生成
        logger.info("\n" + "=" * 60)
        logger.info("ステップ4: 字幕なし動画を生成")
        logger.info("=" * 60)
        
        video_generator = VideoGenerator()
        video_path_no_subs = video_generator.generate(
            audio_path=audio_path,
            image_path=thumbnail_path,
            output_path=str(output_dir / "video_no_subtitles.mp4")
        )
        logger.info(f"✅ 字幕なし動画: {video_path_no_subs}")
        
        # ステップ5: 字幕付き動画を生成（ASS字幕）
        logger.info("\n" + "=" * 60)
        logger.info("ステップ5: 字幕付き動画を生成（ASS字幕 - リッチスタイル）")
        logger.info("=" * 60)
        
        video_path_with_ass = video_generator.generate_with_subtitles(
            audio_path=audio_path,
            image_path=thumbnail_path,
            subtitle_path=ass_path,
            output_path=str(output_dir / "video_with_ass_subtitles.mp4")
        )
        logger.info(f"✅ ASS字幕付き動画: {video_path_with_ass}")
        
        # ステップ6: SRT字幕付き動画も生成（比較用）
        logger.info("\n" + "=" * 60)
        logger.info("ステップ6: SRT字幕付き動画を生成（比較用）")
        logger.info("=" * 60)
        
        video_path_with_srt = video_generator.generate_with_subtitles(
            audio_path=audio_path,
            image_path=thumbnail_path,
            subtitle_path=srt_path,
            output_path=str(output_dir / "video_with_srt_subtitles.mp4")
        )
        logger.info(f"✅ SRT字幕付き動画: {video_path_with_srt}")
        
        # 完了メッセージ
        logger.info("\n" + "=" * 60)
        logger.info("🎉 テスト完了！")
        logger.info("=" * 60)
        logger.info(f"\n生成されたファイル:")
        logger.info(f"  📁 出力ディレクトリ: {output_dir}")
        logger.info(f"  🎵 音楽ファイル: {Path(audio_path).name}")
        logger.info(f"  🖼️  サムネイル: {Path(thumbnail_path).name}")
        logger.info(f"  📝 SRT字幕: {Path(srt_path).name}")
        logger.info(f"  📝 ASS字幕: {Path(ass_path).name} ⭐リッチスタイル")
        logger.info(f"  🎬 字幕なし動画: {Path(video_path_no_subs).name}")
        logger.info(f"  🎬 SRT字幕動画: {Path(video_path_with_srt).name}")
        logger.info(f"  🎬 ASS字幕動画: {Path(video_path_with_ass).name} ⭐リッチスタイル")
        logger.info(f"\n💡 ASS字幕の特徴:")
        logger.info(f"  - 日本語フォント対応（Noto Sans CJK JP）")
        logger.info(f"  - フェードイン/アウトエフェクト")
        logger.info(f"  - 太字、アウトライン、シャドウ")
        logger.info(f"  - 透明背景")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ エラーが発生しました: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
