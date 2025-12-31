"""
クイズページ（むしば・はぐき共通）
"""
import streamlit as st
from pages.utils import navigate_to
from services.quiz_helper import load_quiz_data


def _render_option_buttons(options, selected, key_prefix):
    """選択肢ボタンを表示"""
    state_key = f"{key_prefix}_selected"
    if state_key in st.session_state:
        selected = st.session_state[state_key]
    elif selected is None:
        selected = st.session_state.get(state_key)
    
    cols = st.columns(len(options))
    updated = selected
    for idx, label in enumerate(options):
        button_type = "primary" if selected == idx else "secondary"
        if cols[idx].button(label, key=f"{key_prefix}_btn_{idx}", use_container_width=True, type=button_type):
            updated = idx
            st.session_state[state_key] = idx
            st.rerun()
    if updated is not None:
        st.session_state[state_key] = updated
    return updated


def _show_quiz_page(quiz_type: str):
    """共通クイズロジック
    
    Args:
        quiz_type: 'caries' or 'perio'
    """
    from services.image_helper import display_image
    
    participant_age = st.session_state.get('participant_age', 5)
    quiz_data = load_quiz_data(quiz_type, participant_age)
    questions = quiz_data.get('questions', [])
    rewards = quiz_data.get('rewards', {})
    
    stage_key = f'{quiz_type}_quiz_stage'
    answers_key = f'{quiz_type}_quiz_answers'
    prefix = quiz_type
    
    stage = st.session_state.get(stage_key, 'intro')
    if stage == 'questions':
        stage = 'question_0'
        st.session_state[stage_key] = stage
    
    answers = st.session_state.setdefault(answers_key, [None] * len(questions))
    
    # イントロ画面
    if stage == 'intro':
        st.markdown(f"### 🦷 {quiz_data.get('title', 'クイズ')}")
        intro_image = "cell_07" if quiz_type == 'caries' else "cell_20"
        try:
            display_image("board", intro_image, "")
        except ImportError:
            pass
        if st.button("🦷 クイズへすすむ", type="primary", use_container_width=True):
            st.session_state[stage_key] = 'question_0'
            st.session_state[answers_key] = [None] * len(questions)
            for i in range(len(questions)):
                st.session_state.pop(f'{prefix}_q{i}_selected', None)
                st.session_state.pop(f'{prefix}_q{i}_checked', None)
            st.rerun()
        return
    
    # 問題画面
    if stage.startswith('question_'):
        try:
            question_index = int(stage.split('_')[1])
        except (IndexError, ValueError):
            question_index = 0
        
        if question_index == 0:
            st.markdown(f"### 🦷 {quiz_data.get('title', 'クイズ')}にちょうせん！")
        
        if question_index >= len(questions):
            st.error("問題が見つかりません")
            return
        
        question = questions[question_index]
        state_key_selected = f"{prefix}_q{question_index}_selected"
        state_key_checked = f"{prefix}_q{question_index}_checked"
        
        st.caption(f"もんだい {question_index + 1} / {len(questions)}")
        st.markdown("---")
        
        # 画像表示
        images = question.get('images', [])
        image_category = question.get('image_category')
        image_name = question.get('image_name')
        default_category = f'quiz/{quiz_type}' if quiz_type == 'caries' else 'quiz/periodontitis'
        
        if not images:
            if isinstance(image_name, list):
                images = [{'category': image_category or default_category, 'name': name} for name in image_name]
            elif image_category or image_name:
                images = [{'category': image_category or default_category, 'name': image_name or f'question_{question_index + 1}'}]
        
        if images:
            try:
                if len(images) == 1:
                    display_image(images[0].get('category', default_category), images[0].get('name'), "")
                else:
                    cols = st.columns(len(images))
                    for idx, img in enumerate(images):
                        with cols[idx]:
                            display_image(img.get('category', default_category), img.get('name'), "")
            except (ImportError, KeyError):
                pass
        
        st.markdown(f"<h3 style='font-size: 1.8em; margin: 20px 0;'>もんだい{question_index + 1}: {question.get('text', '')}</h3>", unsafe_allow_html=True)
        
        if state_key_selected not in st.session_state:
            st.session_state[state_key_selected] = None
        
        selected_idx = _render_option_buttons(
            question.get('options', []),
            answers[question_index],
            f"{prefix}_q{question_index}"
        )
        answers[question_index] = selected_idx
        
        st.markdown("---")
        submit_btn = st.button(
            "📝 こたえをかくにん",
            key=f"{prefix}_submit_q{question_index}",
            type="primary",
            use_container_width=True,
        )
        
        if submit_btn:
            if answers[question_index] is None:
                st.warning("こたえをえらんでね！")
            else:
                correct_answer = question.get('correct', 0)
                if answers[question_index] == correct_answer:
                    st.success(question.get('correct_feedback', 'せいかい！'))
                else:
                    st.warning(question.get('incorrect_feedback', 'ざんねん…'))
                    if question.get('explanation'):
                        st.info(f"✅ {question.get('explanation')}")
                st.session_state[state_key_checked] = True
        
        # 次の問題 or 結果表示
        if st.session_state.get(state_key_checked):
            if question_index < len(questions) - 1:
                if st.button("▶️ つぎのもんだいへ", key=f"{prefix}_next_q{question_index}", type="secondary", use_container_width=True):
                    st.session_state.pop(state_key_checked, None)
                    st.session_state[stage_key] = f'question_{question_index + 1}'
                    st.rerun()
            else:
                if st.button("次へすすむ", key=f"{prefix}_finalize_q{question_index}", type="secondary", use_container_width=True):
                    _finalize_quiz(quiz_type, questions, answers, rewards)
        else:
            st.caption("こたえをかくにんしてから つぎへすすもう！")


