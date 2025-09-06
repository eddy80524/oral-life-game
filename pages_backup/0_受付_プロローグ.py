"""
受付・プロローグページ
"""
import streamlit as st
import sys
import os
from datetime import datetime

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.game_logic import initialize_game_state, apply_delta
from services.store import increment_participant_count, get_settings
from services.audio import show_audio_controls
import json

st.set_page_config(
    page_title="受付・プロローグ - お口の人生ゲーム",
    page_icon="📖",
    layout="wide"
)

# 初期化
initialize_game_state()

st.markdown("# 📖 受付・プロローグ")

# 受付セクション
if not st.session_state.player_name:
    st.markdown("## 👋 受付")
    
    with st.container():
        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h3 style="color: #4CAF50;">✨ ようこそ！お口の人生ゲームへ ✨</h3>
            <p>まずは受付をしましょう！</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 撮影許可の確認
    st.markdown("### 📸 撮影許可について")
    photo_consent = st.radio(
        "ゲーム中の写真撮影に同意いただけますか？",
        ["同意する", "同意しない"],
        index=None,
        help="笑顔撮影などで使用します。同意しない場合も楽しくプレイできます。"
    )
    
    if photo_consent:
        st.session_state.photo_consent = (photo_consent == "同意する")
        
        if photo_consent == "同意しない":
            st.info("📷 了解しました。顔が映らないよう配慮いたします。")
    
    # 名前入力
    st.markdown("### ✏️ お名前を教えてね")
    player_name = st.text_input(
        "ニックネームでもOK！",
        placeholder="例: たろうくん、花子ちゃん",
        max_chars=20
    )
    
    # 年齢帯の表示（確認用）
    if st.session_state.age_group:
        st.info(f"年齢帯: {st.session_state.age_group}")
    
    if player_name and photo_consent:
        if st.button("🎉 受付完了！", type="primary", use_container_width=True):
            st.session_state.player_name = player_name
            
            # 参加者数をカウント
            count = increment_participant_count()
            
            st.success(f"ようこそ {player_name} さん！参加者番号: {count}")
            st.rerun()

