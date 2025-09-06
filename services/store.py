"""
データ保存サービス（ローカルJSON）
将来Firebase Firestoreに切り替え可能
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st

# データファイルのパス
LEADERBOARD_FILE = "data/leaderboard.json"
PARTICIPANTS_FILE = "data/participants.json"
SETTINGS_FILE = "data/settings.json"

def ensure_data_files():
    """データファイルが存在することを確認"""
    os.makedirs("data", exist_ok=True)
    
    # リーダーボードファイル
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # 参加者カウントファイル
    if not os.path.exists(PARTICIPANTS_FILE):
        with open(PARTICIPANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"total_count": 0, "daily_counts": {}}, f, ensure_ascii=False, indent=2)
    
    # 設定ファイル
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"staff_pin": "0418", "current_board": "5plus"}, f, ensure_ascii=False, indent=2)

def save_score(player_data: Dict) -> bool:
    """スコアをリーダーボードに保存"""
    try:
        ensure_data_files()
        
        # 既存のデータを読み込み
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            leaderboard = json.load(f)
        
        # 新しいスコアを追加
        score_entry = {
            "player_name": player_data.get("player_name", "匿名"),
            "age_group": player_data.get("age_group", ""),
            "teeth_count": player_data.get("teeth_count", 0),
            "tooth_coins": player_data.get("tooth_coins", 0),
            "play_time": player_data.get("play_time", "0分0秒"),
            "timestamp": datetime.now().isoformat(),
            "score": player_data.get("teeth_count", 0) * 10 + player_data.get("tooth_coins", 0)  # 合計スコア
        }
        
        leaderboard.append(score_entry)
        
        # スコアでソート（降順）、同点の場合は先着順
        leaderboard.sort(key=lambda x: (-x["score"], x["timestamp"]))
        
        # トップ100のみ保持
        leaderboard = leaderboard[:100]
        
        # ファイルに保存
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        st.error(f"スコア保存エラー: {e}")
        return False

def load_leaderboard(top_n: int = 5) -> List[Dict]:
    """リーダーボードを読み込み"""
    try:
        ensure_data_files()
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            leaderboard = json.load(f)
        return leaderboard[:top_n]
    except Exception as e:
        st.error(f"リーダーボード読み込みエラー: {e}")
        return []

def increment_participant_count() -> int:
    """参加者数をインクリメント"""
    try:
        ensure_data_files()
        
        with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 総数をインクリメント
        data["total_count"] += 1
        
        # 日別カウント
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in data["daily_counts"]:
            data["daily_counts"][today] = 0
        data["daily_counts"][today] += 1
        
        with open(PARTICIPANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return data["total_count"]
    except Exception as e:
        st.error(f"参加者カウントエラー: {e}")
        return 0

def get_participant_stats() -> Dict:
    """参加者統計を取得"""
    try:
        ensure_data_files()
        with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = data["daily_counts"].get(today, 0)
        
        return {
            "total": data["total_count"],
            "today": today_count,
            "daily_counts": data["daily_counts"]
        }
    except Exception as e:
        st.error(f"統計取得エラー: {e}")
        return {"total": 0, "today": 0, "daily_counts": {}}

def reset_all_data():
    """全データをリセット"""
    try:
        # 空のファイルで上書き
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        with open(PARTICIPANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"total_count": 0, "daily_counts": {}}, f, ensure_ascii=False, indent=2)
        
        st.success("すべてのデータがリセットされました")
        return True
    except Exception as e:
        st.error(f"リセットエラー: {e}")
        return False

def get_settings() -> Dict:
    """設定を取得"""
    try:
        ensure_data_files()
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"設定読み込みエラー: {e}")
        return {"staff_pin": "0418", "current_board": "5plus"}

def save_settings(settings: Dict) -> bool:
    """設定を保存"""
    try:
        ensure_data_files()
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"設定保存エラー: {e}")
        return False

def save_game_state(game_state: Dict) -> bool:
    """ゲーム状態を保存（セッション内のみ）"""
    try:
        # Streamlitのセッション状態に保存
        st.session_state.game_state = game_state
        return True
    except Exception as e:
        st.error(f"ゲーム状態保存エラー: {e}")
        return False

def load_game_state() -> Optional[Dict]:
    """ゲーム状態を読み込み"""
    try:
        return st.session_state.get('game_state', None)
    except Exception as e:
        st.error(f"ゲーム状態読み込みエラー: {e}")
        return None

def save_game_result(result_data: Dict) -> bool:
    """ゲーム結果をリーダーボードに保存"""
    try:
        ensure_data_files()
        
        # リーダーボードを読み込み
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            leaderboard = json.load(f)
        
        # 新しい結果を追加
        leaderboard.append(result_data)
        
        # スコア順でソート（降順）
        leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
        
        # ファイルに保存
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=2)
        
        return True
    
    except Exception as e:
        st.error(f"結果保存エラー: {e}")
        return False

def get_leaderboard(limit: int = 10) -> List[Dict]:
    """リーダーボードを取得"""
    try:
        ensure_data_files()
        
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            leaderboard = json.load(f)
        
        # スコア順でソート（降順）
        leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
        
        return leaderboard[:limit]
    
    except Exception as e:
        st.error(f"リーダーボード読み込みエラー: {e}")
        return []

def clear_leaderboard() -> bool:
    """リーダーボードをクリア"""
    try:
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"リーダーボードクリアエラー: {e}")
        return False

def reset_participant_count() -> bool:
    """参加者数をリセット"""
    try:
        with open(PARTICIPANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"total_count": 0, "daily_counts": {}}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"参加者数リセットエラー: {e}")
        return False

def update_participant_count() -> bool:
    """参加者数を更新"""
    try:
        ensure_data_files()
        
        # 現在のデータを読み込み
        with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 総数を増加
        data['total_count'] += 1
        
        # 今日の日付で増加
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in data['daily_counts']:
            data['daily_counts'][today] = 0
        data['daily_counts'][today] += 1
        
        # ファイルに保存
        with open(PARTICIPANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    
    except Exception as e:
        st.error(f"参加者数更新エラー: {e}")
        return False
