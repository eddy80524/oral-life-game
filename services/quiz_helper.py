"""
クイズデータの読み込みと管理を担当するヘルパーモジュール
"""
import json
import os
from pathlib import Path


def get_quiz_file_path(quiz_type: str, age: int) -> Path:
    """
    年齢に応じたクイズファイルのパスを取得する
    
    Args:
        quiz_type: 'caries' または 'perio'
        age: 参加者の年齢
    
    Returns:
        クイズJSONファイルのパス
    """
    age_suffix = 'under5' if age < 5 else '5plus'
    filename = f"quiz_{quiz_type}_{age_suffix}.json"
    
    # dataディレクトリのパスを取得
    current_dir = Path(__file__).parent.parent
    data_dir = current_dir / 'data'
    
    return data_dir / filename


def load_quiz_data(quiz_type: str, age: int) -> dict:
    """
    クイズデータをJSONファイルから読み込む
    
    Args:
        quiz_type: 'caries'（むし歯）または 'perio'（歯周病）
        age: 参加者の年齢
    
    Returns:
        クイズデータの辞書
    """
    try:
        file_path = get_quiz_file_path(quiz_type, age)
        
        if not file_path.exists():
            print(f"⚠️ Quiz file not found: {file_path}")
            return get_default_quiz_data(quiz_type, age)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
        
        # データの妥当性チェック
        if not validate_quiz_data(quiz_data):
            print(f"⚠️ Invalid quiz data in {file_path}")
            return get_default_quiz_data(quiz_type, age)
        
        return quiz_data
    
    except Exception as e:
        print(f"❌ Error loading quiz data: {e}")
        return get_default_quiz_data(quiz_type, age)


def validate_quiz_data(quiz_data: dict) -> bool:
    """
    クイズデータの構造を検証する
    
    Args:
        quiz_data: 検証するクイズデータ
    
    Returns:
        有効な場合True
    """
    required_keys = ['title', 'questions', 'rewards']
    
    # 必須キーの存在チェック
    if not all(key in quiz_data for key in required_keys):
        return False
    
    # questionsが配列であることを確認
    if not isinstance(quiz_data['questions'], list) or len(quiz_data['questions']) == 0:
        return False
    
    # 各問題の必須フィールドをチェック
    question_required_keys = ['id', 'text', 'type', 'options', 'correct']
    for question in quiz_data['questions']:
        if not all(key in question for key in question_required_keys):
            return False
    
    # rewardsの構造をチェック
    if not isinstance(quiz_data['rewards'], dict):
        return False
    
    if 'high_score' not in quiz_data['rewards'] or 'low_score' not in quiz_data['rewards']:
        return False
    
    return True


def get_default_quiz_data(quiz_type: str, age: int) -> dict:
    """
    デフォルトのクイズデータを返す（フォールバック用）
    
    Args:
        quiz_type: 'caries' または 'perio'
        age: 参加者の年齢
    
    Returns:
        デフォルトのクイズデータ
    """
    if quiz_type == 'caries':
        if age < 5:
            return {
                "title": "むしばクイズ",
                "questions": [
                    {
                        "id": "q1",
                        "text": "からだのなかで いちばんかたいものは？",
                        "type": "single_choice",
                        "options": ["あたま", "せなか", "は"],
                        "correct": 2,
                        "explanation": "はは、からだのなかで いちばんかたいんだよ。",
                        "correct_feedback": "せいかい！",
                        "incorrect_feedback": "ざんねん…"
                    }
                ],
                "rewards": {
                    "high_score": {"threshold": 1, "coins": 5, "position": 10, "message": "すごい！"},
                    "low_score": {"coins": -3, "position": 7, "message": "がんばろう！"}
                }
            }
        else:
            return {
                "title": "むし歯クイズ",
                "questions": [
                    {
                        "id": "q1",
                        "text": "体の中で一番硬いものは何でしょう？",
                        "type": "single_choice",
                        "options": ["頭", "背骨", "歯"],
                        "correct": 2,
                        "explanation": "歯は体の中で最も硬い組織です。",
                        "correct_feedback": "正解！",
                        "incorrect_feedback": "残念…"
                    }
                ],
                "rewards": {
                    "high_score": {"threshold": 1, "coins": 5, "position": 10, "message": "素晴らしい！"},
                    "low_score": {"coins": -3, "position": 7, "message": "頑張りましょう！"}
                }
            }
    
    elif quiz_type == 'perio':
        if age < 5:
            return {
                "title": "はぐきクイズ",
                "questions": [
                    {
                        "id": "q1",
                        "text": "はみがきしないと どこから ちがでる？",
                        "type": "single_choice",
                        "options": ["は", "はぐき", "した"],
                        "correct": 1,
                        "explanation": "はぐきから ちがでるよ。",
                        "correct_feedback": "せいかい！",
                        "incorrect_feedback": "ざんねん…"
                    }
                ],
                "rewards": {
                    "high_score": {"threshold": 1, "coins": 5, "position": 10, "message": "すごい！"},
                    "low_score": {"coins": -3, "position": 7, "message": "がんばろう！"}
                }
            }
        else:
            return {
                "title": "歯周病クイズ",
                "questions": [
                    {
                        "id": "q1",
                        "text": "歯みがきしないと どこから 血が出る？",
                        "type": "single_choice",
                        "options": ["歯", "歯ぐき", "舌"],
                        "correct": 1,
                        "explanation": "歯ぐきから血が出ます。",
                        "correct_feedback": "正解！",
                        "incorrect_feedback": "残念…"
                    }
                ],
                "rewards": {
                    "high_score": {"threshold": 1, "coins": 5, "position": 10, "message": "素晴らしい！"},
                    "low_score": {"coins": -3, "position": 7, "message": "頑張りましょう！"}
                }
            }
    
    # 想定外のquiz_typeの場合
    return {
        "title": "クイズ",
        "questions": [],
        "rewards": {
            "high_score": {"threshold": 1, "coins": 5, "position": 10, "message": "お疲れ様！"},
            "low_score": {"coins": 0, "position": 0, "message": "お疲れ様！"}
        }
    }
