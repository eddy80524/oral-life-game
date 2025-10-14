"""
お口の人生ゲーム - 単一ページアプリ
"""
import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import json
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

ROULETTE_HTML_TEMPLATE = """
<style>
.roulette-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.2rem;
    padding: 0.5rem 0;
}

.roulette-surface {
    position: relative;
    width: 280px;
    height: 280px;
}

.roulette-pointer {
    position: absolute;
    top: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 20px solid transparent;
    border-right: 20px solid transparent;
    border-top: 32px solid #e74c3c;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.25));
    z-index: 2;
}

.roulette-wheel {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: #f8f7f2;
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    display: flex;
    align-items: center;
    justify-content: center;
}

.roulette-wheel canvas {
    width: 100%;
    height: 100%;
}

.spin-button {
    padding: 0.85rem 2.5rem;
    border: none;
    border-radius: 999px;
    background: linear-gradient(135deg, #ffb347, #ffcc33);
    color: #5a3600;
    font-weight: bold;
    font-size: 1.2rem;
    cursor: pointer;
    box-shadow: 0 6px 12px rgba(0,0,0,0.18);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.spin-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    box-shadow: none;
}

.spin-button:not(:disabled):active {
    transform: scale(0.97);
}

.result-text {
    font-size: 1.05rem;
    color: #444;
    min-height: 1.5rem;
    text-align: center;
}
</style>
<div class="roulette-wrapper">
  <div class="roulette-surface">
    <div class="roulette-pointer"></div>
    <div class="roulette-wheel" id="roulette-wheel">
      <canvas id="roulette-canvas" width="320" height="320"></canvas>
    </div>
  </div>
  <button class="spin-button" id="spin-button">🎡 ルーレットを回す</button>
  <div class="result-text" id="result-text"></div>
</div>
<script>
const allowedResults = __ALLOWED__;
const segments = [1, 2, 3, 1, 2, 3, 1, 2];
const segmentColors = ["#f94144","#f3722c","#f8961e","#f9844a","#f9c74f","#90be6d","#43aa8b","#577590"];
const wheel = document.getElementById("roulette-wheel");
const canvas = document.getElementById("roulette-canvas");
const ctx = canvas.getContext("2d");
const spinButton = document.getElementById("spin-button");
const resultText = document.getElementById("result-text");

function drawWheel() {
  const total = segments.length;
  const segmentAngle = (2 * Math.PI) / total;
  for (let i = 0; i < total; i++) {
    const startAngle = -Math.PI / 2 + (i - 0.5) * segmentAngle;
    const endAngle = startAngle + segmentAngle;
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2, canvas.height / 2);
    ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 2 - 6, startAngle, endAngle);
    ctx.closePath();
    ctx.fillStyle = segmentColors[i % segmentColors.length];
    ctx.fill();
    ctx.save();
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate(startAngle + segmentAngle / 2);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 34px 'Noto Sans JP', sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(segments[i]), canvas.width / 2 - 70, 0);
    ctx.restore();
  }
}
drawWheel();

function setComponentValue(payload) {
  if (window.Streamlit && window.Streamlit.setComponentValue) {
    window.Streamlit.setComponentValue(payload);
  } else if (window.parent && window.parent.Streamlit && window.parent.Streamlit.setComponentValue) {
    window.parent.Streamlit.setComponentValue(payload);
  }
}

function spinWheel() {
  if (!allowedResults.length) {
    resultText.textContent = "ルーレットはおやすみ中だよ。";
    return;
  }
  spinButton.disabled = true;
  resultText.textContent = "くるくる回っているよ...";
  wheel.style.transition = "none";
  wheel.style.transform = "rotate(0deg)";
  void wheel.offsetWidth;
  const chosenValue = allowedResults[Math.floor(Math.random() * allowedResults.length)];
  const matchingSegments = [];
  for (let i = 0; i < segments.length; i++) {
    if (segments[i] === chosenValue) {
      matchingSegments.push(i);
    }
  }
  const winningIndex = matchingSegments[Math.floor(Math.random() * matchingSegments.length)];
  const segmentAngle = 360 / segments.length;
  const extraTurns = 4 + Math.floor(Math.random() * 2);
  const centerOffset = (Math.random() - 0.5) * (segmentAngle * 0.15);
  const finalAngle = extraTurns * 360 - winningIndex * segmentAngle + centerOffset;
  wheel.style.transition = "transform 4s cubic-bezier(0.19, 1, 0.22, 1)";
  wheel.style.transform = `rotate(${finalAngle}deg)`;
  setTimeout(() => {
    resultText.textContent = `「${chosenValue}」が出たよ！`;
    setComponentValue({ value: chosenValue, spinId: Date.now() });
    spinButton.disabled = false;
  }, 4200);
}

spinButton.addEventListener("click", spinWheel);
</script>
"""

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
    """受付・プロローグページ（フルスクリーンウィザード）"""
    from services.game_logic import initialize_game_state
    from services.store import ensure_data_files, update_participant_count
    from services.image_helper import find_image_file, display_image

    initialize_game_state()
    ensure_data_files()

    # セッション初期化
    st.session_state.setdefault('participant_name', "")
    st.session_state.setdefault('participant_age', 5)
    st.session_state.setdefault('photo_consent', False)
    st.session_state.setdefault('reception_step', 0)
    st.session_state.setdefault('reception_age_label', "5さい")
    st.session_state.setdefault('reception_audio_prompt', False)

    step = st.session_state.reception_step
    if step != 1 and st.session_state.reception_audio_prompt:
        st.session_state.reception_audio_prompt = False

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
        image_path = find_image_file("reception", basename)
        if image_path and image_path.exists():
            st.image(str(image_path), use_column_width=True)
        elif basename == "cover":
            if not display_image("board", "okuchi_game", "おくちの人生ゲーム", use_container_width=True):
                st.markdown("<div class='reception-photo-slot'>ここに画像や動画をいれてね</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='reception-photo-slot'>ここに画像や動画をいれてね</div>", unsafe_allow_html=True)

    with central_col:
        if step > 0:
            back_cols = st.columns([0.25, 0.5, 0.25])
            with back_cols[0]:
                if st.button("← もどる", key=f"reception_back_{step}", type="secondary"):
                    st.session_state.reception_step = max(0, step - 1)
                    st.rerun()
            st.markdown("<div style='height:3vh'></div>", unsafe_allow_html=True)

        if step == 0:
            render_reception_image("cover")
            st.markdown("<div style='height:2vh'></div>", unsafe_allow_html=True)
            if st.button("すすむ", key="reception_next_cover", use_container_width=True, type="primary"):
                st.session_state.reception_step = 1
                st.rerun()

        elif step == 1:
            render_reception_image("welcome_teeth")
            st.markdown("<h1 class='reception-heading'>おくちのじんせいゲームへようこそ！</h1>", unsafe_allow_html=True)
            st.markdown("<p class='reception-text'>みんなには100さいになるまで<br>きれいなおくちですごしてもらうよ！</p>", unsafe_allow_html=True)
            audio_cols = st.columns([0.25, 0.5, 0.25])
            with audio_cols[2]:
                if st.button("🔊 おはなしをきく", key="reception_audio", type="secondary"):
                    st.session_state.reception_audio_prompt = True
            if st.session_state.reception_audio_prompt:
                st.info("音声ガイドは準備中だよ！")
            st.markdown("<div style='height:1vh'></div>", unsafe_allow_html=True)
            if st.button("すすむ", key="reception_next_welcome", use_container_width=True, type="primary"):
                st.session_state.reception_step = 2
                st.rerun()

        elif step == 2:
            render_reception_image("name_prompt")
            st.markdown("<h1 class='reception-heading'>きみのなまえを<br>おしえて！</h1>", unsafe_allow_html=True)
            name_input = st.text_input(
                "",
                value=st.session_state.participant_name,
                placeholder="ニックネームを入力してね",
                key="reception_name_input"
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
                "",
                age_options,
                index=age_index,
                key="reception_age_select",
                label_visibility="collapsed"
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
            render_reception_image("wait")
            st.markdown("<h1 class='reception-heading'>まっていてね！</h1>", unsafe_allow_html=True)
            st.markdown(
                "<div class='wait-note'>絵本がめくれるような形だと理想かも<br>もしくは読み聞かせ動画が流れているとか</div>",
                unsafe_allow_html=True
            )
            if st.button("すすむ", key="reception_start_game", use_container_width=True, type="primary"):
                update_participant_count()
                st.session_state.reception_step = 0
                st.session_state.game_board_stage = 'card'
                st.session_state.pop('roulette_feedback', None)
                st.session_state.pop('roulette_last_spin_id', None)
                navigate_to('game_board')

    st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)


