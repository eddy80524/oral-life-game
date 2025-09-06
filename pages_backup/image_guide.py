"""
画像アップロードガイドページ
"""
import streamlit as st
import sys
import os

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.image_helper import create_image_upload_guide

st.set_page_config(
    page_title="画像アップロードガイド",
    page_icon="📷",
    layout="wide"
)

def main():
    st.title("📷 画像アップロードガイド")
    
    create_image_upload_guide()
    
    # 現在のディレクトリ構造を表示
    st.markdown("### 📁 現在のディレクトリ構造")
    
    import os
    from pathlib import Path
    
    assets_path = Path("assets/images")
    
    if assets_path.exists():
        st.code(f"""
assets/images/
├── board/ ({len(list((assets_path / 'board').glob('*'))) if (assets_path / 'board').exists() else 0} files)
├── quiz/
│   ├── caries/ ({len(list((assets_path / 'quiz' / 'caries').glob('*.jpg'))) if (assets_path / 'quiz' / 'caries').exists() else 0} files)
│   │   ├── food/ ({len(list((assets_path / 'quiz' / 'caries' / 'food').glob('*'))) if (assets_path / 'quiz' / 'caries' / 'food').exists() else 0} files)
│   │   └── drink/ ({len(list((assets_path / 'quiz' / 'caries' / 'drink').glob('*'))) if (assets_path / 'quiz' / 'caries' / 'drink').exists() else 0} files)
│   └── periodontitis/ ({len(list((assets_path / 'quiz' / 'periodontitis').glob('*'))) if (assets_path / 'quiz' / 'periodontitis').exists() else 0} files)
└── events/ ({len(list((assets_path / 'events').glob('*'))) if (assets_path / 'events').exists() else 0} files)
        """)
    
    # 推奨ファイル名一覧
    st.markdown("### 📝 推奨ファイル名一覧")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **ボードマス画像** (`board/`)
        - `cell_01.jpg` - マス1: 自己紹介
        - `cell_02.jpg` - マス2: ジャンプ
        - `cell_03.jpg` - マス3: 乳歯脱落
        - `cell_04.jpg` - マス4: 定期検診
        - `cell_05.jpg` - マス5: 虫歯クイズ
        - ...続く...
        
        **イベント画像** (`events/`)
        - `self_introduction.jpg` - 自己紹介
        - `jump.jpg` - ジャンプ
        - `tooth_loss.jpg` - 乳歯脱落
        - `job_experience.jpg` - 職業体験
        - `job_医師.jpg` - 歯科医師
        - `job_衛生士.jpg` - 歯科衛生士  
        - `job_技工士.jpg` - 歯科技工士
        """)
    
    with col2:
        st.markdown("""
        **クイズ画像** (`quiz/caries/`)
        - `question_1.jpg` - 虫歯クイズ問題1
        - `question_2.jpg` - 虫歯クイズ問題2
        
        **食べ物画像** (`quiz/caries/food/`)
        - `菓子パン.jpg` - 菓子パン
        - `チョコバナナ.jpg` - チョコバナナ
        - `チーズ.jpg` - チーズ
        - `キシリトール入りガム.jpg` - ガム
        
        **飲み物画像** (`quiz/caries/drink/`)
        - `お茶.jpg` - お茶
        - `コーラ.jpg` - コーラ
        - `オレンジ_juice.jpg` - オレンジジュース
        - `ブラック_coffee.jpg` - ブラックコーヒー
        - `牛乳.jpg` - 牛乳
        
        **歯周病クイズ画像** (`quiz/periodontitis/`)
        - `question_1.jpg` - 歯周病クイズ問題1
        - `question_2.jpg` - 歯周病クイズ問題2
        """)
    
    # アップロード方法
    st.markdown("### 💾 アップロード方法")
    
    st.info("""
    **方法1: ファイルマネージャーを使用**
    1. Finderまたはエクスプローラーで `assets/images/` フォルダを開く
    2. 対応するサブフォルダに画像ファイルをドラッグ&ドロップ
    
    **方法2: ターミナル/コマンドプロンプトを使用**
    ```bash
    # 例: ボードマス画像をアップロード
    cp your_image.jpg assets/images/board/cell_01.jpg
    
    # 例: 食べ物画像をアップロード
    cp bread_image.jpg assets/images/quiz/caries/food/菓子パン.jpg
    ```
    
    **注意事項:**
    - ファイル形式: JPG, PNG, GIF
    - 推奨サイズ: 横800px以下
    - ファイル名は正確に入力してください
    """)
    
    # テスト用画像表示
    st.markdown("### 🔍 画像表示テスト")
    
    if st.button("画像表示をテスト"):
        from services.image_helper import display_image
        
        st.write("**テスト結果:**")
        
        # 各カテゴリの画像をテスト表示
        test_images = [
            ("board", "cell_01.jpg", "マス1画像"),
            ("events", "self_introduction.jpg", "自己紹介画像"),
            ("quiz_caries", "question_1.jpg", "虫歯クイズ問題1"),
            ("quiz_caries_food", "菓子パン.jpg", "菓子パン画像"),
            ("quiz_caries_drink", "コーラ.jpg", "コーラ画像")
        ]
        
        cols = st.columns(len(test_images))
        for i, (category, filename, caption) in enumerate(test_images):
            with cols[i]:
                success = display_image(category, filename, caption=caption)
                if success:
                    st.success("✅ 表示成功")
                else:
                    st.warning("⚠️ 画像なし")

if __name__ == "__main__":
    main()
