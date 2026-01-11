# 音楽ニュースAI 〜妹アイドル「あいり」が届ける世界〜

ニュースを「音楽」という形で届けることで、難しいニュースも身近に感じられるようにするプロジェクト。

## 🎯 プロジェクトの目的

- ニュースを音楽にして、若い世代にも伝わりやすくする
- AIアイドル「あいり」が、妹のような視点で一緒に考える
- 事実をベースに、意味と影響を構造化して伝える

## ✨ 特徴

- **正確性重視**: ニュースの事実を歪めない
- **妹キャラの人格**: 断定しない、煽らない、一緒に考える
- **4構造化**: Fact / Meaning / Impact / Question
- **ハイブリッドフロー**: 自動化と人間の判断を組み合わせた効率的なワークフロー

## 🌊 ワークフロー

```
┌─────────────────────────────────────────────────┐
│  Part 1: 自動処理（ニュース → 歌詞）            │
│  python scripts/part1_generate_lyrics.py         │
└─────────────────────────────────────────────────┘
        ↓
output/sessions/YYYYMMDD_HHMMSS/
  ├── metadata.json
  ├── structured_news.json
  └── lyrics.txt

┌─────────────────────────────────────────────────┐
│  手動作業: 人間によるクリエイティブ作業          │
│  1. lyrics.txt を確認                            │
│  2. Suno AI で音楽生成                           │
│  3. music.mp3 をセッションディレクトリに配置     │
└─────────────────────────────────────────────────┘
        ↓
output/sessions/YYYYMMDD_HHMMSS/music.mp3

┌─────────────────────────────────────────────────┐
│  Part 2: 自動処理（動画生成 → YouTube）         │
│  python scripts/part2_upload_video.py SESSION_ID │
│  - サムネイル生成                                │
│  - 通常動画（横型）生成                          │
│  - YouTubeショート（縦型）生成                   │
│  - 30秒以上の動画は30秒ごとに分割               │
│  - すべて公開でアップロード                      │
└─────────────────────────────────────────────────┘
        ↓
output/sessions/YYYYMMDD_HHMMSS/
  ├── thumbnail.jpg
  ├── video.mp4
  ├── shorts/
  │   ├── short_01.mp4
  │   ├── short_02.mp4
  │   └── ...
  ├── youtube_info.json
  └── youtube_shorts_info.json
```

## 📁 プロジェクト構成

```
Music_news_airi/
├── README.md              # このファイル
├── docs/                  # ドキュメント
│   ├── 00_philosophy.md   # プロジェクト思想
│   ├── 01_character.md    # キャラクター設定
│   ├── 02_news_policy.md  # ニュース取扱ポリシー
│   ├── 03_lyrics_rules.md # 歌詞生成ルール
│   ├── 04_architecture.md # 旧アーキテクチャ
│   ├── 05_todo.md         # TODO
│   └── 06_new_architecture.md  # 新アーキテクチャ（詳細）
│
├── src/                   # ソースコード
│   ├── # Part 1: ニュース処理
│   ├── news_evaluator.py  # ニュース評価
│   ├── structure_converter.py  # 4構造変換
│   ├── lyrics_generator.py     # 歌詞生成
│   ├── prompt_builder.py       # プロンプト構築
│   │
│   ├── # Part 2: 動画処理（実装予定）
│   ├── thumbnail_generator.py  # サムネイル生成
│   ├── video_generator.py      # 動画生成
│   ├── youtube_uploader.py     # YouTubeアップロード
│   ├── social_poster.py        # X/TikTok投稿
│   │
│   ├── # セッション管理
│   ├── session_manager.py      # セッション管理
│   │
│   ├── # 共通モジュール
│   ├── config.py          # 設定
│   └── utils.py           # ユーティリティ
│
├── scripts/               # 実行スクリプト
│   ├── part1_generate_lyrics.py  # Part 1実行
│   ├── part2_upload_video.py     # Part 2実行
│   └── list_sessions.py          # セッション一覧
│
├── input/                 # 入力データ
│   └── news/              # ニュースデータ
│       └── YYYYMMDD_news.json
│
├── output/                # 出力データ
│   └── sessions/          # セッションディレクトリ
│       └── YYYYMMDD_HHMMSS/
│           ├── metadata.json
│           ├── structured_news.json
│           ├── lyrics.txt
│           ├── music.mp3        # 手動で配置
│           ├── thumbnail.jpg    # Part 2で生成
│           ├── video.mp4        # Part 2で生成
│           └── youtube_info.json
│
├── requirements.txt       # Python依存パッケージ
└── .env.example           # 環境変数サンプル
```

## 🚀 クイックスタート

### 1. インストール

#### ローカル環境の場合

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/Music_news_airi.git
cd Music_news_airi

# 依存パッケージをインストール
pip install -r requirements.txt

