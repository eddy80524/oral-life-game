"""
ゴール・ランキングページ
"""
import streamlit as st
import os
import uuid
from datetime import datetime
from typing import Dict
from pages.utils import navigate_to
from services.store import log_player_session


def _build_session_record(game_state: dict) -> Dict[str, any]:
    """セッション記録を構築"""
    session_id = st.session_state.setdefault('session_uid', str(uuid.uuid4()))
    participant_name = st.session_state.get('participant_name') or "匿名"
    age = st.session_state.get('participant_age', 5)
    age_group = "under5" if age < 5 else "5plus"
    start_time = game_state.get('start_time')
    if isinstance(start_time, datetime):
        elapsed = datetime.now() - start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        play_time = f"{minutes}分{seconds}秒"
        start_time_str = start_time.isoformat()
    else:
        play_time = game_state.get('play_time', "0分0秒")
        start_time_str = start_time
    return {
        "session_id": session_id,
        "participant_name": participant_name,
        "participant_age": age,
        "age_group": age_group,
        "board": age_group,
        "teeth_count": game_state.get('teeth_count', 0),
        "tooth_coins": game_state.get('tooth_coins', 0),
        "turn_count": game_state.get('turn_count', 0),
        "play_time": play_time,
        "start_time": start_time_str,
        "reached_goal": game_state.get('reached_goal', False),
        "caries_correct": game_state.get('caries_correct_count', 0),
        "perio_correct": game_state.get('perio_correct_count', 0),
        "final_position": game_state.get('current_position', 0),
    }


def show_goal_page():
    """ゴール・ランキングページ"""
    from services.store import load_leaderboard, save_score
    
    st.markdown("### 🏁 ゲームクリア！")
    
    player_rank = None
    player_score = 0
    
    if 'game_state' in st.session_state:
        game_state = st.session_state.game_state
        
        # Save session log
        if not st.session_state.get('session_log_saved'):
            record = _build_session_record(game_state)
            if log_player_session(record):
                st.session_state.session_log_saved = True
        
        # Display player's results prominently
        st.markdown("---")
        st.markdown("### 🎉 あなたのけっか")
        
        col1, col2, col3 = st.columns(3)
        teeth_count = game_state.get('teeth_count', 20)
        coins = game_state.get('tooth_coins', 10000)
        player_score = teeth_count * 10 + coins
        
        with col1:
            st.metric("さいしゅうはのかず", f"{teeth_count}ほん")
        with col2:
            st.metric("トゥースコイン", f"{coins}まい")
        with col3:
            st.metric("ごうけいスコア", f"{player_score}てん")
        
        st.success("おめでとう！")
        
        # Save to leaderboard if not already saved
        if not st.session_state.get('score_saved'):
            player_data = {
                "player_name": st.session_state.get('participant_name', '匿名'),
                "participant_age": st.session_state.get('participant_age', 5),
                "age_group": "under5" if st.session_state.get('participant_age', 5) < 5 else "5plus",
                "teeth_count": teeth_count,
                "tooth_coins": coins,
                "play_time": "0分0秒"
            }
            if save_score(player_data):
                st.session_state.score_saved = True
        
        # Display leaderboard
        st.markdown("---")
        st.markdown("### 🏆 トップ10ランキング")
        
        leaderboard = load_leaderboard(top_n=10)
        
        if leaderboard:
            player_name = st.session_state.get('participant_name', '匿名')
            for idx, entry in enumerate(leaderboard):
                if entry.get('player_name') == player_name and entry.get('score') == player_score:
                    player_rank = idx + 1
                    break
            
            for idx, entry in enumerate(leaderboard):
                rank = idx + 1
                is_player = (rank == player_rank)
                
                medal = ""
                if rank == 1:
                    medal = "🥇"
                elif rank == 2:
                    medal = "🥈"
                elif rank == 3:
                    medal = "🥉"
                else:
                    medal = f"{rank}い"
                
                if is_player:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #FFE5D4, #FFF8F0); 
                                border: 2px solid #f3c9a9; 
                                border-radius: 12px; 
                                padding: 12px; 
                                margin: 8px 0;
                                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                display: flex;
                                flex-wrap: wrap;
                                justify-content: space-between;
                                align-items: center;
                                gap: 8px;">
                        <div style="font-size: 1.2em; font-weight: bold;">{medal} {entry.get('player_name', '匿名')}</div>
                        <div style="font-size: 1.1em; color: #c25b2a; display: flex; gap: 10px; flex-wrap: wrap;">
                            <span style="white-space: nowrap;">🦷 {entry.get('teeth_count', 0)}ほん</span>
                            <span style="white-space: nowrap;">💰 {entry.get('tooth_coins', 0)}まい</span>
                            <span style="white-space: nowrap;">🏆 {entry.get('score', 0)}てん</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="border-bottom: 1px solid #eee; 
                                padding: 10px 5px; 
                                display: flex; 
                                flex-wrap: wrap; 
                                justify-content: space-between; 
                                align-items: center; 
                                gap: 5px;">
                        <div style="font-weight: bold; color: #444;">{medal} {entry.get('player_name', '匿名')}</div>
                        <div style="color: #666; font-size: 0.95em; display: flex; gap: 10px; flex-wrap: wrap;">
                            <span style="white-space: nowrap;">🦷 {entry.get('teeth_count', 0)}ほん</span>
                            <span style="white-space: nowrap;">💰 {entry.get('tooth_coins', 0)}まい</span>
                            <span style="white-space: nowrap;">🏆 {entry.get('score', 0)}てん</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("まだだれもゴールしていないよ！")
    
    st.markdown("---")
    if st.button("📱 LINEページへ", use_container_width=True, type="secondary"):
        navigate_to('line_coloring')


def show_line_coloring_page():
    """LINE・ぬりえページ"""
    from pages.utils import load_events_config
    
    # イベント設定を確認
    events_data = load_events_config()
    active_event_id = events_data.get("active_event", "default")
    
    # 埼玉イベント以外の場合のみスムージープレゼントを表示
    if active_event_id != "saitama_0131":
        st.markdown("### 🎁 イベント・プレゼント")
        
        banner_path = "assets/images/event_banner.png"
        if os.path.exists(banner_path):
            st.image(banner_path, use_column_width=True)
        else:
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                margin-bottom: 20px;
                color: #fff;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            '>
                <h2 style='margin:0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>🥤 国産野菜・果物スムージー</h2>
                <p style='font-size: 1.2em; font-weight: bold; margin: 10px 0;'>無料プレゼントキャンペーン中！</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 📱 公式SNSをフォローしよう！")
    st.info("お得な情報やイベントのお知らせをお届けします！")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <a href="https://www.instagram.com/okuchi_channel?igsh=MW5ranZ1djU5a2F4Mw%3D%3D&utm_source=qr" target="_blank" style="text-decoration: none;">
            <div style='
                background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
                color: white;
                padding: 15px 10px;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            '>
                📷 Instagram<br>フォローする
            </div>
        </a>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <a href="https://liff.line.me/2007961525-kYlrjMnn/ts/01kazsr2kph000yybtnpxzmcqn" target="_blank" style="text-decoration: none;">
            <div style='
                background: #00B900;
                color: white;
                padding: 15px 10px;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            '>
                💬 LINE<br>友達追加
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:2vh'></div>", unsafe_allow_html=True)
    
    if st.button("🏠 さいしょからあそぶ", use_container_width=True, type="primary"):
        for key in list(st.session_state.keys()):
            if key not in ['current_page']:
                del st.session_state[key]
        navigate_to('reception')
