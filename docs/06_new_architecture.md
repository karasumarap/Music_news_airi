# 06. 新アーキテクチャ設計（ハイブリッドフロー）

## 設計思想

**自動化すべきもの**: 反復的で創造性が不要なタスク  
**手動で行うもの**: クリエイティブな判断が必要なタスク（音楽生成）

## 全体フロー

```
┌─────────────────────────────────────────────────┐
│  Part 1: 自動処理（ニュース → 歌詞）            │
└─────────────────────────────────────────────────┘
        ↓
input/news/YYYYMMDD_news.json
        ↓
[ニュース評価] news_evaluator.py
        ↓
[4構造化] structure_converter.py
        ↓
[歌詞生成] lyrics_generator.py
        ↓
output/sessions/YYYYMMDD_HHMMSS/
  ├── metadata.json       # セッション情報
  ├── structured_news.json # 4構造化データ
  └── lyrics.txt          # 生成された歌詞

┌─────────────────────────────────────────────────┐
│  手動作業: 人間によるクリエイティブ作業          │
└─────────────────────────────────────────────────┘
        ↓
1. lyrics.txt を確認
2. Suno AI で音楽生成
3. 生成したmp3を以下に配置:
   output/sessions/YYYYMMDD_HHMMSS/music.mp3

┌─────────────────────────────────────────────────┐
│  Part 2: 自動処理（動画生成 → YouTube）         │
└─────────────────────────────────────────────────┘
        ↓
output/sessions/YYYYMMDD_HHMMSS/music.mp3
        ↓
[サムネイル生成] thumbnail_generator.py
        ↓
[動画生成] video_generator.py
        ↓
[YouTubeアップロード] youtube_uploader.py
        ↓
[X/TikTok投稿] social_poster.py
        ↓
output/sessions/YYYYMMDD_HHMMSS/
  ├── thumbnail.jpg
  ├── video.mp4
  └── youtube_info.json   # アップロード結果

```

## ディレクトリ構成

```
Music_news_airi/
├── README.md
├── docs/                    # ドキュメント
│   ├── 00_philosophy.md
│   ├── 01_character.md
│   ├── 02_news_policy.md
│   ├── 03_lyrics_rules.md
│   ├── 04_architecture.md (旧)
│   ├── 05_todo.md
│   ├── 06_new_architecture.md (新)
│   └── 07_youtube_setup.md (YouTube API設定ガイド)
│
├── src/                     # ソースコード
│   ├── __init__.py
│   │
│   ├── # Part 1: ニュース処理モジュール
│   ├── news_evaluator.py    # ニュース評価・選別
│   ├── structure_converter.py  # 4構造への変換
│   ├── lyrics_generator.py  # 歌詞生成
│   ├── prompt_builder.py    # プロンプト構築
│   │
│   ├── # Part 2: 動画処理モジュール
│   ├── thumbnail_generator.py  # サムネイル生成
│   ├── video_generator.py   # 動画生成
│   ├── youtube_uploader.py  # YouTubeアップロード
│   ├── social_poster.py     # X/TikTok投稿
│   │
│   ├── # セッション管理
│   ├── session_manager.py   # セッション管理
│   │
│   ├── # 共通モジュール
│   ├── config.py            # 設定
│   └── utils.py             # ユーティリティ
│
├── input/                   # 入力データ
│   └── news/                # ニュースデータ
│       └── YYYYMMDD_news.json
│
├── output/                  # 出力データ
│   └── sessions/            # セッションごとのディレクトリ
│       └── 20260110_143052/ # タイムスタンプでディレクトリ作成
│           ├── metadata.json
│           ├── structured_news.json
│           ├── lyrics.txt
│           ├── music.mp3        # 手動で配置
│           ├── thumbnail.jpg    # Part 2で生成
│           ├── video.mp4        # Part 2で生成
│           └── youtube_info.json # Part 2で生成
│
├── templates/               # テンプレート
│   ├── thumbnail_base.png   # サムネイルベース画像
│   └── video_template.json  # 動画テンプレート設定
│
├── credentials/             # 認証情報（.gitignore）
│   ├── youtube_client_secret.json
│   └── youtube_token.json
│
├── scripts/                 # 実行スクリプト
│   ├── part1_generate_lyrics.py  # Part 1実行
│   ├── part2_upload_video.py     # Part 2実行
│   └── list_sessions.py          # セッション一覧表示
│
├── tests/                   # テスト
│   └── test_*.py
│
├── .env                     # 環境変数（.gitignore）
├── .env.example             # 環境変数サンプル
├── requirements.txt         # 依存関係
└── run.py (削除予定)        # 旧メインスクリプト
```

