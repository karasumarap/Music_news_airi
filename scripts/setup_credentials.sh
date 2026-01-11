#!/bin/bash
# Codespace初期セットアップスクリプト
# GitHub Secretsから認証情報を自動復元

set -e

echo "🚀 Codespace初期セットアップを開始..."

# credentials ディレクトリを作成
mkdir -p credentials

# GitHub Secretsから認証情報を復元
if [ -n "$YOUTUBE_CLIENT_SECRET" ]; then
    echo "📝 YouTube認証情報を復元中..."
    echo "$YOUTUBE_CLIENT_SECRET" > credentials/youtube_client_secret.json
    chmod 600 credentials/youtube_client_secret.json
    echo "✅ YouTube Client Secret を配置しました"
else
    echo "⚠️  環境変数 YOUTUBE_CLIENT_SECRET が設定されていません"
    echo "   手動で credentials/youtube_client_secret.json を配置してください"
    echo "   詳細: docs/09_codespace_setup.md を参照"
fi

# YouTube Token が環境変数にある場合は復元
if [ -n "$YOUTUBE_TOKEN" ]; then
    echo "📝 YouTube認証トークンを復元中..."
    echo "$YOUTUBE_TOKEN" > credentials/youtube_token.json
    chmod 600 credentials/youtube_token.json
    echo "✅ YouTube Token を配置しました"
fi

# 他のシークレットもここに追加可能
# 例: Suno API キー
if [ -n "$SUNO_API_KEY" ]; then
    echo "📝 Suno API設定を復元中..."
    # config.py または .env に書き込む処理
fi

echo ""
echo "✨ セットアップ完了！"
echo ""
echo "📋 確認:"
ls -lh credentials/ 2>/dev/null || echo "   credentials/ ディレクトリにファイルがありません"
echo ""

if [ ! -f credentials/youtube_client_secret.json ]; then
    echo "⚠️  次のステップ:"
    echo "   1. ローカルの credentials/youtube_client_secret.json をこのワークスペースにコピー"
    echo "   2. または GitHub Secrets で YOUTUBE_CLIENT_SECRET を設定"
    echo ""
    echo "詳細: docs/09_codespace_setup.md を参照"
fi
