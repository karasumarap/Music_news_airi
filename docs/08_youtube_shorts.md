# YouTubeショート自動生成機能

## 概要

音楽ニュースAIでは、通常の横型YouTube動画に加えて、YouTubeショート（縦型短尺動画）を自動生成してアップロードする機能を実装しています。

## YouTubeショートとは

- **最大長さ**: 60秒以内
- **推奨アスペクト比**: 9:16（縦型）または 1:1（正方形）
- **推奨解像度**: 1080x1920（縦型）
- **特徴**: スマートフォンでの視聴に最適化された短尺動画

## 機能の特徴

### 1. 自動分割機能

音楽が30秒を超える場合、自動的に30秒以下のセグメントに分割します。

```
例：90秒の音楽の場合
→ Part 1: 0-30秒
→ Part 2: 30-60秒
→ Part 3: 60-90秒
```

### 2. 縦型フォーマット

YouTubeショート用に縦型（1080x1920）の動画を生成します。

- 元の画像を縦型にリサイズ
- アスペクト比を維持しながらパディング
- スマートフォン視聴に最適化

### 3. 一括アップロード

複数のショート動画を自動的に一括アップロードします。

- Part番号を自動付与
- `#Shorts` タグを自動追加
- すべて公開設定でアップロード
- フル版動画へのリンクを説明文に含む

## 使い方

### 基本的な使い方

```bash
# Part 2スクリプトを実行（通常動画 + ショート）
python scripts/part2_upload_video.py <セッションID>
```

実行すると以下が自動的に行われます：

1. サムネイル生成
2. 通常動画（横型）生成
3. 通常動画をYouTubeにアップロード
4. **YouTubeショート（縦型）を生成**
5. **YouTubeショートを一括アップロード**

### テスト実行

アップロードせずにショート動画の生成だけをテストできます：

```bash
python scripts/test_shorts_generation.py \
  <音声ファイル> \
  <画像ファイル> \
  <出力ディレクトリ>

# 例
python scripts/test_shorts_generation.py \
  output/sessions/20260110_143052/music.mp3 \
  output/sessions/20260110_143052/thumbnail.jpg \
  test_shorts
```

## 出力ファイル

```
output/sessions/YYYYMMDD_HHMMSS/
├── music.mp3                    # 元の音楽ファイル
├── thumbnail.jpg                # サムネイル
├── video.mp4                    # 通常動画（横型）
├── shorts/                      # ショート動画ディレクトリ
│   ├── short_01.mp4            # Part 1（0-30秒）
│   ├── short_02.mp4            # Part 2（30-60秒）
│   └── short_03.mp4            # Part 3（60-90秒）
├── youtube_info.json            # 通常動画アップロード情報
└── youtube_shorts_info.json     # ショートアップロード情報
```

## アップロード情報

### youtube_shorts_info.json

```json
[
  {
    "video_id": "abc123...",
    "url": "https://www.youtube.com/watch?v=abc123...",
    "title": "【音楽ニュース】ニュースタイトル [Part 1/3] #Shorts",
    "privacy_status": "public"
  },
  {
    "video_id": "def456...",
    "url": "https://www.youtube.com/watch?v=def456...",
    "title": "【音楽ニュース】ニュースタイトル [Part 2/3] #Shorts",
    "privacy_status": "public"
  },
  ...
]
```

## 技術詳細

### 動画生成パラメータ

```python
# video_generator.py - generate_shorts()

width: 1080           # 幅（縦型）
height: 1920          # 高さ（縦型）
max_duration: 30      # 最大長さ（秒）
video_codec: libx264  # 動画コーデック
audio_codec: aac      # 音声コーデック
audio_bitrate: 192k   # 音声ビットレート
```

### FFmpegコマンド例

```bash
ffmpeg -y \
  -loop 1 -i thumbnail.jpg \
  -ss 0 -t 30 -i music.mp3 \
  -vf 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2' \
  -c:v libx264 -c:a aac -b:a 192k \
  -preset medium -crf 23 \
  -tune stillimage -pix_fmt yuv420p -r 30 \
  short_01.mp4
```

## 実装クラス

### VideoGenerator.generate_shorts()

```python
from src.video_generator import VideoGenerator

generator = VideoGenerator()

# YouTubeショート生成（自動分割）
short_videos = generator.generate_shorts(
    audio_path="music.mp3",
    image_path="thumbnail.jpg",
    output_dir="shorts",
    max_duration=30,    # 30秒ごとに分割
    width=1080,
    height=1920
)

# 返り値: 生成された動画パスのリスト
# ['shorts/short_01.mp4', 'shorts/short_02.mp4', ...]
```

### YouTubeUploader.upload_shorts()

```python
from src.youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()
uploader.authenticate()

# YouTubeショート一括アップロード
results = uploader.upload_shorts(
    video_paths=short_videos,
    base_title="【音楽ニュース】タイトル",
    base_description="説明文...",
    tags=["音楽ニュース", "AI", "Shorts"],
    privacy_status="public"
)

# 返り値: アップロード結果のリスト
# [{'video_id': '...', 'url': '...', ...}, ...]
```

## タイトルとタグ

### ショート動画タイトル

複数ショートの場合、自動的にPart番号が付与されます：

```
【音楽ニュース】ニュースタイトル [Part 1/3] #Shorts
【音楽ニュース】ニュースタイトル [Part 2/3] #Shorts
【音楽ニュース】ニュースタイトル [Part 3/3] #Shorts
```

### ハッシュタグ

自動的に以下のハッシュタグが追加されます：

- `#Shorts` - YouTubeショート必須タグ
- `#YouTubeShorts` - 追加タグ
- `#音楽ニュース` - プロジェクトタグ
- `#AI`
- `#ニュース`
- `#あいり`

## 注意事項

### YouTube API制限

- YouTube Data API v3には1日あたりのクォータ制限があります
- 動画アップロードは1600クォータ/動画を消費します
- デフォルトクォータは10,000/日です
- 複数ショートをアップロードする場合、クォータに注意してください

### ファイルサイズ

- 各ショート動画のファイルサイズは10-30MB程度
- 通常動画と合わせて合計で数十MBになります
- ストレージ容量に注意してください

### 処理時間

```
90秒の音楽の場合の処理時間（参考値）:

1. ショート生成（3本）: 約3-5分
2. アップロード（3本）: 約3-5分

合計: 約6-10分
```

## トラブルシューティング

### Q: ショートが生成されない

A: FFmpegがインストールされているか確認してください：

```bash
ffmpeg -version
```

### Q: アップロードに失敗する

A: YouTube認証が有効か確認してください：

```bash
# 認証トークンを削除して再認証
rm credentials/youtube_token.json
python scripts/part2_upload_video.py <セッションID>
```

### Q: クォータエラーが出る

A: YouTube APIのクォータ制限に達しています。翌日まで待つか、Google Cloud Consoleでクォータ増加をリクエストしてください。

## 今後の拡張予定

- [ ] 字幕・歌詞オーバーレイ表示
- [ ] カスタムエフェクト追加
- [ ] 再生回数の自動トラッキング
- [ ] アップロード予約機能
- [ ] A/Bテスト機能（複数パターン生成）

---

**音楽ニュースAI - ニュースを音楽にして、未来を一緒に考えよう**
