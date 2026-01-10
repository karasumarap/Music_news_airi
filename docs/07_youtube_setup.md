# 07. YouTube API 設定ガイド

YouTube Data API v3 を使用して動画をアップロードするための設定手順。

## 📋 必要な準備

1. Googleアカウント
2. Google Cloud Platform（GCP）プロジェクト
3. YouTube Data API v3 の有効化
4. OAuth 2.0 認証情報の作成

## 🔧 セットアップ手順

### ステップ1: Google Cloud Platform プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
   - プロジェクト名: `music-news-ai`（任意）
   - 組織: なし（個人利用の場合）

### ステップ2: YouTube Data API v3 の有効化

1. プロジェクトダッシュボードで「APIとサービス」→「ライブラリ」を開く
2. 「YouTube Data API v3」を検索
3. 「有効にする」をクリック

### ステップ3: OAuth 2.0 認証情報の作成

#### 3-1. 同意画面の設定

1. 「APIとサービス」→「OAuth 同意画面」を開く
2. ユーザータイプを選択:
   - **外部**: 個人利用の場合はこちら
   - 内部: Google Workspace 組織内のみ
3. アプリ情報を入力:
   - アプリ名: `音楽ニュースAI`
   - ユーザーサポートメール: 自分のメールアドレス
   - デベロッパーの連絡先: 自分のメールアドレス
4. スコープの追加:
   - 「スコープを追加または削除」をクリック
   - `https://www.googleapis.com/auth/youtube.upload` を検索して追加
   - `https://www.googleapis.com/auth/youtube` を追加（オプション）
5. テストユーザーの追加:
   - 自分のGoogleアカウントを追加
6. 「保存して続行」

#### 3-2. OAuth クライアント ID の作成

1. 「APIとサービス」→「認証情報」を開く
2. 「認証情報を作成」→「OAuth クライアント ID」を選択
3. アプリケーションの種類: **デスクトップアプリ**
4. 名前: `music-news-ai-desktop`（任意）
5. 「作成」をクリック
6. **JSONファイルをダウンロード**
   - これが `client_secret.json` になります

### ステップ4: 認証情報の配置

1. ダウンロードしたJSONファイルを `credentials/` ディレクトリに配置:
   ```bash
   mkdir -p credentials
   mv ~/Downloads/client_secret_*.json credentials/youtube_client_secret.json
   ```

2. ディレクトリ構成の確認:
   ```
   Music_news_airi/
   ├── credentials/
   │   └── youtube_client_secret.json  # ← 配置
   ├── src/
   └── ...
   ```

### ステップ5: 初回認証

初回実行時に認証フローが開始されます:

1. ブラウザが自動的に開きます
2. Googleアカウントでログイン
3. 「音楽ニュースAI」へのアクセス許可を確認
4. 「許可」をクリック
5. 認証トークンが `credentials/youtube_token.json` に保存されます

## 📁 認証ファイル

### youtube_client_secret.json
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "music-news-ai",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

### youtube_token.json（自動生成）
初回認証後に自動生成されます。このファイルにアクセストークンとリフレッシュトークンが保存されます。

## 🔒 セキュリティ

### .gitignore に追加
認証情報をGitにコミットしないように設定:

```gitignore
# YouTube API 認証情報
credentials/
!credentials/.gitkeep
```

### 重要な注意事項

⚠️ **絶対に以下のファイルを公開しないでください:**
- `youtube_client_secret.json`
- `youtube_token.json`

これらのファイルが漏洩すると、あなたのYouTubeアカウントに不正アクセスされる可能性があります。

## 📊 API クォータと制限

### デフォルトのクォータ
- **1日あたり10,000ユニット**
- 動画アップロード: 1回あたり約1,600ユニット
- **1日あたり約6本の動画をアップロード可能**

### クォータの確認
1. [Google Cloud Console](https://console.cloud.google.com/)
2. 「APIとサービス」→「ダッシュボード」
3. YouTube Data API v3 の使用状況を確認

### クォータ増加のリクエスト
大量の動画をアップロードする場合:
1. Google Cloud Console で「割り当て」ページを開く
2. YouTube Data API v3 のクォータを選択
3. 「割り当ての編集」をクリック
4. リクエストを送信（審査に数日かかる場合があります）

## 🛠️ トラブルシューティング

### エラー: `The request cannot be completed because you have exceeded your quota`
- **原因**: 1日のAPIクォータを超えました
- **解決策**: 翌日まで待つか、クォータ増加をリクエスト

### エラー: `invalid_grant: Token has been expired or revoked`
- **原因**: 認証トークンが期限切れまたは無効
- **解決策**: `credentials/youtube_token.json` を削除して再認証

### エラー: `The OAuth client was not found`
- **原因**: `youtube_client_secret.json` が正しく配置されていない
- **解決策**: ファイルパスと内容を確認

### ブラウザが開かない
- **解決策**: 手動で表示されたURLにアクセス

## 📚 参考リンク

- [YouTube Data API v3 公式ドキュメント](https://developers.google.com/youtube/v3)
- [OAuth 2.0 認証フロー](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps)
- [API クォータの管理](https://developers.google.com/youtube/v3/getting-started#quota)
- [Python クライアントライブラリ](https://github.com/googleapis/google-api-python-client)

## ✅ 設定完了チェックリスト

- [ ] Google Cloud Platform プロジェクトを作成
- [ ] YouTube Data API v3 を有効化
- [ ] OAuth 同意画面を設定
- [ ] OAuth クライアント ID を作成
- [ ] `youtube_client_secret.json` を `credentials/` に配置
- [ ] `.gitignore` に `credentials/` を追加
- [ ] 初回認証を完了（`youtube_token.json` が生成される）

設定が完了したら、動画アップロード機能を使用できます！
