"""
受付・プロローグページ
"""
import streamlit as st
from pages.utils import navigate_to


def show_reception_page():
    """受付・プロローグページ（フルスクリーンウィザード）"""
    from services.game_logic import initialize_game_state
    from services.store import ensure_data_files, update_participant_count, get_settings
    from services.image_helper import display_image
    from services.video_helper import display_video

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
            st.markdown("<h1 class='reception-heading'>おくちのテーマパークへようこそ！</h1>", unsafe_allow_html=True)
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
                    
                    # イベントPINをチェック
                    from pages.utils import load_events_config, save_active_event
                    events_data = load_events_config()
                    events = events_data.get("events", [])
                    matched_event = None
                    for event in events:
                        if event.get("pin") == pin:
                            matched_event = event
                            break
                    
                    if matched_event:
                        # イベントPINで認証成功 → そのイベントに切り替え
                        save_active_event(matched_event["id"])
                        st.session_state.reception_wait_unlocked = True
                        st.success(f"✅「{matched_event['name']}」で準備完了！")
                    elif pin == str(staff_pin):
                        # 管理者PINで認証成功
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
