"""
画像表示ヘルパー関数
"""
import logging
import os
from pathlib import Path

import streamlit as st
from streamlit.errors import StreamlitAPIException

logger = logging.getLogger(__name__)

def get_image_path(category, filename):
    """画像パスを取得"""
    base_path = Path("assets/images")
    
    if category == "board":
        return base_path / "board" / filename
    elif category == "quiz/caries" or category == "quiz_caries":
        return base_path / "quiz" / "caries" / filename
    elif category == "quiz/caries/food" or category == "quiz_caries_food":
        return base_path / "quiz" / "caries" / "food" / filename
    elif category == "quiz/caries/drink" or category == "quiz_caries_drink":
        return base_path / "quiz" / "caries" / "drink" / filename
    elif category == "quiz/periodontitis" or category == "quiz_periodontitis":
        return base_path / "quiz" / "periodontitis" / filename
    elif category == "events":
        return base_path / "events" / filename
    elif category == "checkup":
        return base_path / "checkup" / filename
    elif category == "reception" or category == "intro":
        return base_path / "reception" / filename
    else:
        return base_path / filename

def find_image_file(category, base_filename):
    """複数の拡張子で画像ファイルを検索"""
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    # 拡張子が既についている場合はそのまま使用
    if any(base_filename.lower().endswith(ext) for ext in extensions):
        return get_image_path(category, base_filename)
    
    # 拡張子なしの場合は複数の拡張子で試行
    for ext in extensions:
        image_path = get_image_path(category, base_filename + ext)
        if os.path.exists(image_path):
            return image_path
    
    return None

def display_image(category, filename, caption=None, width=None, fill='stretch', **kwargs):
    """画像を表示する（複数の拡張子に対応）

    fill: 'stretch' の場合はカラム幅いっぱいに表示する。
    追加のキーワード引数は st.image にそのまま渡す。
    """
    image_path = find_image_file(category, filename)

    if image_path and os.path.exists(image_path):
        base_kwargs = dict(kwargs)
        attempts = []

        if width is not None:
            attempts.append({**base_kwargs, 'width': width})
        else:
            normalized_fill = fill.lower() if isinstance(fill, str) else fill
            if isinstance(normalized_fill, str) and normalized_fill == 'stretch':
                # 優先的に width='stretch' を試す
                attempts.append({**base_kwargs, 'width': 'stretch'})
                # 互換性のためのフォールバック候補
                attempts.append({**base_kwargs, 'use_container_width': True})
                attempts.append({**base_kwargs, 'use_column_width': True})
            else:
                attempts.append(base_kwargs)

        last_error = None
        for raw_kwargs in attempts:
            image_kwargs = dict(raw_kwargs)
            # 競合するパラメータを除去
            if 'width' in image_kwargs:
                image_kwargs.pop('use_container_width', None)
                image_kwargs.pop('use_column_width', None)
            if image_kwargs.get('use_container_width') is not None and image_kwargs.get('use_column_width') is not None:
                image_kwargs.pop('use_column_width')
            try:
                st.image(str(image_path), caption=caption, **image_kwargs)
                break
            except (TypeError, StreamlitAPIException) as exc:
                last_error = exc
        else:
            # どの表示方法でも失敗した場合は最後のエラーをログし、最小構成で表示
            if last_error:
                logger.warning("画像表示で互換性の問題が発生しました: %s", last_error)
            st.image(str(image_path), caption=caption)
        return True
    else:
        # 画像が見つからない場合はログのみ出力
        logger.warning("画像が見つかりませんでした: category=%s filename=%s", category, filename)
        return False

def display_image_grid(category, image_list, columns=3, captions=None):
    """画像をグリッド表示する"""
    cols = st.columns(columns)
    
    for i, filename in enumerate(image_list):
        with cols[i % columns]:
            caption = captions[i] if captions and i < len(captions) else None
            display_image(category, filename, caption=caption, fill='stretch')

def display_quiz_option_with_image(category, filename, option_text, key, selected_value=None):
    """クイズ選択肢を画像付きで表示"""
    image_path = get_image_path(category, filename)

    # カラムで画像とボタンを並べる
    col1, col2 = st.columns([1, 2])

    with col1:
        if os.path.exists(image_path):
            display_image(category, filename, fill='stretch')
        else:
            st.info("📷")
    
    with col2:
        # 選択状態に応じてボタンスタイルを変更
        button_type = "primary" if selected_value == option_text else "secondary"
        
        if st.button(option_text, key=key, width='stretch', type=button_type):
            return option_text
    
    return None