## セッション管理システム

### セッションIDの形式
- フォーマット: `YYYYMMDD_HHMMSS`
- 例: `20260110_143052`

### metadata.json の構造
```json
{
  "session_id": "20260110_143052",
  "created_at": "2026-01-10T14:30:52+09:00",
  "status": "lyrics_generated",  // lyrics_generated | music_uploaded | video_generated | youtube_uploaded
  "news": {
    "title": "再生可能エネルギー、2030年までに40%目標",
    "source": "環境省",
    "date": "2026-01-10"
  },
  "evaluation": {
    "score": 85,
    "is_suitable": true
  },
  "files": {
    "structured_news": "structured_news.json",
    "lyrics": "lyrics.txt",
    "music": null,  // 手動でアップロード後に "music.mp3"
    "thumbnail": null,
    "video": null,
    "youtube_info": null
  },
  "youtube": {
    "video_id": null,
    "url": null,
    "uploaded_at": null
  }
}
```

## 実行スクリプト

### Part 1: 歌詞生成まで
```bash
python scripts/part1_generate_lyrics.py input/news/20260110_news.json
```

**処理フロー:**
1. ニュースJSONを読み込み
2. セッションIDを生成（タイムスタンプ）
3. セッションディレクトリ作成
4. ニュース評価
5. 4構造化
6. 歌詞生成
7. metadata.json を保存
8. **出力**: セッションIDとlyricsパスを表示

**出力例:**
```
✅ セッション作成: 20260110_143052
✅ 歌詞生成完了: output/sessions/20260110_143052/lyrics.txt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
次のステップ:
1. 以下の歌詞を確認してください:
   output/sessions/20260110_143052/lyrics.txt

2. Suno AI で音楽を生成してください

3. 生成したmp3を以下に配置してください:
   output/sessions/20260110_143052/music.mp3

4. 配置後、以下のコマンドで動画生成・YouTubeアップロード:
   python scripts/part2_upload_video.py 20260110_143052
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Part 2: YouTube アップロードまで
```bash
python scripts/part2_upload_video.py 20260110_143052
```

**処理フロー:**
1. セッションIDを受け取り
2. music.mp3 の存在確認
3. metadata.json を読み込み
4. サムネイル生成
5. 動画生成（音楽 + サムネイル or 歌詞表示）
6. YouTubeアップロード
7. metadata.json を更新（status: youtube_uploaded）

**出力例:**
```
✅ セッション読み込み: 20260110_143052
✅ 音楽ファイル確認: music.mp3
✅ サムネイル生成完了
✅ 動画生成完了
✅ YouTubeアップロード完了

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YouTube動画情報:
URL: https://www.youtube.com/watch?v=xxxxx
タイトル: 【音楽ニュース】再生可能エネルギー、2030年までに40%目標
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### セッション一覧表示
```bash
python scripts/list_sessions.py
```

**出力例:**
```
セッション一覧:

[1] 20260110_143052
    ステータス: youtube_uploaded
    ニュース: 再生可能エネルギー、2030年までに40%目標
    YouTube: https://www.youtube.com/watch?v=xxxxx

[2] 20260110_120530
    ステータス: music_uploaded
    ニュース: AIによる医療診断の精度向上
    次のステップ: python scripts/part2_upload_video.py 20260110_120530

[3] 20260109_180245
    ステータス: lyrics_generated
    ニュース: 宇宙ステーション、新しい実験開始
    次のステップ: music.mp3を配置してください
```

## モジュール詳細

