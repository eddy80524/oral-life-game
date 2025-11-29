"""
お口の人生ゲーム - 単一ページアプリ
"""
import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import json
import random
import time
import uuid
import base64
from datetime import datetime
from typing import Dict

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services import teeth as teeth_service  # noqa: E402
from services.video_helper import display_video, ensure_video_directories  # noqa: E402
from services.quiz_helper import load_quiz_data  # noqa: E402
from services.store import log_player_session  # noqa: E402
from services.image_helper import get_image_path  # noqa: E402

ensure_video_directories()

# -----------------------------------------------------------------------------
# State Persistence Helpers
# -----------------------------------------------------------------------------
def save_state_to_url():
    """Save critical game state to URL parameters for persistence across reloads."""
    if 'game_state' not in st.session_state:
        return

    gs = st.session_state.game_state
    params = {
        'page': st.session_state.current_page,
        'pos': gs.get('current_position', 0),
        'teeth': gs.get('teeth_count', 20),
        'coins': gs.get('tooth_coins', 10000),
        'age': st.session_state.get('participant_age', 5),
        'name': st.session_state.get('participant_name', ''),
        'p_quiz': st.session_state.get('post_quiz_full_teeth', False),
        'job': st.session_state.get('job_experience_completed', False),
    }
    
    # Save quiz state if in quiz pages
    current_page = st.session_state.current_page
    if current_page == 'caries_quiz':
        params['quiz_stage'] = st.session_state.get('caries_quiz_stage', 'intro')
    elif current_page == 'perio_quiz':
        params['quiz_stage'] = st.session_state.get('perio_quiz_stage', 'intro')
    
    # Convert bools to strings
    for k, v in params.items():
        if isinstance(v, bool):
            params[k] = str(v).lower()
            
    st.query_params.update(params)

def load_state_from_url():
    """Load game state from URL parameters if session state is empty."""
    # Only load if we are not already in a valid session (or if we just reloaded)
    # We check if 'game_state' is missing or if we are at 'reception' but params exist
    
    try:
        params = st.query_params
        if not params:
            return

        # If we have 'pos' in params, it implies an active game
        if 'pos' in params:
            from services.game_logic import initialize_game_state
            initialize_game_state()
            
            gs = st.session_state.game_state
            
            # Restore values
            gs['current_position'] = int(params.get('pos', 0))
            gs['teeth_count'] = int(params.get('teeth', 20))
            gs['tooth_coins'] = int(params.get('coins', 10000))
            
            st.session_state.current_page = params.get('page', 'reception')
            st.session_state.participant_age = int(params.get('age', 5))
            st.session_state.participant_name = params.get('name', '')
            
            # Restore bool flags
            if params.get('p_quiz') == 'true':
                st.session_state.post_quiz_full_teeth = True
            if params.get('job') == 'true':
                st.session_state.job_experience_completed = True
            
            # Restore quiz state if applicable
            if 'quiz_stage' in params:
                quiz_stage = params.get('quiz_stage')
                current_page = st.session_state.current_page
                if current_page == 'caries_quiz':
                    st.session_state.caries_quiz_stage = quiz_stage
                elif current_page == 'perio_quiz':
                    st.session_state.perio_quiz_stage = quiz_stage
                
            # Sync session state mirrors
            st.session_state.teeth_count = gs['teeth_count']
            st.session_state.tooth_coins = gs['tooth_coins']
            
            # Ensure tooth chart matches count (simplified restoration)
            teeth_service.ensure_tooth_state(gs)
            if gs['teeth_count'] == 28:
                 teeth_service.reset_all_teeth_to_healthy(gs)
            
            # If we are on game_board, ensure stage is set
            if st.session_state.current_page == 'game_board':
                st.session_state.game_board_stage = 'card'

    except Exception as e:
        print(f"Error loading state from URL: {e}")


