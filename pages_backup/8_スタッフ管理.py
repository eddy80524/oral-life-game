"""
スタッフ管理ページ - お口の人生ゲーム
"""
import streamlit as st
import sys
import os
import json
from datetime import datetime, timedelta

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.store import (
    get_participant_stats, 
    clear_leaderboard, 
    reset_participant_count,
    get_leaderboard,
    load_settings,
    save_settings
)

# ページ設定
st.set_page_config(
    page_title="スタッフ管理 - お口の人生ゲーム",
    page_icon="⚙️",
    layout="wide"
)

def check_staff_auth():
    """スタッフ認証チェック"""
    if 'staff_authenticated' not in st.session_state:
        st.session_state.staff_authenticated = False
    
    return st.session_state.staff_authenticated

def staff_login():
    """スタッフログイン"""
    st.title("🔐 スタッフ管理ログイン")
    
    settings = load_settings()
    correct_pin = settings.get('staff_pin', '0418')
    
    st.markdown("### 認証が必要です")
    st.info("スタッフ管理機能にアクセスするには、PINコードを入力してください。")
    
    pin_input = st.text_input("PINコード", type="password", max_chars=4)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔓 ログイン", use_container_width=True, type="primary"):
            if pin_input == correct_pin:
                st.session_state.staff_authenticated = True
                st.success("✅ 認証成功！")
                st.rerun()
            else:
                st.error("❌ PINコードが正しくありません")
    
    with col2:
        if st.button("🏠 メインページに戻る", use_container_width=True):
            st.switch_page("pages/0_受付_プロローグ.py")

