"""
定期健診ページ - お口の人生ゲーム
"""
import streamlit as st
import sys
import os

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.game_logic import apply_tooth_delta
from services.store import save_game_state
from services.audio import show_audio_controls
from services.image_helper import display_image

# ページ設定
st.set_page_config(
    page_title="定期健診 - お口の人生ゲーム",
    page_icon="🏥",
    layout="wide"
)

def main():
    st.title("🏥 定期健診")
    
    if 'game_state' not in st.session_state:
        st.error("ゲーム状態が見つかりません。ゲームボードからやり直してください。")
        if st.button("🎲 ゲームボードに戻る"):
            st.switch_page("pages/1_ゲームボード.py")
        return
    
    game_state = st.session_state.game_state
    
    # 定期健診状態の初期化
    if 'checkup_state' not in st.session_state:
        st.session_state.checkup_state = {
            'completed': False
        }
    
    checkup_state = st.session_state.checkup_state
    
    # 健診完了後
    if checkup_state['completed']:
        st.success("🎉 定期健診が完了しました！")
        
        # 現在の状態表示
        col1, col2 = st.columns(2)
        with col1:
            st.metric("歯の本数", game_state['teeth_count'])
        with col2:
            st.metric("トゥースコイン", game_state['tooth_coins'])
        
        st.markdown("### 📋 健診結果")
        
        # 健診結果の画像
        display_image("checkup", "checkup_result", caption="健診完了！", use_column_width=True)
        
        st.success("✅ お口の状態は良好です！定期的な健診が大切ですね。")
        
        # アドバイス表示
        st.markdown("### 💡 歯科医師からのアドバイス")
        st.info("""
        **定期健診の重要性:**
        - 虫歯や歯周病の早期発見・早期治療
        - 正しい歯磨き方法の指導
        - 磨きにくい場所のプロフェッショナルクリーニング
        - 予防処置（フッ素塗布など）
        
        **推奨頻度:** 3〜6ヶ月に1回
        """)
        
        # 音声ガイド
        show_audio_controls("checkup_advice", "🔊 定期健診について")
        
        # 次のステップ
        st.markdown("### ➡️ 次のステップ")
        st.info("定期健診の後は、歯周病クイズに挑戦します！")
        
        if st.button("🦷 歯周病クイズに進む", use_container_width=True, type="primary"):
            st.switch_page("pages/6_歯周病クイズ.py")
        
        if st.button("🎲 ゲームボードに戻る", use_container_width=True):
            st.switch_page("pages/1_ゲームボード.py")
        
        return
    
    # 定期健診開始
    st.markdown("### 🏥 定期健診へようこそ")
    
    # 定期健診のメイン画像
    display_image("checkup", "main_checkup", caption="定期健診の様子", use_column_width=True)
    
    st.markdown("""
    **定期健診でやること:**
    1. 口の中の検査
    2. 歯磨き指導
    3. プロフェッショナルクリーニング
    4. 予防処置
    
    **健診完了で+3トゥースコインがもらえます！**
    """)
    
    # 現在の状態表示
    col1, col2 = st.columns(2)
    with col1:
        st.metric("歯の本数", game_state['teeth_count'])
    with col2:
        st.metric("トゥースコイン", game_state['tooth_coins'])
    
    # 健診の流れを説明
    st.markdown("### 📋 健診の流れ")
    
    with st.expander("1. 口の中の検査"):
        # 検査の画像
        display_image("checkup", "examination", caption="口の中の検査", use_column_width=True)
        st.markdown("""
        - 虫歯がないかチェック
        - 歯茎の状態を確認
        - 噛み合わせの確認
        - 口の中全体の健康状態をチェック
        """)
    
    with st.expander("2. 歯磨き指導"):
        # 歯磨き指導の画像
        display_image("checkup", "brushing_instruction", caption="正しい歯磨き指導", use_column_width=True)
        st.markdown("""
        - 正しい歯磨きの方法を教わります
        - 歯ブラシの選び方
        - フロスの使い方
        - 磨き残しやすい場所の確認
        """)
    
    with st.expander("3. プロフェッショナルクリーニング"):
        # クリーニングの画像
        display_image("checkup", "professional_cleaning", caption="プロフェッショナルクリーニング", use_column_width=True)
        st.markdown("""
        - 歯石の除去
        - 歯の表面の着色除去
        - 歯と歯茎の境目のクリーニング
        - 普段の歯磨きでは取れない汚れを除去
        """)
    
    with st.expander("4. 予防処置"):
        # 予防処置の画像
        display_image("checkup", "fluoride_treatment", caption="フッ素塗布などの予防処置", use_column_width=True)
        st.markdown("""
        - フッ素塗布で歯を強化
        - 虫歯になりやすい溝を埋めるシーラント
        - 個人に合った予防プランの提案
        """)
    
    # 健診開始ボタン
    if st.button("🏥 定期健診を受ける", use_container_width=True, type="primary"):
        # トゥースコインを付与
        apply_tooth_delta(game_state, 3)
        checkup_state['completed'] = True
        save_game_state(game_state)
        
        st.balloons()
        st.success("🎉 定期健診が完了しました！")
        st.success("🪙 +3トゥースコインを獲得しました！")
        st.rerun()
    
    # 定期健診の重要性について
    st.markdown("### 🌟 なぜ定期健診が大切なの？")
    
    # 定期健診の重要性を示す画像
    display_image("checkup", "importance", caption="定期健診の大切さ", use_column_width=True)
    
    st.markdown("""
    定期健診は、お口の健康を守るためにとても大切です：
    
    - **早期発見:** 小さな虫歯も見つけることができます
    - **予防効果:** 虫歯や歯周病を予防できます  
    - **専門的ケア:** 自分では取れない汚れもきれいにできます
    - **正しい知識:** 正しいケア方法を教わることができます
    """)
    
    # 音声ガイド
    show_audio_controls("checkup_intro", "🔊 定期健診の説明")
    
    # 戻るボタン
    if st.button("⬅️ ゲームボードに戻る", use_container_width=True):
        st.switch_page("pages/1_ゲームボード.py")
    
    # 進行状況表示（サイドバー）
    st.sidebar.markdown("### 📊 現在の状態")
    st.sidebar.metric("歯の本数", game_state['teeth_count'])
    st.sidebar.metric("トゥースコイン", game_state['tooth_coins'])
    st.sidebar.metric("現在のマス", f"{game_state['current_position'] + 1}マス目")

if __name__ == "__main__":
    main()
