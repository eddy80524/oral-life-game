"""
お口の人生ゲーム - 単一ページアプリ
"""
import streamlit as st
import sys
import os
from datetime import datetime

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

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
    /* サイドバーを完全に隠す */
    .css-1d391kg {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    .css-1lcbmhc {display: none;}
    
    /* モバイル最適化 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
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
        background-color: #f0f8ff;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    .teeth-count {
        background-color: #fff8dc;
        color: #d2691e;
    }
    
    .tooth-coins {
        background-color: #f0fff0;
        color: #228b22;
    }
    
    /* カード風デザイン */
    .game-card {
        background-color: #ffffff;
        border: 2px solid #ddd;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
    """ゲーム状態のヘッダー表示"""
    if 'game_state' in st.session_state and st.session_state.current_page not in ['reception', 'staff_management']:
        game_state = st.session_state.game_state
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="status-badge teeth-count">
                🦷 歯の本数<br><strong>{game_state.get('teeth_count', 20)}本</strong>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # トゥースコインの値を強制的に再取得
            if 'game_state' in st.session_state and st.session_state.game_state:
                tooth_coins = st.session_state.game_state.get('tooth_coins', 10)
            else:
                tooth_coins = 10
            
            st.markdown(f"""
            <div class="status-badge tooth-coins">
                🏅 トゥースコイン<br><strong>{tooth_coins}枚</strong>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="status-badge">
                📍 現在位置<br><strong>{game_state.get('current_position', 0) + 1}マス目</strong>
            </div>
            """, unsafe_allow_html=True)

# 各ページの実装
def show_reception_page():
    """受付・プロローグページ"""
    # 既存の受付ページロジックをここに移植
    from services.game_logic import initialize_game_state
    from services.store import ensure_data_files, update_participant_count
    
    # 初期化
    initialize_game_state()
    ensure_data_files()
    
    st.markdown("### 👋 ようこそ！おくちの人生ゲームへ")
    
    # 参加者情報入力
    if 'participant_name' not in st.session_state:
        st.session_state.participant_name = ""
    if 'participant_age' not in st.session_state:
        st.session_state.participant_age = 5
    if 'photo_consent' not in st.session_state:
        st.session_state.photo_consent = False
    
    with st.form("registration_form"):
        st.markdown("#### 📝 きみのことをおしえて！")
        
        name = st.text_input("なまえ（ニックネーム）", value=st.session_state.participant_name)
        age = st.number_input("なんさい？", min_value=1, max_value=99, value=st.session_state.participant_age)
        
        st.markdown("#### 📸 しゃしんについて")
        photo_consent = st.checkbox("ゲームちゅうのしゃしんさつえいをしてもいいよ", value=st.session_state.photo_consent)
        
        submitted = st.form_submit_button("🚀 ゲームをはじめる", use_container_width=True, type="primary")
        
        if submitted and name.strip():
            st.session_state.participant_name = name.strip()
            st.session_state.participant_age = age
            st.session_state.photo_consent = photo_consent
            
            # 参加者数を更新
            update_participant_count()
            
            st.success(f"🎉 {name}さん、ようこそ！")
            st.info("すごろくボードにいくよ...")
            
            # 少し待ってから遷移
            import time
            time.sleep(1)
            navigate_to('game_board')

def show_game_board_page():
    """ゲームボードページ"""
    st.markdown("### 🎲 すごろくで冒険しよう！")
    
    # ゲーム状態の初期化
    if 'game_state' not in st.session_state:
        from services.game_logic import initialize_game_state
        initialize_game_state()
    
    game_state = st.session_state.game_state
    current_position = game_state['current_position']
    
    # 現在の位置を子供向けに表示
    st.info(f"🌟 いま {current_position + 1}ばんめのマスにいるよ！（{game_state['turn_count']}かいめ）")
    
    # 現在のマスのカード情報を最初に表示
    try:
        import json
        age_group = "under5" if st.session_state.participant_age < 5 else "5plus"
        board_file = f"data/board_main_{age_group}.json"
        
        with open(board_file, 'r', encoding='utf-8') as f:
            board_data = json.load(f)
            
            if current_position < len(board_data) and isinstance(board_data[current_position], dict):
                current_cell = board_data[current_position]
                
                st.markdown("---")
                st.markdown(f"### 📍 {current_cell.get('title', 'マス情報')} (マス{current_position + 1})")
                
                # カード画像表示
                try:
                    from services.image_helper import display_image
                    # まずボードフォルダから探す
                    cell_image_name = f"cell_{current_position + 1:02d}"
                    image_displayed = display_image("board", cell_image_name, current_cell.get('title', ''))
                    
                    # ボードフォルダにない場合はeventsフォルダからactionベースで探す
                    if not image_displayed and 'action' in current_cell:
                        action_name = current_cell['action']
                        # action名から適切な画像名にマッピング
                        action_to_image = {
                            'self_introduction': 'self_introduction',
                            'jump_exercise': 'jump',
                            'tooth_loss': 'tooth_loss',
                            'job_experience': 'job_experience'
                        }
                        if action_name in action_to_image:
                            image_name = action_to_image[action_name]
                            display_image("events", image_name, current_cell.get('title', ''))
                except ImportError:
                    st.warning("画像ヘルパーモジュールが見つかりません")
                except Exception as e:
                    st.error(f"画像表示エラー: {e}")
                
                # カード説明
                if 'desc' in current_cell:
                    st.markdown(f"**{current_cell['desc']}**")
                
                # アクションボタンエリア
                st.markdown("---")
                
                # マスのタイプに応じたアクションボタン
                cell_type = current_cell.get('type', 'normal')
                
                if cell_type == 'quiz':
                    # クイズマス
                    quiz_type = current_cell.get('quiz_type', '')
                    if quiz_type == 'caries':
                        if st.button("🦷 むしばクイズにちょうせん！", use_container_width=True, type="secondary"):
                            navigate_to('caries_quiz')
                    elif quiz_type == 'periodontitis':
                        if st.button("🦷 はぐきのクイズにちょうせん！", use_container_width=True, type="secondary"):
                            navigate_to('perio_quiz')
                elif cell_type == 'stop' or '検診' in current_cell.get('title', ''):
                    # 定期検診マス
                    if st.button("🏥 はいしゃさんにいく", use_container_width=True, type="secondary"):
                        navigate_to('checkup')
                elif '職業' in current_cell.get('title', ''):
                    # 職業体験マス
                    if st.session_state.participant_age >= 5:
                        if st.button("👩‍⚕️ おしごとたいけんをする", use_container_width=True, type="secondary"):
                            navigate_to('job_experience')
                    else:
                        st.info("おしごとたいけんは5さい以上だよ。")
                elif cell_type == 'event':
                    # イベントマス
                    event_button_text = {
                        '初めて言葉を話せるようになった': '🗣️ じこしょうかいをする',
                        'ジャンプができるようになった': '🤸 ジャンプをする',
                        '初めて乳歯が抜けた': '🦷 はのおはなしをする'
                    }
                    title = current_cell.get('title', '')
                    if title in event_button_text:
                        if st.button(event_button_text[title], use_container_width=True, type="secondary"):
                            st.success("たのしい たいけんでした！")
                            st.balloons()
                elif current_position >= 23:  # ゴール
                    if st.button("🏁 ゴール！", use_container_width=True, type="primary"):
                        navigate_to('goal')
                        
    except (FileNotFoundError, json.JSONDecodeError):
        st.error("ボードデータの読み込みに失敗しました")
    
    # サイコロセクション（特定のマスでは表示しない）
    try:
        import json
        age_group = "under5" if st.session_state.participant_age < 5 else "5plus"
        board_file = f"data/board_main_{age_group}.json"
        
        with open(board_file, 'r', encoding='utf-8') as f:
            board_data = json.load(f)
            
            # 現在のマスの情報を取得
            show_dice = True
            if current_position < len(board_data):
                current_cell = board_data[current_position]
                cell_type = current_cell.get('type', 'normal')
                
                # サイコロを表示しないマスの条件
                if (cell_type == 'quiz' or 
                    cell_type == 'stop' or 
                    '検診' in current_cell.get('title', '') or
                    '職業' in current_cell.get('title', '') or
                    current_position >= 23):  # ゴール
                    show_dice = False
            
            if show_dice:
                st.markdown("---")
                st.markdown("### 🎲 つぎのマスへ")
                
                # サイコロを振るボタン（中央に大きく表示）
                dice_container = st.container()
                with dice_container:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        # サイコロを振る前のメッセージ
                        st.markdown("""
                        <div style='text-align: center; background: linear-gradient(135deg, #E6F3FF, #CCE7FF); 
                                    padding: 20px; border-radius: 15px; border: 3px solid #4169E1; margin: 20px 0;'>
                            <h3 style='color: #191970; margin: 10px 0;'>🎲 つぎは なんの数字がでるかな？ 🎲</h3>
                            <p style='color: #4682B4; font-size: 1.1em; margin: 5px 0;'>
                                ボタンを おして サイコロを ふってみよう！
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("🎲 サイコロをふる", use_container_width=True, type="primary", key="dice_roll"):
                            # サイコロを振っている演出を先に表示
                            with st.spinner('🎲 サイコロを ふっているよ... 🎲'):
                                import time
                                import random
                                time.sleep(1)  # 1秒待機して期待感を演出
                            
                            # スマートサイコロロジック（強制停止マスを考慮）
                            # 強制停止マス（定期検診・お仕事体験）
                            stop_positions = [4, 13, 15]  # 4: 1回目定期検診, 13: お仕事体験, 15: 2回目定期検診
                            
                            # 次の強制停止マスまでの距離を計算
                            next_stop_distance = None
                            for stop_pos in stop_positions:
                                if stop_pos > current_position:
                                    next_stop_distance = stop_pos - current_position
                                    break
                            
                            # サイコロの目を決定（ユーザーには気付かれないように自然に調整）
                            if next_stop_distance is not None and next_stop_distance <= 6:
                                # 強制停止マスが6マス以内にある場合は、その範囲内でランダム
                                max_roll = min(next_stop_distance, 6)
                                dice_result = random.randint(1, max_roll)
                            else:
                                # 通常のサイコロ（1-6）
                                dice_result = random.randint(1, 6)
                            
                            # サイコロの目を絵文字で表示
                            dice_emoji = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
                            
                            # 新しい位置を計算
                            old_position = current_position
                            new_position = min(current_position + dice_result, 23)  # 最大24マス（0-23）
                            
                            # ボタンエリアをクリアして結果を表示
                            dice_container.empty()
                            
                            # サイコロの結果を元のボタンエリアに表示
                            with dice_container:
                                st.markdown(f"""
                                <div style='text-align: center; background: linear-gradient(135deg, #FFD700, #FFA500); 
                                            padding: 30px; border-radius: 20px; border: 5px solid #FF6B35; 
                                            margin: 20px 0; box-shadow: 0 8px 16px rgba(0,0,0,0.2);'>
                                    <h1 style='color: #8B4513; margin: 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                                        🎲 サイコロの結果 🎲
                                    </h1>
                                    <div style='background: white; margin: 20px auto; padding: 20px; border-radius: 15px; 
                                               width: 200px; height: 200px; display: flex; align-items: center; justify-content: center;
                                               border: 4px solid #4CAF50; box-shadow: inset 0 4px 8px rgba(0,0,0,0.1);'>
                                        <div style='font-size: 8em; text-shadow: 3px 3px 6px rgba(0,0,0,0.3);'>
                                            {dice_emoji[dice_result]}
                                        </div>
                                    </div>
                                    <h1 style='color: #2E8B57; margin: 0; font-size: 3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                                        【 {dice_result} 】が でたよ！
                                    </h1>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            time.sleep(3)  # 3秒間結果を表示
                            
                            # サイコロ結果を消して移動メッセージを表示
                            dice_container.empty()
                            with dice_container:
                                st.markdown(f"""
                                <div style='text-align: center; background: linear-gradient(135deg, #87CEEB, #4682B4); 
                                            padding: 30px; border-radius: 20px; border: 5px solid #1E90FF; 
                                            margin: 20px 0; box-shadow: 0 8px 16px rgba(0,0,0,0.2);'>
                                    <h1 style='color: #FFFFFF; margin: 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
                                        📍 {new_position + 1}ばんめに いどう中... 📍
                                    </h1>
                                    <div style='margin: 20px 0;'>
                                        <div style='font-size: 4em;'>🏃‍♂️💨</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            time.sleep(1.5)  # 移動メッセージを1.5秒表示
                            
                            # ゲーム状態を更新
                            game_state['current_position'] = new_position
                            game_state['turn_count'] += 1
                            
                            # 特定のマスに到着した場合の自動遷移
                            try:
                                import json
                                age_group = "under5" if st.session_state.participant_age < 5 else "5plus"
                                board_file = f"data/board_main_{age_group}.json"
                                
                                with open(board_file, 'r', encoding='utf-8') as f:
                                    board_data = json.load(f)
                                    
                                    if new_position < len(board_data):
                                        current_cell = board_data[new_position]
                                        cell_type = current_cell.get('type', 'normal')
                                        
                                        # トゥースコインの更新処理
                                        tooth_delta = current_cell.get('tooth_delta', 0)
                                        if tooth_delta != 0:
                                            # セッション状態のトゥースコインを更新
                                            if 'participant_tooth_coin' not in st.session_state:
                                                st.session_state.participant_tooth_coin = 10  # 初期値
                                            
                                            old_coins = st.session_state.participant_tooth_coin
                                            st.session_state.participant_tooth_coin = max(0, old_coins + tooth_delta)
                                            
                                            # ゲーム状態も更新
                                            if 'participants' in st.session_state and st.session_state.current_participant:
                                                participant = st.session_state.current_participant
                                                participant['tooth_coin'] = st.session_state.participant_tooth_coin
                                            
                                            # トゥースコイン変動のメッセージを表示
                                            if tooth_delta > 0:
                                                st.success(f"🏅 トゥースコインを {tooth_delta}枚 もらったよ！（合計: {st.session_state.participant_tooth_coin}枚）")
                                            else:
                                                st.warning(f"💔 トゥースコインを {abs(tooth_delta)}枚 うしなった...（残り: {st.session_state.participant_tooth_coin}枚）")
                                            
                                            time.sleep(2)  # メッセージを2秒表示
                                        
                                        # 特別なマスの処理（子供向けメッセージ）
                                        if cell_type == 'quiz':
                                            if '虫歯' in current_cell.get('title', ''):
                                                st.success("🦷 むしばクイズのマスにとうちゃく！")
                                                st.rerun()
                                            elif '歯周病' in current_cell.get('title', ''):
                                                st.success("🦷 はぐきのクイズのマスにとうちゃく！")
                                                st.rerun()
                                        elif cell_type == 'stop' or '検診' in current_cell.get('title', ''):
                                            st.success("🏥 はいしゃさんのマスにとうちゃく！")
                                            st.rerun()
                                        elif '職業' in current_cell.get('title', ''):
                                            if st.session_state.participant_age >= 5:
                                                st.success("👩‍⚕️ おしごとたいけんのマスにとうちゃく！")
                                                st.rerun()
                                            else:
                                                st.info("おしごとたいけんは5さい以上だよ。")
                                                st.rerun()
                                        elif new_position >= 15:  # ゴール
                                            st.balloons()
                                            st.success("🏁 ゴール！すごいね！")
                                            navigate_to('goal')
                                            return
                                        else:
                                            # 通常のマスの場合も画面を更新
                                            st.rerun()
                                    else:
                                        st.rerun()
                                        
                            except (FileNotFoundError, json.JSONDecodeError):
                                st.rerun()
                
    except (FileNotFoundError, json.JSONDecodeError):
        st.error("ボードデータの読み込みに失敗しました")

def show_caries_quiz_page():
    """むしばクイズページ"""
    st.markdown("### 🦷 むしばクイズにちょうせん！")
    
    # 虫歯クイズメイン画像表示
    try:
        from services.image_helper import display_image
        display_image("quiz/caries", "main_image", "むしばクイズ")
    except ImportError:
        pass
    
    # 問題1: 画像と選択肢をセットで表示
    st.markdown("---")
    st.markdown("**もんだい1: からだのなかで いちばんかたいものは？**")
    try:
        from services.image_helper import display_image
        display_image("quiz/caries", "question_1", "問題1の画像")
    except ImportError:
        pass
    
    question1_options = ["あたま", "せなか", "は"]
    answer1 = st.radio("こたえをえらんでね1", question1_options, key="quiz_0")
    
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = []
    
    if len(st.session_state.quiz_answers) <= 0:
        st.session_state.quiz_answers.append(None)
    st.session_state.quiz_answers[0] = question1_options.index(answer1) if answer1 else None
    
    # 問題2: 食べ物と飲み物の組み合わせを画像で表示
    st.markdown("---")
    st.markdown("**もんだい2: むしばになりにくい たべものは？**")
    try:
        from services.image_helper import display_image
        display_image("quiz/caries", "question_2", "問題2の画像")
    except ImportError:
        pass
    
    # 食べ物と飲み物の組み合わせ選択肢を画像で表示
    st.markdown("**えらんでね：**")
    
    col1, col2, col3 = st.columns(3)
    
    # 選択肢1: チョコバナナ+コーラ
    with col1:
        st.markdown("**せんたくし1**")
        try:
            from services.image_helper import display_image
            display_image("quiz/caries/food", "choco_banana", "チョコバナナ")
            st.markdown("**＋**")
            display_image("quiz/caries/drink", "cola", "コーラ")
        except ImportError:
            st.markdown("チョコバナナ + コーラ")
    
    # 選択肢2: チーズ+おちゃ
    with col2:
        st.markdown("**せんたくし2**")
        try:
            from services.image_helper import display_image
            display_image("quiz/caries/food", "cheese", "チーズ")
            st.markdown("**＋**")
            display_image("quiz/caries/drink", "tea", "おちゃ")
        except ImportError:
            st.markdown("チーズ + おちゃ")
    
    # 選択肢3: パン+ミルク
    with col3:
        st.markdown("**せんたくし3**")
        try:
            from services.image_helper import display_image
            display_image("quiz/caries/food", "bread", "パン")
            st.markdown("**＋**")
            display_image("quiz/caries/drink", "milk", "ミルク")
        except ImportError:
            st.markdown("パン + ミルク")
    
    # 選択肢のラジオボタン
    question2_options = ["せんたくし1 (チョコバナナ+コーラ)", "せんたくし2 (チーズ+おちゃ)", "せんたくし3 (パン+ミルク)"]
    answer2 = st.radio("こたえをえらんでね2", question2_options, key="quiz_1")
    
    if len(st.session_state.quiz_answers) <= 1:
        st.session_state.quiz_answers.append(None)
    st.session_state.quiz_answers[1] = question2_options.index(answer2) if answer2 else None
    
    # 答え合わせボタン
    st.markdown("---")
    if st.button("📝 こたえかんりょう", use_container_width=True, type="primary"):
        # 正解: 問題1は「は」(index 2), 問題2は「チーズ+おちゃ」(index 1)
        correct_answers = [2, 1]  # 問題1の正解: は(index 2), 問題2の正解: チーズ+おちゃ(index 1)
        
        correct_count = sum(1 for i, correct_answer in enumerate(correct_answers) 
                          if len(st.session_state.quiz_answers) > i and st.session_state.quiz_answers[i] == correct_answer)
        
        st.success(f"せいかいかず: {correct_count}/2")
        
        # 結果に応じた分岐ルート画像表示
        try:
            from services.image_helper import display_image
            if correct_count >= 1:
                st.markdown("### 🌟 むしばにならないルート！")
                st.info("けんこうてきなえらびかたをしよう！")
                col1, col2 = st.columns(2)
                with col1:
                    display_image("quiz/caries/food", "cheese", "チーズ（けんこうてき）")
                with col2:
                    display_image("quiz/caries/drink", "tea", "おちゃ（けんこうてき）")
            else:
                st.markdown("### 💧 むしばになるルート...")
                st.warning("きをつけよう！これらはむしばになりやすいよ")
                col1, col2 = st.columns(2)
                with col1:
                    display_image("quiz/caries/food", "choco_banana", "チョコバナナ（むしばになりやすい）")
                with col2:
                    display_image("quiz/caries/drink", "cola", "コーラ（むしばになりやすい）")
        except ImportError:
            pass
        
        # 結果に応じてトゥースコイン調整と条件分岐
        if 'game_state' in st.session_state:
            game_state = st.session_state.game_state
            old_coins = game_state.get('tooth_coins', 0)
            
            if correct_count >= 1:
                # 成功ルート: セル9へ
                game_state['tooth_coins'] += 5
                game_state['current_position'] = 9
                show_coin_change(old_coins, game_state['tooth_coins'], "むしばクイズ せいかい！ けんこうルートへ")
                st.success("🌟 よくできました！ けんこうルートに すすみます！")
            else:
                # 失敗ルート: セル6へ
                game_state['tooth_coins'] = max(0, game_state['tooth_coins'] - 3)
                game_state['current_position'] = 6
                show_coin_change(old_coins, game_state['tooth_coins'], "むしばクイズ ふせいかい... きをつけよう")
                st.warning("💧 もうすこし きをつけましょう。べつのルートに すすみます。")
        
        st.info("つづきは ゲームボードで！")
        navigate_to('game_board')

def show_job_experience_page():
    """おしごとたいけんページ"""
    st.markdown("### 👩‍⚕️ おしごとたいけん")
    
    jobs = ["はいしゃさん", "はのおそうじのせんせい", "はをつくるせんせい"]
    
    if 'selected_job' not in st.session_state:
        st.session_state.selected_job = None
    
    if st.session_state.selected_job is None:
        st.markdown("くじをひいて おしごとをきめよう！")
        
        if st.button("🎯 くじをひく", use_container_width=True, type="primary"):
            import random
            job_index = random.randint(0, 2)
            st.session_state.selected_job = jobs[job_index]
            st.success(f"🎉 {st.session_state.selected_job}にきまったよ！")
            st.rerun()
    else:
        st.info(f"たいけんするおしごと: {st.session_state.selected_job}")
        st.markdown("1ぷんかん たいけんをします...")
        
        if st.button("✅ たいけんかんりょう", use_container_width=True, type="primary"):
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
    st.markdown("### 🏥 ていきけんしん")
    
    st.info("ていきけんしんで おくちのなかを チェックします！")
    
    if st.button("🏥 けんしんをうける", use_container_width=True, type="primary"):
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
    st.markdown("### 🦷 はぐきクイズ")
    
    # 歯周病クイズメイン画像表示
    try:
        from services.image_helper import display_image
        display_image("quiz/periodontitis", "main_image", "はぐきクイズ")
    except ImportError:
        pass
    
    # 歯周病クイズ実装（問題ごとに画像と選択肢をセットで表示）
    questions = [
        {"q": "はみがきしないと どこから ちがでる？", "options": ["は", "はぐき", "した"], "correct": 1},
        {"q": "はの ねっこの ところは どうなってる？", "options": ["①", "②", "③"], "correct": 2}
    ]
    
    if 'perio_quiz_answers' not in st.session_state:
        st.session_state.perio_quiz_answers = []
    
    # 問題1: 画像と選択肢をセットで表示
    st.markdown("---")
    st.markdown("**問題1: はぐきの状態を比べてみよう**")
    try:
        from services.image_helper import display_image
        col1, col2 = st.columns(2)
        with col1:
            display_image("quiz/periodontitis", "question_1a", "はぐきの状態A")
        with col2:
            display_image("quiz/periodontitis", "question_1b", "はぐきの状態B")
    except ImportError:
        pass
    
    # 問題1の質問と選択肢
    st.markdown(f"**もんだい1: {questions[0]['q']}**")
    answer1 = st.radio(f"こたえをえらんでね1", questions[0]['options'], key=f"perio_quiz_0")
    
    if len(st.session_state.perio_quiz_answers) <= 0:
        st.session_state.perio_quiz_answers.append(None)
    st.session_state.perio_quiz_answers[0] = questions[0]['options'].index(answer1) if answer1 else None
    
    # 問題2: 画像と選択肢をセットで表示
    st.markdown("---")
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
    
    # 問題2の質問と選択肢
    st.markdown(f"**もんだい2: {questions[1]['q']}**")
    answer2 = st.radio(f"こたえをえらんでね2", questions[1]['options'], key=f"perio_quiz_1")
    
    if len(st.session_state.perio_quiz_answers) <= 1:
        st.session_state.perio_quiz_answers.append(None)
    st.session_state.perio_quiz_answers[1] = questions[1]['options'].index(answer2) if answer2 else None
    
    # 答え合わせボタン
    st.markdown("---")
    if st.button("📝 こたえかんりょう", use_container_width=True, type="primary"):
        correct_count = sum(1 for i, q in enumerate(questions) 
                          if st.session_state.perio_quiz_answers[i] == q['correct'])
        
        st.success(f"せいかいかず: {correct_count}/{len(questions)}")
        
        # 結果に応じてコイン調整し、cell19に合流
        if 'game_state' in st.session_state:
            game_state = st.session_state.game_state
            old_coins = game_state['tooth_coins']
            
            if correct_count >= 1:
                # 成功時はボーナスコイン
                game_state['tooth_coins'] += 5
                show_coin_change(old_coins, game_state['tooth_coins'], "🌟 よくできました！")
                st.balloons()
            else:
                # 失敗時はペナルティコイン
                game_state['tooth_coins'] = max(0, game_state['tooth_coins'] - 3)
                show_coin_change(old_coins, game_state['tooth_coins'], "💧 もうすこし べんきょうしようね")
            
            # 成功・失敗どちらもcell19に進む
            game_state['current_position'] = 19
        
        st.info("つづきは ゲームボードで！")
        navigate_to('game_board')

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
    
    # LINEへの直接リンクボタンを追加
    st.markdown("""
    <div style='text-align: center; margin: 20px 0;'>
        <a href="https://line.me/R/ti/p/@551bgrrd" target="_blank" style="text-decoration: none;">
            <div style='
                background: linear-gradient(135deg, #00B900, #00C300);
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                font-size: 1.1em;
                font-weight: bold;
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                display: inline-block;
                width: 100%;
                max-width: 350px;
            '>
                📱 LINE公式アカウントをフォロー
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📱 LINEページへ", use_container_width=True, type="secondary"):
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
    
    if st.button("🏠 さいしょからもういちど", use_container_width=True):
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
        if st.button("← スタッフ管理に戻る", use_container_width=True):
            navigate_to('staff_management')
    with col2:
        if st.button("🏠 受付に戻る", use_container_width=True):
            navigate_to('reception')

# メインアプリケーション
def main():
    # タイトル表示
    current_page_info = PAGE_FLOW.get(st.session_state.current_page, {'title': 'お口の人生ゲーム'})
    st.markdown(f"<h1 class='main-title'>{current_page_info['title']}</h1>", unsafe_allow_html=True)
    
    # 進行バー表示
    show_progress_bar()
    
    # 状態ヘッダー表示
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
        show_staff_management_page()
    elif st.session_state.current_page == 'image_test':
        show_image_test_page()
    else:
        st.error("ページが見つかりません")
        navigate_to('reception')

    # スタッフ管理へのリンク（画面下部）
    if st.session_state.current_page == 'reception':
        st.markdown("---")
        if st.button("⚙️ スタッフ管理", use_container_width=False):
            navigate_to('staff_management')

if __name__ == "__main__":
    main()
