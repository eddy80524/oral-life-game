"""
定期健診ページ
"""
import streamlit as st
import json
import os
from pages.utils import navigate_to, get_board_file_for_age


def show_checkup_page():
    """定期健診ページ"""
    from services.image_helper import display_image
    
    def resolve_checkup_target() -> str:
        target = st.session_state.get('pending_checkup_target')
        if target:
            return target
        pending_cell = st.session_state.get('pending_checkup_cell')
        board_position = st.session_state.get('game_state', {}).get('current_position', 0)
        try:
            age = st.session_state.get('participant_age', 5)
            board_file = get_board_file_for_age(age)
            board_path = os.path.join(os.getcwd(), board_file)
            with open(board_path, 'r', encoding='utf-8') as f:
                board_data = json.load(f)
            for cell in board_data:
                cell_id = cell.get('cell')
                if pending_cell is not None and cell_id == pending_cell:
                    return cell.get('checkup_target', 'caries_quiz')
                if cell_id == board_position:
                    return cell.get('checkup_target', 'caries_quiz')
        except Exception:
            pass
        return 'perio_quiz' if board_position >= 14 else 'caries_quiz'
    
    st.markdown("### 🏥 ていきけんしん")
    target_page = resolve_checkup_target()
    if target_page == 'perio_quiz':
        st.caption("おくちをきれいにしたら、つぎは はぐきのクイズに ちょうせん！")
    else:
        st.caption("はいしゃさんで はのけんしんを うけよう！")
    
    pending_image = st.session_state.get('pending_checkup_image')
    if pending_image:
        image_name = pending_image.split('/', 1)[1] if '/' in pending_image else pending_image
    else:
        image_name = "cell_15" if target_page == 'perio_quiz' else "cell_05"
    try:
        display_image("board", image_name, "")
    except Exception:
        st.info("🏥 はいしゃさんに いこう")
    
    st.markdown("<div style='height:3vh'></div>", unsafe_allow_html=True)
    
    # 定期健診に行くボタン
    if st.button("🏥 ていきけんしんに いく", key="goto_caries_quiz", use_container_width=True, type="primary"):
        if 'game_state' in st.session_state:
            st.session_state.game_state['action_taken'] = True
        
        st.session_state.pop('checkup_stage', None)
        target_page = st.session_state.pop('pending_checkup_target', target_page)
        st.session_state.pop('pending_checkup_cell', None)
        st.session_state.pop('pending_checkup_image', None)
        
        # むし歯/歯周病クイズに直接遷移
        navigate_to(target_page)
        return