def staff_dashboard():
    """スタッフダッシュボード"""
    st.title("⚙️ スタッフ管理ダッシュボード")
    
    # ログアウトボタン
    if st.button("🔒 ログアウト", use_container_width=False):
        st.session_state.staff_authenticated = False
        st.rerun()
    
    # 概況表示
    st.markdown("### 📊 運営状況")
    
    stats = get_participant_stats()
    leaderboard = get_leaderboard(limit=10)
    
    # メイン統計
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("総参加者数", stats['total_count'])
    
    with stat_col2:
        today = datetime.now().strftime('%Y-%m-%d')
        today_count = stats['daily_counts'].get(today, 0)
        st.metric("本日の参加者", today_count)
    
    with stat_col3:
        # 現在プレイ中の推定数（簡易）
        active_sessions = len([key for key in st.session_state.keys() if key.startswith('game_state')])
        st.metric("稼働中組数", active_sessions)
    
    with stat_col4:
        # 平均所要時間（ダミー計算）
        if leaderboard:
            avg_time = "15-30分"  # 実際は過去のデータから計算
        else:
            avg_time = "データなし"
        st.metric("平均所要時間", avg_time)
    
    # 詳細統計
    st.markdown("### 📈 詳細統計")
    
    detail_col1, detail_col2 = st.columns(2)
    
    with detail_col1:
        st.markdown("**日別参加者数（直近7日）**")
        
        # 直近7日のデータを表示
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            count = stats['daily_counts'].get(date, 0)
            st.write(f"{date}: {count}人")
    
    with detail_col2:
        st.markdown("**ランキング上位5位**")
        
        if leaderboard:
            for i, record in enumerate(leaderboard[:5]):
                if record.get('ranking_consent', False):
                    rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                    st.write(f"{rank_emoji} {record['participant_name']}: {record['total_score']}pt")
        else:
            st.info("ランキングデータがありません")
    
    # 管理操作
    st.markdown("### 🛠️ 管理操作")
    
    # 設定管理
    st.markdown("#### ⚙️ システム設定")
    
    settings = load_settings()
    
    setting_col1, setting_col2 = st.columns(2)
    
    with setting_col1:
        new_pin = st.text_input("スタッフPIN変更", value=settings.get('staff_pin', '0418'), max_chars=4)
        
        board_options = ["5plus", "under5"]
        current_board = settings.get('current_board', '5plus')
        selected_board = st.selectbox("使用ボード", board_options, index=board_options.index(current_board))
        
        if st.button("💾 設定を保存", use_container_width=True):
            new_settings = {
                'staff_pin': new_pin,
                'current_board': selected_board,
                'last_updated': datetime.now().isoformat()
            }
            if save_settings(new_settings):
                st.success("✅ 設定を保存しました")
            else:
                st.error("❌ 設定の保存に失敗しました")
    
    with setting_col2:
        st.markdown("**現在の設定:**")
        st.info(f"スタッフPIN: {settings.get('staff_pin', '0418')}")
        st.info(f"使用ボード: {settings.get('current_board', '5plus')}")
        
        if settings.get('last_updated'):
            last_updated = datetime.fromisoformat(settings['last_updated'])
            st.info(f"最終更新: {last_updated.strftime('%Y-%m-%d %H:%M')}")
    
    # データ管理
    st.markdown("#### 🗃️ データ管理")
    
    data_col1, data_col2, data_col3 = st.columns(3)
    
    with data_col1:
        if st.button("🗑️ ランキングクリア", use_container_width=True, type="secondary"):
            if st.checkbox("本当にクリアしますか？"):
                if clear_leaderboard():
                    st.success("✅ ランキングをクリアしました")
                    st.rerun()
                else:
                    st.error("❌ クリアに失敗しました")
    
    with data_col2:
        if st.button("🔄 参加者数リセット", use_container_width=True, type="secondary"):
            if st.checkbox("本当にリセットしますか？"):
                if reset_participant_count():
                    st.success("✅ 参加者数をリセットしました")
                    st.rerun()
                else:
                    st.error("❌ リセットに失敗しました")
    
    with data_col3:
        if st.button("🔧 QR nonce再発行", use_container_width=True):
            # QRコードのnonce再発行（実装は簡略化）
            st.info("💡 QRコードのnonceを再発行しました（ダミー）")
    
    # セッション管理
    st.markdown("#### 👥 セッション管理")
    
    session_col1, session_col2 = st.columns(2)
    
    with session_col1:
        st.markdown("**現在のセッション状態:**")
        
        game_sessions = 0
        for key in st.session_state.keys():
            if 'game_state' in key:
                game_sessions += 1
        
        st.info(f"アクティブなゲームセッション: {game_sessions}")
        
        # セッション詳細
        if game_sessions > 0:
            with st.expander("セッション詳細"):
                for key, value in st.session_state.items():
                    if isinstance(value, dict) and 'current_position' in value:
                        st.write(f"位置: {value['current_position'] + 1}マス目")
                        st.write(f"歯: {value.get('teeth_count', 0)}本")
                        st.write(f"コイン: {value.get('tooth_coins', 0)}枚")
                        st.write("---")
    
    with session_col2:
        if st.button("🔄 全セッションクリア", use_container_width=True, type="secondary"):
            if st.checkbox("全てのセッションをクリアしますか？"):
                # セッション状態をクリア
                keys_to_delete = []
                for key in st.session_state.keys():
                    if any(prefix in key for prefix in ['game_state', 'quiz_state', 'job_experience', 'checkup', 'goal']):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del st.session_state[key]
                
                st.success("✅ 全セッションをクリアしました")
                st.rerun()
    
    # システム情報
    st.markdown("### 💻 システム情報")
    
    system_col1, system_col2 = st.columns(2)
    
    with system_col1:
        st.markdown("**ファイル状況:**")
        
        data_files = {
            "参加者データ": "data/participants.json",
            "ランキング": "data/leaderboard.json",
            "ボード(5歳以上)": "data/board_main_5plus.json",
            "ボード(5歳未満)": "data/board_main_under5.json",
            "クイズ": "data/quizzes.json",
            "音声": "data/audio_manifest.json"
        }
        
        for name, path in data_files.items():
            if os.path.exists(path):
                file_size = os.path.getsize(path)
                st.success(f"✅ {name}: {file_size}bytes")
            else:
                st.error(f"❌ {name}: ファイル不存在")
    
    with system_col2:
        st.markdown("**メモリ使用量:**")
        
        session_keys = len(st.session_state.keys())
        st.info(f"セッションキー数: {session_keys}")
        
        # 簡易的なメモリ使用量表示
        import sys
        total_size = sys.getsizeof(st.session_state)
        st.info(f"概算メモリ使用量: {total_size} bytes")

def main():
    if not check_staff_auth():
        staff_login()
    else:
        staff_dashboard()

if __name__ == "__main__":
    main()
