"""
スタッフ管理ページ
"""
import streamlit as st
import json
from pages.utils import navigate_to, load_events_config, save_active_event, load_settings


def show_staff_management_page():
    """スタッフ管理ページ"""
    st.markdown("### ⚙️ スタッフ管理")
    
    # イベント設定を読み込み
    events_data = load_events_config()
    events = events_data.get("events", [])
    active_event_id = events_data.get("active_event", "default")
    
    # 設定ファイルから管理者PINを読み込み
    settings = load_settings()
    admin_pin = settings.get("staff_pin", "0418")
    
    # PIN認証
    pin = st.text_input("PINコード", type="password", help="イベントPINまたは管理者PIN")
    
    # PINでイベントを検索
    matched_event = None
    for event in events:
        if event.get("pin") == pin:
            matched_event = event
            break
    
    is_admin = (pin == admin_pin)
    is_event_pin = (matched_event is not None)
    
    if is_event_pin and not is_admin:
        # イベントPINで認証 → そのイベントに自動切り替え
        st.success(f"✅ イベント「{matched_event['name']}」として認証")
        
        if matched_event["id"] != active_event_id:
            save_active_event(matched_event["id"])
            st.info(f"🔄 ボードを「{matched_event['name']}」に切り替えました")
            st.rerun()
        
        st.markdown("---")
        st.markdown("#### 📋 現在のイベント設定")
        st.info(f"📋 {matched_event.get('description', '')}")
        st.text(f"ボードファイル: {matched_event.get('board_file', 'board_main.json')}")
        
        st.markdown("---")
        st.markdown("#### 🛠️ データ管理")
        
        if st.button("🗑️ 全データリセット", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("データをリセットしました")
            navigate_to('reception')
    
    elif is_admin:
        # 管理者PIN → フル管理画面
        st.success("✅ 管理者として認証")
        
        # イベント設定セクション
        st.markdown("---")
        st.markdown("#### 📅 イベント設定")
        
        # イベント選択
        event_names = [e["name"] for e in events]
        event_ids = [e["id"] for e in events]
        
        current_index = 0
        if active_event_id in event_ids:
            current_index = event_ids.index(active_event_id)
        
        selected_name = st.selectbox(
            "使用するイベント",
            event_names,
            index=current_index
        )
        
        selected_index = event_names.index(selected_name)
        selected_event = events[selected_index]
        
        # 選択したイベントの詳細表示
        st.info(f"📋 {selected_event.get('description', '')}")
        st.text(f"ボードファイル: {selected_event.get('board_file', 'board_main.json')}")
        st.text(f"PIN: {selected_event.get('pin', '-')}")
        
        # イベント変更ボタン
        if selected_event["id"] != active_event_id:
            if st.button("✅ このイベントに変更", use_container_width=True):
                save_active_event(selected_event["id"])
                st.success(f"イベントを「{selected_name}」に変更しました！")
                st.rerun()
        
        st.markdown("---")
        st.markdown("#### 🛠️ データ管理")
        
        if st.button("🗑️ 全データリセット", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("データをリセットしました")
            navigate_to('reception')
            
        st.markdown("---")
        
        if st.button("🏆 ランキングリセット", use_container_width=True):
            from services.store import clear_leaderboard
            if clear_leaderboard():
                st.success("ランキングをリセットしました")
            else:
                st.error("ランキングのリセットに失敗しました")
    
    elif pin:
        st.error("❌ PINコードが正しくありません")
    
    if st.button("🏠 メインページに戻る"):
        navigate_to('reception')
