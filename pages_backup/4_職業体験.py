"""
職業体験ページ - お口の人生ゲーム（5歳以上のみ）
"""
import streamlit as st
import sys
import os
import time
from datetime import datetime

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.game_logic import apply_tooth_delta, roll_1to3
from services.store import save_game_state
from services.audio import show_audio_controls

# ページ設定
st.set_page_config(
    page_title="職業体験 - お口の人生ゲーム",
    page_icon="👩‍⚕️",
    layout="wide"
)

def get_job_experience_data():
    """職業体験データを取得"""
    return {
        1: {
            "title": "歯科医師",
            "subtitle": "CR充填体験",
            "description": "虫歯を削って、白い詰め物をする体験をしてみよう！",
            "activity": "模型の歯に樹脂を詰めて、形を整えてみましょう",
            "tools": ["CR充填材", "光照射器", "バー"],
            "video_url": "https://example.com/dentist_video",
            "icon": "🦷",
            "audio_id": "job_dentist"
        },
        2: {
            "title": "歯科衛生士", 
            "subtitle": "スケーリング体験",
            "description": "歯石を取って、歯をきれいにする体験をしてみよう！",
            "activity": "模型の歯についた歯石を専用器具で取ってみましょう",
            "tools": ["スケーラー", "エアスケーラー", "ミラー"],
            "video_url": "https://example.com/hygienist_video",
            "icon": "✨",
            "audio_id": "job_hygienist"
        },
        3: {
            "title": "歯科技工士",
            "subtitle": "人工歯排列体験", 
            "description": "入れ歯の歯を並べる体験をしてみよう！",
            "activity": "入れ歯の型に人工歯を正しく並べてみましょう",
            "tools": ["人工歯", "ワックス", "排列器具"],
            "video_url": "https://example.com/technician_video",
            "icon": "🔧",
            "audio_id": "job_technician"
        }
    }

