"""
音楽ニュースAI - メイン実行スクリプト
1コマンドでニュースから歌詞までを生成する
"""

import sys
import logging
import os
from pathlib import Path

# 環境変数を読み込む
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("✅ .env ファイルを読み込みました")
except ImportError:
    logging.info("ℹ️ python-dotenvがインストールされていません。環境変数は直接設定してください。")

# srcモジュールをインポートできるようにパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.utils import load_json, save_json, save_text, validate_news_data, get_timestamp
from src.news_evaluator import evaluate_news
from src.structure_converter import convert_to_structure
from src.lyrics_generator import generate_lyrics
from src.music_prompt_generator import generate_music_prompt, generate_music_title
from src.suno_client import create_suno_client

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """バナーを表示する"""
    banner = """
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║      音楽ニュースAI - あいり              ║
    ║      ニュースを音楽にして届けるよ！        ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """メイン処理"""
    try:
        print_banner()
        logger.info("🚀 音楽ニュースAI を起動します")
        
        # 設定を読み込み、ディレクトリを作成
        config = Config()
        config.ensure_directories()
        logger.info(f"📁 ディレクトリを確認しました")
        
        # ========================================
        # 1. ニュースを読み込む
        # ========================================
        input_file = config.INPUT_DIR / "sample_news.json"
        logger.info(f"📰 ニュースを読み込みます: {input_file}")
        
        if not input_file.exists():
            logger.error(f"❌ ニュースファイルが見つかりません: {input_file}")
            logger.error("input/sample_news.json を作成してください")
            return 1
        
        news = load_json(input_file)
        
        # ニュースデータの検証
        if not validate_news_data(news):
            logger.error("❌ ニュースデータの形式が正しくありません")
            return 1
        
        logger.info(f"📰 ニュースタイトル: {news['title']}")
        
        # ========================================
        # 2. ニュースを評価する
        # ========================================
        logger.info("📊 ニュースを評価します")
        evaluation = evaluate_news(news)
        
        logger.info(f"スコア: {evaluation['total_score']:.2f} / 100")
        logger.info(f"理由: {evaluation['reason']}")
        
        if not evaluation["is_suitable"]:
            logger.warning("⚠️ このニュースは音楽化に適していません")
            logger.warning("別のニュースを試してください")
            
            # 評価結果だけは保存する
            output_file = config.OUTPUT_DIR / "evaluation_only.json"
            save_json(output_file, {
                "news": news,
                "evaluation": evaluation,
                "timestamp": get_timestamp(),
            })
            return 0
        
        logger.info("✅ このニュースは音楽化に適しています！")
        
        # ========================================
        # 3. 4構造に変換する
        # ========================================
        logger.info("🔄 ニュースを4構造に変換します")
        structured_news = convert_to_structure(news)
        
        logger.info("✅ Fact/Meaning/Impact/Question の構造化が完了しました")
        
        # ========================================
        # 4. 歌詞を生成する
        # ========================================
        logger.info("🎵 歌詞を生成します")
        lyrics = generate_lyrics(structured_news)
        
        logger.info("✅ 歌詞の生成が完了しました")
        
        # ========================================
        # 5. 音楽を生成する（Phase 2）
        # ========================================
        logger.info("🎵 音楽を生成します（Suno AI）")
        
        # 音楽プロンプトを生成
        music_prompt = generate_music_prompt(structured_news, lyrics)
        music_title = generate_music_title(structured_news)
        
        logger.info(f"🎨 音楽タイトル: {music_title}")
        logger.info(f"🎨 音楽スタイル: {music_prompt}")
        
        # Suno AIクライアントを作成
        suno_client = create_suno_client()
        
        # 音楽を生成
        music_result = suno_client.generate_music(
            lyrics=lyrics,
            prompt=music_prompt,
            title=music_title,
            metadata={
                "date": news.get("date"),
                "source": news.get("source"),
                "category": news.get("category", "news")
            }
        )
        
        # 音楽ファイルをダウンロード
        if music_result.get("success") and music_result.get("audio_url"):
            audio_output_file = config.OUTPUT_DIR / "music.mp3"
            download_success = suno_client.download_audio(
                music_result["audio_url"],
                audio_output_file
            )
            if download_success:
                music_result["music_file"] = str(audio_output_file)
        
        # ========================================
        # 6. 出力する
        # ========================================
        logger.info("💾 結果を保存します")
        
        # 構造化されたニュースをJSONで保存
        structured_output_file = config.OUTPUT_DIR / "structured_news.json"
        
        if music_result.get("success"):
            if music_result.get("dev_mode"):
                print(f"  - output/music.mp3 (モックファイル)")
                print(f"\n💡 音楽生成について:")
                print("  現在は開発モードで実行されています")
                print("  実際に音楽を生成するには:")
                print("  1. .env.example を .env にコピー")
                print("  2. .env に SUNO_API_KEY=your_key を設定")
                print("  3. .env で DEV_MODE=false に設定")
                print("  4. pip install requests を実行")
            else:
                print(f"  - {music_result.get('music_file', 'output/music.mp3')}")
                print(f"\n🎵 音楽情報:")
                print(f"  タイトル: {music_result.get('title', 'N/A')}")
                print(f"  時間: {music_result.get('duration', 'N/A')}秒")
                print(f"  URL: {music_result.get('audio_url', 'N/A')}")
        
        print(f"\n🎵 生成された歌詞のプレビュー:")
        print("-"*50)
        print(lyrics)

        print("-"*50)
        
        if music_result.get("mock"):
            print(f"\n💡 音楽生成について:")
            print("  現在はモックモードで実行されています")
            print("  実際に音楽を生成するには:")
            print("  1. pip install -r requirements.txt")
            print("  2. .env.sample を .env にコピー")
            print("  3. .env に SUNO_API_KEY を設定")
            print("  4. .env で MUSIC_GENERATION_ENABLED=true に設定")
        elif music_result.get("success"):
            print(f"\n🎵 音楽情報:")
            print(f"  タイトル: {music_result.get('title', 'N/A')}")
            print(f"  スタイル: {music_result.get('style', 'N/A')}")
            if music_result.get("duration"):
                print(f"  長さ: {music_result.get('duration', 0)}秒")
        
        print(f"\n💡 次のステップ（将来実装）:")
        print("  1. ✅ 音楽生成（Suno AI）← Phase 2 完了！")
        print("  2. 動画生成（MV自動生成）")
        print("  3. 投稿（YouTube / Twitter等）")
        print("")
        
        logger.info("🎉 処理が正常に完了しました")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ ユーザーによって中断されました")
        return 130
    except Exception as e:
        logger.error(f"❌ エラーが発生しました: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
