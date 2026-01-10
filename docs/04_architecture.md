# 04. システムアーキテクチャ

## 全体フロー

```
[Input: ニュース]
    ↓
[1. ニュース評価・選別]
    ↓
[2. 4構造への変換]
   (Fact / Meaning / Impact / Question)
    ↓
[3. 歌詞生成]
    ↓
[4. 音楽生成] ← 今回は未実装
    ↓
[5. 動画生成] ← 今回は未実装
    ↓
[6. 投稿] ← 今回は未実装
    ↓
[Output: JSON + lyrics.txt]
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
│   ├── 04_architecture.md
│   └── 05_todo.md
├── src/                     # ソースコード
│   ├── __init__.py
│   ├── news_evaluator.py    # ニュース評価・選別
│   ├── structure_converter.py  # 4構造への変換
│   ├── lyrics_generator.py  # 歌詞生成
│   ├── config.py            # 設定
│   └── utils.py             # ユーティリティ
├── input/                   # 入力データ
│   └── sample_news.json     # サンプルニュース
├── output/                  # 出力データ
│   ├── structured_news.json # 構造化されたニュース
│   └── lyrics.txt           # 生成された歌詞
├── tests/                   # テスト（将来実装）
│   └── test_*.py
├── run.py                   # メイン実行スクリプト
└── requirements.txt         # 依存関係
```

## モジュール詳細

### 1. news_evaluator.py
**役割：** ニュースを評価し、音楽化に適しているかを判定する

**入力：**
```json
{
  "title": "ニュースタイトル",
  "content": "ニュース本文",
  "source": "情報源",
  "date": "2026-01-10"
}
```

**出力：**
```json
{
  "is_suitable": true,
  "score": 85,
  "reason": "社会的影響が大きく、若い世代に関連がある"
}
```

**評価基準：**
- 社会的重要度
- 若年層への関連性
- 情報の確実性
- センセーショナル度（低いほど良い）

### 2. structure_converter.py
**役割：** ニュースを4構造（Fact/Meaning/Impact/Question）に変換する

**入力：** news_evaluator.pyの出力 + 元のニュース

**出力：**
```json
{
  "fact": {
    "summary": "何が起きたか（1文）",
    "details": ["詳細1", "詳細2", "詳細3"]
  },
  "meaning": {
    "summary": "何を意味するか（1文）",
    "context": "背景や文脈"
  },
  "impact": {
    "positive": ["ポジティブな影響1", "ポジティブな影響2"],
    "negative": ["ネガティブな影響1", "ネガティブな影響2"],
    "uncertain": ["不確定要素1", "不確定要素2"]
  },
  "question": {
    "main_question": "メインの問いかけ",
    "sub_questions": ["サブの問い1", "サブの問い2"]
  }
}
```

### 3. lyrics_generator.py
**役割：** 4構造から歌詞を生成する

**入力：** structure_converter.pyの出力

**出力：**
```text
[Intro]
ねえ、聞いて
今日、大きなニュースがあったんだ

[Verse 1]
2026年の1月に
政府が発表したのは
...

[Chorus]
...

[Outro]
一緒に、未来を作ろう
```

**生成ルール：**
- docs/03_lyrics_rules.md に従う
- 妹キャラの口調を厳守
- 断定しない、煽らない

### 4. config.py
**役割：** 設定を一元管理

```python
class Config:
    # キャラクター設定
    CHARACTER_NAME = "あいり"
    CHARACTER_AGE = 16
    
    # ニュース評価設定
    MIN_SCORE_THRESHOLD = 70
    
    # 歌詞生成設定
    MAX_LYRICS_LENGTH = 50  # 行数
    
    # ファイルパス
    INPUT_DIR = "input/"
    OUTPUT_DIR = "output/"
```

### 5. utils.py
**役割：** 共通ユーティリティ

- JSONファイルの読み書き
- ログ出力
- エラーハンドリング

### 6. run.py
**役割：** メイン実行スクリプト

```python
def main():
    # 1. ニュースを読み込む
    news = load_news("input/sample_news.json")
    
    # 2. ニュースを評価する
    evaluation = evaluate_news(news)
    
    if not evaluation["is_suitable"]:
        print("このニュースは音楽化に適していません")
        return
    
    # 3. 4構造に変換する
    structured = convert_to_structure(news)
    
    # 4. 歌詞を生成する
    lyrics = generate_lyrics(structured)
    
    # 5. 出力する
    save_json("output/structured_news.json", structured)
    save_text("output/lyrics.txt", lyrics)
    
    print("✅ 完了！")
```

## 拡張ポイント（将来実装）

### Phase 2: 音楽生成
- Suno AI / Udio との連携
- プロンプト生成ロジック
- 音楽ファイルのダウンロード

### Phase 3: 動画生成
- キャラクター画像生成（Stable Diffusion等）
- リップシンク
- 字幕生成
- 動画編集

### Phase 4: 投稿自動化
- YouTube自動投稿
- Twitter/X 連携
- TikTok 連携

### Phase 5: フィードバック学習
- リスナーの反応を分析
- 歌詞生成の改善
- キャラクターの成長

## 今回の実装範囲
- ✅ ニュース評価・選別
- ✅ 4構造への変換
- ✅ 歌詞生成
- ✅ JSON出力
- ❌ 音楽生成（Phase 2）
- ❌ 動画生成（Phase 3）
- ❌ 投稿（Phase 4）

## 技術スタック
- 言語：Python 3.10+
- データ形式：JSON
- モック実装：APIキーは不要
- 将来のAPI連携：OpenAI / Anthropic / Suno / Udio
