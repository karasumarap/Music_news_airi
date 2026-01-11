"""
字幕生成モジュール
歌詞からSRT形式の字幕ファイルを生成する
"""

import logging
from pathlib import Path
from typing import List, Tuple, Optional
import re

logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """字幕生成クラス"""
    
    def __init__(self):
        """初期化"""
        logger.info("📝 字幕生成システム初期化完了")
    
    def generate_srt(
        self,
        lyrics: str,
        output_path: str,
        duration: float = 70.0,
        chars_per_second: float = 15.0
    ) -> str:
        """
        歌詞からSRT字幕ファイルを生成
        
        Args:
            lyrics: 歌詞テキスト
            output_path: 出力SRTファイルパス
            duration: 音楽の長さ（秒）
            chars_per_second: 1秒あたりの文字数（表示速度調整用）
            
        Returns:
            str: 生成されたSRTファイルのパス
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📝 字幕生成開始")
        logger.info(f"   歌詞文字数: {len(lyrics)}文字")
        logger.info(f"   音楽長さ: {duration:.1f}秒")
        
        # 歌詞を行に分割
        lines = self._split_lyrics(lyrics)
        
        # 各行にタイミングを割り当て
        subtitle_entries = self._assign_timings(lines, duration, chars_per_second)
        
        # SRT形式で出力
        self._write_srt(subtitle_entries, output_path)
        
        logger.info(f"✅ 字幕生成完了: {output_path.name}")
        logger.info(f"   字幕数: {len(subtitle_entries)}個")
        
        return str(output_path)
    
    def _split_lyrics(self, lyrics: str) -> List[str]:
        """
        歌詞を行に分割
        
        Args:
            lyrics: 歌詞テキスト
            
        Returns:
            行のリスト
        """
        # 改行で分割
        lines = lyrics.split('\n')
        
        # 空行を除去、前後の空白を削除
        lines = [line.strip() for line in lines if line.strip()]
        
        # セクション見出し（[Intro], [Verse]など）を除去
        lines = [line for line in lines if not re.match(r'^\[.*\]$', line)]
        
        return lines
    
    def _assign_timings(
        self,
        lines: List[str],
        duration: float,
        chars_per_second: float
    ) -> List[Tuple[float, float, str]]:
        """
        各行にタイミングを割り当て
        
        Args:
            lines: 歌詞の行リスト
            duration: 音楽の長さ（秒）
            chars_per_second: 1秒あたりの文字数
            
        Returns:
            (開始時間, 終了時間, テキスト) のタプルのリスト
        """
        if not lines:
            return []
        
        subtitle_entries = []
        
        # 各行の表示時間を文字数から計算
        line_durations = []
        for line in lines:
            # 最低表示時間を2秒に設定
            line_duration = max(2.0, len(line) / chars_per_second)
            line_durations.append(line_duration)
        
        total_calculated_duration = sum(line_durations)
        
        # 実際の音楽の長さに合わせてスケーリング
        if total_calculated_duration > 0:
            scale_factor = duration / total_calculated_duration
        else:
            scale_factor = 1.0
        
        # タイミングを割り当て
        current_time = 0.0
        for line, line_duration in zip(lines, line_durations):
            start_time = current_time
            scaled_duration = line_duration * scale_factor
            end_time = start_time + scaled_duration
            
            # 音楽の長さを超えないように
            if end_time > duration:
                end_time = duration
            
            subtitle_entries.append((start_time, end_time, line))
            current_time = end_time
            
            # 音楽の長さに達したら終了
            if current_time >= duration:
                break
        
        return subtitle_entries
    
    def _write_srt(
        self,
        subtitle_entries: List[Tuple[float, float, str]],
        output_path: Path
    ) -> None:
        """
        SRT形式でファイルに書き込み
        
        Args:
            subtitle_entries: (開始時間, 終了時間, テキスト) のリスト
            output_path: 出力ファイルパス
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, (start_time, end_time, text) in enumerate(subtitle_entries, 1):
                # SRT形式:
                # 1
                # 00:00:00,000 --> 00:00:02,500
                # テキスト
                # (空行)
                
                f.write(f"{i}\n")
                f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                f.write(f"{text}\n")
                f.write("\n")
    
    def _format_time(self, seconds: float) -> str:
        """
        秒をSRT形式の時間に変換
        
        Args:
            seconds: 秒数
            
        Returns:
            SRT形式の時間文字列 (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_time_ass(self, seconds: float) -> str:
        """
        秒をASS形式の時間に変換
        
        Args:
            seconds: 秒数
            
        Returns:
            ASS形式の時間文字列 (H:MM:SS.cc)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
    
    def generate_ass(
        self,
        lyrics: str,
        output_path: str,
        duration: float = 70.0,
        chars_per_second: float = 15.0,
        # スタイル設定
        font_name: str = "Noto Sans CJK JP",
        font_size: int = 52,
        primary_color: str = "&H00FFFFFF",  # 白
        secondary_color: str = "&H00FF00FF",  # マゼンタ（カラオケ用）
        outline_color: str = "&H00000000",  # 黒
        back_color: str = "&H80000000",  # 半透明黒
        outline: float = 3.0,
        shadow: float = 2.0,
        bold: bool = True,
        alignment: int = 2,  # 下中央
        margin_v: int = 40,  # 下マージン
        # エフェクト設定
        fade_in: float = 0.3,
        fade_out: float = 0.3
    ) -> str:
        """
        歌詞からASS字幕ファイルを生成（リッチなスタイル）
        
        Args:
            lyrics: 歌詞テキスト
            output_path: 出力ASSファイルパス
            duration: 音楽の長さ（秒）
            chars_per_second: 1秒あたりの文字数
            font_name: フォント名
            font_size: フォントサイズ
            primary_color: プライマリカラー（&H00BBGGRR形式）
            secondary_color: セカンダリカラー（カラオケ用）
            outline_color: アウトラインカラー
            back_color: 背景カラー（シャドウ）
            outline: アウトライン幅
            shadow: シャドウ深さ
            bold: 太字
            alignment: 配置（1-9）
            margin_v: 垂直マージン
            fade_in: フェードイン時間（秒）
            fade_out: フェードアウト時間（秒）
            
        Returns:
            str: 生成されたASSファイルのパス
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📝 ASS字幕生成開始")
        logger.info(f"   歌詞文字数: {len(lyrics)}文字")
        logger.info(f"   音楽長さ: {duration:.1f}秒")
        logger.info(f"   フォント: {font_name} ({font_size}px)")
        
        # 歌詞を行に分割
        lines = self._split_lyrics(lyrics)
        
        # 各行にタイミングを割り当て
        subtitle_entries = self._assign_timings(lines, duration, chars_per_second)
        
        # ASS形式で出力
        self._write_ass(
            subtitle_entries, output_path,
            font_name, font_size, primary_color, secondary_color,
            outline_color, back_color, outline, shadow, bold,
            alignment, margin_v, fade_in, fade_out
        )
        
        logger.info(f"✅ ASS字幕生成完了: {output_path.name}")
        logger.info(f"   字幕数: {len(subtitle_entries)}個")
        
        return str(output_path)
    
    def _write_ass(
        self,
        subtitle_entries: List[Tuple[float, float, str]],
        output_path: Path,
        font_name: str,
        font_size: int,
        primary_color: str,
        secondary_color: str,
        outline_color: str,
        back_color: str,
        outline: float,
        shadow: float,
        bold: bool,
        alignment: int,
        margin_v: int,
        fade_in: float,
        fade_out: float
    ) -> None:
        """
        ASS形式でファイルに書き込み
        
        ASS (Advanced SubStation Alpha) は、SRTより高度な字幕形式で、
        スタイル、エフェクト、アニメーションなどをサポート
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # ヘッダー
            f.write("[Script Info]\n")
            f.write("Title: Music News AI Subtitles\n")
            f.write("ScriptType: v4.00+\n")
            f.write("Collisions: Normal\n")
            f.write("PlayDepth: 0\n")
            f.write("Timer: 100.0000\n")
            f.write("WrapStyle: 0\n")
            f.write("\n")
            
            # スタイル定義
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
                   "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
                   "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                   "Alignment, MarginL, MarginR, MarginV, Encoding\n")
            
            bold_val = -1 if bold else 0
            f.write(f"Style: Default,{font_name},{font_size},{primary_color},{secondary_color},"
                   f"{outline_color},{back_color},{bold_val},0,0,0,"
                   f"100,100,0,0,1,{outline},{shadow},"
                   f"{alignment},20,20,{margin_v},1\n")
            f.write("\n")
            
            # イベント（字幕）
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            for start_time, end_time, text in subtitle_entries:
                start_str = self._format_time_ass(start_time)
                end_str = self._format_time_ass(end_time)
                
                # フェードインフェードアウトエフェクトを追加
                fade_in_ms = int(fade_in * 1000)
                fade_out_ms = int(fade_out * 1000)
                effect_text = f"{{\\fad({fade_in_ms},{fade_out_ms})}}{text}"
                
                f.write(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{effect_text}\n")


def generate_subtitles(
    lyrics: str,
    output_path: str,
    duration: float = 70.0,
    format: str = "ass",  # "srt" or "ass"
    **kwargs
) -> str:
    """
    字幕を生成する（便利関数）
    
    Args:
        lyrics: 歌詞テキスト
        output_path: 出力ファイルパス
        duration: 音楽の長さ（秒）
        format: 出力形式（"srt" または "ass"）
        **kwargs: その他のオプション
        
    Returns:
        str: 生成されたファイルのパス
    """
    generator = SubtitleGenerator()
    
    if format.lower() == "ass":
        return generator.generate_ass(lyrics, output_path, duration, **kwargs)
    else:
        return generator.generate_srt(lyrics, output_path, duration, **kwargs)


if __name__ == "__main__":
    # テスト用
    logging.basicConfig(level=logging.INFO)
    
    print("📝 字幕生成モジュール")
    
    # サンプル歌詞
    sample_lyrics = """
[Intro]
今日のニュース、お届けします

[Verse 1]
朝の空気が冷たくて
街は静かに目覚める
新しいニュースが届く
世界は回り続ける

[Chorus]
ニュースの時間だよ
聞いてみよう今日の出来事
ニュースの時間だよ
知ろう世界の動き
"""
    
    generator = SubtitleGenerator()
    output = generator.generate_srt(
        lyrics=sample_lyrics,
        output_path="test_subtitles.srt",
        duration=70.0
    )
    
    print(f"✅ テスト完了: {output}")