### session_manager.py
**役割:** セッションの作成・読み込み・更新・一覧取得

```python
class SessionManager:
    def create_session(news_data) -> Session
    def load_session(session_id) -> Session
    def update_session(session_id, updates)
    def list_sessions(status=None) -> List[Session]
```

### thumbnail_generator.py
**役割:** サムネイル画像生成

**オプション1: テンプレートベース（簡易）**
- テンプレート画像に文字を重ねる
- PIL (Pillow) を使用

**オプション2: 動的生成（高度）**
- あいりのキャラクター画像
- ニュースタイトル
- 装飾要素

### video_generator.py
**役割:** 音楽とビジュアルを組み合わせて動画生成

**オプション1: 静止画 + 音楽（簡易）**
- サムネイルを背景に音楽を再生
- FFmpeg を使用

**オプション2: 歌詞表示（中級）**
- 歌詞を順番に表示
- カラオケ風の演出

**オプション3: アニメーション（高度）**
- あいりのキャラクターアニメーション
- 視覚エフェクト

### youtube_uploader.py
**役割:** YouTube Data API v3 を使用して動画アップロード

**機能:**
- OAuth2.0 認証
- 動画アップロード
- メタデータ設定（タイトル、説明、タグ）
- サムネイル設定
- プレイリスト追加（オプション）

## データフロー図

```
┌─────────────────┐
│  Input News     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Session Created │ ← SessionManager.create_session()
│  20260110_143052│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ News Evaluation │ ← news_evaluator.py
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Structuring     │ ← structure_converter.py
│ (4-Structure)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Lyrics Generation│ ← lyrics_generator.py
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Save Metadata   │ ← SessionManager.update_session()
│ & Lyrics        │    status: lyrics_generated
└────────┬────────┘
         │
         │ ============ 手動作業 ============
         │ 人間が Suno AI で music.mp3 を生成・配置
         │ ==================================
         │
         ▼
┌─────────────────┐
│ Thumbnail Gen   │ ← thumbnail_generator.py
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Video Generation│ ← video_generator.py
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ YouTube Upload  │ ← youtube_uploader.py
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update Metadata │ ← SessionManager.update_session()
│ youtube_uploaded│    status: youtube_uploaded
└─────────────────┘
```

## エラーハンドリング

### Part 1 エラー
- ニュース評価で不適格 → ログに記録、処理終了
- 4構造化失敗 → リトライ（最大3回）
- 歌詞生成失敗 → リトライ（最大3回）

### Part 2 エラー
- music.mp3 が存在しない → エラーメッセージ、処理終了
- サムネイル生成失敗 → デフォルトサムネイル使用
- 動画生成失敗 → エラーログ、処理終了
- YouTube アップロード失敗 → リトライ（最大3回）、エラーログ

## 拡張性

### 将来的な拡張ポイント
1. **複数ニュース一括処理**: バッチ処理モード
2. **スケジューリング**: cron で定期実行
3. **Twitter 投稿**: YouTube URL を自動ツイート
4. **分析ダッシュボード**: 視聴数、エンゲージメント分析
5. **A/Bテスト**: サムネイル、タイトルのバリエーション

## 技術スタック

### Part 1（既存）
- Python 3.12
- 設定管理

### Part 2（新規）
- **サムネイル生成**: Pillow (PIL)
- **動画生成**: FFmpeg (python-ffmpeg or subprocess)
- **YouTube API**: google-api-python-client, google-auth

### 依存関係追加
```txt
# 既存
# (既存のrequirements.txt)

# 画像処理
Pillow>=10.0.0

# 動画処理
ffmpeg-python>=0.2.0

# YouTube API
google-api-python-client>=2.100.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
```

## 次のステップ

1. ✅ アーキテクチャ設計完了
2. 🔄 セッション管理システム実装
3. 🔄 Part 1 スクリプト作成
4. 🔄 サムネイル生成機能実装
5. 🔄 動画生成機能実装
6. 🔄 YouTube API 統合
7. 🔄 Part 2 スクリプト作成
8. 🔄 エンドツーエンドテスト
