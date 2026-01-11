# 字幕機能実装ガイド

## 実装内容

### 1. ダミーmp3の70秒生成 ✅

**ファイル**: [src/music_generator.py](src/music_generator.py)

- `_generate_dummy_audio()` メソッドを追加
- FFmpegを使用して70秒の無音mp3を生成
- ビットレート: 192kbps
- サンプルレート: 44100Hz

```python
# 使用例
music_generator = MusicGenerator()
result = music_generator._generate_mock_result(
    structured_news=news_data,
    lyrics=lyrics,
    output_dir=output_dir
)
# result["music_file"] に70秒のダミーmp3が生成される
```

### 2. SRT字幕ファイル生成 ✅

**ファイル**: [src/subtitle_generator.py](src/subtitle_generator.py) (新規作成)

- 歌詞テキストからSRT形式の字幕を自動生成
- タイミングを自動計算（文字数ベース）
- カスタマイズ可能な表示速度

**機能**:
- セクション見出し（`[Verse]`など）の自動除去
- 各行の表示時間を文字数から算出
- 音楽の長さに合わせてタイミングをスケーリング

```python
from src.subtitle_generator import SubtitleGenerator

generator = SubtitleGenerator()
subtitle_path = generator.generate_srt(
    lyrics=lyrics,
    output_path="subtitles.srt",
    duration=70.0,
    chars_per_second=12.0  # 表示速度調整
)
```

**SRT形式例**:
```
1
00:00:00,000 --> 00:00:04,117
今日のニュース、お届けします

2
00:00:04,117 --> 00:00:08,235
朝の空気が冷たくて
```

### 3. FFmpegで動画に字幕を焼き込み ✅

**ファイル**: [src/video_generator.py](src/video_generator.py)

- `generate_with_subtitles()` メソッドを追加
- FFmpegの`subtitles`フィルターを使用
- 豊富なスタイル設定オプション

**字幕スタイル設定**:
- フォント名、サイズ
- フォント色、縁取り色
- 背景色（透明度設定可能）
- 字幕位置（上/中央/下）

```python
from src.video_generator import VideoGenerator

generator = VideoGenerator()
video_path = generator.generate_with_subtitles(
    audio_path="music.mp3",
    image_path="thumbnail.jpg",
    subtitle_path="subtitles.srt",
    output_path="video_with_subtitles.mp4",
    # スタイル設定
    font_size=32,
    font_color="white",
    border_color="black",
    border_width=3,
    background_color="black@0.6",  # 60%透明
    subtitle_position="bottom"
)
```

### 4. テストスクリプト ✅

**ファイル**: [scripts/test_subtitles.py](scripts/test_subtitles.py)

完全なワークフローをテストするスクリプト:

1. ダミーmp3生成（70秒）
2. サムネイル画像生成
3. SRT字幕ファイル生成
4. 字幕なし動画生成
5. 字幕付き動画生成

**実行方法**:
```bash
python scripts/test_subtitles.py
```

**出力ファイル**:
```
output/test_subtitles/
├── music_dummy.mp3          # 70秒のダミー音声
├── thumbnail.jpg            # サムネイル画像
├── subtitles.srt            # 字幕ファイル
├── video_no_subtitles.mp4   # 字幕なし動画
└── video_with_subtitles.mp4 # 字幕付き動画
```

## 技術的詳細

### FFmpegコマンド例

**ダミー音声生成**:
```bash
ffmpeg -y \
  -f lavfi -i anullsrc=r=44100:cl=stereo \
  -t 70 \
  -c:a libmp3lame \
  -b:a 192k \
  output.mp3
```

**字幕付き動画生成**:
```bash
ffmpeg -y \
  -loop 1 -i image.jpg \
  -i audio.mp3 \
  -vf "subtitles='subtitles.srt':force_style='FontSize=32,PrimaryColour=&H00FFFFFF'" \
  -c:v libx264 -c:a aac \
  -preset medium -crf 23 \
  -shortest \
  output.mp4
```

