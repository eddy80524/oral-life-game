"""
歯周病クイズページ - お口の人生ゲーム
"""
import streamlit as st
import sys
import os
import json
from datetime import datetime

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.game_logic import apply_branch_after_quiz, roll_1to3, apply_teeth_delta, apply_tooth_delta
from services.store import save_game_state
from services.audio import show_audio_controls

# ページ設定
st.set_page_config(
    page_title="歯周病クイズ - お口の人生ゲーム",
    page_icon="🦷",
    layout="wide"
)

def load_perio_quiz_data():
    """歯周病クイズデータを読み込み"""
    try:
        with open('data/quizzes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('perio', [])
    except FileNotFoundError:
        # デフォルトのクイズデータ
        return [
            {
                "id": 1,
                "question": "はみがきをしないと、どこから血が出やすくなるでしょう？",
                "options": ["歯", "歯茎（歯ぐき）", "舌", "ほっぺた"],
                "correct": 1,
                "explanation": "歯茎の炎症が起きると出血しやすくなります。これが歯周病の始まりです。",
                "audio_id": "perio_q1",
                "follow_up": "歯茎の炎症→歯周病→歯がぐらぐらになってしまいます"
            },
            {
                "id": 2,
                "question": "歯の根っこの周りは何で支えられているでしょう？",
                "options": ["筋肉", "血管", "骨", "神経"],
                "correct": 2,
                "explanation": "歯は骨（歯槽骨）に支えられています。歯周病が進むとこの骨が溶けて歯がぐらつきます。",
                "audio_id": "perio_q2"
            }
        ]

def main():
    st.title("🦷 歯周病クイズ")
    
    if 'game_state' not in st.session_state:
        st.error("ゲーム状態が見つかりません。ゲームボードからやり直してください。")
        if st.button("🎲 ゲームボードに戻る"):
            st.switch_page("pages/1_ゲームボード.py")
        return
    
    game_state = st.session_state.game_state
    
    # クイズ状態の初期化
    if 'perio_quiz_state' not in st.session_state:
        st.session_state.perio_quiz_state = {
            'current_question': 0,
            'answers': [],
            'completed': False,
            'started': False
        }
    
    quiz_state = st.session_state.perio_quiz_state
    quiz_data = load_perio_quiz_data()
    
    # クイズ開始前の説明
    if not quiz_state['started']:
        st.markdown("""
        ### 🎯 歯周病クイズについて
        
        **ルール:**
        - 2問のクイズに挑戦します
        - 1問以上正解で「歯周病にならないルート」
        - 0問正解で「歯周病になるルート」に進みます
        - 制限時間はありませんが、未回答は不正解になります
        
        **歯周病とは:**
        歯を支える歯茎や骨の病気です。進行すると歯が抜けてしまうこともあります。
        """)
        
        # 現在の状態表示
        col1, col2 = st.columns(2)
        with col1:
            st.metric("現在の歯の本数", game_state['teeth_count'])
        with col2:
            st.metric("トゥースコイン", game_state['tooth_coins'])
        
        if st.button("🚀 クイズを始める", use_container_width=True, type="primary"):
            quiz_state['started'] = True
            st.rerun()
        
        if st.button("⬅️ ゲームボードに戻る", use_container_width=True):
            st.switch_page("pages/1_ゲームボード.py")
        
        return
    
    # クイズ完了後の結果表示
    if quiz_state['completed']:
        correct_count = sum(1 for answer in quiz_state['answers'] if answer['correct'])
        
        st.markdown("### 🎉 歯周病クイズ完了！")
        
        # 結果表示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("正解数", f"{correct_count}/2問")
        with col2:
            st.metric("現在の歯の本数", game_state['teeth_count'])
        with col3:
            st.metric("トゥースコイン", game_state['tooth_coins'])
        
        # 分岐処理
        if correct_count >= 1:
            st.success("🌟 おめでとう！歯周病にならないルートに進みます！")
            route_type = "correct"
            
            # 撮影同意チェック
            if st.session_state.get('photo_consent', False):
                st.info("📸 ベストスマイルで写真撮影のお時間です！")
                show_audio_controls("smile_photo", "🔊 写真撮影の案内")
        else:
            st.warning("💧 歯周病になるルートに進みます。気をつけましょう！")
            route_type = "incorrect"
            
            # 歯を失う処理
            st.markdown("### 🎲 歯を失う数を決めます")
            if st.button("🎲 サイコロを振る", use_container_width=True):
                dice_result = roll_1to3()
                st.error(f"🎲 出た目: {dice_result} → {dice_result}本の歯を失います")
                
                # 歯を失う
                apply_teeth_delta(game_state, -dice_result)
                
                # 歯の本数×2のトゥースを支払い
                teeth_penalty = game_state['teeth_count'] * 2
                apply_tooth_delta(game_state, -teeth_penalty)
                
                st.error(f"💸 {teeth_penalty}トゥースコインも支払いました（歯{game_state['teeth_count']}本×2）")
                
                save_game_state(game_state)
                st.rerun()
        
        # 分岐適用
        apply_branch_after_quiz(game_state, "perio", correct_count)
        save_game_state(game_state)
        
        # 各問題の振り返り
        st.markdown("### 📚 問題の振り返り")
        for i, (quiz, answer) in enumerate(zip(quiz_data, quiz_state['answers'])):
            with st.expander(f"問題{i+1}: {quiz['question'][:20]}..."):
                st.markdown(f"**問題:** {quiz['question']}")
                st.markdown(f"**あなたの回答:** {quiz['options'][answer['selected']] if answer['selected'] is not None else '未回答'}")
                st.markdown(f"**正解:** {quiz['options'][quiz['correct']]}")
                st.markdown(f"**解説:** {quiz['explanation']}")
                
                if quiz.get('follow_up'):
                    st.info(f"**補足:** {quiz['follow_up']}")
                
                if answer['correct']:
                    st.success("✅ 正解！")
                else:
                    st.error("❌ 不正解")
                
                # 音声ガイド
                if quiz.get('audio_id'):
                    show_audio_controls(quiz['audio_id'], f"🔊 問題{i+1}の解説")
        
        # 次へ進むボタン
        if st.button("🏁 ゴールに向かう", use_container_width=True, type="primary"):
            st.switch_page("pages/7_ゴール_ランキング.py")
        
        return
    
    # クイズ進行中
    current_q = quiz_state['current_question']
    total_questions = len(quiz_data)
    
    if current_q >= total_questions:
        # 全問完了
        quiz_state['completed'] = True
        st.rerun()
        return
    
    question = quiz_data[current_q]
    
    # 進行状況表示
    progress = (current_q + 1) / total_questions
    st.progress(progress, text=f"問題 {current_q + 1} / {total_questions}")
    
    # 問題表示
    st.markdown(f"### 問題 {current_q + 1}")
    st.markdown(f"**{question['question']}**")
    
    # 音声ガイド
    if question.get('audio_id'):
        show_audio_controls(question['audio_id'], f"🔊 問題{current_q + 1}を読み上げ")
    
    # 選択肢
    st.markdown("#### 選択肢を選んでください:")
    
    # ラジオボタンで選択肢表示
    selected = st.radio(
        "選択してください：",
        options=range(len(question['options'])),
        format_func=lambda x: f"{chr(65 + x)}. {question['options'][x]}",
        key=f"perio_quiz_q{current_q}",
        index=None
    )
    
    # 回答ボタン
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📝 この答えで決定", use_container_width=True, type="primary"):
            if selected is not None:
                # 回答を記録
                is_correct = selected == question['correct']
                quiz_state['answers'].append({
                    'question_id': question['id'],
                    'selected': selected,
                    'correct': is_correct
                })
                
                # 次の問題へ
                quiz_state['current_question'] += 1
                
                # フィードバック表示
                if is_correct:
                    st.success("✅ 正解！")
                else:
                    st.error("❌ 不正解")
                
                st.info(f"**解説:** {question['explanation']}")
                
                # 特別な解説（問題1の場合）
                if question.get('follow_up'):
                    st.warning(f"**重要:** {question['follow_up']}")
                    show_audio_controls("gum_inflammation", "🔊 歯茎の炎症について")
                
                # 少し待ってから次へ
                st.balloons() if is_correct else None
                st.rerun()
            else:
                st.warning("⚠️ 選択肢を選んでください")
    
    with col2:
        if st.button("⏭️ 答えない（不正解）", use_container_width=True):
            # 未回答として記録
            quiz_state['answers'].append({
                'question_id': question['id'],
                'selected': None,
                'correct': False
            })
            
            quiz_state['current_question'] += 1
            st.warning("❌ 未回答のため不正解です")
            st.rerun()
    
    # 現在の状態表示
    st.sidebar.markdown("### 📊 現在の状態")
    st.sidebar.metric("歯の本数", game_state['teeth_count'])
    st.sidebar.metric("トゥースコイン", game_state['tooth_coins'])
    st.sidebar.metric("現在のマス", f"{game_state['current_position'] + 1}マス目")

if __name__ == "__main__":
    main()