def main():
    st.title("👩‍⚕️ 職業体験")
    
    if 'game_state' not in st.session_state:
        st.error("ゲーム状態が見つかりません。ゲームボードからやり直してください。")
        if st.button("🎲 ゲームボードに戻る"):
            st.switch_page("pages/1_ゲームボード.py")
        return
    
    game_state = st.session_state.game_state
    
    # 年齢チェック
    if st.session_state.get('participant_age', 0) < 5:
        st.warning("職業体験は5歳以上の方が対象です。")
        if st.button("⬅️ ゲームボードに戻る"):
            st.switch_page("pages/1_ゲームボード.py")
        return
    
    # 職業体験状態の初期化
    if 'job_experience_state' not in st.session_state:
        st.session_state.job_experience_state = {
            'selected_job': None,
            'completed': False,
            'start_time': None
        }
    
    job_state = st.session_state.job_experience_state
    job_data = get_job_experience_data()
    
    # 体験完了後
    if job_state['completed']:
        selected_job = job_data[job_state['selected_job']]
        
        st.success("🎉 職業体験が完了しました！")
        st.markdown(f"### {selected_job['icon']} {selected_job['title']}体験")
        
        # 報酬付与
        if not game_state.get('job_experience_done', False):
            apply_tooth_delta(game_state, 5)
            game_state['job_experience_done'] = True
            save_game_state(game_state)
            st.balloons()
            st.success("🪙 +5トゥースコインを獲得しました！")
        
        # 現在の状態表示
        col1, col2 = st.columns(2)
        with col1:
            st.metric("歯の本数", game_state['teeth_count'])
        with col2:
            st.metric("トゥースコイン", game_state['tooth_coins'])
        
        # 体験の振り返り
        st.markdown("### 📚 体験の振り返り")
        st.info(f"**{selected_job['title']}**は、{selected_job['description']}")
        
        # 音声ガイド
        if selected_job.get('audio_id'):
            show_audio_controls(selected_job['audio_id'], f"🔊 {selected_job['title']}について")
        
        # 次へ進む
        st.markdown("### ➡️ 次のステップ")
        st.info("職業体験の後は定期健診に向かいます（+3トゥースコイン）")
        
        if st.button("🏥 定期健診に進む", use_container_width=True, type="primary"):
            st.switch_page("pages/5_定期健診.py")
        
        return
    
    # 職業選択
    if job_state['selected_job'] is None:
        st.markdown("""
        ### 🎯 職業体験について
        
        歯科医療に関わる3つの職業から1つを選んで体験してみよう！
        くじを引いて、出た番号の職業を体験します。
        
        **体験完了で+5トゥースコインがもらえます！**
        """)
        
        # 現在の状態表示
        col1, col2 = st.columns(2)
        with col1:
            st.metric("歯の本数", game_state['teeth_count'])
        with col2:
            st.metric("トゥースコイン", game_state['tooth_coins'])
        
        # 職業の紹介
        st.markdown("### 👥 選べる職業")
        
        for job_id, job in job_data.items():
            with st.expander(f"{job['icon']} {job_id}. {job['title']} - {job['subtitle']}"):
                st.markdown(f"**説明:** {job['description']}")
                st.markdown(f"**体験内容:** {job['activity']}")
                st.markdown(f"**使用器具:** {', '.join(job['tools'])}")
        
        # くじ引き
        st.markdown("### 🎲 くじを引いて職業を決めよう")
        
        if st.button("🎯 くじを引く（1〜3）", use_container_width=True, type="primary"):
            selected_number = roll_1to3()
            job_state['selected_job'] = selected_number
            
            selected_job = job_data[selected_number]
            st.success(f"🎉 {selected_number}番が出ました！")
            st.info(f"**{selected_job['icon']} {selected_job['title']}** を体験します！")
            
            time.sleep(2)
            st.rerun()
        
        if st.button("⬅️ ゲームボードに戻る", use_container_width=True):
            st.switch_page("pages/1_ゲームボード.py")
        
        return
    
    # 職業体験中
    selected_job = job_data[job_state['selected_job']]
    
    st.markdown(f"### {selected_job['icon']} {selected_job['title']}体験")
    st.markdown(f"**{selected_job['subtitle']}**")
    
    # 体験説明
    st.info(selected_job['description'])
    
    # 体験内容詳細
    st.markdown("### 📋 体験内容")
    st.markdown(f"**やること:** {selected_job['activity']}")
    st.markdown(f"**使用器具:** {', '.join(selected_job['tools'])}")
    
    # 動画リンク（プレースホルダ）
    st.markdown("### 📺 参考動画")
    st.markdown(f"[{selected_job['title']}の仕事を見てみよう]({selected_job['video_url']})")
    st.warning("※実際の現場では、準備された動画や資料を使用します")
    
    # タイマー機能
    st.markdown("### ⏱️ 体験タイマー（1分間）")
    
    if job_state['start_time'] is None:
        if st.button("⏰ 体験を開始", use_container_width=True, type="primary"):
            job_state['start_time'] = datetime.now()
            st.success("体験を開始しました！1分間体験してみてください。")
            st.rerun()
    else:
        # 経過時間を表示
        elapsed = (datetime.now() - job_state['start_time']).total_seconds()
        remaining = max(0, 60 - elapsed)
        
        if remaining > 0:
            st.progress(elapsed / 60, text=f"残り時間: {int(remaining)}秒")
            
            # 自動更新のためのスペース
            time.sleep(1)
            st.rerun()
        else:
            st.success("⏰ 1分間の体験が完了しました！")
            
            if st.button("✅ 体験完了", use_container_width=True, type="primary"):
                job_state['completed'] = True
                st.rerun()
    
    # 音声ガイド
    if selected_job.get('audio_id'):
        show_audio_controls(selected_job['audio_id'], f"🔊 {selected_job['title']}の説明")
    
    # 進行状況表示（サイドバー）
    st.sidebar.markdown("### 📊 現在の状態")
    st.sidebar.metric("歯の本数", game_state['teeth_count'])
    st.sidebar.metric("トゥースコイン", game_state['tooth_coins'])
    st.sidebar.metric("現在のマス", f"{game_state['current_position'] + 1}マス目")
    
    if job_state['selected_job']:
        st.sidebar.markdown("### 👩‍⚕️ 体験中の職業")
        st.sidebar.info(f"{selected_job['icon']} {selected_job['title']}")

if __name__ == "__main__":
    main()