else:
    # プロローグセクション
    st.markdown(f"## 👤 プレイヤー: {st.session_state.player_name}")
    st.markdown(f"**年齢帯**: {st.session_state.age_group}")
    
    if st.session_state.photo_consent:
        st.success("📸 写真撮影: 同意済み")
    else:
        st.info("📸 写真撮影: 配慮対象")
    
    st.markdown("---")
    
    # プロローグ内容
    st.markdown("## 🎬 プロローグ")
    
    # 音声ガイド
    show_audio_controls("prologue", "🔊 プロローグ音声を聞く")
    
    st.markdown("""
    <div style="background-color: #fff8dc; padding: 20px; border-radius: 15px; margin: 15px 0;">
        <h3 style="color: #d2691e;">🦷 歯について学ぼう！</h3>
        <p style="font-size: 1.1rem;">
            みんなのお口には大切な歯がたくさんあります。<br>
            歯は食べ物を噛んだり、きれいに話したり、<br>
            笑顔を素敵にしてくれる大切な役割があります。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 年齢に応じた説明
    if st.session_state.age_group == "5歳未満":
        content = """
        <h4>🍼 5歳未満のお友達へ</h4>
        <ul>
            <li>🦷 歯はとても大切です</li>
            <li>🪥 毎日歯みがきしましょう</li>
            <li>🍭 甘いものは時間を決めて食べましょう</li>
            <li>👨‍⚕️ 歯医者さんは怖くないよ</li>
        </ul>
        """
    elif st.session_state.age_group in ["5-8歳", "9-12歳"]:
        content = """
        <h4>🧒 子ども向け説明</h4>
        <h5>🦠 虫歯とは？</h5>
        <p>
            お口の中にいる悪い菌（ミュータンス菌）が、甘いものを食べて酸を作ります。<br>
            この酸が歯を溶かしてしまうのが虫歯です。
        </p>
        
        <h5>🩸 歯周病とは？</h5>
        <p>
            歯ぐきが腫れて血が出る病気です。<br>
            歯みがきをしないと、歯の周りの骨まで溶けてしまいます。
        </p>
        
        <h5>✨ 予防方法</h5>
        <ul>
            <li>🪥 正しい歯みがき（1日3回）</li>
            <li>🧶 フロス（歯間清掃）の使用</li>
            <li>🍃 フッ素の活用</li>
            <li>👨‍⚕️ 定期的な歯科検診</li>
            <li>🥛 バランスの良い食事</li>
        </ul>
        """
    else:  # 13歳以上・保護者
        content = """
        <h4>🧑‍🦳 年長者・保護者向け説明</h4>
        <h5>🦠 う蝕（虫歯）のメカニズム</h5>
        <p>
            口腔内のStreptococcus mutansなどの細菌が糖質を代謝し、産生された酸により<br>
            歯質が脱灰されることで発生します。
        </p>
        
        <h5>🦴 歯周病の進行</h5>
        <p>
            歯肉炎から始まり、歯周ポケットの深化、歯槽骨の吸収により<br>
            最終的に歯の動揺・脱落に至る慢性炎症性疾患です。
        </p>
        
        <h5>📊 予防の科学的根拠</h5>
        <ul>
            <li>🔬 フッ化物による再石灰化促進</li>
            <li>📏 プラークコントロールの重要性</li>
            <li>🍎 シュガーコントロール</li>
            <li>⏰ 規則正しい食生活</li>
            <li>🏥 専門的なメンテナンス</li>
        </ul>
        """
    
    st.markdown(content, unsafe_allow_html=True)
    
    # イラスト・写真の説明（実際の画像は後で追加）
    st.markdown("### 🖼️ 参考資料")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="border: 2px dashed #ccc; padding: 20px; text-align: center; border-radius: 10px;">
            <h4>🦷 健康な歯</h4>
            <p>※ イラスト予定</p>
            <p>白くて丈夫な歯</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="border: 2px dashed #ccc; padding: 20px; text-align: center; border-radius: 10px;">
            <h4>🦠 虫歯の歯</h4>
            <p>※ イラスト予定</p>
            <p>穴があいた歯</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 待ち時間用コンテンツ
    if not st.session_state.game_started:
        st.markdown("---")
        st.markdown("### ⏳ 待ち時間の間に...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎨 塗り絵をダウンロード", use_container_width=True):
                st.info("塗り絵は後で LINE・塗り絵 ページからダウンロードできます")
        
        with col2:
            if st.button("🧩 クロスワード", use_container_width=True):
                st.info("クロスワードも後で利用できます")
    
    # ゲーム開始
    st.markdown("---")
    st.markdown("### 🚀 ゲーム開始")
    
    if not st.session_state.game_started:
        # 初期コイン配布の説明
        st.markdown("""
        <div style="background-color: #f0fff0; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;">
            <h4>🎁 初期配布</h4>
            <p>ゲーム開始時に以下をお渡しします：</p>
            <ul>
                <li>🦷 歯: 20本</li>
                <li>🪙 Toothコイン: 10枚</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎮 ゲームボードへ進む", type="primary", use_container_width=True):
            # ゲーム開始フラグを設定
            st.session_state.game_started = True
            st.session_state.start_time = datetime.now()
            
            # 初期奥歯の追加（クイズ前の設定）
            if st.session_state.age_group != "5歳未満":
                # 虫歯クイズ開始時に奥歯4本を追加する準備
                pass
            
            st.success("🎉 ゲーム開始！ボードでサイコロを振りましょう！")
            
            # ボードページに移動
            st.switch_page("pages/1_ゲームボード.py")
    else:
        st.info("🎮 ゲーム進行中です。ボードで続きを進めてください。")
        
        if st.button("🎲 ゲームボードに戻る", use_container_width=True):
            st.switch_page("pages/1_ゲームボード.py")