def show_game_board_page():
    """ゲームボードページ（カード表示とルーレット画面に分離）"""
    if 'game_state' not in st.session_state:
        from services.game_logic import initialize_game_state
        initialize_game_state()

    st.session_state.setdefault('game_board_stage', 'card')
    stage = st.session_state.game_board_stage

    game_state = st.session_state.game_state
    current_position = game_state['current_position']

    # ボードデータ読み込み
    board_data = []
    current_cell = None
    max_position_index = 0
    try:
        age_group = "under5" if st.session_state.participant_age < 5 else "5plus"
        board_file = f"data/board_main_{age_group}.json"
        with open(board_file, 'r', encoding='utf-8') as f:
            board_data = json.load(f)
        max_position_index = max(len(board_data) - 1, 0)
        if 0 <= current_position < len(board_data) and isinstance(board_data[current_position], dict):
            current_cell = board_data[current_position]
    except (FileNotFoundError, json.JSONDecodeError):
        board_data = []
        current_cell = None
        st.error("ボードデータの読み込みに失敗しました")

    # ステージ補正
    if stage not in {'card', 'roulette'}:
        stage = st.session_state.game_board_stage = 'card'

    def render_cell_media(position: int, cell_info: dict) -> None:
        try:
            from services.image_helper import display_image
            cell_image_name = f"cell_{position + 1:02d}"
            if not display_image("board", cell_image_name, cell_info.get('title', ''), use_container_width=True):
                action_name = cell_info.get('action')
                action_to_image = {
                    'self_introduction': 'self_introduction',
                    'jump_exercise': 'jump',
                    'tooth_loss': 'tooth_loss',
                    'job_experience': 'job_experience'
                }
                if action_name in action_to_image:
                    display_image("events", action_to_image[action_name], cell_info.get('title', ''), use_container_width=True)
        except ImportError:
            pass

    def process_spin_result(result_value: int):
        new_position = min(current_position + result_value, max_position_index)
        game_state['current_position'] = new_position
        game_state['turn_count'] += 1

        feedback = {
            'result': result_value,
            'old_position': current_position,
            'new_position': new_position,
            'move_message': f"➡️ {current_position + 1}ばんめ → {new_position + 1}ばんめ にすすんだよ！",
            'coin_messages': [],
            'landing_message': None,
            'landing_tone': None,
            'next_page': 'refresh',
            'next_button_label': "つぎのマスをみる"
        }

        if board_data and 0 <= new_position < len(board_data):
            landing_cell = board_data[new_position]
            landing_title = landing_cell.get('title', '')
            landing_type = landing_cell.get('type', 'normal')

            tooth_delta = landing_cell.get('tooth_delta', 0)
            if tooth_delta != 0:
                st.session_state.setdefault('participant_tooth_coin', 10)
                old_coins = st.session_state.participant_tooth_coin
                st.session_state.participant_tooth_coin = max(0, old_coins + tooth_delta)
                if 'participants' in st.session_state and st.session_state.current_participant:
                    participant = st.session_state.current_participant
                    participant['tooth_coin'] = st.session_state.participant_tooth_coin
                tone = 'success' if tooth_delta > 0 else 'warning'
                message = (f"🏅 トゥースコインを {tooth_delta}枚 もらったよ！（合計: {st.session_state.participant_tooth_coin}枚）" if tooth_delta > 0
                           else f"💔 トゥースコインを {abs(tooth_delta)}枚 うしなった...（残り: {st.session_state.participant_tooth_coin}枚）")
                feedback['coin_messages'].append((tone, message))

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
        else:
            if current_position >= max_position_index:
                feedback['landing_message'] = "🏁 ゴール！すごいね！"
                feedback['landing_tone'] = 'success'
                feedback['next_page'] = 'goal'
                feedback['next_button_label'] = "🏁 ゴールへすすむ"
                st.balloons()

        game_state['current_position'] = feedback['new_position']
        return feedback

    st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)
    focus_col = st.columns([0.06, 0.88, 0.06])[1]

    with focus_col:
        if stage == 'card':
            recent_feedback = st.session_state.pop('roulette_recent_feedback', None)
            if recent_feedback:
                st.success(f"🎯 {recent_feedback['result']}マスすすんだよ！")
                st.info(recent_feedback['move_message'])
                for tone, message in recent_feedback.get('coin_messages', []):
                    if tone == 'success':
                        st.success(message)
                    elif tone == 'warning':
                        st.warning(message)
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

            render_cell_media(current_position, current_cell)
            st.markdown(f"<p class='reception-caption'>マス {current_position + 1}</p>", unsafe_allow_html=True)
            if current_cell.get('desc'):
                st.markdown(f"<h2 style='text-align:center;'>{current_cell['desc']}</h2>")

            cell_type = current_cell.get('type', 'normal')
            title = current_cell.get('title', '')
            action_taken = False

            if cell_type == 'quiz':
                quiz_type = current_cell.get('quiz_type', '')
                if quiz_type == 'caries':
                    if st.button("🦷 むしばクイズにちょうせん！", use_container_width=True, type="primary"):
                        navigate_to('caries_quiz')
                        action_taken = True
                elif quiz_type == 'periodontitis':
                    if st.button("🦷 はぐきのクイズにちょうせん！", use_container_width=True, type="primary"):
                        navigate_to('perio_quiz')
                        action_taken = True
            elif cell_type == 'stop' or '検診' in title:
                if st.button("🏥 はいしゃさんにいく", use_container_width=True, type="primary"):
                    navigate_to('checkup')
                    action_taken = True
            elif '職業' in title:
                if st.session_state.participant_age >= 5:
                    if st.button("👩‍⚕️ おしごとたいけんをする", use_container_width=True, type="primary"):
                        navigate_to('job_experience')
                        action_taken = True
                else:
                    st.info("おしごとたいけんは5さい以上だよ。")

            elif cell_type == 'event':
                event_button_text = {
                    '初めて言葉を話せるようになった': '🗣️ じこしょうかいをする',
                    'ジャンプができるようになった': '🤸 ジャンプをする',
                    '初めて乳歯が抜けた': '🦷 はのおはなしをする'
                }
                if title in event_button_text:
                    if st.button(event_button_text[title], use_container_width=True, type='secondary', key=f'event_action_{current_position}'):
                        st.success('たのしい たいけんでした！')
                        st.balloons()

            can_spin = (not action_taken and cell_type not in {'quiz', 'stop'}
                        and '検診' not in title and '職業' not in title
                        and current_position < max_position_index)

            if can_spin:
                st.markdown("<div style='height:2vh'></div>", unsafe_allow_html=True)
                if st.button("🎡 ルーレットをまわす", key="board_to_roulette", use_container_width=True, type="primary"):
                    st.session_state.game_board_stage = 'roulette'
                    st.rerun()
            elif not action_taken and current_position >= max_position_index:
                if st.button("🏁 ゴールへ", use_container_width=True, type="primary"):
                    navigate_to('goal')

        elif stage == 'roulette':
            st.markdown("<h1 style='text-align:center;'>ゲームスタート！</h1>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style='width:100%;max-width:360px;margin:0 auto 1.5rem;'>
                    <div style='height:18px;border-radius:999px;background:#cfe0b5;'>
                        <div style='width:35%;height:100%;border-radius:999px;background:#6aa06f;'></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            forced_stop_positions = [4, 13, 15]
            distance_to_goal = max(0, max_position_index - current_position)
            next_stop_distance = None
            for stop_pos in forced_stop_positions:
                if stop_pos > current_position:
                    next_stop_distance = stop_pos - current_position
                    break

            max_spin = 3
            max_reachable = min(max_spin, distance_to_goal if distance_to_goal > 0 else max_spin)
            allowed_numbers = list(range(1, max_reachable + 1))
            if next_stop_distance is not None and next_stop_distance <= max_spin:
                allowed_numbers = list(range(1, min(max_reachable, next_stop_distance) + 1))

            if not allowed_numbers:
                st.info("すすむマスはないよ。マスに戻るね。")
                st.session_state.game_board_stage = 'card'
                st.rerun()
            else:
                spinner_html = ROULETTE_HTML_TEMPLATE.replace("__ALLOWED__", json.dumps(allowed_numbers))
                component_value = components.html(spinner_html, height=520, scrolling=False)
                if isinstance(component_value, dict):
                    spin_id = component_value.get("spinId")
                    result_value = component_value.get("value")
                    if spin_id is not None and result_value is not None:
                        last_spin_id = st.session_state.get('roulette_last_spin_id')
                        if last_spin_id != spin_id:
                            try:
                                value_int = int(result_value)
                            except ValueError:
                                value_int = int(float(result_value))
                            feedback = process_spin_result(value_int)
                            st.session_state.roulette_last_spin_id = spin_id
                            st.session_state.roulette_recent_feedback = feedback
                            st.session_state.game_board_stage = 'card'
                            next_page = feedback.get('next_page')
                            if next_page and next_page != 'refresh':
                                navigate_to(next_page)
                            else:
                                st.rerun()

    st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)

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
    if st.session_state.current_page != 'reception':
        st.markdown(f"<h1 class='main-title'>{current_page_info['title']}</h1>", unsafe_allow_html=True)
        show_progress_bar()
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
    if st.session_state.current_page == 'reception':
        staff_cols = st.columns([0.5, 0.5])
        with staff_cols[1]:
            if st.button("⚙️ スタッフ管理", use_container_width=True):
                navigate_to('staff_management')

if __name__ == "__main__":
    main()
