"""
ページ間共通ユーティリティ
"""
import streamlit as st
import json
from typing import Dict


def navigate_to(page_name: str):
    """ページ遷移"""
    st.session_state.current_page = page_name
    st.rerun()


def load_settings() -> Dict:
    """設定ファイルを読み込み"""
    try:
        with open('data/settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"staff_pin": "0418", "debug_mode": False}


def debug_log(message: str):
    """デバッグモードが有効な場合のみ出力"""
    settings = load_settings()
    if settings.get("debug_mode", False):
        print(message)


def load_events_config() -> Dict:
    """イベント設定を読み込み"""
    try:
        with open('data/events.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading events.json: {e}")
        return {
            "events": [{"id": "default", "name": "デフォルト", "description": "通常設定",
                       "board_file": "board_main.json"}],
            "active_event": "default"
        }


def save_active_event(event_id: str) -> bool:
    """アクティブイベントを保存"""
    try:
        events_data = load_events_config()
        events_data["active_event"] = event_id
        with open('data/events.json', 'w', encoding='utf-8') as f:
            json.dump(events_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving active event: {e}")
        return False


def get_board_file_for_age(age: int) -> str:
    """ボードファイルパスを返す（イベント設定を考慮）
    
    Note: 将来的にPINコードでゲーム種類を切り替える機能を追加予定
    """
    events_data = load_events_config()
    active_event_id = events_data.get("active_event", "default")
    events = events_data.get("events", [])
    
    # アクティブイベントを検索
    active_event = None
    for event in events:
        if event["id"] == active_event_id:
            active_event = event
            break
    
    # デフォルトのボードファイル（統一）
    if not active_event:
        return "data/board_main.json"
    
    # イベント設定のボードを使用
    return f"data/{active_event.get('board_file', 'board_main.json')}"
