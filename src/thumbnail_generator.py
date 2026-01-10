"""
サムネイル生成モジュール
ニュースタイトルと情報をもとにYouTube用サムネイル画像を生成する
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import textwrap

logger = logging.getLogger(__name__)


class ThumbnailGenerator:
    """サムネイル生成クラス"""
    
    # デフォルト設定
    DEFAULT_SIZE = (1280, 720)  # YouTube推奨サイズ
    DEFAULT_BG_COLOR = (25, 25, 40)  # ダークブルー
    DEFAULT_TEXT_COLOR = (255, 255, 255)  # 白
    DEFAULT_ACCENT_COLOR = (138, 85, 247)  # 紫（あいりのテーマカラー）
    
    def __init__(
        self,
        size: Tuple[int, int] = DEFAULT_SIZE,
        bg_color: Tuple[int, int, int] = DEFAULT_BG_COLOR
    ):
        """
        初期化
        
        Args:
            size: 画像サイズ (width, height)
            bg_color: 背景色 (R, G, B)
        """
        self.size = size
        self.bg_color = bg_color
        logger.info(f"🎨 サムネイル生成設定: サイズ={size}, 背景色={bg_color}")
    
    def generate(
        self,
        title: str,
        subtitle: Optional[str] = None,
        output_path: str = "thumbnail.jpg",
        quality: int = 95
    ) -> str:
        """
        サムネイル画像を生成
        
        Args:
            title: メインタイトル（ニュース見出し）
            subtitle: サブタイトル（日付など）
            output_path: 保存先パス
            quality: JPEG品質 (1-100)
            
        Returns:
            str: 生成された画像のパス
        """
        logger.info(f"🎨 サムネイル生成開始: {title}")
        
        # 画像を作成
        image = Image.new('RGB', self.size, self.bg_color)
        draw = ImageDraw.Draw(image)
        
        # フォントを設定
        try:
            # システムフォントを試す
            title_font = self._get_font(size=80, bold=True)
            subtitle_font = self._get_font(size=40, bold=False)
            logo_font = self._get_font(size=60, bold=True)
        except Exception as e:
            logger.warning(f"⚠️ フォント読み込みエラー: {e}")
            # デフォルトフォントにフォールバック
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            logo_font = ImageFont.load_default()
        
        # アクセントバーを描画（上部）
        accent_height = 20
        draw.rectangle(
            [(0, 0), (self.size[0], accent_height)],
            fill=self.DEFAULT_ACCENT_COLOR
        )
        
        # ロゴ/ブランド名を描画（左上）
        logo_text = "音楽ニュースAI - あいり"
        logo_y = 60
        draw.text(
            (40, logo_y),
            logo_text,
            fill=self.DEFAULT_ACCENT_COLOR,
            font=logo_font
        )
        
        # タイトルを描画（中央）
        title_y = 250
        wrapped_title = self._wrap_text(title, width=30)
        
        for i, line in enumerate(wrapped_title):
            # テキストのバウンディングボックスを取得
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.size[0] - text_width) // 2
            y = title_y + i * (text_height + 20)
            
            # 影を描画（視認性向上）
            shadow_offset = 4
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                line,
                fill=(0, 0, 0),
                font=title_font
            )
            
            # メインテキストを描画
            draw.text(
                (x, y),
                line,
                fill=self.DEFAULT_TEXT_COLOR,
                font=title_font
            )
        
        # サブタイトルを描画（下部）
        if subtitle:
            subtitle_y = self.size[1] - 120
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            text_width = bbox[2] - bbox[0]
            x = (self.size[0] - text_width) // 2
            
            draw.text(
                (x, subtitle_y),
                subtitle,
                fill=(180, 180, 180),
                font=subtitle_font
            )
        
        # アクセントバーを描画（下部）
        draw.rectangle(
            [(0, self.size[1] - accent_height), (self.size[0], self.size[1])],
            fill=self.DEFAULT_ACCENT_COLOR
        )
        
        # 保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        image.save(output_path, 'JPEG', quality=quality)
        logger.info(f"✅ サムネイル保存: {output_path}")
        
        return str(output_path)
    
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """
        フォントを取得
        
        Args:
            size: フォントサイズ
            bold: 太字かどうか
            
        Returns:
            ImageFont: フォントオブジェクト
        """
        # 日本語フォントのパス候補
        font_paths = [
            # Linux
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            # macOS
            "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc" if bold else "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            # Windows
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\meiryo.ttc",
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue
        
        # フォールバック: デフォルトフォント
        logger.warning("⚠️ 日本語フォントが見つかりません。デフォルトフォントを使用します")
        return ImageFont.load_default()
    
    def _wrap_text(self, text: str, width: int) -> list:
        """
        テキストを指定幅で折り返し
        
        Args:
            text: テキスト
            width: 文字数
            
        Returns:
            list: 折り返されたテキスト行のリスト
        """
        # 日本語対応の折り返し
        if len(text) <= width:
            return [text]
        
        lines = []
        current_line = ""
        
        for char in text:
            if len(current_line) >= width:
                lines.append(current_line)
                current_line = char
            else:
                current_line += char
        
        if current_line:
            lines.append(current_line)
        
        return lines


def generate_thumbnail(
    title: str,
    subtitle: Optional[str] = None,
    output_path: str = "thumbnail.jpg",
    size: Tuple[int, int] = ThumbnailGenerator.DEFAULT_SIZE,
    quality: int = 95
) -> str:
    """
    サムネイル生成の便利関数
    
    Args:
        title: メインタイトル
        subtitle: サブタイトル
        output_path: 保存先パス
        size: 画像サイズ
        quality: JPEG品質
        
    Returns:
        str: 生成された画像のパス
    """
    generator = ThumbnailGenerator(size=size)
    return generator.generate(
        title=title,
        subtitle=subtitle,
        output_path=output_path,
        quality=quality
    )


if __name__ == "__main__":
    # テスト用
    logging.basicConfig(level=logging.INFO)
    
    # サンプル生成
    generate_thumbnail(
        title="日本政府、再生可能エネルギー目標を40%に引き上げ",
        subtitle="2026年1月10日",
        output_path="test_thumbnail.jpg"
    )
    
    print("✅ テスト用サムネイルを生成しました: test_thumbnail.jpg")