# 日本語フォント（字幕用）をインストール
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra
```

#### GitHub Codespacesの場合

新しいCodespace起動時は自動的にセットアップが実行されます。
認証情報の設定については [docs/09_codespace_setup.md](docs/09_codespace_setup.md) を参照してください。

**重要**: YouTube認証情報は手動で配置が必要です:
```bash
# 1. ローカルから credentials/youtube_client_secret.json をコピー
# 2. または以下のコマンドを実行して対話的にセットアップ
bash scripts/setup_credentials.sh
```

### 2. Part 1: 歌詞生成まで

```bash
# ニュースJSONを準備
# input/news/20260110_news.json

# Part 1を実行
python scripts/part1_generate_lyrics.py input/news/20260110_news.json

# 出力:
# output/sessions/20260110_HHMMSS/
#   ├── metadata.json
#   ├── structured_news.json
#   └── lyrics.txt
```

### 3. 手動作業: 音楽生成

```bash
# 1. 生成された歌詞を確認
cat output/sessions/20260110_HHMMSS/lyrics.txt

# 2. Suno AI で音楽を生成
#    https://suno.ai/

# 3. 生成したmp3をセッションディレクトリに配置
cp /path/to/generated.mp3 output/sessions/20260110_HHMMSS/music.mp3
```

### 4. Part 2: YouTube アップロードまで

```bash
# Part 2を実行（通常動画 + YouTubeショートを自動生成＆アップロード）
python scripts/part2_upload_video.py 20260110_HHMMSS

# 実行内容:
# 1. サムネイル生成（thumbnail.jpg）
# 2. 通常動画生成（video.mp4 - 横型）
# 3. YouTube通常動画アップロード（公開）
# 4. YouTubeショート生成（shorts/*.mp4 - 縦型）
#    - 30秒以上の動画は30秒ごとに分割
#    - 30秒以下は1本のショート
# 5. YouTubeショート一括アップロード（公開）
# 6. X自動投稿（環境変数が設定されている場合）
# 7. TikTok自動投稿（ショート動画を再利用、環境変数が設定されている場合）
```

### X / TikTok 自動投稿の設定

環境変数を設定すると Part 2 実行時に自動投稿が有効になります。

- X: `X_CONSUMER_KEY`, `X_CONSUMER_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`
- TikTok: `TIKTOK_ACCESS_TOKEN`, `TIKTOK_OPEN_ID`

それぞれのキーは各プラットフォームの開発者ポータルで取得してください。認証情報は `.env` などで安全に管理してください。

### テスト機能

```bash
# YouTubeショート生成のテスト（アップロードなし）
python scripts/test_shorts_generation.py \
  output/sessions/20260110_HHMMSS/music.mp3 \
  output/sessions/20260110_HHMMSS/thumbnail.jpg \
  test_shorts
```

### セッション管理

```bash
# 全セッションを表示
python scripts/list_sessions.py
```

## 📊 セッション管理

各ニュース処理は「セッション」として管理されます。

### セッションID
- フォーマット: `YYYYMMDD_HHMMSS`
- 例: `20260110_143052`

### セッションステータス
- `created`: セッション作成直後
- `lyrics_generated`: 歌詞生成完了
- `music_uploaded`: 音楽ファイル配置完了
- `video_generated`: 動画生成完了
- `youtube_uploaded`: YouTubeアップロード完了（通常動画）
- `shorts_uploaded`: YouTubeショートアップロード完了

## 🎵 ニュースJSONフォーマット

```json
{
  "title": "ニュースタイトル",
  "content": "ニュース本文（詳細な内容）",
  "source": "情報源（例: 経済産業省公式発表）",
  "date": "YYYY-MM-DD"
}
```

サンプル: `input/news/20260110_news.json`

## 📖 詳細ドキュメント

詳しい仕様や設計思想は `docs/` ディレクトリを参照してください:

- [00_philosophy.md](docs/00_philosophy.md) - プロジェクトの思想
- [01_character.md](docs/01_character.md) - あいりのキャラクター設定
- [02_news_policy.md](docs/02_news_policy.md) - ニュース取扱ポリシー
- [03_lyrics_rules.md](docs/03_lyrics_rules.md) - 歌詞生成ルール
- [06_new_architecture.md](docs/06_new_architecture.md) - システムアーキテクチャ（詳細）

## 🛠️ 実装状況

### ✅ 完了
- ✅ Part 1: ニュース評価 → 4構造化 → 歌詞生成
- ✅ セッション管理システム
- ✅ スクリプト: `part1_generate_lyrics.py`
- ✅ スクリプト: `list_sessions.py`
- ✅ Part 2: サムネイル・動画生成・YouTubeアップロード
- ✅ **YouTubeショート自動生成機能**
  - 30秒以上の動画を自動分割
  - 縦型（1080x1920）動画生成
  - 複数ショートの一括アップロード
  - すべて公開設定

### 📝 将来的な拡張
- Twitter 投稿機能
- LLM統合による高度な生成
- 分析ダッシュボード

## 🤝 コントリビューション

このプロジェクトは現在開発中です。

## 📄 ライセンス

MIT License

## 👤 作者

karasumarap

---

**音楽ニュースAI - ニュースを音楽にして、未来を一緒に考えよう**
