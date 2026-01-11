# Codespace初期セットアップガイド

## 概要
GitHub Codespacesで新しい環境を起動した際、認証情報などのシークレット情報は同期されません。
このドキュメントでは、新しいCodespace環境での初期セットアップ手順を説明します。

## 必要な認証情報

### 1. YouTube API認証情報

**必要なファイル:**
- `credentials/youtube_client_secret.json` - OAuth 2.0クライアントシークレット
- `credentials/youtube_token.json` - 認証トークン（初回認証後に自動生成）

**セットアップ手順:**

1. ローカルマシンから認証情報をコピー:
   ```bash
   # ローカルの credentials/ ディレクトリから client_secret をコピー
   # VS Code のファイルエクスプローラーにドラッグ&ドロップ、または
   # ターミナルでコピー&ペースト
   ```

2. ファイル名を確認・リネーム:
   ```bash
   # Googleからダウンロードしたファイル名が長い場合
   mv client_secret_*.json credentials/youtube_client_secret.json
   ```

3. 認証を実行:
   ```bash
   # 動画アップロードスクリプトを実行すると認証プロンプトが表示される
   python scripts/part2_upload_video.py <session_id>
   ```

## GitHub Secretsを使った自動化（推奨）

Codespaceでの認証情報管理には、GitHub Secretsを使う方法が推奨されます。

### セットアップ手順

1. **GitHub Secretsに認証情報を登録:**
   - リポジトリの Settings > Secrets and variables > Codespaces
   - "New repository secret" をクリック
   - Secret名: `YOUTUBE_CLIENT_SECRET`
   - 値: `credentials/youtube_client_secret.json` の内容全体をコピー&ペースト

2. **起動スクリプトの作成:**
   ```bash
   # .devcontainer/postCreateCommand.sh を作成（既存の場合は追記）
   ```

3. **自動セットアップスクリプト:**
   `scripts/setup_credentials.sh` を実行すると、GitHub Secretsから認証情報を自動復元

## 手動セットアップ（簡易版）

GitHub Secretsを使わない場合の手順:

1. ローカルから `credentials/` ディレクトリ全体を保存
2. 新しいCodespace起動時に以下を実行:
   ```bash
   # 1. client_secret ファイルを配置
   # VS Code のファイルエクスプローラーから credentials/ にドラッグ&ドロップ
   
   # 2. ファイル名を確認
   ls -la credentials/
   
   # 3. 必要に応じてリネーム
   mv credentials/client_secret_*.json credentials/youtube_client_secret.json
   
   # 4. 権限を確認
   chmod 600 credentials/*.json
   ```

## 自動セットアップスクリプト

新しいCodespaceで以下のコマンドを実行するだけでセットアップ完了:

```bash
bash scripts/setup_credentials.sh
```

このスクリプトは:
- GitHub Secretsから認証情報を読み込み
- `credentials/` ディレクトリを作成
- 必要なファイルを配置
- 適切な権限を設定

## トラブルシューティング

### エラー: "クライアントシークレットファイルが見つかりません"

```bash
# ファイルの存在を確認
ls -la credentials/

# ファイル名を確認
# 必要な名前: youtube_client_secret.json
```

### エラー: "認証トークンが無効"

```bash
# 古いトークンを削除して再認証
rm credentials/youtube_token.json
python scripts/part2_upload_video.py <session_id>
```

### GitHub Secretsが機能しない

```bash
# 環境変数を確認
echo $YOUTUBE_CLIENT_SECRET

# 空の場合、GitHub Secretsが正しく設定されていない
# Settings > Codespaces > Secrets を確認
```

## セキュリティベストプラクティス

1. **認証情報をGitにコミットしない**
   - `.gitignore` で `credentials/` を除外（既に設定済み）

2. **GitHub Secretsを使う**
   - Codespacesとの統合が簡単
   - 安全に認証情報を管理

3. **トークンの有効期限を定期的に更新**
   - 古いトークンは削除して再認証

4. **ファイル権限を制限**
   ```bash
   chmod 600 credentials/*.json
   ```

## 参考リンク

- [YouTube API認証設定](./07_youtube_setup.md)
- [GitHub Codespaces Secrets](https://docs.github.com/ja/codespaces/managing-your-codespaces/managing-secrets-for-your-codespaces)
