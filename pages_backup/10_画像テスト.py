"""
画像表示テストページ
"""
import streamlit as st
import sys
import os

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.image_helper import display_image, create_image_upload_guide

st.set_page_config(
    page_title="画像表示テスト",
    page_icon="📷",
    layout="wide"
)

def main():
    st.title("📷 画像表示テスト")
    
    # タブでセクション分け
    tab1, tab2, tab3 = st.tabs(["🎮 画像テスト", "📁 アップロードガイド", "🔍 ファイル検索テスト"])
    
    with tab1:
        st.markdown("### 🎮 ゲーム画像表示テスト")
        
        # ボードマス画像テスト
        st.markdown("#### ボードマス画像")
        col1, col2 = st.columns(2)
        with col1:
            cell_num = st.number_input("マス番号", min_value=1, max_value=25, value=1)
            display_image("board", f"cell_{cell_num:02d}", 
                         caption=f"マス{cell_num}の画像", use_column_width=True)
        
        # イベント画像テスト
        st.markdown("#### イベント画像")
        event_options = ["self_introduction", "jump", "tooth_loss", "job_experience"]
        event_choice = st.selectbox("イベントを選択", event_options)
        display_image("events", event_choice, caption=f"{event_choice}の画像", use_column_width=True)
        
        # クイズ画像テスト
        st.markdown("#### クイズ画像")
        quiz_type = st.selectbox("クイズタイプ", ["caries", "periodontitis"])
        if quiz_type == "caries":
            quiz_num = st.number_input("虫歯クイズ問題番号", min_value=1, max_value=2, value=1)
            display_image("quiz_caries", f"question_{quiz_num}", 
                         caption=f"虫歯クイズ問題{quiz_num}", use_column_width=True)
        else:
            quiz_num = st.number_input("歯周病クイズ問題番号", min_value=1, max_value=2, value=1)
            display_image("quiz_periodontitis", f"question_{quiz_num}", 
                         caption=f"歯周病クイズ問題{quiz_num}", use_column_width=True)
        
        # 選択肢画像テスト
        st.markdown("#### 選択肢画像")
        choice_type = st.radio("選択肢タイプ", ["食べ物", "飲み物"])
        
        if choice_type == "食べ物":
            foods = ["菓子パン", "チョコバナナ", "チーズ", "キシリトール入りガム"]
            food_choice = st.selectbox("食べ物を選択", foods)
            display_image("quiz_caries_food", food_choice.replace('入り', '').replace('ー', '').lower(), 
                         caption=food_choice, use_column_width=True)
        else:
            drinks = ["お茶", "コーラ", "オレンジジュース", "ブラックコーヒー", "牛乳"]
            drink_choice = st.selectbox("飲み物を選択", drinks)
            display_image("quiz_caries_drink", 
                         drink_choice.replace('ジュース', '_juice').replace('コーヒー', '_coffee').lower(), 
                         caption=drink_choice, use_column_width=True)
        
        # 定期検診画像テスト
        st.markdown("#### 定期検診画像")
        checkup_options = ["main_checkup", "examination", "brushing_instruction", 
                          "professional_cleaning", "fluoride_treatment", "checkup_result", "importance"]
        checkup_choice = st.selectbox("定期検診画像を選択", checkup_options)
        display_image("checkup", checkup_choice, caption=f"{checkup_choice}の画像", use_column_width=True)
    
    with tab2:
        create_image_upload_guide()
    
    with tab3:
        st.markdown("### 🔍 ファイル検索テスト")
        st.write("現在アップロードされている画像ファイルを確認できます。")
        
        # 各フォルダの画像ファイル一覧
        import os
        from pathlib import Path
        
        folders = {
            "ボードマス": "assets/images/board",
            "イベント": "assets/images/events", 
            "虫歯クイズ": "assets/images/quiz/caries",
            "食べ物選択肢": "assets/images/quiz/caries/food",
            "飲み物選択肢": "assets/images/quiz/caries/drink",
            "歯周病クイズ": "assets/images/quiz/periodontitis",
            "定期検診": "assets/images/checkup"
        }
        
        for folder_name, folder_path in folders.items():
            st.markdown(f"#### {folder_name}")
            if os.path.exists(folder_path):
                files = []
                for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    files.extend(Path(folder_path).glob(f"*{ext}"))
                
                if files:
                    file_names = [f.name for f in files]
                    st.success(f"📁 {len(file_names)}個のファイル: {', '.join(file_names)}")
                else:
                    st.info("📁 画像ファイルが見つかりません")
            else:
                st.warning(f"📁 フォルダが存在しません: {folder_path}")

if __name__ == "__main__":
    main()
