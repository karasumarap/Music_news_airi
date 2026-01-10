"""
動画生成モジュール
音楽ファイル（mp3）と画像を組み合わせて動画を生成する
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional
import shutil

logger = logging.getLogger(__name__)


class VideoGenerator:
    """動画生成クラス"""
    
    def __init__(self):
        """初期化"""
        # FFmpegの存在確認
        if not self._check_ffmpeg():
            raise RuntimeError(
                "FFmpegがインストールされていません。\n"
                "インストール方法:\n"
                "  Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "  macOS: brew install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html"
            )
        
        logger.info("🎬 動画生成システム初期化完了")
    
    def _check_ffmpeg(self) -> bool:
        """
        FFmpegがインストールされているか確認
        
        Returns:
            bool: インストールされている場合True
        """
        return shutil.which('ffmpeg') is not None
    
    def generate(
        self,
        audio_path: str,
        image_path: str,
        output_path: str,
        fps: int = 30,
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        audio_bitrate: str = "192k",
        preset: str = "medium",
        crf: int = 23
    ) -> str:
        """
        動画を生成
        
        Args:
            audio_path: 音楽ファイルパス（mp3など）
            image_path: 画像ファイルパス（jpg, pngなど）
            output_path: 出力動画パス（mp4）
            fps: フレームレート
            video_codec: 動画コーデック
            audio_codec: 音声コーデック
            audio_bitrate: 音声ビットレート
            preset: エンコードプリセット（ultrafast, fast, medium, slow, veryslow）
            crf: 品質設定（0-51、低いほど高品質、推奨18-28）
            
        Returns:
            str: 生成された動画のパス
        """
        audio_path = Path(audio_path)
        image_path = Path(image_path)
        output_path = Path(output_path)
        
        # ファイル存在確認
        if not audio_path.exists():
            raise FileNotFoundError(f"音楽ファイルが見つかりません: {audio_path}")
        
        if not image_path.exists():
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
        
        # 出力ディレクトリ作成
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🎬 動画生成開始")
        logger.info(f"   音楽: {audio_path.name}")
        logger.info(f"   画像: {image_path.name}")
        logger.info(f"   出力: {output_path.name}")
        
        # FFmpegコマンドを構築
        command = [
            'ffmpeg',
            '-y',  # 上書き確認なし
            '-loop', '1',  # 画像をループ
            '-i', str(image_path),  # 入力画像
            '-i', str(audio_path),  # 入力音声
            '-c:v', video_codec,  # 動画コーデック
            '-c:a', audio_codec,  # 音声コーデック
            '-b:a', audio_bitrate,  # 音声ビットレート
            '-preset', preset,  # エンコードプリセット
            '-crf', str(crf),  # 品質
            '-tune', 'stillimage',  # 静止画用最適化
            '-shortest',  # 音声の長さに合わせる
            '-pix_fmt', 'yuv420p',  # 互換性のあるピクセルフォーマット
            '-r', str(fps),  # フレームレート
            str(output_path)
        ]
        
        try:
            # FFmpegを実行
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            logger.info(f"✅ 動画生成完了: {output_path}")
            logger.info(f"   ファイルサイズ: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ FFmpegエラー: {e.stderr}")
            raise RuntimeError(f"動画生成に失敗しました: {e.stderr}")
    
    def generate_with_lyrics(
        self,
        audio_path: str,
        image_path: str,
        lyrics_path: str,
        output_path: str,
        **kwargs
    ) -> str:
        """
        歌詞表示付き動画を生成（将来実装）
        
        現在は通常の動画生成と同じ動作
        将来的には歌詞をオーバーレイ表示する機能を追加予定
        
        Args:
            audio_path: 音楽ファイルパス
            image_path: 画像ファイルパス
            lyrics_path: 歌詞ファイルパス
            output_path: 出力動画パス
            **kwargs: その他のオプション
            
        Returns:
            str: 生成された動画のパス
        """
        logger.info("📝 歌詞表示機能は将来実装予定です")
        logger.info("📝 現在は通常の動画を生成します")
        
        # TODO: 歌詞をオーバーレイ表示する機能を実装
        # - 歌詞ファイルを解析
        # - FFmpegのdrawtext フィルターで歌詞を表示
        # - タイミングに合わせてテキストを切り替え
        
        return self.generate(
            audio_path=audio_path,
            image_path=image_path,
            output_path=output_path,
            **kwargs
        )
    
    def get_video_info(self, video_path: str) -> dict:
        """
        動画の情報を取得
        
        Args:
            video_path: 動画ファイルパス
            
        Returns:
            dict: 動画情報
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
        
        command = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]
        
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            import json
            return json.loads(result.stdout)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ffprobeエラー: {e.stderr}")
            return {}
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        音声ファイルの長さを取得（秒）
        
        Args:
            audio_path: 音声ファイルパス
            
        Returns:
            float: 長さ（秒）
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_path}")
        
        command = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            str(audio_path)
        ]
        
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            import json
            info = json.loads(result.stdout)
            duration = float(info['format']['duration'])
            return duration
            
        except (subprocess.CalledProcessError, KeyError, ValueError) as e:
            logger.error(f"❌ 音声長さ取得エラー: {e}")
            return 0.0
    
    def generate_shorts(
        self,
        audio_path: str,
        image_path: str,
        output_dir: str,
        max_duration: int = 30,
        width: int = 1080,
        height: int = 1920,
        **kwargs
    ) -> list:
        """
        YouTubeショート用に動画を分割生成
        
        Args:
            audio_path: 音楽ファイルパス
            image_path: 画像ファイルパス
            output_dir: 出力ディレクトリ
            max_duration: 最大長さ（秒）
            width: 動画幅（ショートは縦型: 1080推奨）
            height: 動画高さ（ショートは縦型: 1920推奨）
            **kwargs: その他のオプション
            
        Returns:
            list: 生成された動画パスのリスト
        """
        audio_path = Path(audio_path)
        image_path = Path(image_path)
        output_dir = Path(output_dir)
        
        # ファイル存在確認
        if not audio_path.exists():
            raise FileNotFoundError(f"音楽ファイルが見つかりません: {audio_path}")
        
        if not image_path.exists():
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
        
        # 出力ディレクトリ作成
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 音声の長さを取得
        duration = self.get_audio_duration(str(audio_path))
        logger.info(f"🎬 YouTubeショート生成開始")
        logger.info(f"   音楽長さ: {duration:.1f}秒")
        logger.info(f"   最大長さ: {max_duration}秒")
        
        # 分割数を計算
        import math
        num_parts = math.ceil(duration / max_duration)
        logger.info(f"   分割数: {num_parts}個")
        
        generated_videos = []
        
        for i in range(num_parts):
            start_time = i * max_duration
            # 最後のパートの長さを調整
            segment_duration = min(max_duration, duration - start_time)
            
            output_path = output_dir / f"short_{i+1:02d}.mp4"
            
            logger.info(f"📹 Part {i+1}/{num_parts}: {start_time:.1f}秒 - {start_time + segment_duration:.1f}秒")
            
            # FFmpegコマンドを構築（縦型ショート用）
            command = [
                'ffmpeg',
                '-y',  # 上書き確認なし
                '-loop', '1',  # 画像をループ
                '-i', str(image_path),  # 入力画像
                '-ss', str(start_time),  # 開始時間
                '-t', str(segment_duration),  # 長さ
                '-i', str(audio_path),  # 入力音声
                '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',  # 縦型リサイズとパディング
                '-c:v', kwargs.get('video_codec', 'libx264'),
                '-c:a', kwargs.get('audio_codec', 'aac'),
                '-b:a', kwargs.get('audio_bitrate', '192k'),
                '-preset', kwargs.get('preset', 'medium'),
                '-crf', str(kwargs.get('crf', 23)),
                '-tune', 'stillimage',
                '-shortest',  # 音声の長さに合わせる
                '-pix_fmt', 'yuv420p',
                '-r', str(kwargs.get('fps', 30)),
                '-movflags', '+faststart',  # Web再生最適化（moov atom を先頭に配置）
                str(output_path)
            ]
            
            try:
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                
                logger.info(f"   ✅ 生成完了: {output_path.name}")
                logger.info(f"      ファイルサイズ: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
                generated_videos.append(str(output_path))
                
            except subprocess.CalledProcessError as e:
                logger.error(f"   ❌ FFmpegエラー: {e.stderr}")
                raise RuntimeError(f"ショート動画生成に失敗しました: {e.stderr}")
        
        logger.info(f"✅ YouTubeショート生成完了: {len(generated_videos)}個")
        return generated_videos


def generate_video(
    audio_path: str,
    image_path: str,
    output_path: str,
    **kwargs
) -> str:
    """
    動画生成の便利関数
    
    Args:
        audio_path: 音楽ファイルパス
        image_path: 画像ファイルパス
        output_path: 出力動画パス
        **kwargs: その他のオプション
        
    Returns:
        str: 生成された動画のパス
    """
    generator = VideoGenerator()
    return generator.generate(
        audio_path=audio_path,
        image_path=image_path,
        output_path=output_path,
        **kwargs
    )


if __name__ == "__main__":
    # テスト用
    logging.basicConfig(level=logging.INFO)
    
    print("🎬 動画生成モジュール")
    print("FFmpegの確認...")
    
    try:
        generator = VideoGenerator()
        print("✅ FFmpegが利用可能です")
        print("\n使用方法:")
        print("  from src.video_generator import generate_video")
        print("  generate_video(")
        print("      audio_path='music.mp3',")
        print("      image_path='thumbnail.jpg',")
        print("      output_path='video.mp4'")
        print("  )")
    except RuntimeError as e:
        print(f"❌ {e}")
