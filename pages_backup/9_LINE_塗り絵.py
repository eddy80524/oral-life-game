"""
LINE・塗り絵ページ - お口の人生ゲーム
"""
import streamlit as st
import sys
import os
import json
import random

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.store import save_game_state

# ページ設定
st.set_page_config(
    page_title="LINE・塗り絵 - お口の人生ゲーム",
    page_icon="🎨",
    layout="wide"
)

def load_coloring_data():
    """塗り絵データを読み込み"""
    try:
        with open('data/coloring_pages.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # デフォルトの塗り絵データ
        return {
            "pages": [
                {
                    "id": 1,
                    "title": "歯磨きをする子ども",
                    "description": "正しい歯磨きをしている子どもの絵です",
                    "age_group": "all",
                    "difficulty": "easy",
                    "download_url": "/assets/coloring/tooth_brushing.pdf",
                    "thumbnail": "/assets/images/coloring_thumb1.png"
                },
                {
                    "id": 2,
                    "title": "健康な歯の構造",
                    "description": "歯の構造を学べる塗り絵です",
                    "age_group": "5plus",
                    "difficulty": "medium",
                    "download_url": "/assets/coloring/tooth_structure.pdf",
                    "thumbnail": "/assets/images/coloring_thumb2.png"
                },
                {
                    "id": 3,
                    "title": "歯科医院での検診",
                    "description": "歯科医院での検診の様子です",
                    "age_group": "all",
                    "difficulty": "easy",
                    "download_url": "/assets/coloring/dental_checkup.pdf",
                    "thumbnail": "/assets/images/coloring_thumb3.png"
                }
            ],
            "crossword": {
                "title": "お口の健康クロスワード",
                "description": "歯や口に関する言葉のクロスワードパズル",
                "age_group": "9plus",
                "download_url": "/assets/crossword/oral_health_crossword.pdf",
                "thumbnail": "/assets/images/crossword_thumb.png"
            },
            "mini_quiz": [
                {
                    "question": "1日に何回歯を磨くのが理想的でしょう？",
                    "options": ["1回", "2回", "3回", "4回"],
                    "correct": 2,
                    "explanation": "朝・昼・夜の3回磨くのが理想的です！"
                },
                {
                    "question": "歯磨きは何分くらいするのが良いでしょう？",
                    "options": ["30秒", "1分", "3分", "10分"],
                    "correct": 2,
                    "explanation": "3分程度しっかりと磨きましょう！"
                }
            ]
        }

def get_line_info():
    """LINE公式アカウント情報"""
    return {
        "account_name": "お口の健康サポート",
        "qr_code_url": "/assets/images/line_qr_placeholder.png",
        "official_url": "https://line.me/R/ti/p/@oral-health-support",
        "features": [
            "定期的な歯磨きリマインダー",
            "月齢に応じた口腔ケアアドバイス",
            "歯科健診の予約サポート",
            "歯の健康に関するQ&A",
            "お得な歯科グッズ情報"
        ]
    }

def mini_quiz_challenge():
    """ミニクイズチャレンジ"""
    coloring_data = load_coloring_data()
    quiz_data = coloring_data['mini_quiz']
    
    if 'mini_quiz_state' not in st.session_state:
        st.session_state.mini_quiz_state = {
            'current_question': 0,
            'correct_answers': 0,
            'completed': False,
            'unlocked': False
        }
    
    quiz_state = st.session_state.mini_quiz_state
    
    if quiz_state['completed'] and quiz_state['unlocked']:
        return True
    
    if quiz_state['completed']:
        if quiz_state['correct_answers'] >= 1:
            st.success("🎉 ミニクイズクリア！塗り絵をダウンロードできます！")
            quiz_state['unlocked'] = True
            return True
        else:
            st.warning("もう少し頑張りましょう。1問以上正解で塗り絵が解放されます。")
            if st.button("🔄 もう一度挑戦", use_container_width=True):
                quiz_state['current_question'] = 0
                quiz_state['correct_answers'] = 0
                quiz_state['completed'] = False
                st.rerun()
            return False
    
    # クイズ進行中
    if quiz_state['current_question'] < len(quiz_data):
        question = quiz_data[quiz_state['current_question']]
        
        st.markdown(f"### 問題 {quiz_state['current_question'] + 1}")
        st.markdown(f"**{question['question']}**")
        
        selected = st.radio(
            "選択してください：",
            options=range(len(question['options'])),
            format_func=lambda x: f"{chr(65 + x)}. {question['options'][x]}",
            key=f"mini_quiz_{quiz_state['current_question']}"
        )
        
        if st.button("回答する", use_container_width=True, type="primary"):
            if selected == question['correct']:
                st.success("✅ 正解！")
                quiz_state['correct_answers'] += 1
            else:
                st.error("❌ 不正解")
            
            st.info(f"**解説:** {question['explanation']}")
            quiz_state['current_question'] += 1
            
            if quiz_state['current_question'] >= len(quiz_data):
                quiz_state['completed'] = True
            
            st.rerun()
    
    return False

def main():
    st.title("🎨 LINE・塗り絵")
    
    # タブで機能を分割
    tab1, tab2, tab3 = st.tabs(["📱 LINE公式アカウント", "🎨 塗り絵ダウンロード", "🧩 クロスワード"])
    
    with tab1:
        line_info = get_line_info()
        
        st.markdown("### 📱 LINE公式アカウントのご案内")
        
        line_col1, line_col2 = st.columns([1, 2])
        
        with line_col1:
            # LINE QRコード表示（プレースホルダ）
            st.markdown("**QRコードでお友達追加:**")
            
            # QRコード画像のプレースホルダ
            st.markdown("""
            <div style="border: 2px dashed #ccc; padding: 50px; text-align: center; margin: 10px 0;">
                <h3>📱 LINE QRコード</h3>
                <p>（実際のQRコード画像）</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 直接リンク
            st.markdown(f"[🔗 直接LINEで開く]({line_info['official_url']})")
        
        with line_col2:
            st.markdown(f"### 🌟 {line_info['account_name']}")
            st.markdown("**LINEで受け取れるサービス:**")
            
            for feature in line_info['features']:
                st.markdown(f"✅ {feature}")
            
            st.markdown("""
            **特典:**
            - お友達登録で歯磨きカレンダーをプレゼント！
            - 定期健診の予約が簡単にできます
            - 歯の健康に関する情報を定期配信
            """)
        
        # お友達追加ボタン
        if st.button("🎁 今すぐお友達追加", use_container_width=True, type="primary"):
            st.success("LINEアプリが開きます！（実際の運用時）")
            st.balloons()
    
    with tab2:
        st.markdown("### 🎨 塗り絵ダウンロード")
        
        # ミニクイズチャレンジ
        st.markdown("#### 🧠 塗り絵解放チャレンジ")
        st.info("ミニクイズに1問以上正解すると、塗り絵をダウンロードできます！")
        
        quiz_unlocked = mini_quiz_challenge()
        
        if quiz_unlocked:
            coloring_data = load_coloring_data()
            
            st.markdown("### 🎉 塗り絵ダウンロード解放！")
            
            participant_age = st.session_state.get('participant_age', 5)
            
            # 年齢に応じた塗り絵を表示
            available_pages = []
            for page in coloring_data['pages']:
                if page['age_group'] == 'all':
                    available_pages.append(page)
                elif page['age_group'] == '5plus' and participant_age >= 5:
                    available_pages.append(page)
                elif page['age_group'] == 'under5' and participant_age < 5:
                    available_pages.append(page)
            
            if available_pages:
                for page in available_pages:
                    with st.container():
                        page_col1, page_col2 = st.columns([1, 2])
                        
                        with page_col1:
                            # サムネイル表示（プレースホルダ）
                            st.markdown(f"""
                            <div style="border: 1px solid #ddd; padding: 20px; text-align: center; border-radius: 5px;">
                                <h4>{page['title']}</h4>
                                <p>（サムネイル画像）</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with page_col2:
                            st.markdown(f"**{page['title']}**")
                            st.markdown(f"説明: {page['description']}")
                            st.markdown(f"難易度: {page['difficulty']}")
                            
                            if st.button(f"📥 {page['title']}をダウンロード", key=f"download_{page['id']}", use_container_width=True):
                                st.success(f"'{page['title']}'をダウンロードしました！")
                                st.info("💡 実際の運用では、PDF形式でダウンロードされます")
                        
                        st.markdown("---")
            else:
                st.info("お客様の年齢に適した塗り絵がありません。")
        else:
            # ロックされた塗り絵の表示
            st.markdown("### 🔒 塗り絵（ロック中）")
            st.warning("上記のミニクイズに正解すると、塗り絵をダウンロードできます！")
            
            # プレビュー表示
            coloring_data = load_coloring_data()
            for page in coloring_data['pages'][:2]:  # 最初の2つを表示
                st.markdown(f"🔒 **{page['title']}** - {page['description']}")
    
    with tab3:
        st.markdown("### 🧩 クロスワードパズル")
        
        participant_age = st.session_state.get('participant_age', 5)
        coloring_data = load_coloring_data()
        crossword = coloring_data['crossword']
        
        if participant_age >= 9:  # 9歳以上
            st.markdown(f"### {crossword['title']}")
            st.markdown(f"**説明:** {crossword['description']}")
            
            # クロスワード画像表示（プレースホルダ）
            st.markdown("""
            <div style="border: 2px solid #4CAF50; padding: 30px; text-align: center; margin: 20px 0; border-radius: 10px;">
                <h3>🧩 クロスワードパズル</h3>
                <p>歯や口の健康に関する言葉を探してみよう！</p>
                <p>（実際のクロスワード画像）</p>
            </div>
            """, unsafe_allow_html=True)
            
            # ヒント表示
            with st.expander("💡 ヒント"):
                st.markdown("""
                **タテのカギ:**
                1. 口の中にある白いもの（2文字）
                2. 虫歯を防ぐために毎日すること（4文字）
                
                **ヨコのカギ:**
                1. 歯を支えているピンク色の部分（3文字）
                2. 甘いものを食べすぎるとできる（2文字）
                """)
            
            if st.button("📥 クロスワードをダウンロード", use_container_width=True, type="primary"):
                st.success("クロスワードパズルをダウンロードしました！")
                st.info("💡 実際の運用では、PDF形式でダウンロードされます")
                st.balloons()
        else:
            st.info("🧩 クロスワードパズルは9歳以上の方が対象です。")
            st.markdown("代わりに、塗り絵をお楽しみください！")
    
    # 家庭での継続学習案内
    st.markdown("### 🏠 家庭での継続学習")
    
    home_col1, home_col2 = st.columns(2)
    
    with home_col1:
        st.markdown("**今日から始めよう:**")
        st.markdown("""
        ✅ 毎日3回の歯磨き
        ✅ フロスの使用
        ✅ 甘いものは控えめに
        ✅ 定期的な歯科健診
        """)
    
    with home_col2:
        st.markdown("**継続学習ツール:**")
        st.markdown("""
        🎨 ダウンロードした塗り絵
        🧩 クロスワードパズル
        📱 LINE公式アカウント
        📚 歯の健康に関する本
        """)
    
    # ナビゲーション
    st.markdown("### 🧭 次のアクション")
    
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        if st.button("🏁 ランキングを見る", use_container_width=True):
            st.switch_page("pages/7_ゴール_ランキング.py")
    
    with nav_col2:
        if st.button("🏠 最初から始める", use_container_width=True):
            # ゲーム状態をリセット
            for key in list(st.session_state.keys()):
                if any(prefix in key for prefix in ['game_state', 'quiz_state', 'job_experience', 'checkup', 'goal', 'mini_quiz']):
                    del st.session_state[key]
            st.switch_page("pages/0_受付_プロローグ.py")
    
    with nav_col3:
        if st.button("⚙️ スタッフ管理", use_container_width=True):
            st.switch_page("pages/8_スタッフ管理.py")
    
    # 進行状況表示（サイドバー）
    st.sidebar.markdown("### 🎨 アクティビティ")
    if 'mini_quiz_state' in st.session_state:
        quiz_state = st.session_state.mini_quiz_state
        if quiz_state.get('unlocked', False):
            st.sidebar.success("✅ 塗り絵解放済み")
        else:
            st.sidebar.info("🔒 塗り絵ロック中")
    
    if 'game_state' in st.session_state:
        game_state = st.session_state.game_state
        st.sidebar.metric("最終歯数", f"{game_state['teeth_count']}本")
        st.sidebar.metric("最終コイン", f"{game_state['tooth_coins']}枚")

if __name__ == "__main__":
    main()