### 字幕スタイル（ASS形式）

- **色指定**: `&H00BBGGRR` (BGR順序)
  - 白: `&H00FFFFFF`
  - 黒: `&H00000000`
  - 赤: `&H000000FF`

- **透明度**: `&HAA...` (AAが透明度、00=透明、FF=不透明)
  - 黒60%透明: `&H99000000`

- **位置指定** (Alignment):
  - 1=左下, 2=中央下, 3=右下
  - 4=左中, 5=中央, 6=右中
  - 7=左上, 8=中央上, 9=右上

## 使用方法

### 既存のワークフローへの統合

```python
from src.music_generator import MusicGenerator
from src.subtitle_generator import SubtitleGenerator
from src.video_generator import VideoGenerator

# 1. 音楽生成（またはダミー）
music_gen = MusicGenerator()
music_result = music_gen.generate(news_data, lyrics, output_dir)
audio_path = music_result["music_file"]

# 2. 字幕生成
subtitle_gen = SubtitleGenerator()
subtitle_path = subtitle_gen.generate_srt(
    lyrics=lyrics,
    output_path=output_dir / "subtitles.srt",
    duration=70.0
)

# 3. 字幕付き動画生成
video_gen = VideoGenerator()
video_path = video_gen.generate_with_subtitles(
    audio_path=audio_path,
    image_path=thumbnail_path,
    subtitle_path=subtitle_path,
    output_path=output_dir / "video.mp4"
)
```

### カスタマイズ例

**表示速度の調整**:
```python
# ゆっくり表示
subtitle_gen.generate_srt(lyrics, "slow.srt", duration=70, chars_per_second=10)

# 速く表示
subtitle_gen.generate_srt(lyrics, "fast.srt", duration=70, chars_per_second=20)
```

**字幕スタイルのカスタマイズ**:
```python
# 大きく目立つ字幕
video_gen.generate_with_subtitles(
    ...,
    font_size=48,
    font_color="yellow",
    border_color="black",
    border_width=4,
    background_color="black@0.8"
)
```

## 必要なパッケージ

- **FFmpeg**: 音声・動画処理
  ```bash
  sudo apt-get install ffmpeg  # Ubuntu/Debian
  brew install ffmpeg          # macOS
  ```

- **Python パッケージ**:
  ```bash
  pip install Pillow  # サムネイル生成用
  ```

## テスト結果

✅ すべての機能が正常に動作確認済み:

- ダミーmp3: 正確に70秒 (70.034286秒)
- 字幕ファイル: 正しいSRT形式で生成
- 字幕付き動画: 70秒、1280x720、H.264/AAC
- 字幕なし動画: 比較用に生成

**生成されたファイルサイズ**:
- music_dummy.mp3: 1.7MB
- subtitles.srt: 1.1KB
- thumbnail.jpg: 26KB
- video_no_subtitles.mp4: 193KB
- video_with_subtitles.mp4: 225KB

## 今後の拡張可能性

1. **カラオケモード**: 現在の行をハイライト表示
2. **多言語対応**: 複数の字幕トラック
3. **アニメーション**: フェードイン/アウト効果
4. **自動歌詞同期**: 音声認識によるタイミング調整
5. **フォント選択**: 日本語フォントの自動検出と使用

## トラブルシューティング

### FFmpegがない
```bash
# インストール方法は「必要なパッケージ」を参照
which ffmpeg  # インストール確認
```

### 字幕が表示されない
- SRTファイルの文字エンコーディングをUTF-8に確認
- 字幕ファイルのパスに特殊文字がないか確認

### フォントの問題
- システムにフォントがインストールされているか確認
- `font_name`パラメータでフォントを明示的に指定

---

**実装完了日**: 2026年1月11日  
**実装者**: GitHub Copilot  
**テスト環境**: Ubuntu 24.04.3 LTS (Dev Container)
