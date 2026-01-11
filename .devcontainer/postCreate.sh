#!/bin/bash
# Codespace作成後に自動実行されるスクリプト

set -e

echo "🚀 Codespace環境をセットアップ中..."

# Pythonパッケージのインストール
echo "📦 Pythonパッケージをインストール..."
pip install -r requirements.txt

# 日本語フォントのインストール
echo "🈯 日本語フォントをインストール..."
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra fonts-takao-gothic fonts-ipafont-gothic fonts-ipafont-mincho

# FFmpegの確認（通常は既にインストール済み）
if ! command -v ffmpeg &> /dev/null; then
    echo "🎬 FFmpegをインストール..."
    sudo apt-get install -y ffmpeg
fi

# 必要なディレクトリを作成
echo "📁 ディレクトリ構造を作成..."
mkdir -p credentials
mkdir -p input/news
mkdir -p output/sessions

# GitHub Secretsから認証情報を復元
echo "🔑 認証情報をセットアップ..."
bash scripts/setup_credentials.sh

echo ""
echo "✅ Codespace環境のセットアップ完了！"
echo ""
echo "📋 次のステップ:"
echo "   1. credentials/ に認証情報があることを確認"
echo "   2. python run.py でパイプライン実行"
echo ""
