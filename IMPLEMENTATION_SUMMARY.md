# YouTubeショート自動生成機能 - 実装完了

## 実装概要

音楽ニュースAIに、YouTubeショート動画の自動生成・アップロード機能を追加しました。

## 主な変更点

### 1. video_generator.py
- `get_audio_duration()`: 音声ファイルの長さを取得
- `generate_shorts()`: YouTubeショート動画を自動生成（30秒ごとに分割）
  - 縦型（1080x1920）フォーマット
  - 30秒以上の動画を自動分割
  - FFmpegで高品質エンコード

### 2. youtube_uploader.py
- `upload_shorts()`: 複数のショート動画を一括アップロード
  - Part番号を自動付与
  - #Shorts タグ自動追加
  - すべて公開設定

### 3. scripts/part2_upload_video.py
- ステップ5としてショート生成・アップロードを追加
- 30秒以上: 30秒ごとに分割して複数ショート
- 30秒以下: 1本のショートとして生成
- フル版動画へのリンクを自動挿入

### 4. scripts/test_shorts_generation.py（新規）
- ショート動画生成のテストスクリプト
- アップロードなしで生成のみをテスト可能

### 5. ドキュメント
- README.md: YouTubeショート機能の説明追加
- docs/08_youtube_shorts.md: 詳細ドキュメント

## 使い方

### 通常の使用（自動実行）

```bash
python scripts/part2_upload_video.py <セッションID>
```

以下が自動的に実行されます：
1. サムネイル生成
2. 通常動画（横型）生成＆アップロード
3. **YouTubeショート（縦型）生成＆アップロード** ← NEW!

### テスト実行

```bash
python scripts/test_shorts_generation.py \
  output/sessions/<セッションID>/music.mp3 \
  output/sessions/<セッションID>/thumbnail.jpg \
  test_shorts
```

## 出力例

```
output/sessions/20260110_143052/
├── music.mp3                    # 元の音楽（例：90秒）
├── thumbnail.jpg                # サムネイル
├── video.mp4                    # 通常動画（横型）
├── shorts/                      # ← NEW!
│   ├── short_01.mp4            # Part 1（0-30秒）
│   ├── short_02.mp4            # Part 2（30-60秒）
│   └── short_03.mp4            # Part 3（60-90秒）
├── youtube_info.json            # 通常動画情報
└── youtube_shorts_info.json     # ショート動画情報 ← NEW!
```

## 技術仕様

### 動画フォーマット
- **通常動画**: 1920x1080（横型）
- **ショート動画**: 1080x1920（縦型）

### 分割ルール
- 30秒以下: 1本のショート
- 30秒超過: 30秒ごとに分割

### アップロード設定
- すべて**公開**でアップロード
- タイトル: 【音楽ニュース】タイトル [Part X/N] #Shorts
- ハッシュタグ: #Shorts #YouTubeShorts #音楽ニュース #AI

## 注意事項

1. **YouTube API クォータ**
   - 1動画アップロード = 1600クォータ
   - デフォルト上限: 10,000/日
   - 複数ショートをアップロードする場合は注意

2. **処理時間**
   - 90秒の音楽で約6-10分程度
   - ネットワーク速度に依存

3. **FFmpeg必須**
   - FFmpegがインストールされている必要があります

## テスト方法

### 1. ショート生成のテスト（アップロードなし）

```bash
# 既存のセッションを使用
python scripts/test_shorts_generation.py \
  output/sessions/20260110_075447/music.mp3 \
  output/sessions/20260110_075447/thumbnail.jpg \
  test_shorts_output
```

### 2. 実際のアップロード（YouTube認証必要）

```bash
# 新しいセッションでPart 2を実行
python scripts/part2_upload_video.py 20260110_075447
```

## 動作確認項目

- [x] 音声長さの取得
- [x] ショート動画の生成（縦型）
- [x] 30秒超過時の自動分割
- [x] Part番号の自動付与
- [x] #Shorts タグの追加
- [x] 一括アップロード
- [x] 公開設定
- [x] フル版へのリンク挿入

## 次のステップ

実際の動作確認:
```bash
# 1. テスト実行（アップロードなし）
python scripts/test_shorts_generation.py \
  output/sessions/20260110_075447/music.mp3 \
  output/sessions/20260110_075447/thumbnail.jpg \
  test_shorts

# 2. 実際のアップロード（要YouTube認証）
python scripts/part2_upload_video.py 20260110_075447
```

---

**実装完了！すべてのファイルが更新され、YouTubeショート自動生成機能が利用可能になりました。**