def create_image_upload_guide():
    """画像アップロードガイドを表示"""
    st.markdown("""
    ## 📷 画像アップロードガイド
    
    ### 📁 ディレクトリ構造
    
    ```
    assets/images/
    ├── board/              # ボードマス関連の写真
    │   ├── cell_01.jpg     # マス1: スタート
    │   ├── cell_02.jpg     # マス2: 自己紹介
    │   ├── cell_03.jpg     # マス3: ジャンプ
    │   ├── cell_04.jpg     # マス4: 乳歯脱落
    │   ├── cell_05.jpg     # マス5: 定期検診
    │   └── ...
    ├── quiz/
    │   ├── caries/         # 虫歯クイズ
    │   │   ├── main_image.jpg      # 虫歯クイズメイン画像
    │   │   ├── question_1.jpg      # 問題1の説明画像
    │   │   ├── question_2.jpg      # 問題2の説明画像
    │   │   ├── food/       # 食べ物選択肢（JPEG形式）
    │   │   │   ├── bread.jpeg           # 菓子パン
    │   │   │   ├── choco_banana.jpeg    # チョコバナナ
    │   │   │   ├── cheese.jpeg          # チーズ
    │   │   │   └── xylitol_gum.jpeg     # キシリトール入りガム
    │   │   └── drink/      # 飲み物選択肢（JPEG形式）
    │   │       ├── tea.jpeg             # お茶
    │   │       ├── cola.jpeg            # コーラ
    │   │       ├── orange_juice.jpeg    # オレンジジュース
    │   │       ├── black_coffee.jpeg    # ブラックコーヒー
    │   │       └── milk.jpeg            # 牛乳
    │   └── periodontitis/  # 歯周病クイズ
    │       ├── main_image.jpg      # 歯周病クイズメイン画像
    │       ├── question_1.jpg
    │       └── question_2.jpg
    ├── events/             # イベント関連
    │   ├── self_introduction.jpg
    │   ├── jump.jpg
    │   ├── tooth_loss.jpg
    │   └── job_experience.jpg
    └── checkup/            # 定期検診関連
        ├── main_checkup.jpg            # メイン画像
        ├── examination.jpg             # 口の中の検査
        ├── brushing_instruction.jpg    # 歯磨き指導
        ├── professional_cleaning.jpg   # プロフェッショナルクリーニング
        ├── fluoride_treatment.jpg      # 予防処置
        ├── checkup_result.jpg          # 健診結果
        └── importance.jpg              # 定期検診の重要性
    ```
    
    ### 📋 ファイル命名規則
    
    - **ファイル形式**: JPG, JPEG, PNG, GIF, WebP (複数の形式に対応)
    - **ファイル名**: 英数字とアンダースコア、ハイフンのみ
    - **推奨サイズ**: 横800px以下（モバイル対応）
    - **拡張子**: .jpg, .jpeg, .png, .gif, .webp のいずれでもOK
    
    **注意**: 同じファイル名で複数の拡張子がある場合、優先順位は JPG > JPEG > PNG > GIF > WebP
    
    ### 🎯 画像の用途
    
    1. **ボードマス画像** (`board/`): 各マスのイベントを説明する画像
       - 例: `cell_01.png`, `cell_02.jpg` など
    2. **クイズ問題画像** (`quiz/`): 問題の説明や理解を助ける画像
       - 例: `question_1.png`, `question_2.jpg` など
    3. **選択肢画像** (`quiz/*/food/`, `quiz/*/drink/`): 食べ物・飲み物の写真
       - 例: `菓子パン.png`, `コーラ.jpg` など
    4. **イベント画像** (`events/`): 自己紹介、ジャンプなどのイベント説明画像
       - 例: `jump.png`, `job_experience.jpg` など
    
    ### 💡 アップロード例
    
    ```bash
    # PNG形式でアップロード
    cp my_image.png assets/images/board/cell_01.png
    
    # JPG形式でアップロード  
    cp bread_photo.jpg assets/images/quiz/caries/food/菓子パン.jpg
    
    # 拡張子なしのファイル名でも自動検出
    # cell_01.png または cell_01.jpg が自動的に見つかります
    ```
    """)
