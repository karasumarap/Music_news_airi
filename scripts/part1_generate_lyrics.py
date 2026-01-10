"""
Part 1: ニュースから歌詞生成まで
入力: ニュースJSON
出力: セッションディレクトリ（歌詞含む）
"""

import sys
import logging
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.session_manager import SessionManager, format_session_info, get_next_step_message
from src.config import Config
from src.utils import load_json, save_json, save_text
from src.news_evaluator import evaluate_news
from src.structure_converter import convert_to_structure
from src.lyrics_generator import generate_lyrics

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
    ║      Part 1: 歌詞生成                     ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """
    print(banner)


def validate_news_json(news_data: dict) -> bool:
    """
    ニュースJSONの必須フィールドを検証
    
    Args:
        news_data: ニュースデータ
        
    Returns:
        bool: 有効かどうか
    """
    required_fields = ["title", "content", "source", "date"]
    
    for field in required_fields:
        if field not in news_data:
            logger.error(f"❌ 必須フィールド '{field}' が見つかりません")
            return False
    
    return True


def main():
    """メイン処理"""
    print_banner()
    
    # コマンドライン引数をチェック
    if len(sys.argv) < 2:
        print("使い方: python scripts/part1_generate_lyrics.py <ニュースJSONファイル>")
        print("例: python scripts/part1_generate_lyrics.py input/news/20260110_news.json")
        sys.exit(1)
    
    news_file = Path(sys.argv[1])
    
    # ファイル存在確認
    if not news_file.exists():
        logger.error(f"❌ ファイルが見つかりません: {news_file}")
        sys.exit(1)
    
    logger.info(f"📰 ニュース読み込み: {news_file}")
    
    try:
        # ニュースを読み込み
        news_data = load_json(str(news_file))
        
        # 検証
        if not validate_news_json(news_data):
            logger.error("❌ ニュースJSONの形式が不正です")
            sys.exit(1)
        
        logger.info(f"📰 ニュースタイトル: {news_data['title']}")
        logger.info(f"📰 ソース: {news_data['source']}")
        logger.info(f"📰 日付: {news_data['date']}")
        
        # セッション管理を初期化
        session_manager = SessionManager()
        
        # ステップ1: ニュース評価
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("ステップ1: ニュース評価")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        evaluation = evaluate_news(news_data)
        
        logger.info(f"📊 評価スコア: {evaluation['total_score']}")
        logger.info(f"📊 音楽化に適しているか: {evaluation['is_suitable']}")
        logger.info(f"📊 理由: {evaluation['reason']}")
        
        # 評価が低い場合は警告
        if not evaluation['is_suitable']:
            logger.warning("⚠️ このニュースは音楽化に適していません")
            logger.warning("⚠️ それでも続行しますか？ (yes/no)")
            
            response = input().strip().lower()
            if response not in ['yes', 'y']:
                logger.info("❌ 処理を中止しました")
                sys.exit(0)
        
        # セッション作成
        session = session_manager.create_session(
            news_title=news_data['title'],
            news_source=news_data['source'],
            news_date=news_data['date'],
            evaluation_score=int(evaluation['total_score']),
            is_suitable=evaluation['is_suitable']
        )
        
        session_dir = session_manager.get_session_dir(session.session_id)
        logger.info(f"✅ セッション作成: {session.session_id}")
        logger.info(f"📁 ディレクトリ: {session_dir}")
        
        # ステップ2: 4構造化
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("ステップ2: 4構造化（Fact/Meaning/Impact/Question）")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        structured = convert_to_structure(news_data)
        
        logger.info(f"✅ Fact: {structured['fact']['summary']}")
        logger.info(f"✅ Meaning: {structured['meaning']['summary']}")
        logger.info(f"✅ Impact: ポジティブ {len(structured['impact']['positive'])}件、ネガティブ {len(structured['impact']['negative'])}件")
        logger.info(f"✅ Question: {structured['question']['main_question']}")
        
        # 構造化データを保存
        structured_file = session_dir / "structured_news.json"
        save_json(
            str(structured_file),
            {
                "news": news_data,
                "evaluation": evaluation,
                "structure": structured
            }
        )
        logger.info(f"💾 構造化データ保存: {structured_file.name}")
        
        # ステップ3: 歌詞生成
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("ステップ3: 歌詞生成")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        lyrics = generate_lyrics(structured)
        
        # 歌詞を保存
        lyrics_file = session_dir / "lyrics.txt"
        save_text(str(lyrics_file), lyrics)
        logger.info(f"💾 歌詞保存: {lyrics_file.name}")
        
        # プレビュー表示
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("生成された歌詞（プレビュー）:")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # 最初の10行を表示
        lines = lyrics.split('\n')
        for i, line in enumerate(lines[:10], 1):
            print(f"  {line}")
        
        if len(lines) > 10:
            print(f"  ... (残り {len(lines) - 10} 行)")
        
        # セッション更新
        session = session_manager.update_session(
            session.session_id,
            status="lyrics_generated"
        )
        
        # 結果表示
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("✅ Part 1 完了")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        print("\n" + format_session_info(session))
        print(get_next_step_message(session))
        
    except Exception as e:
        logger.error(f"❌ エラーが発生しました: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
