"""
虫歯クイズページ - お口の人生ゲーム
"""
import streamlit as st
import sys
import os
import json
from datetime import datetime

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.game_logic import apply_branch_after_quiz, apply_tooth_delta, apply_teeth_delta
from services.store import save_game_state
from services.audio import show_audio_controls

# ページ設定
st.set_page_config(
    page_title="虫歯クイズ - お口の人生ゲーム",
    page_icon="🦷",
    layout="wide"
)

def load_quiz_data():
    """クイズデータを読み込み"""
    try:
        with open('data/quizzes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('caries', [])
    except FileNotFoundError:
        # デフォルトのクイズデータ
        return [
            {
                "id": 1,
                "question": "体の中で一番かたいものは何でしょう？",
                "options": ["骨", "歯", "爪", "筋肉"],
                "correct": 1,
                "explanation": "歯は体の中で最も硬い組織です！エナメル質という成分でできています。",
                "audio_id": "caries_q1"
            },
            {
                "id": 2,
                "question": "むし歯になりにくい組み合わせはどれでしょう？",
                "options": [
                    "チョコバナナ + コーラ",
                    "菓子パン + オレンジジュース", 
                    "チーズ + お茶",
                    "キャンディ + ジュース"
                ],
                "correct": 2,
                "explanation": "チーズはカルシウムが豊富で歯を強くし、お茶には抗菌作用があります！",
                "audio_id": "caries_q2"
            }
        ]

def main():
    st.title("🦷 虫歯クイズ")
    
    if 'game_state' not in st.session_state:
        st.error("ゲーム状態が見つかりません。ゲームボードからやり直してください。")
        if st.button("🎲 ゲームボードに戻る"):
            st.switch_page("pages/1_ゲームボード.py")
        return
    
    game_state = st.session_state.game_state
    
    # クイズ状態の初期化
    if 'caries_quiz_state' not in st.session_state:
        st.session_state.caries_quiz_state = {
            'current_question': 0,
            'answers': [],
            'completed': False,
            'started': False
        }
    
    quiz_state = st.session_state.caries_quiz_state
    quiz_data = load_quiz_data()
    
    # クイズ開始前の説明
    if not quiz_state['started']:
        st.markdown("""
        ### 🎯 虫歯クイズについて
        
        **ルール:**
        - 2問のクイズに挑戦します
        - 1問以上正解で「虫歯にならないルート」
        - 0問正解で「虫歯になるルート」に進みます
        - 制限時間はありませんが、未回答は不正解になります
        
        **特典:**
        クイズ開始時に奥歯が4本追加されます！（上下左右の奥歯）
        """)
        
        # 現在の状態表示
        col1, col2 = st.columns(2)
        with col1:
            st.metric("現在の歯の本数", game_state['teeth_count'])
        with col2:
            st.metric("トゥースコイン", game_state['tooth_coins'])
        
        if st.button("🚀 クイズを始める", use_container_width=True, type="primary"):
            # 奥歯を4本追加
            apply_teeth_delta(game_state, 4)
            quiz_state['started'] = True
            save_game_state(game_state)
            st.success("🦷 奥歯が4本追加されました！")
            st.rerun()
        
        if st.button("⬅️ ゲームボードに戻る", use_container_width=True):
            st.switch_page("pages/1_ゲームボード.py")
        
        return
    
    # クイズ完了後の結果表示
    if quiz_state['completed']:
        correct_count = sum(1 for answer in quiz_state['answers'] if answer['correct'])
        
        st.markdown("### 🎉 クイズ完了！")
        
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
            st.success("🌟 おめでとう！虫歯にならないルートに進みます！")
            route_type = "correct"
        else:
            st.warning("💧 虫歯になるルートに進みます。気をつけましょう！")
            route_type = "incorrect"
        
        # 分岐適用
        apply_branch_after_quiz(game_state, "caries", correct_count)
        save_game_state(game_state)
        
        # 各問題の振り返り
        st.markdown("### 📚 問題の振り返り")
        for i, (quiz, answer) in enumerate(zip(quiz_data, quiz_state['answers'])):
            with st.expander(f"問題{i+1}: {quiz['question'][:20]}..."):
                st.markdown(f"**問題:** {quiz['question']}")
                st.markdown(f"**あなたの回答:** {quiz['options'][answer['selected']] if answer['selected'] is not None else '未回答'}")
                st.markdown(f"**正解:** {quiz['options'][quiz['correct']]}")
                st.markdown(f"**解説:** {quiz['explanation']}")
                
                if answer['correct']:
                    st.success("✅ 正解！")
                else:
                    st.error("❌ 不正解")
                
                # 音声ガイド
                if quiz.get('audio_id'):
                    show_audio_controls(quiz['audio_id'], f"🔊 問題{i+1}の解説")
        
        # 次へ進むボタン
        if st.button("➡️ 分岐ルートに進む", use_container_width=True, type="primary"):
            # 分岐ルートの処理は自動的にゲームボードで行われる
            st.switch_page("pages/1_ゲームボード.py")
        
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
    
    # セッション状態でカレントの回答を管理
    answer_key = f"q{current_q}_answer"
    if answer_key not in st.session_state:
        st.session_state[answer_key] = None
    
    # ラジオボタンで選択肢表示
    selected = st.radio(
        "選択してください：",
        options=range(len(question['options'])),
        format_func=lambda x: f"{chr(65 + x)}. {question['options'][x]}",
        key=f"quiz_q{current_q}",
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
