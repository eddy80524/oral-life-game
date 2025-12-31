"""
おしごとたいけんページ
"""
import streamlit as st
import time
import random
from datetime import datetime
from pages.utils import navigate_to, debug_log, load_settings


def show_job_experience_page():
    """おしごとたいけんページ（ルーレット機能付き）"""
    try:
        from services.image_helper import display_image
    except ImportError:
        display_image = None
    
    if display_image:
        display_image("board", "cell_13", "", fill='stretch')
    
    # 職業データ
    jobs = [
        {"id": "dentist", "name": "はいしゃさん", "emoji": "🦷"},
        {"id": "hygienist", "name": "しかえいせいしさん", "emoji": "✨"},
        {"id": "technician", "name": "しかぎこうしさん", "emoji": "🔧"}
    ]
    
    # ルーレットの状態管理
    if 'job_roulette_state' not in st.session_state or st.session_state.job_roulette_state is None:
        st.session_state.job_roulette_state = 'idle'
    
    if 'job_roulette_result' not in st.session_state:
        st.session_state.job_roulette_result = None
    
    if 'job_timer_start' not in st.session_state:
        st.session_state.job_timer_start = None
    
    if 'job_force_complete' not in st.session_state:
        st.session_state.job_force_complete = False
    
    if 'job_force_complete_unlocked' not in st.session_state:
        st.session_state.job_force_complete_unlocked = False
    
    roulette_state = st.session_state.job_roulette_state
    result = st.session_state.job_roulette_result
    
    # ルーレット初期状態
    if roulette_state == 'idle' or roulette_state is None:
        st.markdown("<p style='text-align:center; font-size:1.2em; color:#5d4037; margin:20px 0;'>どの おしごとに ちょうせんするか ルーレットできめよう！</p>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, (col, job) in enumerate(zip(cols, jobs)):
            with col:
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #fff8ec, #ffebd4);
                    border: 3px solid #d6c5a5;
                    border-radius: 20px;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                '>
                    <div style='font-size: 4em; margin: 10px 0;'>{job["emoji"]}</div>
                    <div style='font-size: 1.1em; font-weight: bold; color: #5d4037; margin: 10px 0;'>{job["name"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:2vh'></div>", unsafe_allow_html=True)
        
        if st.button("🎰 ルーレットをまわす", key="start_job_roulette", use_container_width=True, type="primary"):
            st.session_state.job_roulette_state = 'spinning'
            st.rerun()
    
    # ルーレット回転中
    elif roulette_state == 'spinning':
        st.markdown("<p style='text-align:center; font-size:1.2em; color:#ff6b6b;'>🎰 ルーレット ちゅう…</p>", unsafe_allow_html=True)
        
        card_placeholder = st.empty()
        
        animation_sequence = [random.randint(0, 2) for _ in range(12)]
        final_result = random.randint(0, 2)
        animation_sequence.append(final_result)
        
        for active_idx in animation_sequence:
            with card_placeholder.container():
                cols = st.columns(3)
                for idx, (col, job) in enumerate(zip(cols, jobs)):
                    with col:
                        border_color = "#ff6b6b" if idx == active_idx else "#d6c5a5"
                        box_shadow = "0 0 30px rgba(255, 107, 107, 0.6)" if idx == active_idx else "0 4px 8px rgba(0,0,0,0.1)"
                        transform = "scale(1.1)" if idx == active_idx else "scale(1)"
                        
                        st.markdown(f"""
                        <div style='
                            background: linear-gradient(135deg, #fff8ec, #ffebd4);
                            border: 3px solid {border_color};
                            border-radius: 20px;
                            padding: 20px;
                            text-align: center;
                            box-shadow: {box_shadow};
                            transform: {transform};
                            transition: all 0.3s ease;
                            height: 200px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        '>
                            <div style='font-size: 4em; margin: 10px 0;'>{job["emoji"]}</div>
                            <div style='font-size: 1.1em; font-weight: bold; color: #5d4037; margin: 10px 0;'>{job["name"]}</div>
                        </div>
                        """, unsafe_allow_html=True)
            time.sleep(0.15)
        
        st.session_state.job_roulette_result = final_result
        st.session_state.job_roulette_state = 'result'
        st.rerun()
    
    # 結果表示
    elif roulette_state == 'result' and result is not None:
        selected_job = jobs[result]
        
        st.success(f"🎉 {selected_job['name']} にきまったよ！")
        
        cols = st.columns(3)
        for idx, (col, job) in enumerate(zip(cols, jobs)):
            with col:
                if idx == result:
                    border_color = "#4CAF50"
                    background = "linear-gradient(135deg, #d4f4dd, #c8e6c9)"
                    box_shadow = "0 0 30px rgba(76, 175, 80, 0.6)"
                else:
                    border_color = "#d6c5a5"
                    background = "linear-gradient(135deg, #fff8ec, #ffebd4)"
                    box_shadow = "0 4px 8px rgba(0,0,0,0.1)"
                
                st.markdown(f"""
                <div style='
                    background: {background};
                    border: 3px solid {border_color};
                    border-radius: 20px;
                    padding: 20px;
                    text-align: center;
                    box-shadow: {box_shadow};
                    height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                '>
                    <div style='font-size: 4em; margin: 10px 0;'>{job["emoji"]}</div>
                    <div style='font-size: 1.1em; font-weight: bold; color: #5d4037; margin: 10px 0;'>{job["name"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:2vh'></div>", unsafe_allow_html=True)
        st.info(f"これから {selected_job['name']}の おしごとを たいけんするよ！")
        
        # タイマー表示（5分）
        if st.session_state.job_timer_start is None:
            if st.button("⏱️ たいけん スタート！", key="start_job_timer", use_container_width=True, type="primary"):
                st.session_state.job_timer_start = datetime.now()
                st.session_state.job_force_complete = False
                st.rerun()
        else:
            start_time = st.session_state.job_timer_start
            elapsed = (datetime.now() - start_time).total_seconds()
            # 設定から読み込み
            settings = load_settings()
            game_config = settings.get('game', {})
            time_limit = game_config.get('job_experience_timer_seconds', 300)
            remaining = max(0, time_limit - elapsed)
            
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            
            st.markdown(f"""
            <div style='text-align:center; background:#fff3cd; border:3px solid #ffc107; 
                        border-radius:15px; padding:20px; margin:20px 0;'>
                <p style='font-size:1.2em; color:#856404; margin:0 0 10px 0;'>⏱️ のこり じかん</p>
                <p style='font-size:2.5em; font-weight:bold; color:#856404; margin:0;'>
                    {minutes:02d}:{seconds:02d}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # スタッフ用強制完了機能
            if not st.session_state.job_force_complete_unlocked:
                with st.expander("⚙️ スタッフ用"):
                    from services.store import get_settings
                    settings = get_settings()
                    staff_pin = settings.get("staff_pin", "0418")
                    
                    pin = st.text_input("スタッフ用パスコード", type="password", key="job_force_pin")
                    if st.button("体験を完了にする", key="job_force_check", type="secondary"):
                        if pin == str(staff_pin):
                            st.session_state.job_force_complete_unlocked = True
                            st.session_state.job_force_complete = True
                            st.success("体験が即座に完了しました！")
                            st.rerun()
                        else:
                            st.error("PINがちがうよ。もういちど確認してね。")
            
            if st.session_state.get('job_force_complete'):
                st.success("⚡ スタッフによって体験が即座に完了しました！")
                remaining = 0
            elif remaining > 0:
                time.sleep(1)
                st.rerun()
            else:
                st.success("⏰ 5ふん たっせい！ おしごとたいけん かんりょう！")
                
            # 完了ボタン
            if st.button("✅ たいけん かんりょう", key="finish_job", use_container_width=True, type="primary"):
                if 'game_state' in st.session_state:
                    game_state = st.session_state.game_state
                    
                    # 設定から報酬を取得
                    settings = load_settings()
                    rewards = settings.get('game', {}).get('rewards', {})
                    
                    if st.session_state.get('job_force_complete'):
                        reward = rewards.get('job_force_complete', 10)
                    elif remaining > 0:
                        reward = rewards.get('job_complete_on_time', 10)
                    else:
                        reward = rewards.get('job_complete_late', 5)
                    
                    game_state['tooth_coins'] = game_state.get('tooth_coins', 10) + reward
                    
                    game_state['action_taken'] = True
                    game_state['action_completed'] = True
                
                st.session_state.job_roulette_state = None
                st.session_state.job_roulette_result = None
                st.session_state.job_timer_start = None
                st.session_state.job_force_complete = False
                st.session_state.job_force_complete_unlocked = False
                st.session_state.job_experience_completed = True
                
                navigate_to('game_board')
                st.rerun()


def auto_complete_job_experience(cell_position: int) -> None:
    """物理シャッフル済み前提でデジタル体験をスキップ"""
    if st.session_state.get('job_auto_processed_cell') == cell_position:
        return
    reward = st.session_state.get('job_auto_reward', 5)
    game_state = st.session_state.get('game_state')
    if game_state:
        game_state['tooth_coins'] = game_state.get('tooth_coins', 0) + reward
        game_state['action_taken'] = True
        game_state['action_completed'] = True
    st.session_state.job_experience_completed = True
    st.session_state.job_auto_processed_cell = cell_position
    st.session_state.job_auto_last_reward = reward
