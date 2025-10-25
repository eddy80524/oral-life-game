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
from datetime import datetime

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services import teeth as teeth_service  # noqa: E402
from services.video_helper import display_video, ensure_video_directories  # noqa: E402

ensure_video_directories()

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
    
    /* ヘッダーバッジ */
    .status-badge {
        background-color: #FEFCF7;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    .teeth-count {
        background-color: #FFF5E6;
        color: #d2691e;
    }
    
    .tooth-coins {
        background-color: #F0FFF0;
        color: #228b22;
    }
    
    /* カード風デザイン */
    .game-card {
        background-color: #FEFCF7;
        border: 2px solid #E8DCC0;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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
    
    /* 進行バー */
    .progress-container {
        background-color: #e0e0e0;
        border-radius: 15px;
        height: 35px;
        margin: 15px 0;
        overflow: hidden;
        border: 2px solid #ddd;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        height: 100%;
        transition: width: 0.8s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        min-width: 120px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* モバイル対応 */
    @media (max-width: 768px) {
        .progress-container {
            height: 40px;
            margin: 10px 0;
        }
        
        .progress-fill {
            font-size: 0.8rem;
            min-width: 100px;
        }
    }
    
    /* タイトル */
    .main-title {
        text-align: center;
        color: #4CAF50;
        margin-bottom: 20px;
    }
    
    /* シンプルな歯の表示 */
    .simple-teeth-container {
        background: linear-gradient(135deg, #FFF8EC, #FFEBD4);
        border: 3px solid #D6C5A5;
        border-radius: 24px;
        padding: 18px 20px 16px;
        margin: 12px 0;
        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
        position: relative;
    }
    .simple-teeth-container::after {
        content: "";
        position: absolute;
        top: 16px;
        bottom: 40px;
        left: 50%;
        transform: translateX(-50%);
        width: 3px;
        background: linear-gradient(180deg, transparent 0%, #bca88e 15%, #8f775e 50%, #bca88e 85%, transparent 100%);
        border-radius: 999px;
        opacity: 0.9;
    }
    .simple-teeth-row {
        display: flex;
        justify-content: center;
        gap: 5px;
        margin: 8px 0;
    }
    .simple-tooth-block,
    .simple-tooth-block-labeled {
        width: 38px;
        height: 44px;
        border-radius: 12px;
        border: 2px solid #d9cfc1;
        background: #f6f1e8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        color: #6b5135;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        position: relative;
    }
    .simple-tooth-block.is-filled,
    .simple-tooth-block-labeled.is-filled {
        background: linear-gradient(180deg, #ffffff, #f3ede2);
    }
    .simple-tooth-block.is-missing,
    .simple-tooth-block-labeled.is-missing {
        background: linear-gradient(180deg, #fde7e7, #f8d8d8);
        border-style: dashed;
        color: #a56464;
        opacity: 0.75;
    }
    .simple-tooth-block-labeled::after {
        content: attr(data-label);
        position: absolute;
        bottom: -1.6rem;
        left: 50%;
        transform: translate(-50%, 4px);
        background: rgba(123, 85, 46, 0.92);
        color: #fff;
        font-size: 0.68rem;
        padding: 3px 7px;
        border-radius: 10px;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.15s ease, transform 0.15s ease;
        box-shadow: 0 3px 6px rgba(0,0,0,0.16);
    }
    .simple-tooth-block-labeled:hover::after {
        opacity: 1;
        transform: translate(-50%, 0);
    }
    .teeth-midline {
        height: 2px;
        width: 86%;
        margin: 0 auto;
        background: linear-gradient(90deg, transparent 0%, #bca88e 10%, #8f775e 50%, #bca88e 90%, transparent 100%);
        border-radius: 999px;
    }
    .simple-teeth-label {
        text-align: center;
        font-weight: bold;
        color: #7a4e27;
        margin-top: 6px;
    }
    .teeth-count-label {
        text-align: center;
        font-size: 1.15em;
        font-weight: bold;
        color: #8B4513;
        margin-top: 12px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .coin-visual-container {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border: 3px solid #FF8C00;
        border-radius: 20px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .coin-stack {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 8px;
        margin: 10px 0;
    }
    
    .coin {
        width: 40px;
        height: 40px;
        background: radial-gradient(circle at 30% 30%, #FFD700, #FFA500);
        border: 3px solid #B8860B;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #8B4513;
        font-size: 1.2em;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        animation: coinShine 2s infinite;
    }
    
    @keyframes coinShine {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); box-shadow: 0 6px 12px rgba(255, 215, 0, 0.5); }
    }
    
    .coin-count-label {
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
        color: #8B4513;
        margin-top: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
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
    
    @media (max-width: 768px) {
        .tooth {
            width: 24px;
            height: 30px;
        }
        .coin {
            width: 35px;
            height: 35px;
            font-size: 1em;
        }
    }
</style>
""", unsafe_allow_html=True)

# ページ管理用の状態初期化
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'reception'

# ページ進行状況の定義
PAGE_FLOW = {
    'reception': {'title': '📋 受付・プロローグ', 'next': 'game_board'},
    'game_board': {'title': '🎲 ゲームボード', 'next': 'caries_quiz'},
    'caries_quiz': {'title': '🦷 むし歯クイズ', 'next': 'game_board'},
    'job_experience': {'title': '👩‍⚕️ 職業体験', 'next': 'checkup'},
    'checkup': {'title': '🏥 定期健診', 'next': 'game_board'},
    'perio_quiz': {'title': '🦷 歯周病クイズ', 'next': 'goal'},
    'goal': {'title': '🏁 ゴール・ランキング', 'next': 'line_coloring'},
    'line_coloring': {'title': '📱 LINE', 'next': 'reception'},
    'staff_management': {'title': '⚙️ スタッフ管理', 'next': 'reception'}
}


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



def show_coin_change(old_coins, new_coins, reason=""):
    """トゥースコインの増減を視覚的に表示"""
    change = new_coins - old_coins
    
    if change > 0:
        # コイン増加
        st.markdown(f"""
        <div style='text-align: center; background: linear-gradient(135deg, #FFD700, #FFA500); 
                    padding: 20px; border-radius: 15px; border: 3px solid #FF8C00; 
                    margin: 20px 0; box-shadow: 0 6px 12px rgba(0,0,0,0.2);'>
            <h2 style='color: #B8860B; margin: 5px 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>
                🪙 トゥースコイン ゲット！ 🪙
            </h2>
            <div style='font-size: 2.5em; margin: 10px 0;'>
                <span style='color: #8B4513; font-weight: bold;'>{old_coins}</span>
                <span style='color: #228B22; font-size: 1.2em; margin: 0 10px;'>+{change}</span>
                <span style='color: #8B4513; font-weight: bold;'>→ {new_coins}</span>
            </div>
            <p style='color: #8B4513; font-size: 1.2em; margin: 5px 0; font-weight: bold;'>
                {reason}
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    elif change < 0:
        # コイン減少
        st.markdown(f"""
        <div style='text-align: center; background: linear-gradient(135deg, #FFB6C1, #FFA0B4); 
                    padding: 20px; border-radius: 15px; border: 3px solid #DC143C; 
                    margin: 20px 0; box-shadow: 0 6px 12px rgba(0,0,0,0.2);'>
            <h2 style='color: #8B0000; margin: 5px 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>
                💸 トゥースコイン へっちゃった... 💸
            </h2>
            <div style='font-size: 2.5em; margin: 10px 0;'>
                <span style='color: #8B4513; font-weight: bold;'>{old_coins}</span>
                <span style='color: #DC143C; font-size: 1.2em; margin: 0 10px;'>{change}</span>
                <span style='color: #8B4513; font-weight: bold;'>→ {new_coins}</span>
            </div>
            <p style='color: #8B0000; font-size: 1.2em; margin: 5px 0; font-weight: bold;'>
                {reason}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 変化なし
        st.info(f"🪙 トゥースコイン: {new_coins}まい (変化なし)")


def apply_tooth_effects(game_state, landing_cell, feedback):
    """ボードイベントに応じた歯の状態変化を適用"""
    teeth_service.ensure_tooth_state(game_state)
    tooth_messages = feedback.setdefault('tooth_messages', [])
    title = landing_cell.get('title', '')
    action = landing_cell.get('action')
    effect_applied = False

    if title == "虫歯クイズ":
        if teeth_service.upgrade_to_adult(game_state):
            teeth_service.sync_teeth_count(game_state)
            game_state['teeth_count'] = 28
            game_state['teeth_max'] = 28
            st.session_state.teeth_count = 28
            tooth_messages.append(('success', '✨ 大人の歯が ぜんぶ生えそろったよ！28本になったね。'))
            effect_applied = True
    if title == "初めて乳歯が抜けた":
        lost = teeth_service.lose_primary_tooth(game_state, count=1)
        if lost:
            tooth_messages.append(('info', '👶 乳歯が1本ぬけたよ。大人の歯がはえてくるまでまっていよう！'))
            effect_applied = True
    if title == "虫歯ができた":
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
            tooth_messages.append(('warning', '⚠️ 虫歯ができちゃった…定期検診でなおそう！'))
            effect_applied = True
    if title == "ジュースをおねだり":
        stained = teeth_service.stain_teeth(game_state, count=3)
        if stained:
            tooth_messages.append(('warning', '🥤 ジュースばかりで歯がすこし黄ばんできたよ。'))
            effect_applied = True
    if title == "バイクで大事故":
        lost = teeth_service.lose_specific_teeth(game_state, ["UL1", "UR1"], permanent=True)
        if lost:
            tooth_messages.append(('error', '💥 まえ歯が2本おれてしまった…きをつけよう！'))
            effect_applied = True
    if title == "茶渋除去":
        cleaned = teeth_service.whiten_teeth(game_state)
        if cleaned:
            tooth_messages.append(('success', '✨ 茶渋をきれいにして歯がピカピカになったよ！'))
            effect_applied = True
    if title == "入れ歯作成":
        added = teeth_service.add_prosthetics(game_state, count=2)
        if added:
            tooth_messages.append(('info', '🦷 入れ歯でなくなった歯がもどったよ。'))
            effect_applied = True
    if landing_cell.get('type') == 'stop':
        repaired = teeth_service.repair_damaged_teeth(game_state)
        cleaned = teeth_service.whiten_teeth(game_state)
        if repaired or cleaned:
            tooth_messages.append(('success', '🪥 定期検診で歯がきれいになったよ！'))
            effect_applied = True
    if action == 'floss_check':
        repaired = teeth_service.repair_damaged_teeth(game_state)
        if repaired:
            tooth_messages.append(('success', '🧵 フロスで歯が元気になったよ！'))
            effect_applied = True
    if action == 'smile_together':
        cleaned = teeth_service.whiten_teeth(game_state)
        if cleaned:
            tooth_messages.append(('success', '😁 きれいな歯茎でにっこり笑顔！'))
            effect_applied = True
    if action == 'dice_tooth_loss':
        from services.game_logic import lose_teeth_and_pay  # 遅延インポートで循環対策
        outcome = lose_teeth_and_pay()
        payment = outcome.get('payment', 0)
        if payment:
            feedback['coin_messages'].append(('warning', f"💸 治療費として {payment} トゥースしはらったよ。"))
        lost_ids = outcome.get('lost_tooth_ids', [])
        dice_roll = outcome.get('dice_roll', 0)
        teeth_lost = outcome.get('teeth_lost', 0)
        tooth_messages.append(('warning', f"🎲 サイコロは {dice_roll}！ はを {teeth_lost}本 うしなってしまったよ。"))
        if lost_ids:
            tooth_messages.append(('error', f"😢 歯を{len(lost_ids)}本 なくしてしまった…"))
        feedback['landing_message'] = "🦷 歯をたいせつにしよう！"
        feedback['landing_tone'] = 'warning'
        feedback['next_page'] = 'refresh'
        feedback['next_button_label'] = "ボードにもどる"
        effect_applied = True

    teeth_service.sync_teeth_count(game_state)
    st.session_state.teeth_count = game_state.get('teeth_count', st.session_state.get('teeth_count', 0))
    return effect_applied

def navigate_to(page_name):
    """ページ遷移"""
    st.session_state.current_page = page_name
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
    
    # 子供向けの進捗メッセージ
    if progress_percentage <= 10:
        progress_message = "🌱 スタート"
    elif progress_percentage <= 25:
        progress_message = "🚀 いいね！"
    elif progress_percentage <= 50:
        progress_message = "⭐ はんぶん"
    elif progress_percentage <= 75:
        progress_message = "🎉 がんばれ"
    elif progress_percentage <= 90:
        progress_message = "🏆 あとすこし"
    else:
        progress_message = "🎊 ゴール！"
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-fill" style="width: {max(progress_percentage, 15)}%;">
            <span>{progress_message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_status_header():
    """ゲーム状態のヘッダー表示（ビジュアル版）"""
    if 'game_state' in st.session_state and st.session_state.current_page not in ['reception', 'staff_management', 'checkup', 'perio_quiz', 'caries_quiz']:
        if st.session_state.current_page == 'game_board':
            stage = st.session_state.get('game_board_stage', 'board')
            if stage == 'roulette':
                return
            if stage == 'card':
                current_position = st.session_state.game_state.get('current_position', 0)
                if current_position == 0:
                    return

        game_state = st.session_state.game_state

        col_teeth, col_coin = st.columns([0.6, 0.4])

        with col_teeth:
            current_position = game_state.get('current_position', 0)
            tooth_stage = game_state.get('tooth_stage')
            if tooth_stage in {'child', 'adult'}:
                stage = tooth_stage
            else:
                stage = 'child' if current_position < 6 else 'adult'

            if stage == 'child':
                base_order = ["乳中切歯", "乳側切歯", "乳犬歯", "第一乳臼歯", "第二乳臼歯"]
                short_map = {
                    "乳中切歯": "乳中",
                    "乳側切歯": "乳側",
                    "乳犬歯": "乳犬",
                    "第一乳臼歯": "乳臼1",
                    "第二乳臼歯": "乳臼2",
                }
                total_teeth = 20
            else:
                base_order = ["中切歯", "側切歯", "犬歯", "第一小臼歯", "第二小臼歯", "第一大臼歯", "第二大臼歯"]
                short_map = {
                    "中切歯": "中切",
                    "側切歯": "側切",
                    "犬歯": "犬歯",
                    "第一小臼歯": "小臼1",
                    "第二小臼歯": "小臼2",
                    "第一大臼歯": "大臼1",
                    "第二大臼歯": "大臼2",
                }
                total_teeth = 28

            left_side = base_order[::-1]
            right_side = base_order
            upper_labels = left_side + right_side
            lower_labels = upper_labels
            present_teeth = min(game_state.get('teeth_count', total_teeth), total_teeth)
            if stage == 'adult' and game_state.get('teeth_missing', 0) == 0:
                present_teeth = total_teeth

            def render_row(labels, offset):
                cells = []
                for idx, label in enumerate(labels):
                    short = short_map.get(label, label)
                    filled = (offset + idx) < present_teeth
                    classes = "simple-tooth-block-labeled " + ("is-filled" if filled else "is-missing")
                    cells.append(f"<div class='{classes}' data-label='{short}'></div>")
                return ''.join(cells)

            upper_html = render_row(upper_labels, 0)
            lower_html = render_row(lower_labels, len(upper_labels))

            st.markdown(
                f"""
                <div class="simple-teeth-container">
                    <div class="simple-teeth-row teeth-upper">{upper_html}</div>
                    <div class="teeth-midline"></div>
                    <div class="simple-teeth-row teeth-lower">{lower_html}</div>
                    <div class="simple-teeth-label">🦷 {present_teeth} / {total_teeth} 本</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_coin:
            tooth_coins = game_state.get('tooth_coins', 10)
            st.metric("🏅 トゥースコイン", f"{tooth_coins}枚")

            coins_to_show = min(tooth_coins, 10)
            if coins_to_show > 0:
                icons = ["💰"] * coins_to_show
                while icons:
                    line = " ".join(icons[:5])
                    st.markdown(f"#### {line}")
                    icons = icons[5:]
            else:
                st.caption("まだコインはないよ！")

            extra_coins = tooth_coins - coins_to_show
            if extra_coins > 0:
                st.caption(f"+ {extra_coins}枚")

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
            if st.button("はじめる", key="reception_next_cover", width='stretch', type="primary"):
                st.session_state.reception_step = 1
                st.rerun()

        elif step == 1:
            st.markdown("<h1 class='reception-heading'>おくちのじんせいゲームへようこそ！</h1>", unsafe_allow_html=True)
            render_reception_image("welcome_teeth")
            st.markdown("<p class='reception-text'>みんなには100さいになるまで<br>きれいなおくちですごしてもらうよ！</p>", unsafe_allow_html=True)
            st.caption("※ 音声ガイドは準備中だよ。")
            st.markdown("<div style='height:1vh'></div>", unsafe_allow_html=True)
            if st.button("すすむ", key="reception_next_welcome", width='stretch', type="primary"):
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
            if st.button("すすむ", key="reception_next_name", width='stretch', type="primary"):
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
            if st.button("すすむ", key="reception_next_age", width='stretch', type="primary"):
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

            if st.button("すすむ", key="reception_start_game", width='stretch', type="primary", disabled=not st.session_state.reception_wait_unlocked):
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
    if 'game_state' not in st.session_state:
        from services.game_logic import initialize_game_state
        initialize_game_state()

    st.session_state.setdefault('game_board_stage', 'card')
    stage = st.session_state.game_board_stage

    # game_stateは常にst.session_stateから直接参照
    game_state = st.session_state.game_state
    current_position = game_state.get('current_position', 0)

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
            cell_image_name = f"cell_{position + 1:02d}"
            if not display_image("board", cell_image_name, cell_info.get('title', ''), fill='stretch'):
                action_name = cell_info.get('action')
                action_to_image = {
                    'self_introduction': 'self_introduction',
                    'jump_exercise': 'jump',
                    'tooth_loss': 'tooth_loss',
                    'job_experience': 'job_experience'
                }
                if action_name in action_to_image:
                    display_image("events", action_to_image[action_name], cell_info.get('title', ''), fill='stretch')
        except ImportError:
            pass

    def process_spin_result(result_value: int):
        # 最新の位置を取得
        old_position = st.session_state.game_state.get('current_position', 0)
        new_position = min(old_position + result_value, max_position_index)
        
        # game_stateを直接更新
        st.session_state.game_state['current_position'] = new_position
        st.session_state.game_state['turn_count'] = st.session_state.game_state.get('turn_count', 0) + 1
        st.session_state.game_state['just_moved'] = True

        feedback = {
            'result': result_value,
            'old_position': old_position,
            'new_position': new_position,
            'move_message': f"➡️ {old_position + 1}ばんめ → {new_position + 1}ばんめ にすすんだよ！",
            'coin_messages': [],
            'tooth_messages': [],
            'landing_message': None,
            'landing_tone': None,
            'next_page': None,
            'next_button_label': "つぎのマスをみる"
        }

        if board_data and 0 <= new_position < len(board_data):
            landing_cell = board_data[new_position]
            landing_title = landing_cell.get('title', '')
            landing_type = landing_cell.get('type', 'normal')

            tooth_delta = landing_cell.get('tooth_delta', 0)
            if tooth_delta != 0:
                old_coins = st.session_state.game_state.get('tooth_coins', 10)
                new_coins = max(0, old_coins + tooth_delta)
                st.session_state.game_state['tooth_coins'] = new_coins
                
                tone = 'success' if tooth_delta > 0 else 'warning'
                message = (f"🏅 トゥースコインを {tooth_delta}枚 もらったよ！（合計: {new_coins}枚）" if tooth_delta > 0
                           else f"💔 トゥースコインを {abs(tooth_delta)}枚 うしなった...（残り: {new_coins}枚）")
                feedback['coin_messages'].append((tone, message))

            apply_tooth_effects(st.session_state.game_state, landing_cell, feedback)

            if feedback.get('next_page') is None:
                if landing_type == 'quiz':
                    if '虫歯' in landing_title:
                        feedback['landing_message'] = "🦷 むしばクイズのマスにとうちゃく！"
                        feedback['landing_tone'] = 'success'
                        feedback['next_page'] = 'caries_quiz'
                        feedback['next_button_label'] = "🦷 クイズへすすむ"
                    elif '歯周病' in landing_title:
                        feedback['landing_message'] = "🦷 はぐきのクイズのマスにとうちゃく！"
                        feedback['landing_tone'] = 'success'
                        feedback['next_page'] = 'perio_quiz'
                        feedback['next_button_label'] = "🦷 クイズへすすむ"
                elif landing_type == 'stop' or '検診' in landing_title:
                    feedback['landing_message'] = "🏥 はいしゃさんのマスにとうちゃく！"
                    feedback['landing_tone'] = 'success'
                    feedback['next_page'] = 'checkup'
                    feedback['next_button_label'] = "🏥 けんしんへすすむ"
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
            st.session_state.pop('roulette_feedback', None)
            st.session_state.pop('roulette_last_spin_id', None)
            if current_cell is None:
                st.warning("マスの情報がみつかりませんでした。")
                return

            total_cells = len(board_data)
            if total_cells:
                nodes_html = []
                for idx in range(total_cells):
                    classes = ["board-progress-node"]
                    if idx == current_position:
                        classes.append("is-current")
                    elif idx < current_position:
                        classes.append("is-visited")
                    nodes_html.append(f"<div class='{' '.join(classes)}'>{idx + 1}</div>")
                st.markdown(
                    f"<div class='board-progress-track'>{''.join(nodes_html)}</div>",
                    unsafe_allow_html=True,
                )

            render_cell_media(current_position, current_cell)

            cell_type = current_cell.get('type', 'normal')
            title = current_cell.get('title', '')
            action_taken = False

            event_effect_messages = {
                'ジャンプができるようになった': "ジャンプでからだをうごかして げんきいっぱい！",
                '初めて乳歯が抜けた': "ぬけた歯のおはなしをして たいせつにしよう。",
            }

            if cell_type == 'quiz':
                quiz_type = current_cell.get('quiz_type', '')
                if quiz_type == 'caries':
                    if st.button("🦷 むしばクイズにちょうせん！", width='stretch', type="primary"):
                        navigate_to('caries_quiz')
                        action_taken = True
                elif quiz_type == 'periodontitis':
                    if st.button("🦷 はぐきのクイズにちょうせん！", width='stretch', type="primary"):
                        navigate_to('perio_quiz')
                        action_taken = True
            elif cell_type == 'stop' or '検診' in title:
                if st.button("🏥 はいしゃさんにいく", width='stretch', type="primary"):
                    navigate_to('checkup')
                    action_taken = True
            elif '職業' in title:
                if st.session_state.participant_age >= 5:
                    if st.button("👩‍⚕️ おしごとたいけんをする", width='stretch', type="primary"):
                        navigate_to('job_experience')
                        action_taken = True
                else:
                    st.info("おしごとたいけんは5さい以上だよ。")
            elif cell_type == 'goal' or current_position == max_position_index:
                st.success("🎉 ゴールにとうちゃく！")
                if st.button("▶️ ゴールへ", width='stretch', type="primary"):
                    navigate_to('goal')
                action_taken = True

            elif cell_type == 'event':
                event_button_text = {
                    '初めて言葉を話せるようになった': '🗣️ じこしょうかいをする',
                    'ジャンプができるようになった': '🤸 ジャンプをする',
                    '初めて乳歯が抜けた': '🦷 はのおはなしをする'
                }
                extra_caption = event_effect_messages.get(title)
                if extra_caption:
                    st.caption(extra_caption)
                if title in event_button_text:
                    if st.button(event_button_text[title], width='stretch', type='secondary', key=f'event_action_{current_position}'):
                        st.success('たのしい たいけんでした！ トゥースコインはそのままだよ。')
                        st.balloons()

            can_spin = (not action_taken and cell_type not in {'quiz', 'stop'}
                        and '検診' not in title and '職業' not in title
                        and current_position < max_position_index)

            if can_spin:
                allowed_numbers, _, _ = compute_allowed_numbers(current_position)
                if not allowed_numbers:
                    st.info("今回はすすむマスがないよ。")
                else:
                    st.markdown("<div style='height:1.5vh'></div>", unsafe_allow_html=True)
                    if st.button("🎡 ルーレットをまわす", key="board_to_roulette", width='stretch', type="primary"):
                        st.session_state.pending_spin_allowed = allowed_numbers
                        st.session_state.pop('roulette_spin_state', None)
                        st.session_state.game_board_stage = 'roulette'
                        st.session_state.pop('roulette_recent_feedback', None)
                        st.rerun()
            elif not action_taken and current_position >= max_position_index:
                if st.button("🏁 ゴールへ", width='stretch', type="primary"):
                    navigate_to('goal')

        elif stage == 'roulette':
            if current_position >= max_position_index or (current_cell and current_cell.get('type') == 'goal'):
                st.success("🎉 ゴールにとうちゃく！")
                if st.button("▶️ ゴールへ", width='stretch', type="primary"):
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
                    for _ in range(3):
                        animation_sequence.extend(base_sequence)
                    animation_sequence.extend(pool)
                    for value in animation_sequence:
                        card_placeholder.markdown(
                            render_card(value, subtitle="ルーレット くるくる…", message="どの数字になるかな？"),
                            unsafe_allow_html=True,
                        )
                        time.sleep(0.07)
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
    """むしばクイズページ"""
    from services.image_helper import display_image

    stage = st.session_state.get('caries_quiz_stage', 'intro')
    answers = st.session_state.setdefault('caries_quiz_answers', [None, None])

    if stage == 'intro':
        st.markdown("### 🦷 むしばクイズ")
        st.caption("カードを読んだら、ボタンを押してクイズにすすもう！")
        try:
            display_image("board", "cell_06", "むしばクイズのカード")
        except ImportError:
            st.markdown("カードを確認したかな？むしばについてのクイズに備えてね。")
        if st.button("🦷 クイズへすすむ", type="primary", use_container_width=True):
            st.session_state.caries_quiz_stage = 'question_0'
            st.session_state.caries_quiz_answers = [None, None]
            st.session_state.pop('caries_q1_selected', None)
            st.session_state.pop('caries_q2_selected', None)
            st.session_state.pop('caries_q1_checked', None)
            st.session_state.pop('caries_q2_checked', None)
            st.rerun()
        return

    if stage.startswith('question_'):
        try:
            question_index = int(stage.split('_')[1])
        except (IndexError, ValueError):
            question_index = 0

        st.markdown("### 🦷 むしばクイズにちょうせん！")

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

        if question_index == 0:
            if 'caries_q1_selected' not in st.session_state:
                st.session_state.caries_q1_selected = None
            st.markdown("---")
            st.markdown("**もんだい1: からだのなかで いちばんかたいものは？**")
            try:
                display_image("quiz/caries", "question_1", "問題1の画像")
            except ImportError:
                pass

            question1_options = ["あたま", "せなか", "は"]
            selected_idx = render_option_buttons(question1_options, answers[0], "caries_q1")
            answers[0] = selected_idx

            st.markdown("---")
            submit_q1 = st.button(
                "📝 こたえをかくにん",
                key="caries_submit_q1",
                type="primary",
                use_container_width=True,
            )

            if submit_q1:
                if answers[0] is None:
                    st.warning("こたえをえらんでね！")
                else:
                    if answers[0] == 2:
                        st.success("せいかい！『は』はエナメルしつで からだのなかで いちばんかたいんだよ。")
                    else:
                        st.warning("ざんねん… いちばんかたいのは『は』だよ。エナメルしつが つよいんだ。")
                        st.info("✅ せいかいは『は』だよ。")
                    st.session_state.caries_q1_checked = True

            if st.session_state.get('caries_q1_checked'):
                if st.button(
                    "▶️ つぎのもんだいへ",
                    key="caries_next_q1",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state.pop('caries_q1_checked', None)
                    st.session_state.caries_quiz_stage = 'question_1'
                    st.rerun()
            else:
                st.caption("こたえをかくにんしてから つぎへすすもう！")
            return

        if question_index == 1:
            if 'caries_q2_selected' not in st.session_state:
                st.session_state.caries_q2_selected = None
            st.markdown("**もんだい2: むしばになりやすい くみあわせは？**")
            try:
                display_image("quiz/caries", "question_2", "問題2の画像")
            except ImportError:
                pass

            if answers[1] is None:
                answers[1] = st.session_state.get('caries_q2_selected')

            combo_meta = [
                ("choco_banana", "コーラ", "cola", "チョコバナナ + コーラ"),
                ("cheese", "おちゃ", "tea", "チーズ + おちゃ"),
                ("bread", "ミルク", "milk", "パン + ミルク"),
            ]

            st.markdown("**えらんでね：**")
            try:
                option_cols = st.columns(len(combo_meta))
                for idx, (food_key, drink_label, drink_key, display_label) in enumerate(combo_meta):
                    with option_cols[idx]:
                        st.markdown(f"**{display_label}**")
                        food_col, drink_col = st.columns(2)
                        with food_col:
                            display_image("quiz/caries/food", food_key, display_label.split(" + ")[0])
                        with drink_col:
                            display_image("quiz/caries/drink", drink_key, drink_label)
                        button_type = "primary" if answers[1] == idx else "secondary"
                        if st.button(
                            "このくみあわせにする",
                            key=f"caries_q2_btn_{idx}",
                            use_container_width=True,
                            type=button_type,
                        ):
                            answers[1] = idx
                            st.session_state['caries_q2_selected'] = idx
                            st.rerun()
            except ImportError:
                st.warning("画像を表示できませんでした。")

            submit_q2 = st.button(
                "📝 こたえをかくにん",
                key="caries_submit_q2",
                type="primary",
                use_container_width=True,
            )

            if submit_q2:
                if answers[1] is None:
                    st.warning("こたえをえらんでね！")
                else:
                    if answers[1] == 0:
                        st.success("せいかい！ あまいおやつと あまいのみもののくみあわせは むしばのきけんがたかいよ。")
                    else:
                        st.warning("ざんねん… むしばになりやすいのは『チョコバナナ + コーラ』だよ。")
                        st.info("✅ せいかいは『チョコバナナ + コーラ』だよ。")
                    st.session_state.caries_q2_checked = True

            finalize_pressed = False
            if st.session_state.get('caries_q2_checked'):
                finalize_pressed = st.button(
                    "▶️ つぎへ",
                    key="caries_finalize_q2",
                    type="secondary",
                    use_container_width=True,
                )
            else:
                st.caption("こたえをかくにんしてから けっていしよう！")

            if finalize_pressed:
                st.session_state.pop('caries_q2_checked', None)
                correct_answers = [2, 0]
                correct_count = sum(
                    1
                    for i, correct_answer in enumerate(correct_answers)
                    if i < len(answers) and answers[i] == correct_answer
                )

                st.success(f"せいかいかず: {correct_count}/2")

                try:
                    if correct_count >= 1:
                        st.markdown("### 🌟 むしばになりやすい くみあわせを みつけられたね！")
                        st.warning("これは むしばになりやすいので きをつけよう！")
                        col1, col2 = st.columns(2)
                        with col1:
                            display_image("quiz/caries/food", "choco_banana", "チョコバナナ（むしばになりやすい）")
                        with col2:
                            display_image("quiz/caries/drink", "cola", "コーラ（むしばになりやすい）")
                    else:
                        st.markdown("### 💧 これは むしばになりにくいよ")
                        st.info("おやつやのみものの えらびかたを かんがえてみよう！")
                        col1, col2 = st.columns(2)
                        with col1:
                            display_image("quiz/caries/food", "cheese", "チーズ（むしばになりにくい）")
                        with col2:
                            display_image("quiz/caries/drink", "tea", "おちゃ（むしばになりにくい）")
                except ImportError:
                    pass

                selected_combo_idx = answers[1]
                if selected_combo_idx == 0:
                    st.success("✅ チョコバナナとコーラは むしばになりやすい くみあわせだよ。きをつけようね！")
                else:
                    st.warning("❌ えらんだ くみあわせは そこまで むしばになりやすくないよ。")

                if answers[0] == correct_answers[0]:
                    st.success("もんだい1せいかい！「は」はエナメルしつで からだのなかで いちばんかたいんだよ。")
                else:
                    st.warning("もんだい1は ざんねん… いちばんかたいのは「は」だよ。エナメルしつが つよいんだ。")

                if answers[1] == correct_answers[1]:
                    st.info("もんだい2せいかい！あまいチョコバナナと あまいのみもののくみあわせは むしばになりやすいから きをつけよう。")
                else:
                    st.info("もんだい2は もうすこし！ あまいものと あまいのみものを あわせると むしばのきけんが ふえるよ。")

                if 'game_state' in st.session_state:
                    game_state = st.session_state.game_state
                    old_coins = game_state.get('tooth_coins', 0)

                    if correct_count >= 1:
                        game_state['tooth_coins'] += 5
                        show_coin_change(old_coins, game_state['tooth_coins'], "むしばクイズ せいかい！ きをつけられたね")
                        st.success("🌟 よくできました！ けんこうルートに すすみます！")
                        game_state['current_position'] = 10
                    else:
                        game_state['tooth_coins'] = max(0, game_state['tooth_coins'] - 3)
                        show_coin_change(old_coins, game_state['tooth_coins'], "むしばクイズ ふせいかい... きをつけよう")
                        st.warning("💧 もうすこし きをつけましょう。べつのルートに すすみます。")
                        game_state['current_position'] = 7

                st.info("つづきは ゲームボードで！")
                st.session_state.caries_quiz_stage = 'intro'
                st.session_state.pop('caries_quiz_answers', None)
                st.session_state.pop('caries_q1_selected', None)
                st.session_state.pop('caries_q2_selected', None)
                navigate_to('game_board')
            return

def show_job_experience_page():
    """おしごとたいけんページ"""
    st.markdown("### 👩‍⚕️ おしごとたいけん")
    
    jobs = ["はいしゃさん", "はのおそうじのせんせい", "はをつくるせんせい"]
    
    if 'selected_job' not in st.session_state:
        st.session_state.selected_job = None
    
    if st.session_state.selected_job is None:
        st.markdown("くじをひいて おしごとをきめよう！")
        
        if st.button("🎯 くじをひく", width='stretch', type="primary"):
            import random
            job_index = random.randint(0, 2)
            st.session_state.selected_job = jobs[job_index]
            st.success(f"🎉 {st.session_state.selected_job}にきまったよ！")
            st.rerun()
    else:
        st.info(f"たいけんするおしごと: {st.session_state.selected_job}")
        st.markdown("1ぷんかん たいけんをします...")
        
        if st.button("✅ たいけんかんりょう", width='stretch', type="primary"):
            # 体験完了報酬
            if 'game_state' in st.session_state:
                game_state = st.session_state.game_state
                old_coins = game_state.get('tooth_coins', 0)
                game_state['tooth_coins'] += 5
                
                # コイン増加を表示
                show_coin_change(old_coins, game_state['tooth_coins'], "おしごとたいけん ありがとう！")
            
            st.session_state.selected_job = None  # リセット
            navigate_to('checkup')

def show_checkup_page():
    """ていきけんしんページ"""
    try:
        from services.image_helper import display_image
        display_image("board", "cell_05", caption=None, fill='stretch')
    except ImportError:
        pass
    
    if st.button("🏥 けんしんをうける", width='stretch', type="primary"):
        # 健診報酬
        if 'game_state' in st.session_state:
            game_state = st.session_state.game_state
            old_coins = game_state.get('tooth_coins', 0)
            game_state['tooth_coins'] += 3
            current_position = game_state.get('current_position', 0)
            
            # コイン増加を表示
            show_coin_change(old_coins, game_state['tooth_coins'], "ていきけんしん ありがとう！")
            
            # ボードデータから現在のセルの次のアクションを取得
            try:
                import json
                age_group = "under5" if st.session_state.participant_age < 5 else "5plus"
                board_file = f"data/board_main_{age_group}.json"
                
                with open(board_file, 'r', encoding='utf-8') as f:
                    board_data = json.load(f)
                
                current_cell = None
                for cell in board_data:
                    if cell['cell'] == current_position:
                        current_cell = cell
                        break
                
                if current_cell and current_cell.get('next_action'):
                    next_action = current_cell['next_action']
                    if next_action == 'caries_quiz':
                        st.success("けんしん かんりょう！")
                        st.info("つぎは むしばクイズに ちょうせんしよう！")
                        navigate_to('caries_quiz')
                    elif next_action == 'periodontitis_quiz':
                        st.success("けんしん かんりょう！")
                        st.info("つぎは はぐきクイズに ちょうせんしよう！")
                        navigate_to('perio_quiz')
                    else:
                        st.success("けんしん かんりょう！")
                        st.info("つづきは ゲームボードで！")
                        navigate_to('game_board')
                else:
                    # 位置15の場合は歯茎クイズに進む
                    if current_position == 15:
                        st.success("けんしん かんりょう！")
                        st.info("つぎは はぐきクイズに ちょうせんしよう！")
                        navigate_to('perio_quiz')
                    else:
                        st.success("けんしん かんりょう！")
                        st.info("つづきは ゲームボードで！")
                        navigate_to('game_board')
                    
            except (FileNotFoundError, json.JSONDecodeError):
                st.success("🎉 +3コインゲット！")
                st.success("けんしん かんりょう！")
                st.info("つづきは ゲームボードで！")
                navigate_to('game_board')
        else:
            st.success("けんしん かんりょう！")
            navigate_to('game_board')

def show_perio_quiz_page():
    """はぐきクイズページ"""
    questions = [
        {"q": "はみがきしないと どこから ちがでる？", "options": ["は", "はぐき", "した"], "correct": 1},
        {"q": "はの ねっこの ところは どうなってる？", "options": ["①", "②", "③"], "correct": 2}
    ]

    stage = st.session_state.get('perio_quiz_stage', 'intro')
    if stage == 'questions':
        stage = 'question_0'
        st.session_state.perio_quiz_stage = stage

    if stage == 'intro':
        st.markdown("### 🦷 はぐきクイズ")
        st.caption("カードをよんだら、ボタンをおしてクイズにすすもう！")
        try:
            from services.image_helper import display_image
            display_image("quiz/periodontitis", "main_image", "はぐきクイズのカード")
        except ImportError:
            st.info("カードをよんで はぐきクイズのじゅんびをしよう。")
        if st.button("🦷 クイズへすすむ", type="primary", use_container_width=True):
            st.session_state.perio_quiz_stage = 'question_0'
            st.session_state.perio_quiz_answers = [None] * len(questions)
            st.session_state.pop('perio_q1_selected', None)
            st.session_state.pop('perio_q2_selected', None)
            st.session_state.pop('perio_q1_checked', None)
            st.session_state.pop('perio_q2_checked', None)
            st.rerun()
        return

    st.markdown("### 🦷 はぐきクイズ")
    
    answers = st.session_state.setdefault('perio_quiz_answers', [None] * len(questions))

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

    if stage.startswith('question_'):
        try:
            question_index = int(stage.split('_')[1])
        except (IndexError, ValueError):
            question_index = 0

        st.caption(f"もんだい {question_index + 1} / {len(questions)}")
        st.markdown("---")

        if question_index == 0:
            if 'perio_q1_selected' not in st.session_state:
                st.session_state.perio_q1_selected = None
            st.markdown("**問題1: はぐきの状態を比べてみよう**")
            try:
                from services.image_helper import display_image
                col1, col2 = st.columns(2)
                with col1:
                    display_image("quiz/periodontitis", "question_1a", "問題")
                with col2:
                    display_image("quiz/periodontitis", "question_1b", "はぐきの状態")
            except ImportError:
                pass

            st.markdown(f"**もんだい1: {questions[0]['q']}**")
            answers[0] = render_option_buttons(questions[0]['options'], answers[0], "perio_q1")

            st.markdown("---")
            submit_q1 = st.button(
                "📝 こたえをかくにん",
                key="perio_submit_q1",
                type="primary",
                use_container_width=True,
            )

            if submit_q1:
                if answers[0] is None:
                    st.warning("こたえをえらんでね！")
                else:
                    if answers[0] == questions[0]['correct']:
                        st.success("せいかい！ はみがきしないと はぐきから ちがでることが あるんだよ。")
                    else:
                        st.warning("ざんねん… はぐきから ちがでてしまうことがあるから ていねいにはみがきしようね。")
                        st.info("✅ せいかいは『はぐき』だよ。")
                    st.session_state.perio_q1_checked = True

            if st.session_state.get('perio_q1_checked'):
                if st.button(
                    "▶️ つぎのもんだいへ",
                    key="perio_next_q1",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state.pop('perio_q1_checked', None)
                    st.session_state.perio_quiz_stage = 'question_1'
                    st.rerun()
            else:
                st.caption("こたえをかくにんしてから つぎへすすもう！")
            return

        if question_index == 1:
            if 'perio_q2_selected' not in st.session_state:
                st.session_state.perio_q2_selected = None
            st.markdown("**問題2: もう一つの比較問題**")
            try:
                from services.image_helper import display_image
                col3, col4 = st.columns(2)
                with col3:
                    display_image("quiz/periodontitis", "question_2a", "はぐきの状態C")
                with col4:
                    display_image("quiz/periodontitis", "question_2b", "はぐきの状態D")
            except ImportError:
                pass

            st.markdown(f"**もんだい2: {questions[1]['q']}**")
            answers[1] = render_option_buttons(questions[1]['options'], answers[1], "perio_q2")

            st.markdown("---")
            submit_q2 = st.button(
                "📝 こたえをかくにん",
                key="perio_submit_q2",
                type="primary",
                use_container_width=True,
            )

            if submit_q2:
                if answers[1] is None:
                    st.warning("こたえをえらんでね！")
                else:
                    if answers[1] == questions[1]['correct']:
                        st.success("せいかい！ はのねもとは ほねと はぐきで しっかり ささえられているよ。")
                    else:
                        st.warning("ざんねん… はのねもとは ほねと はぐきで ささえられているんだ。")
                        st.info("✅ せいかいは『③』だよ。")
                    st.session_state.perio_q2_checked = True

            finalize_perio = False
            if st.session_state.get('perio_q2_checked'):
                finalize_perio = st.button(
                    "▶️ つぎへ",
                    key="perio_finalize_q2",
                    type="secondary",
                    use_container_width=True,
                )
            else:
                st.caption("こたえをかくにんしてから けっていしよう！")

            if finalize_perio:
                st.session_state.pop('perio_q2_checked', None)
                if answers[1] is None:
                    st.warning("こたえをえらんでね！")
                    return

                correct_count = sum(
                    1
                    for i, q in enumerate(questions)
                    if i < len(answers) and answers[i] == q['correct']
                )

                st.success(f"せいかいかず: {correct_count}/{len(questions)}")

                if answers[0] == questions[0]['correct']:
                    st.success("もんだい1せいかい！ はみがきしないと はぐきから ちがでることが あるんだよ。")
                else:
                    st.warning("もんだい1は ざんねん… はぐきから ちがでてしまうことがあるから ていねいにはみがきしようね。")

                if answers[1] == questions[1]['correct']:
                    st.info("もんだい2せいかい！ はのねもとは しっかり はぐきや ほねで ささえられているよ。")
                else:
                    st.info("もんだい2は もうすこし！ はのねもとは ほねと はぐきで ささえられているんだ。")

                if 'game_state' in st.session_state:
                    game_state = st.session_state.game_state
                    old_coins = game_state['tooth_coins']

                    if correct_count >= 1:
                        game_state['tooth_coins'] += 5
                        show_coin_change(old_coins, game_state['tooth_coins'], "🌟 よくできました！")
                        st.balloons()
                    else:
                        game_state['tooth_coins'] = max(0, game_state['tooth_coins'] - 3)
                        show_coin_change(old_coins, game_state['tooth_coins'], "💧 もうすこし べんきょうしようね")

                    game_state['current_position'] = 19

                st.session_state.perio_quiz_stage = 'intro'
                st.session_state.pop('perio_quiz_answers', None)
                st.session_state.pop('perio_q1_selected', None)
                st.session_state.pop('perio_q2_selected', None)
                st.session_state.pop('perio_q1_checked', None)
                st.session_state.pop('perio_q2_checked', None)
                st.info("つづきは ゲームボードで！")
                navigate_to('game_board')
            return

def show_goal_page():
    """ゴール・ランキングページ"""
    st.markdown("### 🏁 ゲームクリア！")
    
    if 'game_state' in st.session_state:
        game_state = st.session_state.game_state
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("さいしゅうはのかず", f"{game_state.get('teeth_count', 20)}ほん")
        with col2:
            st.metric("トゥースコイン", f"{game_state.get('tooth_coins', 10)}まい")
    
    st.success("おめでとう！")
    
    if st.button("📱 LINEページへ", width='stretch', type="secondary"):
        navigate_to('line_coloring')

def show_line_coloring_page():
    """LINE・ぬりえページ"""
    st.markdown("### 📱 LINE公式アカウント")
    
    st.info("LINE公式アカウントをフォローしよう！お口の健康に関する情報や楽しいコンテンツをお届けします！")
    
    # LINEへの誘導ボタン
    st.markdown("""
    <div style='text-align: center; margin: 20px 0;'>
        <a href="https://line.me/R/ti/p/@551bgrrd" target="_blank" style="text-decoration: none;">
            <div style='
                background: linear-gradient(135deg, #00B900, #00C300);
                color: white;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 1.2em;
                font-weight: bold;
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                display: inline-block;
                width: 100%;
                max-width: 400px;
            '>
                📱 LINE公式アカウントをフォロー
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style='text-align: center; color: #666; font-size: 0.9em; margin: 10px 0;'>
        ボタンをクリックするとLINEアプリまたは新しいタブでLINEページが開きます
    </p>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 さいしょからもういちど", width='stretch'):
        # ゲーム状態をリセット
        for key in list(st.session_state.keys()):
            if key.startswith(('game_state', 'quiz_', 'selected_job')):
                del st.session_state[key]
        navigate_to('reception')

def show_staff_management_page():
    """スタッフ管理ページ"""
    st.markdown("### ⚙️ スタッフ管理")
    
    # PIN認証
    pin = st.text_input("PINコード", type="password")
    
    if pin == "0418":
        st.success("✅ 認証成功")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 全データリセット"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("データをリセットしました")
                navigate_to('reception')
        
        with col2:
            if st.button("🧪 画像テスト"):
                navigate_to('image_test')
    elif pin:
        st.error("❌ PINコードが正しくありません")
    
    if st.button("🏠 メインページに戻る"):
        navigate_to('reception')

def show_image_test_page():
    """画像テストページ"""
    st.title("🧪 画像テスト")
    st.markdown("---")
    
    try:
        from services.image_helper import display_image
        
        # ボード画像テスト
        st.subheader("1. ボードマス画像テスト")
        board_images = ["cell_01", "cell_02", "cell_03", "cell_04", "cell_05"]
        for cell_name in board_images:
            display_image("board", cell_name, f"ボードマス画像: {cell_name}")
        
        # クイズ画像テスト
        st.subheader("2. クイズ画像テスト")
        
        # 虫歯クイズメイン画像
        st.markdown("**虫歯クイズ - メイン画像**")
        display_image("quiz/caries", "main_image", "虫歯クイズメイン画像")
        
        # 虫歯クイズ問題画像
        st.markdown("**虫歯クイズ - 問題画像**")
        display_image("quiz/caries", "question_1", "虫歯クイズ問題1")
        display_image("quiz/caries", "question_2", "虫歯クイズ問題2")
        
        # 食べ物選択肢（JPEG対応）
        st.markdown("**食べ物選択肢 (JPEG形式)**")
        food_items = ["bread", "choco_banana", "cheese", "xylitol_gum"]
        cols = st.columns(4)
        for i, food in enumerate(food_items):
            with cols[i]:
                display_image("quiz/caries/food", food, f"{food}")
        
        # 飲み物選択肢（JPEG対応）
        st.markdown("**飲み物選択肢 (JPEG形式)**")
        drink_items = ["tea", "cola", "orange_juice", "black_coffee", "milk"]
        cols = st.columns(5)
        for i, drink in enumerate(drink_items):
            with cols[i]:
                display_image("quiz/caries/drink", drink, f"{drink}")
        
        # 歯周病クイズ
        st.markdown("**歯周病クイズ**")
        display_image("quiz/periodontitis", "main_image", "歯周病クイズメイン画像")
        display_image("quiz/periodontitis", "question_1", "歯周病クイズ問題1")
        display_image("quiz/periodontitis", "question_2", "歯周病クイズ問題2")
        
        # イベント画像テスト
        st.subheader("3. イベント画像テスト")
        event_images = ["self_introduction", "jump", "tooth_loss", "job_experience"]
        for event_name in event_images:
            display_image("events", event_name, f"イベント画像: {event_name}")
        
        # 定期検診画像テスト
        st.subheader("4. 定期検診画像テスト")
        checkup_images = ["main_checkup", "examination", "brushing_instruction", 
                         "professional_cleaning", "fluoride_treatment", 
                         "checkup_result", "importance"]
        for checkup_name in checkup_images:
            display_image("checkup", checkup_name, f"定期検診画像: {checkup_name}")
        
        st.success("すべての画像カテゴリをテストしました。上記で表示されない画像は、対応するファイルが assets/images/ フォルダにアップロードされていません。")
        
    except ImportError:
        st.error("image_helper モジュールが見つかりません")
    
    # ナビゲーション
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← スタッフ管理に戻る", width='stretch'):
            navigate_to('staff_management')
    with col2:
        if st.button("🏠 受付に戻る", width='stretch'):
            navigate_to('reception')

# メインアプリケーション
def main():
    # タイトル表示
    current_page_info = PAGE_FLOW.get(st.session_state.current_page, {'title': 'お口の人生ゲーム'})
    staff_mode = staff_access_enabled()

    if st.session_state.current_page != 'reception':
        caries_intro = (
            st.session_state.current_page == 'caries_quiz'
            and st.session_state.get('caries_quiz_stage', 'intro') == 'intro'
        )

        hide_progress_pages = {'game_board', 'checkup', 'perio_quiz', 'caries_quiz', 'goal', 'line_coloring'}
        if st.session_state.current_page not in hide_progress_pages and not caries_intro:
            st.markdown(f"<h1 class='main-title'>{current_page_info['title']}</h1>", unsafe_allow_html=True)
            show_progress_bar()

        hide_status_pages = {'caries_quiz', 'perio_quiz'}
        if not caries_intro and st.session_state.current_page not in hide_status_pages:
            show_status_header()
    
    # 現在のページに応じてコンテンツを表示
    if st.session_state.current_page == 'reception':
        show_reception_page()
    elif st.session_state.current_page == 'game_board':
        show_game_board_page()
    elif st.session_state.current_page == 'caries_quiz':
        show_caries_quiz_page()
    elif st.session_state.current_page == 'job_experience':
        show_job_experience_page()
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
    elif st.session_state.current_page == 'image_test':
        if staff_mode:
            show_image_test_page()
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