# ページ設定
st.set_page_config(
    page_title="お口の人生ゲーム",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# カスタムCSS（スマホ最適化）
st.markdown("""
<style>
    /* プルトゥリフレッシュ（引っ張って更新）を無効化 */
    body, html {
        overscroll-behavior-y: contain;
    }
    
    .stApp {
        overscroll-behavior-y: contain;
    }
    
    /* アプリ全体の背景色設定 */
    .main {
        background-color: #EFE4D0;
    }
    
    /* StreamlitのデフォルトCSSクラスによる背景色設定 */
    .stApp {
        background-color: #EFE4D0;
    }
    
    /* コンテナの背景も同色に */
    .main .block-container {
        background-color: #EFE4D0;
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* サイドバーを完全に隠す */
    .css-1d391kg {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    .css-1lcbmhc {display: none;}
    
    /* 大きなボタン */
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        font-size: 1.3rem;
        font-weight: bold;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    
    /* より確実な背景色適用 */
    html, body, [data-testid="stApp"] {
        background-color: #EFE4D0 !important;
    }
    
    /* 全体のコンテナ背景 */
    .stApp > div:first-child {
        background-color: #EFE4D0 !important;
    }
    
    /* メインエリアの背景 */
    section.main > div {
        background-color: #EFE4D0 !important;
    }
    
    /* ルーレットパネル */
    .roulette-card {
        background: linear-gradient(135deg, #fffdf5, #fff6e6);
        border: 2px solid #f5d7a1;
        border-radius: 22px;
        padding: 1.75rem 1.5rem;
        text-align: center;
        box-shadow: 0 10px 18px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .roulette-subtitle {
        margin: 0 0 1rem;
        font-weight: 600;
        color: #7b552e;
        letter-spacing: 0.03em;
    }
    
    .roulette-number-row {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin: 1rem 0 1.25rem;
    }
    
    .roulette-number-chip {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.65rem;
        font-weight: bold;
        color: #fff;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
    }
    
    .roulette-number-chip[data-value="1"] {
        background: linear-gradient(135deg, #f94144, #f3722c);
    }
    
    .roulette-number-chip[data-value="2"] {
        background: linear-gradient(135deg, #f8961e, #f9c74f);
        color: #5c3b00;
    }
    
    .roulette-number-chip[data-value="3"] {
        background: linear-gradient(135deg, #43aa8b, #577590);
    }

    .roulette-number-chip.is-active {
        transform: scale(1.08);
        box-shadow: 0 10px 22px rgba(0,0,0,0.2);
        outline: 4px solid rgba(255, 255, 255, 0.9);
        outline-offset: -4px;
    }

    .roulette-number-chip.is-disabled {
        opacity: 1;
        filter: none;
    }

    .roulette-result-card {
        background: linear-gradient(135deg, #fffef8, #fef2d8);
        border: 2px dashed #f3c577;
        border-radius: 18px;
        padding: 1.25rem 1.5rem;
        margin-top: 1rem;
        color: #7b552e;
        font-weight: 600;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.7);
    }
    
    .roulette-actions {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        justify-content: center;
        margin-top: 1.2rem;
    }
    
    .roulette-actions .stButton button {
        min-width: 180px;
    }
    
    /* ローディング演出 */
    .loading-dots {
        display: inline-flex;
        gap: 0.35rem;
        align-items: center;
        justify-content: center;
    }
    .loading-dots span {
        width: 0.55rem;
        height: 0.55rem;
        border-radius: 50%;
        background: #f59e0b;
        opacity: 0.2;
        animation: dotPulse 1.2s infinite ease-in-out;
    }
    .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
    .loading-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes dotPulse {
        0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
        40% { opacity: 1; transform: scale(1.1); }
    }
    
    /* ボード進行トラッカー */
    .board-progress-track {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.35rem;
        margin: 0.75rem 0 1.5rem;
    }
    .board-progress-node {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #dacab2;
        color: #715739;
        font-size: 0.75rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.6);
    }
    .board-progress-node.is-visited {
        background: linear-gradient(135deg, #b5d17a, #9ac755);
        color: #fff;
        opacity: 0.9;
    }
    .board-progress-node.is-current {
        background: linear-gradient(135deg, #4caf50, #66bb6a);
        color: #fff;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.25);
        transform: scale(1.05);
    }
    
</style>
""", unsafe_allow_html=True)

# ページ管理用の状態初期化
if 'current_page' not in st.session_state:
    load_state_from_url()  # Try to load from URL first
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'reception'


def staff_access_enabled() -> bool:
    """Query parameter based toggle for exposing staff tools."""
    try:
        params = st.query_params  # Streamlit 1.31+
    except Exception:
        params = {}

    raw_value = params.get('staff', '0') if params else '0'
    if isinstance(raw_value, list):
        raw_value = raw_value[0] if raw_value else '0'

    flag = str(raw_value).lower() in {'1', 'true', 'yes', 'on'}
    st.session_state.staff_mode_allowed = flag
    return st.session_state.staff_mode_allowed



def apply_tooth_effects(game_state, landing_cell, feedback):
    """ボードイベントに応じた歯の状態変化を適用"""
    teeth_service.ensure_tooth_state(game_state)
    tooth_messages = feedback.setdefault('tooth_messages', [])
    title = landing_cell.get('title', '')
    action = landing_cell.get('action')
    effect_applied = False

    if title == "虫歯クイズ":
        if teeth_service.upgrade_to_adult(game_state):
            # 抜けていた歯も含めて完全に28本にリセット
            teeth_service.reset_all_teeth_to_healthy(game_state)
            teeth_service.sync_teeth_count(game_state)
            game_state['teeth_count'] = 28
            game_state['teeth_max'] = 28
            game_state['teeth_missing'] = 0
            st.session_state.teeth_count = 28
            tooth_messages.append(('success', '✨ 大人の歯が ぜんぶ生えそろったよ！28本になったね。'))
            effect_applied = True
    if title == "初めて乳歯が抜けた" or title == "歯が抜けた":
        # 現在の歯の数を確認
        teeth_data = teeth_service.load_teeth_json()
        max_tooth_number = max(int(k) for k in teeth_data["UR"].keys())
        
        if max_tooth_number <= 5:
            # 乳歯（20本）の場合は永久歯（28本）に移行
            new_teeth = teeth_service.transition_to_adult_teeth()
            st.session_state.teeth_data = new_teeth
            tooth_messages.append(('success', '✨ 大人の歯に生え変わったよ！全部で28本になったね。'))
            effect_applied = True
        else:
            # すでに永久歯の場合は通常の歯の喪失処理
            lost = teeth_service.lose_primary_tooth(game_state, count=1)
            if lost:
                tooth_messages.append(('info', '👶 乳歯が1本ぬけたよ。大人の歯がはえてくるまでまっていよう！'))
                effect_applied = True
            # teeth.jsonも更新
            teeth_service.update_tooth_status_random("E", count=1)
            st.session_state.teeth_data = teeth_service.load_teeth_json()
    if title == "虫歯ができた" or title == "むし歯治療":
        damaged = teeth_service.damage_random_tooth(
            game_state,
            kinds=(
                "first_premolar",
                "second_premolar",
                "first_molar",
                "second_molar",
                "primary_first_molar",
                "primary_second_molar",
            ),
        )
        if damaged:
            if title == "むし歯治療":
                # 治療マスの場合は、治療ボタンを表示するフラグをセット
                tooth_messages.append(('warning', '🦷 むし歯ができちゃった！治療を受けよう！'))
                st.session_state.needs_caries_treatment = True
            else:
                tooth_messages.append(('warning', '⚠️ 虫歯ができちゃった…定期検診でなおそう！'))
            effect_applied = True
        # teeth.jsonも更新
        teeth_service.update_tooth_status_random("C", count=1)
        st.session_state.teeth_data = teeth_service.load_teeth_json()
    if title == "ジュースをおねだり" or title == "ジュース":
        stained = teeth_service.stain_teeth(game_state, count=3)
        if stained:
            tooth_messages.append(('warning', '🥤 ジュースばかりで歯がすこし黄ばんできたよ。'))
            effect_applied = True
        # teeth.jsonも更新
        teeth_service.update_tooth_status_random("S", count=3)
        st.session_state.teeth_data = teeth_service.load_teeth_json()
    if title == "むし歯を放置" or title == "抜歯":
        # ランダムに1本の歯を失う
        lost = teeth_service.lose_random_teeth(game_state, count=1, permanent=True)
        if lost:
            tooth_messages.append(('error', '😢 むし歯を放っておいたら歯を1本失ってしまった…'))
            effect_applied = True
        # teeth.jsonも更新
        teeth_service.update_tooth_status_random("E", count=1)
        st.session_state.teeth_data = teeth_service.load_teeth_json()
    if title == "バイクで大事故" or title == "バイク事故":
        lost = teeth_service.lose_specific_teeth(game_state, ["UL1", "UR1"], permanent=True)
        if lost:
            tooth_messages.append(('error', '😢 バイク事故で前歯を2本失ってしまった…'))
            effect_applied = True
        # teeth.jsonも更新（前歯2本）
        teeth_data = teeth_service.load_teeth_json()
        teeth_data["UL"]["1"] = "E"
        teeth_data["UR"]["1"] = "E"
        teeth_service.save_teeth_json(teeth_data)
        st.session_state.teeth_data = teeth_data
    if title == "茶渋除去" or title == "茶渋" or title == "お茶":
        if "除去" in title or "クリーニング" in title:
            cleaned = teeth_service.whiten_teeth(game_state)
            if cleaned:
                tooth_messages.append(('success', '✨ 茶渋をきれいにして歯がピカピカになったよ！'))
                effect_applied = True
            # teeth.jsonも更新（S→N）
            teeth_service.restore_stained_teeth()
            st.session_state.teeth_data = teeth_service.load_teeth_json()
        else:
            stained = teeth_service.stain_teeth(game_state, count=3)
            if stained:
                tooth_messages.append(('warning', '☕ お茶で茶渋がついてしまった…'))
                effect_applied = True
            # teeth.jsonも更新
            teeth_service.update_tooth_status_random("S", count=3)
            st.session_state.teeth_data = teeth_service.load_teeth_json()
    if title == "入れ歯作成" or title == "入れ歯":
        added = teeth_service.add_prosthetics(game_state, count=2)
        if added:
            tooth_messages.append(('info', '🦷 入れ歯でなくなった歯がもどったよ。'))
            effect_applied = True
        # teeth.jsonも更新（E→R）
        teeth_service.restore_missing_teeth(count=2)
        st.session_state.teeth_data = teeth_service.load_teeth_json()
    if (landing_cell.get('type') == 'stop' and '検診' in title) or title == "クリーニング":
        repaired = teeth_service.repair_damaged_teeth(game_state)
        cleaned = teeth_service.whiten_teeth(game_state)
        
        # メッセージを表示（治療がなくても表示）
        if repaired or cleaned:
            tooth_messages.append(('success', '🪥 定期検診で歯がきれいになったよ！'))
        else:
            tooth_messages.append(('info', '🪥 お口をきれいにしてもらったよ！'))
        effect_applied = True
        
        # teeth.jsonも更新（C→R, S→N）
        teeth_service.restore_damaged_teeth()
        teeth_service.restore_stained_teeth()
        st.session_state.teeth_data = teeth_service.load_teeth_json()

    teeth_service.sync_teeth_count(game_state)
    st.session_state.teeth_count = game_state.get('teeth_count', st.session_state.get('teeth_count', 0))
    save_state_to_url()  # Save state after effects
    return effect_applied

def navigate_to(page_name):
    """ページ遷移"""
    st.session_state.current_page = page_name
    save_state_to_url()  # Save state on navigation
    st.rerun()

def show_progress_bar():
    """ゲーム進行状況を表示"""
    if st.session_state.current_page == 'reception' or st.session_state.current_page == 'staff_management':
        return
    
    # 進行段階の定義
    progress_stages = ['reception', 'game_board', 'caries_quiz', 'job_experience', 'checkup', 'perio_quiz', 'goal', 'line_coloring']
    current_stage_index = 0
    
    # 現在の段階を特定
    if st.session_state.current_page in progress_stages:
        current_stage_index = progress_stages.index(st.session_state.current_page)
    
    progress_percentage = (current_stage_index / (len(progress_stages) - 1)) * 100
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-fill" style="width: {max(progress_percentage, 15)}%;"></div>
    </div>
    """, unsafe_allow_html=True)

def show_status_header():
    if st.session_state.current_page not in ['reception', 'staff_management', 'checkup', 'perio_quiz', 'caries_quiz']:
        if st.session_state.current_page == 'game_board':
            stage = st.session_state.get('game_board_stage', 'board')
            if stage == 'roulette':
                return
            if stage == 'card':
                current_position = st.session_state.game_state.get('current_position', 0)
                if current_position == 0:
                    return
        
        # teeth.jsonを読み込む（セッション状態から、またはファイルから）
        if 'teeth_data' not in st.session_state:
            st.session_state.teeth_data = teeth_service.load_teeth_json()
        
        teeth_data = st.session_state.teeth_data
        
        def get_tooth_image_base64(image_name: str) -> str:
            """歯の画像をBase64エンコード"""
            image_path = get_image_path("teeth", image_name)
            
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                    return f"data:image/png;base64,{encoded}"
            return ""
        
        # CSSスタイル
        st.markdown("""
        <style>
        .teeth-table {
            border-collapse: collapse;
            margin: 0 auto;
            background: transparent;
            border-radius: 0;
            padding: 0;
            border: none;   
        }
        .teeth-table td, .teeth-table th {
            text-align: center;
            height: 50px;
            margin: 0;
            padding: 0;
        }
        .teeth-table th {
            background-color: #f59696;
            color: white;
            font-size: 12px;
            padding: 0;
        }
        .teeth-table img {
            vertical-align: bottom;
            height: 40px;
            width: auto;
        }
        .upper-teeth img {
            vertical-align: top;
            transform: rotate(180deg);
            transform-origin: center center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 上の歯（UR, UL）
        upper_row_html = '<tr class="upper-teeth">'
        
        # UR (右上) 7→1の順
        for i in range(7, 0, -1):
            status = teeth_data.get("UR", {}).get(str(i), "N")
            img_name = teeth_service.get_tooth_image_filename("UR", i, status)
            img_url = get_tooth_image_base64(img_name)
            upper_row_html += f'<td><img src="{img_url}" alt="UR{i}"></td>' if img_url else '<td></td>'
        
        # UL (左上) 1→7の順
        for i in range(1, 8):
            status = teeth_data.get("UL", {}).get(str(i), "N")
            img_name = teeth_service.get_tooth_image_filename("UL", i, status)
            img_url = get_tooth_image_base64(img_name)
            upper_row_html += f'<td><img src="{img_url}" alt="UL{i}"></td>' if img_url else '<td></td>'
        
        upper_row_html += '</tr>'
        
        # 下の歯（LR, LL）
        lower_row_html = '<tr>'
        
        # LR (右下) 7→1の順
        for i in range(7, 0, -1):
            status = teeth_data.get("LR", {}).get(str(i), "N")
            img_name = teeth_service.get_tooth_image_filename("LR", i, status)
            img_url = get_tooth_image_base64(img_name)
            lower_row_html += f'<td><img src="{img_url}" alt="LR{i}"></td>' if img_url else '<td></td>'
        
        # LL (左下) 1→7の順
        for i in range(1, 8):
            status = teeth_data.get("LL", {}).get(str(i), "N")
            img_name = teeth_service.get_tooth_image_filename("LL", i, status)
            img_url = get_tooth_image_base64(img_name)
            lower_row_html += f'<td><img src="{img_url}" alt="LL{i}"></td>' if img_url else '<td></td>'
        
        lower_row_html += '</tr>'
        
        # テーブル全体のHTML
        st.markdown(f"""
        <table class="teeth-table">
            <tr>
                <th colspan="7"></th>
                <th colspan="7"></th>
            </tr>
            {upper_row_html}
            {lower_row_html}
            <tr>
                <th colspan="7"></th>
                <th colspan="7"></th>
            </tr>
        </table>
        """, unsafe_allow_html=True)

def show_reception_page():
    """受付・プロローグページ（フルスクリーンウィザード）"""
    from services.game_logic import initialize_game_state
    from services.store import ensure_data_files, update_participant_count, get_settings
    from services.image_helper import display_image

    initialize_game_state()
    ensure_data_files()

    # セッション初期化
    st.session_state.setdefault('participant_name', "")
    st.session_state.setdefault('participant_age', 5)
    st.session_state.setdefault('photo_consent', False)
    st.session_state.setdefault('reception_step', 0)
    st.session_state.setdefault('reception_age_label', "5さい")
    if st.session_state.reception_step == 0:
        st.session_state.pop('post_quiz_full_teeth', None)
        st.session_state.pop('session_log_saved', None)
        st.session_state.pop('session_uid', None)

    step = st.session_state.reception_step

    # 受付画面用のスタイル
    st.markdown(
        """
        <style>
        body[data-current-page="reception"] .main .block-container {
            min-height: calc(100vh - 2rem);
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding-bottom: 2rem;
        }
        body[data-current-page="reception"] .reception-heading {
            font-size: clamp(1.9rem, 3vw + 1rem, 2.6rem);
            line-height: 1.35;
            color: #2f2311;
            margin-bottom: 0.25rem;
        }
        body[data-current-page="reception"] .reception-text {
            font-size: clamp(1.05rem, 1vw + 0.8rem, 1.25rem);
            color: #2f2311;
            margin: 0;
        }
        body[data-current-page="reception"] .reception-caption {
            color: #6b655d;
        }
        body[data-current-page="reception"] div[data-testid="baseButton-primary"] > button {
            border-radius: 999px;
            height: 3.4rem;
            font-size: 1.25rem;
        }
        body[data-current-page="reception"] div[data-testid="baseButton-secondary"] > button {
            border-radius: 999px;
            height: 3rem;
            font-size: 1.05rem;
        }
        body[data-current-page="reception"] .stTextInput input {
            border-radius: 14px;
            font-size: 1.3rem;
            padding: 0.8rem 1rem;
            text-align: center;
        }
        body[data-current-page="reception"] div[data-baseweb="select"] {
            border-radius: 14px;
            font-size: 1.3rem;
            min-height: 3.4rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        body[data-current-page="reception"] .stSelectbox label,
        body[data-current-page="reception"] .stTextInput label {
            display: none;
        }
        body[data-current-page="reception"] .reception-photo-slot {
            width: 100%;
            max-width: 520px;
            height: min(48vh, 360px);
            margin: 0 auto 1.2rem;
            border-radius: 22px;
            border: 2px dashed #ccbfa4;
            background: #efe6d4;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #b6ab97;
            font-size: 1.1rem;
        }
        body[data-current-page="reception"] .wait-note {
            background: #d5e3c0;
            border-radius: 18px;
            padding: 1.5rem;
            margin: 0.5rem 0 1.5rem;
            font-size: 1.05rem;
            color: #2f2311;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 中央寄せレイアウト
    st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)
    central_col = st.columns([0.08, 0.84, 0.08])[1]

    def render_reception_image(basename: str) -> None:
        if basename in {"name_prompt", "age_prompt"}:
            return
        if display_image("reception", basename, caption=None, fill='stretch'):
            return
        if basename == "cover":
            display_image("board", "okuchi_game", caption=None, fill='stretch')
            return
        if basename == "welcome_teeth":
            display_image("board", "welcome_teeth", caption=None, fill='stretch')
            return

    with central_col:
        if step == 0:
            render_reception_image("cover")
            st.markdown("<div style='height:2vh'></div>", unsafe_allow_html=True)
            if st.button("はじめる", key="reception_next_cover", use_container_width=True, type="primary"):
                st.session_state.reception_step = 1
                st.rerun()

        elif step == 1:
            st.markdown("<h1 class='reception-heading'>おくちのじんせいゲームへようこそ！</h1>", unsafe_allow_html=True)
            render_reception_image("welcome_teeth")
            st.markdown("<p class='reception-text'>みんなには100さいになるまで<br>きれいなおくちですごしてもらうよ！</p>", unsafe_allow_html=True)
            st.caption("※ 広報のために写真撮影をさせていただく場合がございます。あらかじめご了承ください。")
            st.markdown("<div style='height:1vh'></div>", unsafe_allow_html=True)
            if st.button("すすむ", key="reception_next_welcome", use_container_width=True, type="primary"):
                st.session_state.reception_step = 2
                st.rerun()

        elif step == 2:
            render_reception_image("name_prompt")
            st.markdown("<h1 class='reception-heading'>きみのなまえを<br>おしえて！</h1>", unsafe_allow_html=True)
            name_input = st.text_input(
                "ニックネーム",
                value=st.session_state.participant_name,
                placeholder="ニックネームを入力してね",
                key="reception_name_input",
                label_visibility="collapsed"
            )
            if st.button("すすむ", key="reception_next_name", use_container_width=True, type="primary"):
                if not name_input.strip():
                    st.warning("なまえをいれてね！")
                else:
                    st.session_state.participant_name = name_input.strip()
                    st.session_state.reception_step = 3
                    st.rerun()

        elif step == 3:
            render_reception_image("age_prompt")
            st.markdown("<h1 class='reception-heading'>なんさいかな？</h1>", unsafe_allow_html=True)
            age_options = [f"{i}さい" for i in range(0, 11)] + ["11さい以上"]
            default_label = st.session_state.reception_age_label
            if default_label not in age_options:
                default_label = "5さい"
            age_index = age_options.index(default_label)
            selected_label = st.selectbox(
                "なんさいかな？",
                age_options,
                index=age_index,
                key="reception_age_select",
                label_visibility="collapsed",
                help="プルダウンからえらんでね"
            )
            st.session_state.reception_age_label = selected_label
            if st.button("すすむ", key="reception_next_age", use_container_width=True, type="primary"):
                if selected_label == "11さい以上":
                    participant_age = 11
                else:
                    participant_age = int(selected_label.replace("さい", ""))
                st.session_state.participant_age = participant_age
                st.session_state.age_under_5 = participant_age < 5
                st.session_state.reception_step = 4
                st.rerun()

        elif step == 4:
            st.markdown("<h1 class='reception-heading'>まっていてね！</h1>", unsafe_allow_html=True)
            display_video(
                "reception",
                "wait_intro",
                caption=None,
                autoplay=True,
                loop=True,
                muted=True,
                controls=False,
                height=320,
            )
            st.markdown(
                "<div style='margin:1rem 0; text-align:center;'>"
                "<div class='loading-dots'><span></span><span></span><span></span></div>"
                "<p style='margin-top:0.5rem; color:#7b552e;'>じゅんびがおわったら「すすむ」をおしてね。</p>"
                "</div>",
                unsafe_allow_html=True,
            )
            st.session_state.setdefault('reception_wait_unlocked', False)
            if not st.session_state.reception_wait_unlocked:
                pin = st.text_input("スタッフ用パスコード", type="password", key="reception_wait_pin")
                if st.button("スタッフ確認", key="reception_wait_check", type="secondary"):
                    settings = get_settings()
                    staff_pin = settings.get("staff_pin", "0418")
                    if pin == str(staff_pin):
                        st.session_state.reception_wait_unlocked = True
                        st.success("スタートの準備ができました！")
                    else:
                        st.error("PINがちがうよ。もういちど確認してね。")

            if st.button("すすむ", key="reception_start_game", use_container_width=True, type="primary", disabled=not st.session_state.reception_wait_unlocked):
                update_participant_count()
                st.session_state.reception_step = 0
                st.session_state.game_board_stage = 'card'
                st.session_state.pop('roulette_feedback', None)
                st.session_state.pop('roulette_last_spin_id', None)
                st.session_state.pop('reception_wait_unlocked', None)
                navigate_to('game_board')

    st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)


def show_game_board_page():
    """ゲームボードページ（カード表示とルーレット画面に分離）"""
    import random  # 最初にインポート
    
    if 'game_state' not in st.session_state:
        from services.game_logic import initialize_game_state
        initialize_game_state()
    
    # 歯の初期化（ゲーム開始時に乳歯20本で開始）
    if 'teeth_data' not in st.session_state:
        st.session_state.teeth_data = teeth_service.initialize_child_teeth()

    st.session_state.setdefault('game_board_stage', 'card')
    stage = st.session_state.game_board_stage

    # game_stateは常にst.session_stateから直接参照
    game_state = st.session_state.game_state
    current_position = game_state.get('current_position', 0)
    
    # ヘルパー関数の定義（使用前に定義）
    def compute_allowed_numbers_for_action(position: int, game_state: dict):
        """アクション完了後の次のマス計算"""
        board_file = f"data/board_main_{'under5' if st.session_state.participant_age < 5 else '5plus'}.json"
        try:
            with open(board_file, 'r', encoding='utf-8') as f:
                board_data = json.load(f)
            max_position_index = max(len(board_data) - 1, 0)
            distance_to_goal = max(0, max_position_index - position)
            if distance_to_goal <= 0:
                return []
            max_reachable = min(3, distance_to_goal)
            return list(range(1, max_reachable + 1))
        except:
            return [1, 2, 3]

    def ensure_post_quiz_full_teeth():
        if st.session_state.get('post_quiz_full_teeth'):
            return
        # 虫歯クイズ（5マス目 = 位置4）以降かチェック
        if game_state.get('current_position', 0) < 5:
            return
        from services import teeth as teeth_service
        teeth_service.ensure_tooth_state(game_state)
        if game_state.get('tooth_stage') != 'adult':
            teeth_service.upgrade_to_adult(game_state)
        for tooth in game_state.get('tooth_chart', []):
            tooth['status'] = 'healthy'
            tooth['permanent_loss'] = False
        teeth_service.sync_teeth_count(game_state)
        game_state['teeth_count'] = 28
        game_state['teeth_max'] = 28
        game_state['teeth_missing'] = 0
        st.session_state.teeth_count = 28
        st.session_state.post_quiz_full_teeth = True

    ensure_post_quiz_full_teeth()

    # ボードデータ読み込み
    board_data = []
    current_cell = None
    max_position_index = 0
    forced_stop_indices = []
    required_stop_titles = {"虫歯クイズ", "歯周病クイズ", "お仕事体験"}
    try:
        age_group = "under5" if st.session_state.participant_age < 5 else "5plus"
        board_file = f"data/board_main_{age_group}.json"
        with open(board_file, 'r', encoding='utf-8') as f:
            board_data = json.load(f)
        max_position_index = max(len(board_data) - 1, 0)
        if 0 <= current_position < len(board_data) and isinstance(board_data[current_position], dict):
            current_cell = board_data[current_position]
        forced_stop_indices = [
            idx for idx, cell in enumerate(board_data)
            if isinstance(cell, dict) and (
                cell.get('type') == 'stop'
                or cell.get('must_stop')
                or cell.get('force_stop')
                or cell.get('title') in required_stop_titles
            )
        ]
    except (FileNotFoundError, json.JSONDecodeError):
        board_data = []
        current_cell = None
        st.error("ボードデータの読み込みに失敗しました")

    # ステージ補正
    if stage not in {'card', 'roulette'}:
        stage = st.session_state.game_board_stage = 'card'

    def compute_allowed_numbers(position: int):
        distance_to_goal = max(0, max_position_index - position)
        if distance_to_goal <= 0:
            return [], None, distance_to_goal

        max_spin = 3
        max_reachable = min(max_spin, distance_to_goal)

        next_stop_distance = None
        for stop_pos in forced_stop_indices:
            if stop_pos > position:
                next_stop_distance = stop_pos - position
                break

        if next_stop_distance is not None and next_stop_distance > 0:
            limit = min(max_reachable, next_stop_distance)
        else:
            limit = max_reachable

        allowed = list(range(1, limit + 1))

        return allowed, next_stop_distance, distance_to_goal

    def render_cell_media(position: int, cell_info: dict) -> None:
        try:
            from services.image_helper import display_image
            image_spec = cell_info.get('image')
            category = "board"
            filename = None
            if isinstance(image_spec, str) and image_spec.strip():
                parts = image_spec.strip().split("/", 1)
                if len(parts) == 2:
                    category, filename = parts
                else:
                    filename = parts[0]
            if not filename:
                filename = f"cell_{position + 1:02d}"
            if not display_image(category, filename, "", fill='stretch'):
                action_name = cell_info.get('action')
                action_to_image = {
                    'self_introduction': 'self_introduction',
                    'jump_exercise': 'jump',
                    'tooth_loss': 'tooth_loss',
                    'job_experience': 'job_experience'
                }
                if action_name in action_to_image:
                    display_image("events", action_to_image[action_name], "", fill='stretch')
        except ImportError:
            pass

    def get_display_label(position: int) -> str:
        if 0 <= position < len(board_data):
            label = board_data[position].get('display_label')
            if label:
                return str(label)
        return str(position)

    def process_spin_result(result_value: int):
        # 最新の位置を取得
        old_position = st.session_state.game_state.get('current_position', 0)
        new_position = min(old_position + result_value, max_position_index)
        old_label = get_display_label(old_position)
        
        # game_stateを直接更新
        st.session_state.game_state['current_position'] = new_position
        st.session_state.game_state['turn_count'] = st.session_state.game_state.get('turn_count', 0) + 1
        st.session_state.game_state['just_moved'] = True

        feedback = {
            'result': result_value,
            'old_position': old_position,
            'new_position': new_position,
            'move_message': f"➡️ {old_label}ばんめ → {get_display_label(new_position)}ばんめ にすすんだよ！",
            'coin_messages': [],
            'tooth_messages': [],
            'landing_message': None,
            'landing_tone': None,
            'next_page': None,
            'next_button_label': "つぎのマスをみる"
        }

        if board_data and 0 <= new_position < len(board_data):
            game_state_ref = st.session_state.game_state

            def apply_coin_delta(cell: dict) -> None:
                tooth_delta = cell.get('tooth_delta', 0)
                if tooth_delta == 0:
                    return
                old_coins = game_state_ref.get('tooth_coins', 10)
                new_coins = max(0, old_coins + tooth_delta)
                game_state_ref['tooth_coins'] = new_coins

            def resolve_cell_effect(cell: dict) -> None:
                apply_coin_delta(cell)
                apply_tooth_effects(game_state_ref, cell, feedback)

            landing_cell = board_data[new_position]
            resolve_cell_effect(landing_cell)

            landing_title = landing_cell.get('title', '')
            landing_type = landing_cell.get('type', 'normal')
            feedback['move_message'] = f"➡️ {old_label}ばんめ → {get_display_label(new_position)}ばんめ にすすんだよ！"
            feedback['new_position'] = new_position

            if feedback.get('next_page') is None:
                if landing_type == 'quiz':
                    quiz_type = landing_cell.get('quiz_type', '')
                    if quiz_type == 'caries' or '虫歯' in landing_title:
                        feedback['landing_message'] = "🦷 むしばクイズのマスにとうちゃく！"
                        feedback['landing_tone'] = 'success'
                        feedback['next_page'] = 'caries_quiz'
                        feedback['next_button_label'] = "🦷 クイズへすすむ"
                    elif quiz_type == 'periodontitis' or '歯周病' in landing_title or 'はぐき' in landing_title:
                        feedback['landing_message'] = "🦷 はぐきのクイズのマスにとうちゃく！"
                        feedback['landing_tone'] = 'success'
                        feedback['next_page'] = 'perio_quiz'
                        feedback['next_button_label'] = "🦷 クイズへすすむ"
                elif landing_type == 'stop':
                    next_action = landing_cell.get('next_action') or landing_cell.get('route')
                    if not next_action and '検診' in landing_title:
                        next_action = 'checkup'
                    if next_action:
                        action_map = {
                            'checkup': {
                                'message': "🏥 ていきけんしんに いこう！",
                                'tone': 'success',
                                'page': 'checkup',
                                'button': "🏥 けんしんへすすむ"
                            },
                            'caries_quiz': {
                                'message': "🦷 むしばクイズのじゅんびが できたよ！",
                                'tone': 'success',
                                'page': 'caries_quiz',
                                'button': "🦷 クイズへすすむ"
                            },
                            'periodontitis_quiz': {
                                'message': "🦷 はぐきクイズに すすもう！",
                                'tone': 'success',
                                'page': 'perio_quiz',
                                'button': "🦷 クイズへすすむ"
                            },
                            'job_experience': {
                                'message': "👩‍⚕️ おしごとたいけんに いこう！",
                                'tone': 'success',
                                'page': 'job_experience',
                                'button': "👩‍⚕️ おしごとたいけんへ"
                            },
                            'refresh': {
                                'message': "🔁 ボードにもどろう！",
                                'tone': 'info',
                                'page': 'refresh'
                            }
                        }
                        action_cfg = action_map.get(next_action)
                        if action_cfg:
                            feedback['landing_message'] = action_cfg['message']
                            feedback['landing_tone'] = action_cfg['tone']
                            feedback['next_page'] = action_cfg['page']
                            feedback['next_button_label'] = action_cfg.get('button', feedback['next_button_label'])
                            if next_action == 'checkup':
                                target = landing_cell.get('checkup_target') or landing_cell.get('route') or 'caries_quiz'
                                st.session_state.pending_checkup_target = target
                                st.session_state.pending_checkup_cell = landing_cell.get('cell', new_position)
                                st.session_state.pending_checkup_image = landing_cell.get('image')
                        else:
                            feedback['landing_message'] = "🏥 はいしゃさんのマスにとうちゃく！"
                            feedback['landing_tone'] = 'success'
                            feedback['next_page'] = next_action
                        feedback['landing_message'] = "🏥 はいしゃさんのマスにとうちゃく！"
                        feedback['landing_tone'] = 'success'
                elif landing_cell.get('coupon_url'):
                    # クーポンマスの処理
                    coupon_url = landing_cell.get('coupon_url')
                    feedback['landing_message'] = "🎟️ クーポンをゲット！"
                    feedback['landing_tone'] = 'success'
                    feedback['coupon_url'] = coupon_url
                elif '職業' in landing_title:
                    if st.session_state.participant_age >= 5:
                        feedback['landing_message'] = "👩‍⚕️ おしごとたいけんのマスにとうちゃく！"
                        feedback['landing_tone'] = 'success'
                        feedback['next_page'] = 'job_experience'
                        feedback['next_button_label'] = "👩‍⚕️ おしごとたいけんへ"
                    else:
                        feedback['landing_message'] = "おしごとたいけんは5さい以上だよ。"
                        feedback['landing_tone'] = 'info'
                elif new_position >= max_position_index:
                    feedback['landing_message'] = "🏁 ゴール！すごいね！"
                    feedback['landing_tone'] = 'success'
                    feedback['next_page'] = 'goal'
                    feedback['next_button_label'] = "🏁 ゴールへすすむ"
                    st.session_state.game_state['reached_goal'] = True
                    st.balloons()
            elif new_position >= max_position_index:
                feedback['landing_message'] = "🏁 ゴール！すごいね！"
                feedback['landing_tone'] = 'success'
                feedback['next_page'] = 'goal'
                feedback['next_button_label'] = "🏁 ゴールへすすむ"
                st.session_state.game_state['reached_goal'] = True
                st.balloons()
        else:
            if old_position >= max_position_index:
                feedback['landing_message'] = "🏁 ゴール！すごいね！"
                feedback['landing_tone'] = 'success'
                feedback['next_page'] = 'goal'
                feedback['next_button_label'] = "🏁 ゴールへすすむ"
                st.balloons()

        return feedback

    def finalize_spin(move_value: int):
        feedback = process_spin_result(move_value)
        st.session_state.roulette_recent_feedback = feedback
        st.session_state.pop('pending_spin_allowed', None)
        st.session_state.pop('roulette_spin_state', None)
        st.session_state.game_board_stage = 'card'

        next_page = feedback.get('next_page')
        if next_page and next_page != 'refresh':
            navigate_to(next_page)
        else:
            st.session_state.current_page = 'game_board'
            st.rerun()

    st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)
    focus_col = st.columns([0.06, 0.88, 0.06])[1]

    with focus_col:
        if stage == 'card':
            recent_feedback = st.session_state.pop('roulette_recent_feedback', None)
            if recent_feedback:
                for tone, message in recent_feedback.get('coin_messages', []):
                    if tone == 'success':
                        st.success(message)
                    elif tone == 'warning':
                        st.warning(message)
                    else:
                        st.info(message)
                for tone, message in recent_feedback.get('tooth_messages', []):
                    if tone == 'success':
                        st.success(message)
                    elif tone == 'warning':
                        st.warning(message)
                    elif tone == 'error':
                        st.error(message)
                    else:
                        st.info(message)
                landing_message = recent_feedback.get('landing_message')
                if landing_message and recent_feedback.get('next_page') == 'refresh':
                    tone = recent_feedback.get('landing_tone', 'info')
                    if tone == 'success':
                        st.success(landing_message)
                    elif tone == 'warning':
                        st.warning(landing_message)
                    else:
                        st.info(landing_message)

                
                # クーポン表示
                if recent_feedback.get('coupon_url'):
                    import streamlit.components.v1 as components
                    coupon_url = recent_feedback.get('coupon_url')
                    
                    components.html(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <button id="couponBtn2" style="
                            background-color: #FF4B4B;
                            color: white;
                            padding: 15px 32px;
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 16px;
                            margin: 4px 2px;
                            cursor: pointer;
                            border: none;
                            border-radius: 12px;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                            transition: all 0.3s ease;
                        ">
                            🎟️ クーポンをゲット！
                        </button>
                        <p style="font-size: 0.85em; color: #666; margin-top: 10px;">※別のブラウザタブで開きます</p>
                        <p style="font-size: 0.75em; color: #999;">クーポン取得後、このゲームに戻って続きをお楽しみください</p>
                    </div>
                    <script>
                        document.getElementById('couponBtn2').addEventListener('click', function() {{
                            window.open('{coupon_url}', '_blank');
                        }});
                        
                        document.getElementById('couponBtn2').addEventListener('mouseover', function() {{
                            this.style.backgroundColor = '#E63946';
                            this.style.transform = 'scale(1.05)';
                        }});
                        document.getElementById('couponBtn2').addEventListener('mouseout', function() {{
                            this.style.backgroundColor = '#FF4B4B';
                            this.style.transform = 'scale(1)';
                        }});
                    </script>
                    """, height=150)

            st.session_state.pop('roulette_feedback', None)
            st.session_state.pop('roulette_last_spin_id', None)
            if current_cell is None:
                st.warning("マスの情報がみつかりませんでした。")
                return

            total_cells = len(board_data)
            if total_cells:
                # 論理的なステップ（表示ラベル）のユニークなリストを作成
                logical_steps = []
                seen_labels = set()
                
                # 現在位置のラベルを取得
                current_label = get_display_label(current_position)
                
                # 全セルのラベルを順に取得し、ユニークなステップリストを作成
                for idx in range(total_cells):
                    label = get_display_label(idx)
                    if label not in seen_labels:
                        logical_steps.append(label)
                        seen_labels.add(label)
                
                nodes_html = []
                current_step_found = False
                
                for label in logical_steps:
                    classes = ["board-progress-node"]
                    
                    # 現在のステップかどうかの判定
                    is_current = (label == current_label)
                    
                    if is_current:
                        classes.append("is-current")
                        current_step_found = True
                    elif not current_step_found:
                        classes.append("is-visited")
                        
                    nodes_html.append(f"<div class='{' '.join(classes)}'>{label}</div>")
                    
                st.markdown(
                    f"<div class='board-progress-track'>{''.join(nodes_html)}</div>",
                    unsafe_allow_html=True,
                )

            title = current_cell.get('title', '')
            skip_media = (
                current_cell
                and ('職業' in title or 'おしごと' in title or 'お仕事' in title or current_cell.get('type') == 'job_experience')
                and st.session_state.participant_age >= 5
            )
            if not skip_media:
                render_cell_media(current_position, current_cell)
                
                # captionがあれば表示
                caption = current_cell.get('caption')
                if caption:
                    st.markdown(f"<div style='text-align: center; color: #5c4033; margin-top: 1rem; padding: 0 1rem; line-height: 1.6;'>{caption}</div>", unsafe_allow_html=True)
                
                # クーポンボタンを表示（現在のセルにcoupon_urlがある場合）
                if current_cell.get('coupon_url'):
                    coupon_url = current_cell.get('coupon_url')
                    
                    # st.components.v1.htmlを使って確実にJavaScriptを実行
                    import streamlit.components.v1 as components
                    
                    components.html(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <button id="couponBtn" style="
                            background-color: #FF4B4B;
                            color: white;
                            padding: 15px 32px;
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 16px;
                            margin: 4px 2px;
                            cursor: pointer;
                            border: none;
                            border-radius: 12px;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                            transition: all 0.3s ease;
                        ">
                            🎟️ クーポンをゲット！
                        </button>
                        <p style="font-size: 0.85em; color: #666; margin-top: 10px;">※別のブラウザタブで開きます</p>
                        <p style="font-size: 0.75em; color: #999;">クーポン取得後、このゲームに戻って続きをお楽しみください</p>
                    </div>
                    <script>
                        document.getElementById('couponBtn').addEventListener('click', function() {{
                            window.open('{coupon_url}', '_blank');
                        }});
                        
                        // ホバー効果
                        document.getElementById('couponBtn').addEventListener('mouseover', function() {{
                            this.style.backgroundColor = '#E63946';
                            this.style.transform = 'scale(1.05)';
                        }});
                        document.getElementById('couponBtn').addEventListener('mouseout', function() {{
                            this.style.backgroundColor = '#FF4B4B';
                            this.style.transform = 'scale(1)';
                        }});
                    </script>
                    """, height=150)

            cell_type = current_cell.get('type', 'normal')
            action_taken = False

            if cell_type == 'quiz':
                quiz_type = current_cell.get('quiz_type', '')
                if quiz_type == 'caries':
                    if st.button("🦷 むしばクイズにちょうせん！", use_container_width=True, type="primary"):
                        st.session_state.caries_quiz_stage = 'question_0'
                        st.session_state.caries_quiz_answers = [None] * 5 # Initialize with safe size, will be resized if needed
                        navigate_to('caries_quiz')
                        action_taken = True
                elif quiz_type == 'perio':
                    if st.button("🦷 はぐきのクイズにちょうせん！", use_container_width=True, type="primary"):
                        st.session_state.perio_quiz_stage = 'question_0'
                        st.session_state.perio_quiz_answers = [None] * 5
                        navigate_to('perio_quiz')
                        action_taken = True
            next_action = current_cell.get('next_action') or current_cell.get('route')
            if cell_type == 'stop' or '検診' in title:
                # next_actionがperiodontitis_quizの場合は定期検診ページに行かず、
                # すでに検診完了とみなしてルーレットを表示する
                if next_action == 'periodontitis_quiz':
                    # cell_15: 定期検診完了済み、次は歯周病クイズへ
                    action_taken = True  # ボタン表示せず、ルーレットを有効化
                    st.success("🏥 ていきけんしん かんりょう！")
                    st.info("つぎのマスへすすもう！")
                elif next_action in {'checkup', 'caries_quiz', 'perio_quiz'} or '検診' in title:
                    # cell_4: 定期検診ページへ遷移
                    if st.button("🏥 はいしゃさんにいく", use_container_width=True, type="primary"):
                        target = current_cell.get('checkup_target') or next_action or 'caries_quiz'
                        st.session_state.pending_checkup_target = target
                        st.session_state.pending_checkup_cell = current_cell.get('cell', current_position)
                        st.session_state.pending_checkup_image = current_cell.get('image')
                        navigate_to('checkup')
            elif cell_type == 'goal' or current_position == max_position_index:
                st.success("🎉 ゴールにとうちゃく！")
                if st.button("▶️ ゴールへ", use_container_width=True, type="primary"):
                    navigate_to('goal')
                action_taken = True

            elif cell_type == 'event':
                # 通常のイベントは特別なアクションなし
                action_taken = False

            # むし歯治療ボタンの表示
            if st.session_state.get('needs_caries_treatment', False):
                st.markdown("<div style='height:1vh'></div>", unsafe_allow_html=True)
                if st.button("🦷 治療を受ける", key="caries_treatment_btn", use_container_width=True, type="primary"):
                    # 虫歯を治療済みに変更（C → R）
                    teeth_service.restore_damaged_teeth()
                    teeth_service.restore_stained_teeth()
                    st.session_state.teeth_data = teeth_service.load_teeth_json()
                    
                    # フラグをクリア
                    st.session_state.needs_caries_treatment = False
                    
                    # 成功メッセージ
                    st.success("✨ 虫歯の治療が完了しました！")
                    st.rerun()


            # cell_15 (next_action='periodontitis_quiz') の場合は、action_taken=Trueでもルーレットを表示
            next_action = current_cell.get('next_action', '')
            is_completed_checkup = (next_action == 'periodontitis_quiz')
            
            can_spin = ((not action_taken or is_completed_checkup) 
                        and cell_type != 'quiz'
                        and not (cell_type == 'stop' and next_action and next_action != 'periodontitis_quiz')
                        and current_position < max_position_index)
            
            print(f"🔍 DEBUG [can_spin]: action_taken={action_taken}, cell_type='{cell_type}', title='{title}', next_action='{next_action}', can_spin={can_spin}")

            if can_spin:
                allowed_numbers, _, _ = compute_allowed_numbers(current_position)
                if not allowed_numbers:
                    st.info("今回はすすむマスがないよ。")
                else:
                    st.markdown("<div style='height:1.5vh'></div>", unsafe_allow_html=True)
                    if st.button("🎡 ルーレットをまわす", key="board_to_roulette", use_container_width=True, type="primary"):
                        st.session_state.pending_spin_allowed = allowed_numbers
                        st.session_state.pop('roulette_spin_state', None)
                        st.session_state.game_board_stage = 'roulette'
                        st.session_state.pop('roulette_recent_feedback', None)
                        st.rerun()
            elif not action_taken and current_position >= max_position_index:
                if st.button("🏁 ゴールへ", use_container_width=True, type="primary"):
                    navigate_to('goal')

        elif stage == 'roulette':
            if current_position >= max_position_index or (current_cell and current_cell.get('type') == 'goal'):
                st.success("🎉 ゴールにとうちゃく！")
                if st.button("▶️ ゴールへ", use_container_width=True, type="primary"):
                    st.session_state.game_board_stage = 'card'
                    navigate_to('goal')
                return

            allowed_numbers = st.session_state.get('pending_spin_allowed', [])

            if not allowed_numbers:
                st.session_state.game_board_stage = 'card'
                st.rerun()

            st.markdown("<h2 style='text-align:center; margin-bottom:1rem;'>ルーレットを回そう！</h2>", unsafe_allow_html=True)

            spin_state = st.session_state.get('roulette_spin_state')

            if spin_state:
                snapshot = spin_state.get('allowed_snapshot') or []
                if set(snapshot) != set(allowed_numbers):
                    st.info("ボードの状況が変わったので、ルーレットをもういちど用意するね。")
                    st.session_state.pop('roulette_spin_state', None)
                    st.rerun()

            def render_chips(active_value):
                display_numbers = [1, 2, 3]
                chips = []
                for num in display_numbers:
                    classes = ["roulette-number-chip"]
                    if active_value == num:
                        classes.append("is-active")
                    if num not in allowed_numbers:
                        classes.append("is-disabled")
                    classes_str = ' '.join(classes)
                    chips.append(f"<div class='{classes_str}' data-value='{num}'>{num}</div>")
                return ''.join(chips)

            def render_card(active_value, subtitle="でるかず", message="でた数だけ、ゲームボードがすすむよ！"):
                return f"""
                    <div class="roulette-card">
                        <p class="roulette-subtitle">{subtitle}</p>
                        <div class="roulette-number-row">{render_chips(active_value)}</div>
                        <p style="margin:0; color:#7b552e;">{message}</p>
                    </div>
                """

            card_placeholder = st.empty()

            if not spin_state:
                card_placeholder.markdown(render_card(None), unsafe_allow_html=True)
                if st.button("🎡 ルーレットを回す", key="roulette_spin_button", type="primary"):
                    pool = allowed_numbers or [1]
                    animation_sequence = []
                    base_sequence = list(range(1, 4))
                    for _ in range(5):
                        animation_sequence.extend(base_sequence)
                    animation_sequence.extend(pool)
                    for value in animation_sequence:
                        card_placeholder.markdown(
                            render_card(value, subtitle="ルーレット くるくる…", message="どの数字になるかな？"),
                            unsafe_allow_html=True,
                        )
                        time.sleep(0.08)
                    result_value = pool[-1] if len(pool) == 1 else random.choice(pool)
                    st.session_state.roulette_spin_state = {
                        'status': 'result',
                        'value': result_value,
                        'allowed_snapshot': pool,
                        'timestamp': datetime.now().isoformat(),
                    }
                    st.rerun()
            else:
                if spin_state.get('status') != 'result':
                    st.session_state.pop('roulette_spin_state', None)
                    st.rerun()
                result_value = spin_state.get('value', allowed_numbers[0] if allowed_numbers else 1)
                card_placeholder.markdown(render_card(result_value), unsafe_allow_html=True)
                if st.button(f"{result_value}マスすすむ", key="roulette_apply", type="primary", use_container_width=True):
                    st.session_state.pop('roulette_spin_state', None)
                    finalize_spin(result_value)
                    return

    st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)

def show_caries_quiz_page():
    """むしばクイズページ（JSON対応）"""
    from services.image_helper import display_image
    
    # 参加者の年齢を取得
    participant_age = st.session_state.get('participant_age', 5)
    
    # JSONからクイズデータを読み込む
    quiz_data = load_quiz_data('caries', participant_age)
    questions = quiz_data.get('questions', [])
    rewards = quiz_data.get('rewards', {})
    
    stage = st.session_state.get('caries_quiz_stage', 'intro')
    answers = st.session_state.setdefault('caries_quiz_answers', [None] * len(questions))

    if stage == 'intro':
        st.markdown(f"### 🦷 {quiz_data.get('title', 'むしばクイズ')}")
        try:
            display_image("board", "cell_07", "")
        except ImportError:
            st.markdown("カードを確認したかな？むしばについてのクイズに備えてね。")
        if st.button("🦷 クイズへすすむ", type="primary", use_container_width=True):
            st.session_state.caries_quiz_stage = 'question_0'
            st.session_state.caries_quiz_answers = [None] * len(questions)
            # 各問題のセッションステートをクリア
            for i in range(len(questions)):
                st.session_state.pop(f'caries_q{i}_selected', None)
                st.session_state.pop(f'caries_q{i}_checked', None)
            st.rerun()
        return

    if stage.startswith('question_'):
        try:
            question_index = int(stage.split('_')[1])
        except (IndexError, ValueError):
            question_index = 0

        # 1問目のみタイトル表示
        if question_index == 0:
            st.markdown(f"### 🦷 {quiz_data.get('title', 'むしばクイズ')}にちょうせん！")
        
        if question_index >= len(questions):
            st.error("問題が見つかりません")
            return
        
        question = questions[question_index]
        question_id = question.get('id', f'q{question_index}')
        state_key_selected = f"caries_q{question_index}_selected"
        state_key_checked = f"caries_q{question_index}_checked"

        def render_option_buttons(options, selected, key_prefix):
            state_key = f"{key_prefix}_selected"
            if selected is None:
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

        st.markdown("---")
        st.markdown(f"{question.get('text', '')}</h3>", unsafe_allow_html=True)
        
        # 画像表示
        images = question.get('images', [])  # Support multiple images
        image_category = question.get('image_category')
        image_name = question.get('image_name')
        
        # Single image from legacy fields
        if (image_category or image_name) and not images:
            images = [{'category': image_category or 'quiz/caries', 'name': image_name or f'question_{question_index + 1}'}]
        
        if images and len(images) > 0:
            try:
                if len(images) == 1:
                    # Center single image
                    display_image(
                        images[0].get('category', 'quiz/caries'),
                        images[0].get('name', f'question_{question_index + 1}'),
                        f"問題{question_index + 1}の画像",
                    )
                else:
                    # Multiple images in columns
                    cols = st.columns(len(images))
                    for idx, img in enumerate(images):
                        with cols[idx]:
                            display_image(
                                img.get('category', 'quiz/caries'),
                                img.get('name', f'question_{question_index + 1}_{idx + 1}'),
                                f"問題{question_index + 1}の画像{idx + 1}",
                            )
            except (ImportError, KeyError):
                pass

        # 選択肢表示
        if state_key_selected not in st.session_state:
            st.session_state[state_key_selected] = None
        
        selected_idx = render_option_buttons(
            question.get('options', []),
            answers[question_index],
            f"caries_q{question_index}"
        )
        answers[question_index] = selected_idx

        st.markdown("---")
        submit_btn = st.button(
            "📝 こたえをかくにん",
            key=f"caries_submit_q{question_index}",
            type="primary",
            use_container_width=True,
        )

        if submit_btn:
            if answers[question_index] is None:
                st.warning("こたえをえらんでね！")
            else:
                correct_answer = question.get('correct', 0)
                if answers[question_index] == correct_answer:
                    feedback = question.get('correct_feedback', 'せいかい！')
                    st.success(feedback)
                else:
                    feedback = question.get('incorrect_feedback', 'ざんねん…')
                    st.warning(feedback)
                    explanation = question.get('explanation', '')
                    if explanation:
                        st.info(f"✅ {explanation}")
                st.session_state[state_key_checked] = True

        # 次の問題へ or 結果表示
        if st.session_state.get(state_key_checked):
            if question_index < len(questions) - 1:
                # 次の問題へ
                if st.button(
                    "▶️ つぎのもんだいへ",
                    key=f"caries_next_q{question_index}",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state.pop(state_key_checked, None)
                    st.session_state.caries_quiz_stage = f'question_{question_index + 1}'
                    save_state_to_url()
                    st.rerun()
            else:
                # 最終問題の場合、結果表示
                if st.button(
                    "次へすすむ",
                    key=f"caries_finalize_q{question_index}",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state.pop(state_key_checked, None)
                    
                    # 正解数をカウント
                    correct_count = sum(
                        1
                        for i, q in enumerate(questions)
                        if i < len(answers) and answers[i] == q.get('correct', 0)
                    )
                    
                    st.success(f"せいかいかず: {correct_count}/{len(questions)}")
                    
                    # 各問題の結果表示
                    for i, q in enumerate(questions):
                        if i < len(answers):
                            if answers[i] == q.get('correct', 0):
                                st.success(f"もんだい{i+1}せいかい！ {q.get('explanation', '')}")
                            else:
                                st.warning(f"もんだい{i+1}は ざんねん… {q.get('explanation', '')}")
                    
                    # 報酬とポジション更新
                    if 'game_state' in st.session_state:
                        game_state = st.session_state.game_state
                        high_score = rewards.get('high_score', {})
                        low_score = rewards.get('low_score', {})
                        
                        threshold = high_score.get('threshold', 1)
                        
                        if correct_count >= threshold:
                            coins = high_score.get('coins', 0)
                            position = high_score.get('position', 11)  # 正解ルート: cell 11 フロス
                            message = high_score.get('message', '🌟 よくできました！')
                            
                            game_state['tooth_coins'] += coins
                            game_state['current_position'] = position
                            st.success(message)
                        else:
                            coins = low_score.get('coins', 0)
                            position = low_score.get('position', 8)  # 不正解ルート: cell 8 むし歯治療
                            message = low_score.get('message', '💧 もう少し頑張りましょう')
                            
                            game_state['tooth_coins'] = max(0, game_state['tooth_coins'] + coins)
                            game_state['current_position'] = position
                            st.warning(message)
                        
                        # Tooth transition: 20 (baby teeth) -> 28 (adult teeth)
                        # This simulates the natural transition from baby teeth to adult teeth
                        st.info("🦷 **おとなのはに はえかわったよ！** 20ほん → 28ほん")
                        
                        # Upgrade to adult teeth (28 teeth)
                        from services import teeth as teeth_service
                        teeth_service.ensure_tooth_state(game_state)
                        if teeth_service.upgrade_to_adult(game_state):
                            # Reset all teeth to healthy state with 28 teeth
                            teeth_service.reset_all_teeth_to_healthy(game_state)
                            game_state['teeth_count'] = 28
                            game_state['teeth_max'] = 28
                            game_state['teeth_missing'] = 0
                            st.session_state.teeth_count = 28
                            st.session_state.post_quiz_full_teeth = True
                            st.balloons()
                        
                        # クイズ完了後はaction_takenをFalseにして、分岐マスでルーレットを表示できるようにする
                        game_state['action_taken'] = False
                        game_state['action_completed'] = False
                    
                    st.info("つづきは ゲームボードで！")
                    
                    # セッションステートをクリア
                    st.session_state.caries_quiz_stage = 'intro'
                    st.session_state.pop('caries_quiz_answers', None)
                    for i in range(len(questions)):
                        st.session_state.pop(f'caries_q{i}_selected', None)
                        st.session_state.pop(f'caries_q{i}_checked', None)
                    
                    navigate_to('game_board')
        else:
            st.caption("こたえをかくにんしてから つぎへすすもう！")
        return

def show_job_experience_page():
    """おしごとたいけんページ（ルーレット機能付き）"""
    import time
    try:
        from services.image_helper import display_image
    except ImportError:
        display_image = None
    
    # デバッグ情報（ターミナルのみ）
    print(f"\n🔍 DEBUG [job_experience]: page loaded")
    
    if display_image:
        display_image("board", "cell_13", "", fill='stretch')
    
    # 職業データ
    jobs = [
        {
            "id": "dentist",
            "name": "はいしゃさん",
            "emoji": "🦷",
            #"description": "むしばをなおす おいしゃさんだよ"
        },
        {
            "id": "hygienist", 
            "name": "しかえいせいしさん",
            "emoji": "✨",
            #"description": "はをきれいにする せんせいだよ"
        },
        {
            "id": "technician",
            "name": "しかぎこうしさん", 
            "emoji": "🔧",
            #"description": "ぎばや はのかぶせものをつくる せんせいだよ"
        }
    ]
    
    # ルーレットの状態管理（強制的に初期化）
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
    
    # ターミナルデバッグ出力
    print(f"\n🔍 DEBUG [job_experience]: roulette_state={roulette_state}, result={result}")
    print(f"🔍 DEBUG [job_experience]: session_keys={list(st.session_state.keys())}")
    
    # ルーレット初期状態
    if roulette_state == 'idle' or roulette_state is None:
        print(f"🔍 DEBUG [job_experience]: 初期画面表示")
        
        st.markdown("<p style='text-align:center; font-size:1.2em; color:#5d4037; margin:20px 0;'>どの おしごとに ちょうせんするか ルーレットできめよう！</p>", unsafe_allow_html=True)
        
        # Streamlitのcolumnsを使ってカード表示
        cols = st.columns(3)
        
        for idx, (col, job) in enumerate(zip(cols, jobs)):
            with col:
                # カード風のコンテナ
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
        print(f"🔍 DEBUG [job_experience]: st.columns()でカード表示")
        
        # ルーレットボタン
        if st.button("🎰 ルーレットをまわす", key="start_job_roulette", use_container_width=True, type="primary"):
            print(f"🔍 DEBUG [job_experience]: ルーレットボタンクリック")
            st.session_state.job_roulette_state = 'spinning'
            st.rerun()
    
    # ルーレット回転中
    elif roulette_state == 'spinning':
        print(f"🔍 DEBUG [job_experience]: ルーレット回転中")
        st.markdown("<p style='text-align:center; font-size:1.2em; color:#ff6b6b;'>🎰 ルーレット ちゅう…</p>", unsafe_allow_html=True)
        
        # プレースホルダー
        card_placeholder = st.empty()
        
        # ランダムアニメーション
        import random
        animation_sequence = [random.randint(0, 2) for _ in range(12)]
        final_result = random.randint(0, 2)
        animation_sequence.append(final_result)
        
        print(f"🔍 DEBUG [job_experience]: 最終結果 = {final_result}")
        
        # アニメーション実行
        for active_idx in animation_sequence:
            with card_placeholder.container():
                cols = st.columns(3)
                for idx, (col, job) in enumerate(zip(cols, jobs)):
                    with col:
                        # activeクラスの代わりにborder-colorを変更
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
        
        # 結果保存
        st.session_state.job_roulette_result = final_result
        st.session_state.job_roulette_state = 'result'
        print(f"🔍 DEBUG [job_experience]: ルーレット完了")
        st.rerun()
    
    # 結果表示
    elif roulette_state == 'result' and result is not None:
        selected_job = jobs[result]
        
        st.success(f"🎉 {selected_job['name']} にきまったよ！")
        
        # 選択された職業を強調表示
        cols = st.columns(3)
        for idx, (col, job) in enumerate(zip(cols, jobs)):
            with col:
                # 選択されたカードは緑色
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
        print(f"🔍 DEBUG [job_experience]: 結果表示 - st.columns()使用")
        st.info(f"これから {selected_job['name']}の おしごとを たいけんするよ！")
        
        # タイマー表示（5分）
        if st.session_state.job_timer_start is None:
            if st.button("⏱️ たいけん スタート！", key="start_job_timer", use_container_width=True, type="primary"):
                st.session_state.job_timer_start = datetime.now()
                st.session_state.job_force_complete = False  # 強制完了フラグ初期化
                st.rerun()
        else:
            start_time = st.session_state.job_timer_start
            elapsed = (datetime.now() - start_time).total_seconds()
            time_limit = 300  # 5分 = 300秒
            remaining = max(0, time_limit - elapsed)
            
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            
            # タイマー表示
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
            if 'job_force_complete_unlocked' not in st.session_state:
                st.session_state.job_force_complete_unlocked = False
            
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
            
            # 強制完了された場合の表示
            if st.session_state.get('job_force_complete'):
                st.success("⚡ スタッフによって体験が即座に完了しました！")
                remaining = 0  # タイマーを0にする
            elif remaining > 0:
                # 自動更新
                time.sleep(1)
                st.rerun()
            else:
                st.success("⏰ 5ふん たっせい！ おしごとたいけん かんりょう！")
                
            # 完了ボタン
            if st.button("✅ たいけん かんりょう", key="finish_job", use_container_width=True, type="primary"):
                # 報酬付与
                if 'game_state' in st.session_state:
                    game_state = st.session_state.game_state
                    
                    if st.session_state.get('job_force_complete'):
                        # 強制完了の場合も10コイン付与
                        game_state['tooth_coins'] = game_state.get('tooth_coins', 10) + 10
                        st.success("🎁 おしごとたいけん かんりょう！ +10トゥースコイン！")
                    elif remaining > 0:
                        game_state['tooth_coins'] = game_state.get('tooth_coins', 10) + 10
                        st.success("🎁 じかんないに かんりょう！ +10トゥースコイン！")
                    else:
                        game_state['tooth_coins'] = game_state.get('tooth_coins', 10) + 5
                        st.success("🎁 おつかれさま！ +5トゥースコイン！")
                    
                    # action_taken と action_completed を True にして次へ進めるようにする
                    game_state['action_taken'] = True
                    game_state['action_completed'] = True
                
                # 状態リセット
                st.session_state.job_roulette_state = None
                st.session_state.job_roulette_result = None
                st.session_state.job_timer_start = None
                st.session_state.job_force_complete = False
                st.session_state.job_force_complete_unlocked = False
                
                # job_experience_completed フラグを立てる
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

def show_checkup_page():
    """定期健診ページ"""
    from services.image_helper import display_image
    import json
    import os
    
    def resolve_checkup_target() -> str:
        target = st.session_state.get('pending_checkup_target')
        if target:
            return target
        pending_cell = st.session_state.get('pending_checkup_cell')
        board_position = st.session_state.get('game_state', {}).get('current_position', 0)
        try:
            game_state = st.session_state.get('game_state', {})
            age = st.session_state.get('participant_age', 5)
            board_file = f"data/board_main_{'under5' if age < 5 else '5plus'}.json"
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

def show_perio_quiz_page():
    """はぐきクイズページ（JSON対応）"""
    from services.image_helper import display_image
    
    # 参加者の年齢を取得
    participant_age = st.session_state.get('participant_age', 5)
    
    # JSONからクイズデータを読み込む
    quiz_data = load_quiz_data('perio', participant_age)
    questions = quiz_data.get('questions', [])
    rewards = quiz_data.get('rewards', {})

    stage = st.session_state.get('perio_quiz_stage', 'intro')
    if stage == 'questions':
        stage = 'question_0'
        st.session_state.perio_quiz_stage = stage

    if stage == 'intro':
        st.markdown(f"### 🦷 {quiz_data.get('title', 'はぐきクイズ')}")
        st.caption("カードをよんだら、ボタンをおしてクイズにすすもう！")
        try:
            display_image("board", "cell_20", "", use_container_width=True)
        except ImportError:
            st.info("カードをよんで はぐきクイズのじゅんびをしよう。")
        if st.button("🦷 クイズへすすむ", type="primary", use_container_width=True):
            st.session_state.perio_quiz_stage = 'question_0'
            st.session_state.perio_quiz_answers = [None] * len(questions)
            # 各問題のセッションステートをクリア
            for i in range(len(questions)):
                st.session_state.pop(f'perio_q{i}_selected', None)
                st.session_state.pop(f'perio_q{i}_checked', None)
            st.rerun()
        return

    answers = st.session_state.setdefault('perio_quiz_answers', [None] * len(questions))

    def render_option_buttons(options, selected, key_prefix):
        state_key = f"{key_prefix}_selected"
        # セッションステートに値があればそれを優先（クリック直後の反映のため）
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

    if stage.startswith('question_'):
        try:
            question_index = int(stage.split('_')[1])
        except (IndexError, ValueError):
            question_index = 0

        # 1問目のみタイトル表示
        if question_index == 0:
            st.markdown(f"### 🦷 {quiz_data.get('title', 'はぐきクイズ')}")

        if question_index >= len(questions):
            st.error("問題が見つかりません")
            return
        
        question = questions[question_index]
        state_key_selected = f"perio_q{question_index}_selected"
        state_key_checked = f"perio_q{question_index}_checked"

        st.caption(f"もんだい {question_index + 1} / {len(questions)}")
        st.markdown("---")

        if state_key_selected not in st.session_state:
            st.session_state[state_key_selected] = None
        
        # 問題の画像表示
        images = question.get('images', [])  # Support multiple images
        image_category = question.get('image_category')
        image_name = question.get('image_name')
        
        # Handle legacy single image or list of image names
        if not images:
            if isinstance(image_name, list):
                # Convert list of names to images format
                images = [{'category': image_category or 'quiz/periodontitis', 'name': name} for name in image_name]
            elif image_category or image_name:
                # Single image from legacy fields
                images = [{'category': image_category or 'quiz/periodontitis', 'name': image_name or f'question_{question_index + 1}'}]
        
        if images and len(images) > 0:
            try:
                if len(images) == 1:
                    # Center single image
                    display_image(
                        images[0].get('category', 'quiz/periodontitis'),
                        images[0].get('name', f'question_{question_index + 1}'),
                        f"問題{question_index + 1}の画像",
                    )
                else:
                    # Multiple images in columns
                    cols = st.columns(len(images))
                    for idx, img in enumerate(images):
                        with cols[idx]:
                            display_image(
                                img.get('category', 'quiz/periodontitis'),
                                img.get('name', f'question_{question_index + 1}_{idx + 1}'),
                                f"問題{question_index + 1}の画像{idx + 1}",
                            )
            except (ImportError, KeyError):
                pass

        st.markdown(f"<h3 style='font-size: 1.8em; margin: 20px 0;'>もんだい{question_index + 1}: {question.get('text', '')}</h3>", unsafe_allow_html=True)
        answers[question_index] = render_option_buttons(
            question.get('options', []),
            answers[question_index],
            f"perio_q{question_index}"
        )

        st.markdown("---")
        submit_btn = st.button(
            "📝 こたえをかくにん",
            key=f"perio_submit_q{question_index}",
            type="primary",
            use_container_width=True,
        )

        if submit_btn:
            if answers[question_index] is None:
                st.warning("こたえをえらんでね！")
            else:
                correct_answer = question.get('correct', 0)
                if answers[question_index] == correct_answer:
                    feedback = question.get('correct_feedback', 'せいかい！')
                    st.success(feedback)
                else:
                    feedback = question.get('incorrect_feedback', 'ざんねん…')
                    st.warning(feedback)
                    explanation = question.get('explanation', '')
                    if explanation:
                        st.info(f"✅ {explanation}")
                st.session_state[state_key_checked] = True

        # 次の問題へ or 結果表示
        if st.session_state.get(state_key_checked):
            if question_index < len(questions) - 1:
                # 次の問題へ
                if st.button(
                    "▶️ つぎのもんだいへ",
                    key=f"perio_next_q{question_index}",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state.pop(state_key_checked, None)
                    st.session_state.perio_quiz_stage = f'question_{question_index + 1}'
                    save_state_to_url()
                    st.rerun()
            else:
                # 最終問題の場合、結果表示
                if st.button(
                    "▶次へすすむ",
                    key=f"perio_finalize_q{question_index}",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state.pop(state_key_checked, None)
                    
                    if answers[question_index] is None:
                        st.warning("こたえをえらんでね！")
                        return

                    # 正解数をカウント
                    correct_count = sum(
                        1
                        for i, q in enumerate(questions)
                        if i < len(answers) and answers[i] == q.get('correct', 0)
                    )

                    st.success(f"せいかいかず: {correct_count}/{len(questions)}")

                    # 各問題の結果表示
                    for i, q in enumerate(questions):
                        if i < len(answers):
                            if answers[i] == q.get('correct', 0):
                                st.success(f"もんだい{i+1}せいかい！ {q.get('explanation', '')}")
                            else:
                                st.warning(f"もんだい{i+1}は ざんねん… {q.get('explanation', '')}")

                    # 報酬とポジション更新
                    if 'game_state' in st.session_state:
                        game_state = st.session_state.game_state
                        high_score = rewards.get('high_score', {})
                        low_score = rewards.get('low_score', {})
                        
                        threshold = high_score.get('threshold', 1)

                        if correct_count >= threshold:
                            coins = high_score.get('coins', 5)
                            position = high_score.get('position', 24)
                            message = high_score.get('message', '🌟 よくできました！')
                            
                            game_state['tooth_coins'] += coins
                            game_state['current_position'] = position
                            st.success(message)
                            st.balloons()
                        else:
                            coins = low_score.get('coins', -3)
                            position = low_score.get('position', 21)
                            message = low_score.get('message', '💧 もう少し頑張りましょう')
                            
                            game_state['tooth_coins'] = max(0, game_state['tooth_coins'] + coins)
                            game_state['current_position'] = position
                            st.warning(message)
                        
                        # クイズ完了フラグをセット（ループ防止）
                        game_state['action_taken'] = True
                        game_state['action_completed'] = True

                    # セッションステートをクリア
                    st.session_state.perio_quiz_stage = 'intro'
                    st.session_state.pop('perio_quiz_answers', None)
                    for i in range(len(questions)):
                        st.session_state.pop(f'perio_q{i}_selected', None)
                        st.session_state.pop(f'perio_q{i}_checked', None)
                    
                    st.info("つづきは ゲームボードで！")
                    navigate_to('game_board')
        else:
            st.caption("こたえをかくにんしてから つぎへすすもう！")
        return

def _build_session_record(game_state: dict) -> Dict[str, any]:
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
                "age_group": "under5" if st.session_state.get('participant_age', 5) < 5 else "5plus",
                "teeth_count": teeth_count,
                "tooth_coins": coins,
                "play_time": "0分0秒"  # Can be calculated if needed
            }
            if save_score(player_data):
                st.session_state.score_saved = True
        
        # Display leaderboard
        st.markdown("---")
        st.markdown("### 🏆 トップ10ランキング")
        
        leaderboard = load_leaderboard(top_n=10)
        
        if leaderboard:
            # Find player's rank
            player_name = st.session_state.get('participant_name', '匿名')
            for idx, entry in enumerate(leaderboard):
                if entry.get('player_name') == player_name and entry.get('score') == player_score:
                    player_rank = idx + 1
                    break
            
            # Display leaderboard table
            for idx, entry in enumerate(leaderboard):
                rank = idx + 1
                is_player = (rank == player_rank)
                
                # Medals for top 3
                medal = ""
                if rank == 1:
                    medal = "🥇"
                elif rank == 2:
                    medal = "🥈"
                elif rank == 3:
                    medal = "🥉"
                else:
                    medal = f"{rank}い"
                
                # Highlight player's row
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
                    # Use HTML for consistent responsive layout instead of st.columns
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
    if st.button("📱 LINEページへ", width='stretch', type="secondary"):
        navigate_to('line_coloring')

def show_line_coloring_page():
    """LINE・ぬりえページ"""
    st.markdown("### 🎁 イベント・プレゼント")
    
    # 1. Smoothie Banner
    banner_path = "assets/images/event_banner.png"
    if os.path.exists(banner_path):
        st.image(banner_path, use_column_width=True)
    else:
        # Placeholder if image doesn't exist
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

    # 2. SNS Buttons (Instagram & LINE)
    col1, col2 = st.columns(2)
    
    with col1:
        # Instagram Button
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
                transition: transform 0.2s;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            '>
                📷 Instagram<br>フォローする
            </div>
        </a>
        """, unsafe_allow_html=True)
        
    with col2:
        # LINE Button
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
                transition: transform 0.2s;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            '>
                💬 LINE<br>友だち追加
            </div>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

def show_staff_management_page():
    """スタッフ管理ページ"""
    st.markdown("### ⚙️ スタッフ管理")
    
    # PIN認証
    pin = st.text_input("PINコード", type="password")
    
    if pin == "0418":
        st.success("✅ 認証成功")
        
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

# メインアプリケーション
def main():
    # ターミナルデバッグ出力
    print(f"\n{'='*60}")
    print(f"🔍 DEBUG: Current Page = {st.session_state.current_page}")
    if 'game_state' in st.session_state:
        game_state = st.session_state.game_state
        print(f"🔍 DEBUG: Current Position = {game_state.get('current_position', 0)}")
        print(f"🔍 DEBUG: Tooth Coins = {game_state.get('tooth_coins', 10)}")
        print(f"🔍 DEBUG: Teeth Count = {game_state.get('teeth_count', 20)}")
    print(f"🔍 DEBUG: Game Board Stage = {st.session_state.get('game_board_stage', 'N/A')}")
    print(f"🔍 DEBUG: Job Roulette State = {st.session_state.get('job_roulette_state', 'N/A')}")
    print(f"{'='*60}\n")
    
    # スタッフモード確認
    staff_mode = staff_access_enabled()

    if st.session_state.current_page != 'reception':
        caries_intro = (
            st.session_state.current_page == 'caries_quiz'
            and st.session_state.get('caries_quiz_stage', 'intro') == 'intro'
        )

        # 歯のUI表示（一番上）- game_board以外は常に最初に表示
        if st.session_state.current_page != 'game_board':
            hide_status_pages = {'caries_quiz', 'perio_quiz', 'job_experience'}
            if not caries_intro and st.session_state.current_page not in hide_status_pages:
                show_status_header()

        # プログレスバー表示
        hide_progress_pages = {'game_board', 'checkup', 'perio_quiz', 'caries_quiz', 'goal', 'line_coloring', 'job_experience'}
        if st.session_state.current_page not in hide_progress_pages and not caries_intro:
            show_progress_bar()
    
    # 現在のページに応じてコンテンツを表示
    if st.session_state.current_page == 'reception':
        show_reception_page()
    elif st.session_state.current_page == 'game_board':
        # game_boardの場合は最初に歯のUIを表示
        show_status_header()
        show_game_board_page()
    elif st.session_state.current_page == 'caries_quiz':
        show_caries_quiz_page()
    elif st.session_state.current_page == 'checkup':
        show_checkup_page()
    elif st.session_state.current_page == 'perio_quiz':
        show_perio_quiz_page()
    elif st.session_state.current_page == 'goal':
        show_goal_page()
    elif st.session_state.current_page == 'line_coloring':
        show_line_coloring_page()
    elif st.session_state.current_page == 'staff_management':
        if staff_mode:
            show_staff_management_page()
        else:
            st.warning("このページはスタッフ専用だよ。")
            navigate_to('reception')
    else:
        st.error("ページが見つかりません")
        navigate_to('reception')

    # 現在ページ情報を body に反映（スタイル切り替え用）
    components.html(
        f"""
        <script>
        const body = window.parent.document.body;
        if (body) {{
            body.setAttribute('data-current-page', '{st.session_state.current_page}');
        }}
        </script>
        """,
        height=0,
        width=0
    )
    
    # スタッフ管理へのリンク（画面下部）
    if st.session_state.current_page == 'reception' and staff_mode:
        staff_cols = st.columns([0.5, 0.5])
        with staff_cols[1]:
            if st.button("⚙️ スタッフ管理", width='stretch'):
                navigate_to('staff_management')

if __name__ == "__main__":
    main()