def _finalize_quiz(quiz_type: str, questions: list, answers: list, rewards: dict):
    """クイズ完了処理"""
    prefix = quiz_type
    stage_key = f'{quiz_type}_quiz_stage'
    answers_key = f'{quiz_type}_quiz_answers'
    
    correct_count = sum(
        1 for i, q in enumerate(questions)
        if i < len(answers) and answers[i] == q.get('correct', 0)
    )
    
    st.success(f"せいかいかず: {correct_count}/{len(questions)}")
    
    for i, q in enumerate(questions):
        if i < len(answers):
            if answers[i] == q.get('correct', 0):
                st.success(f"もんだい{i+1}せいかい！ {q.get('explanation', '')}")
            else:
                st.warning(f"もんだい{i+1}は ざんねん… {q.get('explanation', '')}")
    
    if 'game_state' in st.session_state:
        game_state = st.session_state.game_state
        high_score = rewards.get('high_score', {})
        low_score = rewards.get('low_score', {})
        threshold = high_score.get('threshold', 1)
        
        if correct_count >= threshold:
            coins = high_score.get('coins', 0)
            position = high_score.get('position', 11)
            message = high_score.get('message', '🌟 よくできました！')
            game_state['tooth_coins'] += coins
            game_state['current_position'] = position
            st.success(message)
            st.balloons()
        else:
            coins = low_score.get('coins', 0)
            position = low_score.get('position', 8)
            message = low_score.get('message', '💧 もう少し頑張りましょう')
            game_state['tooth_coins'] = max(0, game_state['tooth_coins'] + coins)
            game_state['current_position'] = position
            st.warning(message)
        
        # むしばクイズでは永久歯への移行
        if quiz_type == 'caries':
            st.info("🦷 **おとなのはに はえかわったよ！** 20ほん → 28ほん")
            from services import teeth as teeth_service
            teeth_service.ensure_tooth_state(game_state)
            if teeth_service.upgrade_to_adult(game_state):
                teeth_service.reset_all_teeth_to_healthy(game_state)
                game_state['teeth_count'] = 28
                game_state['teeth_max'] = 28
                game_state['teeth_missing'] = 0
                st.session_state.teeth_count = 28
                st.session_state.post_quiz_full_teeth = True
            game_state['action_taken'] = False
            game_state['action_completed'] = False
        else:
            game_state['action_taken'] = True
            game_state['action_completed'] = True
    
    # セッションクリア
    st.session_state[stage_key] = 'intro'
    st.session_state.pop(answers_key, None)
    for i in range(len(questions)):
        st.session_state.pop(f'{prefix}_q{i}_selected', None)
        st.session_state.pop(f'{prefix}_q{i}_checked', None)
    
    st.info("つづきは ゲームボードで！")
    navigate_to('game_board')


def show_caries_quiz_page():
    """むしばクイズページ"""
    _show_quiz_page('caries')


def show_perio_quiz_page():
    """はぐきクイズページ"""
    _show_quiz_page('perio')
