"""
ゴール・ランキングページ - お口の人生ゲーム
"""
import streamlit as st
import sys
import os
import json
from datetime import datetime

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.game_logic import calculate_play_time
from services.store import save_game_result, get_leaderboard, update_participant_count
from services.audio import show_audio_controls

# ページ設定
st.set_page_config(
    page_title="ゴール・ランキング - お口の人生ゲーム",
    page_icon="🏁",
    layout="wide"
)

def calculate_final_score(game_state):
    """最終スコアを計算"""
    teeth_score = game_state['teeth_count'] * 10  # 歯1本 = 10ポイント
    tooth_coin_score = game_state['tooth_coins']   # トゥースコイン = 1ポイント
    
    # ボーナスポイント
    bonus_score = 0
    if game_state['teeth_count'] >= 20:
        bonus_score += 50  # 歯を多く保てたボーナス
    if game_state['tooth_coins'] >= 20:
        bonus_score += 30  # トゥースコインボーナス
    
    total_score = teeth_score + tooth_coin_score + bonus_score
    
    return {
        'teeth_score': teeth_score,
        'tooth_coin_score': tooth_coin_score,
        'bonus_score': bonus_score,
        'total_score': total_score
    }

def main():
    st.title("🏁 ゴール・ランキング")
    
    if 'game_state' not in st.session_state:
        st.error("ゲーム状態が見つかりません。ゲームボードからやり直してください。")
        if st.button("🏠 最初に戻る"):
            st.switch_page("pages/0_受付_プロローグ.py")
        return
    
    game_state = st.session_state.game_state
    
    # ゴール状態の初期化
    if 'goal_state' not in st.session_state:
        st.session_state.goal_state = {
            'result_saved': False,
            'ranking_consent': None
        }
    
    goal_state = st.session_state.goal_state
    
    st.markdown("### 🎉 ゲームクリア！おめでとうございます！")
    
    # 音声ガイド
    show_audio_controls("goal_congratulations", "🔊 ゴールの挨拶")
    
    # 最終結果表示
    play_time = calculate_play_time(game_state['start_time'])
    score_data = calculate_final_score(game_state)
    
    st.markdown("### 📊 最終結果")
    
    # メイン結果表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🦷 最終歯数",
            f"{game_state['teeth_count']}本",
            delta=f"{game_state['teeth_count'] - 20:+d}本"
        )
    
    with col2:
        st.metric(
            "🪙 トゥースコイン",
            f"{game_state['tooth_coins']}枚",
            delta=f"{game_state['tooth_coins'] - 10:+d}枚"
        )
    
    with col3:
        st.metric(
            "⏰ プレイ時間",
            play_time
        )
    
    # スコア詳細
    st.markdown("### 🏆 スコア詳細")
    
    score_col1, score_col2 = st.columns(2)
    
    with score_col1:
        st.markdown("**スコア内訳:**")
        st.write(f"歯の本数: {game_state['teeth_count']}本 × 10 = {score_data['teeth_score']}ポイント")
        st.write(f"トゥースコイン: {game_state['tooth_coins']}枚 = {score_data['tooth_coin_score']}ポイント")
        st.write(f"ボーナス: {score_data['bonus_score']}ポイント")
        st.markdown(f"**合計: {score_data['total_score']}ポイント**")
    
    with score_col2:
        st.markdown("**ボーナス条件:**")
        if game_state['teeth_count'] >= 20:
            st.success("✅ 歯数維持ボーナス: +50ポイント")
        else:
            st.info("⚪ 歯数維持ボーナス: 20本以上で+50ポイント")
        
        if game_state['tooth_coins'] >= 20:
            st.success("✅ トゥースコインボーナス: +30ポイント")
        else:
            st.info("⚪ トゥースコインボーナス: 20枚以上で+30ポイント")
    
    # ランキング掲載の同意確認
    if goal_state['ranking_consent'] is None:
        st.markdown("### 📋 ランキング掲載について")
        st.info("トップ5ランキングに掲載してもよろしいですか？（ニックネームが表示されます）")
        
        consent_col1, consent_col2 = st.columns(2)
        
        with consent_col1:
            if st.button("✅ 掲載に同意する", use_container_width=True, type="primary"):
                goal_state['ranking_consent'] = True
                st.success("ランキング掲載に同意いただきありがとうございます！")
                st.rerun()
        
        with consent_col2:
            if st.button("❌ 掲載しない", use_container_width=True):
                goal_state['ranking_consent'] = False
                st.info("ランキングには掲載されませんが、結果は記録されます。")
                st.rerun()
    
    else:
        # 結果保存
        if not goal_state['result_saved']:
            participant_name = st.session_state.get('participant_name', 'Unknown')
            participant_age = st.session_state.get('participant_age', 0)
            
            result_data = {
                'participant_name': participant_name,
                'participant_age': participant_age,
                'teeth_count': game_state['teeth_count'],
                'tooth_coins': game_state['tooth_coins'],
                'total_score': score_data['total_score'],
                'play_time': play_time,
                'timestamp': datetime.now().isoformat(),
                'ranking_consent': goal_state['ranking_consent']
            }
            
            save_game_result(result_data)
            goal_state['result_saved'] = True
            
            # 参加者数カウント更新
            update_participant_count()
        
        # ランキング表示
        st.markdown("### 🏆 トップ5ランキング")
        
        leaderboard = get_leaderboard(limit=5)
        
        if leaderboard:
            for i, record in enumerate(leaderboard):
                if record.get('ranking_consent', False):  # 掲載同意者のみ
                    rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                    
                    with st.container():
                        rank_col1, rank_col2, rank_col3, rank_col4 = st.columns([1, 3, 2, 2])
                        
                        with rank_col1:
                            st.markdown(f"**{rank_emoji}**")
                        
                        with rank_col2:
                            st.markdown(f"**{record['participant_name']}**")
                        
                        with rank_col3:
                            st.markdown(f"{record['total_score']}ポイント")
                        
                        with rank_col4:
                            st.markdown(f"{record['play_time']}")
                        
                        st.markdown("---")
        else:
            st.info("まだランキングデータがありません。")
        
        # 結果カードダウンロード
        st.markdown("### 📄 結果カード")
        
        result_card_html = f"""
        <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; margin: 10px 0; background-color: #f9f9f9;">
            <h3 style="text-align: center; color: #4CAF50;">🦷 お口の人生ゲーム 結果カード</h3>
            <hr>
            <p><strong>プレイヤー:</strong> {st.session_state.get('participant_name', 'Unknown')}</p>
            <p><strong>年齢:</strong> {st.session_state.get('participant_age', 0)}歳</p>
            <p><strong>最終歯数:</strong> {game_state['teeth_count']}本</p>
            <p><strong>トゥースコイン:</strong> {game_state['tooth_coins']}枚</p>
            <p><strong>合計スコア:</strong> {score_data['total_score']}ポイント</p>
            <p><strong>プレイ時間:</strong> {play_time}</p>
            <p><strong>プレイ日:</strong> {datetime.now().strftime('%Y年%m月%d日')}</p>
            <hr>
            <p style="text-align: center; font-style: italic;">定期的な歯科健診を忘れずに！</p>
        </div>
        """
        
        st.markdown(result_card_html, unsafe_allow_html=True)
        
        # ダウンロードボタン（プレースホルダ）
        if st.button("📥 結果カードをダウンロード", use_container_width=True):
            st.info("💡 実際の運用では、PDF形式でダウンロードできます")
        
        # 次のアクション
        st.markdown("### 🎯 次のステップ")
        
        next_col1, next_col2 = st.columns(2)
        
        with next_col1:
            if st.button("📱 LINE・塗り絵ページへ", use_container_width=True, type="primary"):
                st.switch_page("pages/9_LINE_塗り絵.py")
        
        with next_col2:
            if st.button("🏠 最初からもう一度", use_container_width=True):
                # ゲーム状態をリセット
                for key in list(st.session_state.keys()):
                    if key.startswith(('game_state', 'caries_quiz', 'perio_quiz', 'job_experience', 'checkup', 'goal')):
                        del st.session_state[key]
                st.switch_page("pages/0_受付_プロローグ.py")
    
    # アドバイス表示
    st.markdown("### 💡 お口の健康アドバイス")
    
    if game_state['teeth_count'] >= 20:
        st.success("🌟 素晴らしい！歯をよく保てています。この調子で頑張りましょう！")
    elif game_state['teeth_count'] >= 15:
        st.info("👍 歯の数は比較的良好です。定期健診で維持していきましょう。")
    else:
        st.warning("⚠️ 歯の数が少なくなっています。歯科医師に相談しましょう。")
    
    st.markdown("""
    **お口の健康を保つために:**
    - 毎日の正しい歯磨き
    - フロスや歯間ブラシの使用
    - 定期的な歯科健診（3〜6ヶ月に1回）
    - バランスの良い食事
    - 禁煙・節酒
    """)
    
    # 進行状況表示（サイドバー）
    st.sidebar.markdown("### 🏁 ゲーム完了")
    st.sidebar.metric("最終歯数", f"{game_state['teeth_count']}本")
    st.sidebar.metric("最終トゥースコイン", f"{game_state['tooth_coins']}枚")
    st.sidebar.metric("合計スコア", f"{score_data['total_score']}ポイント")

if __name__ == "__main__":
    main()
