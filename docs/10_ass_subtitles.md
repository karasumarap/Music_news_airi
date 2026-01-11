# ASS字幕対応完了 🎉

## 問題の解決

### 1. 文字化け問題 ✅
- **原因**: 日本語フォントが不足
- **解決**: 以下のフォントをインストール
  - Noto Sans CJK JP（Google製、高品質）
  - IPAフォント
  - Takaフォント

```bash
sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra \
  fonts-takao-gothic fonts-ipafont-gothic fonts-ipafont-mincho
```

### 2. ASS形式への移行 ✅
- **SRT形式の制限**: 基本的なスタイルのみ
- **ASS形式の利点**:
  - リッチなスタイル（グラデーション、影、アウトライン）
  - エフェクト（フェードイン/アウト、アニメーション）
  - 完全なフォント制御
  - 透明度コントロール

## 実装内容

### 新機能: `generate_ass()` メソッド

[src/subtitle_generator.py](src/subtitle_generator.py)に追加：

```python
subtitle_gen = SubtitleGenerator()
ass_path = subtitle_gen.generate_ass(
    lyrics=lyrics,
    output_path="subtitles.ass",
    duration=70.0,
    # リッチスタイル設定
    font_name="Noto Sans CJK JP Bold",
    font_size=56,
    primary_color="&H00FFFFFF",      # 白
    outline_color="&H00000000",      # 黒アウトライン
    back_color="&HA0000000",         # 半透明黒背景
    outline=4.0,                      # 太いアウトライン
    shadow=2.5,                       # シャドウ
    bold=True,
    fade_in=0.4,                      # フェードイン効果
    fade_out=0.4                      # フェードアウト効果
)
```

### ASS形式の特徴

**スタイル定義**:
```
Style: Default,Noto Sans CJK JP Bold,56,&H00FFFFFF,&H0000FFFF,
       &H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,4.0,2.5,2,20,20,50,1
```

**エフェクト付き字幕**:
```
Dialogue: 0,0:00:00.00,0:00:04.11,Default,,0,0,0,,{\fad(400,400)}今日のニュース、お届けします
```

- `{\fad(400,400)}`: 400msのフェードイン/アウト
- タグを使って様々なエフェクトを追加可能

### 色コード（ASS形式）

ASS形式は `&HAABBGGRR` 形式：
- **AA**: 透明度（00=不透明、FF=透明）
- **BB**: 青
- **GG**: 緑  
- **RR**: 赤

例：
- `&H00FFFFFF` = 白（不透明）
- `&HA0000000` = 黒（透明度40%）
- `&H000000FF` = 赤
- `&H0000FF00` = 緑
- `&H00FF0000` = 青

## テスト結果

### 生成されたファイル

```
output/test_subtitles/
├── music_dummy.mp3              # 1.7MB - 70秒音声
├── thumbnail.jpg                # 57KB - サムネイル
├── subtitles.srt                # 1.1KB - SRT字幕
├── subtitles.ass                # 2.2KB - ASS字幕 ⭐
├── video_no_subtitles.mp4       # 316KB - 字幕なし
├── video_with_srt_subtitles.mp4 # 406KB - SRT字幕
└── video_with_ass_subtitles.mp4 # 1.2MB - ASS字幕 ⭐リッチ
```

### ファイルサイズ比較

- **SRT字幕動画**: 406KB
- **ASS字幕動画**: 1.2MB（高品質レンダリングのため）

ASS字幕は複雑なレンダリングが必要なため、ファイルサイズが大きくなりますが、
視覚的な品質は大幅に向上しています。

## 使用方法

### 基本的な使用

```python
from src.subtitle_generator import SubtitleGenerator
from src.video_generator import VideoGenerator

# 1. ASS字幕を生成
subtitle_gen = SubtitleGenerator()
ass_path = subtitle_gen.generate_ass(
    lyrics=lyrics,
    output_path="subtitles.ass",
    duration=70.0
)

# 2. ASS字幕付き動画を生成
video_gen = VideoGenerator()
video_path = video_gen.generate_with_subtitles(
    audio_path="music.mp3",
    image_path="thumbnail.jpg",
    subtitle_path=ass_path,  # .ass拡張子を自動検出
    output_path="video.mp4"
)
```

### カスタムスタイル

```python
# 派手なネオンスタイル
ass_path = subtitle_gen.generate_ass(
    lyrics=lyrics,
    output_path="subtitles.ass",
    duration=70.0,
    font_name="Noto Sans CJK JP Black",
    font_size=64,
    primary_color="&H0000FFFF",      # シアン
    outline_color="&H00FF00FF",      # マゼンタアウトライン
    back_color="&HC0000000",         # 濃い半透明背景
    outline=5.0,
    shadow=3.0,
    bold=True,
    fade_in=0.5,
    fade_out=0.5
)
```

## ASS vs SRT 比較

| 機能 | SRT | ASS |
|------|-----|-----|
| 基本テキスト | ✅ | ✅ |
| タイミング精度 | 良い | 非常に良い |
| フォント指定 | 限定的 | 完全制御 |
| 色・スタイル | 基本のみ | フル制御 |
| アウトライン | 固定 | カスタム可能 |
| 影・グロー | なし | あり |
| フェード効果 | なし | あり ⭐ |
| アニメーション | なし | 可能 |
| 透明度 | なし | あり ⭐ |
| ファイルサイズ | 小 | 中 |
| 互換性 | 高 | 高（FFmpeg） |

## 推奨設定

### YouTube向け
```python
font_size=52,
primary_color="&H00FFFFFF",      # 白
outline_color="&H00000000",      # 黒
back_color="&HA0000000",         # 半透明黒
outline=3.5,
shadow=2.0,
margin_v=45
```

### アニメ風
```python
font_name="Noto Sans CJK JP Bold",
font_size=58,
primary_color="&H00FFFFFF",
outline_color="&H00000000",
back_color="&HC0000000",
outline=4.5,
shadow=2.5,
bold=True
```

### クリーン・ミニマル
```python
font_size=48,
primary_color="&H00FFFFFF",
outline_color="&H00000000",
back_color="&H60000000",         # 薄い背景
outline=2.5,
shadow=1.0,
bold=False
```

## トラブルシューティング

### 日本語が表示されない
```bash
# フォントを確認
fc-list :lang=ja

# フォントがない場合はインストール
sudo apt-get install fonts-noto-cjk
```

### 字幕が表示されない
- ASSファイルがUTF-8エンコーディングか確認
- フォント名が正確か確認（`fc-list`で確認）
- FFmpegのエラーメッセージを確認

### フォントサイズが合わない
- 動画解像度に応じて調整が必要
- 1280x720: font_size=52推奨
- 1920x1080: font_size=78推奨
- 3840x2160: font_size=156推奨

## 今後の拡張可能性

1. **カラオケモード**: 
   ```
   {\k100}今{\k50}日{\k80}の...
   ```
   
2. **ポジションアニメーション**:
   ```
   {\move(x1,y1,x2,y2)}
   ```

3. **回転エフェクト**:
   ```
   {\frz360}テキスト
   ```

4. **グラデーション**:
   - 複数色のグラデーション適用

5. **ルビ（ふりがな）**:
   - ASS形式で実装可能

---

**実装完了**: 2026年1月11日  
**テスト**: ✅ 全機能正常動作
