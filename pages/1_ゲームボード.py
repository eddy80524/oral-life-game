"""
ゲームボードページ - お口の人生ゲーム
新しい仕様に基づいた完全版
"""
import streamlit as st
import sys
import os
import json
import random
import time
from datetime import datetime

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.game_logic import (
    initialize_game_state, 
    move_player, 
    handle_cell_action,
    is_game_finished,
    calculate_play_time
)
from services.store import save_game_state, load_game_state
from services.audio import show_audio_controls
from services.image_helper import display_image, display_quiz_option_with_image, display_image_grid

# ページ設定
st.set_page_config(
    page_title="ゲームボード - お口の人生ゲーム",
    page_icon="🎲",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
    .game-board {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 8px;
        margin: 20px 0;
        padding: 10px;
        background-color: #f0f8ff;
        border-radius: 15px;
    }
    
    .cell {
        border: 3px solid #ddd;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        background-color: white;
        transition: all 0.3s ease;
    }
    
    .cell:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .player-position {
        background: linear-gradient(135deg, #ff6b6b, #ff8e8e) !important;
        border-color: #ff5252 !important;
        color: white !important;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 107, 107, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
    }
    
    .start-cell {
        background: linear-gradient(135deg, #4caf50, #66bb6a);
        color: white;
        font-weight: bold;
    }
    
    .goal-cell {
        background: linear-gradient(135deg, #2196f3, #42a5f5);
        color: white;
        font-weight: bold;
    }
    
    .stop-cell {
        background: linear-gradient(135deg, #ff9800, #ffb74d);
        color: white;
        font-weight: bold;
    }
    
    .quiz-cell {
        background: linear-gradient(135deg, #9c27b0, #ba68c8);
        color: white;
        font-weight: bold;
    }
    
    .branch-fail-cell {
        background: linear-gradient(135deg, #f44336, #e57373);
        color: white;
    }
    
    .branch-pass-cell {
        background: linear-gradient(135deg, #4caf50, #81c784);
        color: white;
    }
    
    .dice-container {
        text-align: center;
        margin: 20px 0;
        padding: 20px;
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-radius: 20px;
    }
    
    .dice {
        font-size: 5rem;
        margin: 15px;
        animation: roll 0.5s ease-in-out;
    }
    
    @keyframes roll {
        0% { transform: rotate(0deg); }
        50% { transform: rotate(180deg); }
        100% { transform: rotate(360deg); }
    }
    
    .player-info {
        background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 5px solid #2196f3;
    }
    
    .status-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 2px;
    }
    
    .teeth-count {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        color: #e65100;
    }
    
    .tooth-count {
        background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
        color: #2e7d32;
    }
    
    .quiz-option {
        background: white;
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .quiz-option:hover {
        border-color: #2196f3;
        background-color: #e3f2fd;
    }
    
    .quiz-option.selected {
        border-color: #2196f3;
        background-color: #2196f3;
        color: white;
    }
    
    .combination-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def load_board_data():
    """年齢に応じたボードデータを読み込み"""
    if 'participant_age' not in st.session_state:
        st.error("参加者情報が見つかりません。受付ページからやり直してください。")
        st.switch_page("pages/0_受付_プロローグ.py")
        return None
    
    age = st.session_state.participant_age
    
    # 年齢に応じてボードファイルを選択
    if age < 5:
        board_file = "data/board_main_under5.json"
    else:
        board_file = "data/board_main_5plus.json"  # 新しいボードファイルを使用
    
    try:
        with open(board_file, 'r', encoding='utf-8') as f:
            board_cells = json.load(f)
            return board_cells
    except FileNotFoundError:
        st.error(f"ボードデータファイル '{board_file}' が見つかりません。")
        return None

def get_cell_css_class(cell, current_position, cell_index):
    """セルのCSSクラスを決定"""
    base_class = "cell"
    
    if cell_index == current_position:
        return base_class + " player-position"
    
    cell_type = cell.get('type', 'event')
    
    if cell_type == 'start':
        return base_class + " start-cell"
    elif cell_type == 'goal':
        return base_class + " goal-cell"
    elif cell_type == 'stop':
        return base_class + " stop-cell"
    elif cell_type == 'quiz':
        return base_class + " quiz-cell"
    elif cell_type == 'branch_fail':
        return base_class + " branch-fail-cell"
    elif cell_type == 'branch_pass':
        return base_class + " branch-pass-cell"
    else:
        return base_class

def display_board(board_data, current_position):
    """ゲームボードを表示"""
    if not board_data:
        st.error("ボードデータが正しく読み込まれませんでした。")
        return
    
    total_cells = len(board_data)
    
    st.markdown("### 🎲 お口の人生ゲーム ボード")
    
    # ボードをHTMLで表示
    board_html = '<div class="game-board">'
    
    for i, cell in enumerate(board_data):
        cell_class = get_cell_css_class(cell, current_position, i)
        cell_content = f"<div style='font-weight: bold;'>{i+1}</div><div style='font-size: 0.7rem;'>{cell.get('title', f'マス{i+1}')}</div>"
        board_html += f'<div class="{cell_class}">{cell_content}</div>'
    
    board_html += '</div>'
    st.markdown(board_html, unsafe_allow_html=True)

def initialize_new_game_state():
    """新しいゲーム状態を初期化"""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'current_position': 0,
            'teeth_count': 20,  # 初期歯数
            'tooth_count': 10,  # 初期トゥース
            'turn_count': 0,
            'start_time': datetime.now(),
            'quiz_results': {},
            'branch_path': None,
            'actions_taken': [],
            'just_moved': False,  # 今移動したばかりかどうかのフラグ
            'pending_event': None  # 処理待ちのイベント
        }

def handle_self_introduction():
    """自己紹介イベント"""
    st.markdown("### 🗣️ 自己紹介をしよう！")
    st.write("初めて言葉を話せるようになったね！")
    
    # イベント画像を表示
    display_image("events", "self_introduction", caption="自己紹介の時間です", use_column_width=True)
    
    with st.form("self_introduction"):
        st.write("**名前と好きなものを教えてね**")
        name_input = st.text_input("あなたの名前は？", value=st.session_state.get('participant_name', ''))
        favorite_input = st.text_input("好きなものは何？")
        
        if st.form_submit_button("自己紹介完了！"):
            if name_input and favorite_input:
                st.success(f"よろしくね、{name_input}さん！{favorite_input}が好きなんだね！")
                st.session_state.game_state['actions_taken'].append({
                    'action': 'self_introduction',
                    'name': name_input,
                    'favorite': favorite_input
                })
                st.session_state.game_state['just_moved'] = False  # イベント完了後フラグをリセット
                return True
            else:
                st.warning("名前と好きなものを両方教えてね！")
    return False

def handle_jump_exercise():
    """ジャンプ運動イベント"""
    st.markdown("### 🤸 ジャンプしよう！")
    st.write("ジャンプができるようになったね！")
    
    # イベント画像を表示
    display_image("events", "jump", caption="みんなでジャンプ！", use_column_width=True)
    
    if st.button("その場で3回ジャンプ！", use_container_width=True):
        with st.spinner("ジャンプ中..."):
            import time
            for i in range(3):
                st.write(f"ジャンプ {i+1} 回目！")
                time.sleep(1)
        st.success("上手にジャンプできたね！")
        st.balloons()
        st.session_state.game_state['actions_taken'].append({'action': 'jump_exercise'})
        st.session_state.game_state['just_moved'] = False  # イベント完了後フラグをリセット
        return True
    return False

def handle_tooth_loss_story():
    """乳歯脱落イベント"""
    st.markdown("### 🦷 初めて乳歯が抜けた！")
    st.write("抜けた歯はどうしたかな？")
    
    # イベント画像を表示
    display_image("events", "tooth_loss", caption="初めて歯が抜けた思い出", use_column_width=True)
    
    options = ["枕の下に置いた", "歯の妖精にあげた", "大切に保管した", "屋根に投げた"]
    choice = st.radio("抜けた歯をどうした？", options)
    
    if st.button("決定", use_container_width=True):
        st.success(f"「{choice}」んだね！いい思い出だね！")
        st.session_state.game_state['actions_taken'].append({
            'action': 'tooth_loss_story',
            'choice': choice
        })
        st.session_state.game_state['just_moved'] = False  # イベント完了後フラグをリセット
        return True
    return False

def handle_caries_quiz():
    """虫歯クイズの処理"""
    st.markdown("### 🦷 虫歯クイズ")
    st.write("成長して全部大人の歯に生え変わった！虫歯について学ぼう！")
    
    # クイズデータを読み込み
    try:
        with open('data/quizzes.json', 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
        caries_quiz = quiz_data['sets']['kids']['caries']
    except:
        st.error("クイズデータの読み込みに失敗しました。")
        return False
    
    if 'caries_quiz_state' not in st.session_state:
        st.session_state.caries_quiz_state = {
            'current_question': 0,
            'answers': [],
            'completed': False
        }
    
    quiz_state = st.session_state.caries_quiz_state
    
    if quiz_state['current_question'] < len(caries_quiz):
        question = caries_quiz[quiz_state['current_question']]
        
        st.write(f"**問題 {quiz_state['current_question'] + 1}/{len(caries_quiz)}**")
        st.write(question['text'])
        
        # 問題画像を表示
        display_image("quiz_caries", f"question_{quiz_state['current_question'] + 1}", 
                     caption=f"問題{quiz_state['current_question'] + 1}の説明", use_column_width=True)
        
        if question['type'] == 'single':
            # 単一選択問題
            answer = st.radio("答えを選んでね", question['choices'], key=f"q{quiz_state['current_question']}")
            
            if st.button("回答", use_container_width=True):
                correct = question['choices'].index(answer) == question['answer']
                quiz_state['answers'].append({
                    'question_id': question['id'],
                    'answer': answer,
                    'correct': correct
                })
                
                if correct:
                    st.success("正解！" + question['explain'])
                else:
                    st.error(f"残念！正解は「{question['choices'][question['answer']]}」でした。")
                    st.info(question['explain'])
                
                quiz_state['current_question'] += 1
                time.sleep(2)
                st.rerun()
                
        elif question['type'] == 'combination':
            # 組み合わせ問題
            
            # セッション状態で選択を管理
            if 'selected_food' not in st.session_state:
                st.session_state.selected_food = None
            if 'selected_drink' not in st.session_state:
                st.session_state.selected_drink = None
            
            st.write("**食べ物を選んでね**")
            food_cols = st.columns(len(question['food_choices']))
            
            for i, food in enumerate(question['food_choices']):
                with food_cols[i]:
                    # 食べ物の画像を表示
                    display_image("quiz_caries_food", food['name'].replace('入り', '').replace('ー', '').lower(), 
                                 caption=food['name'], use_column_width=True)
                    
                    # 選択状態に応じてボタンの見た目を変更
                    button_type = "primary" if st.session_state.selected_food == food['name'] else "secondary"
                    if st.button(food['name'], key=f"food_{i}", use_container_width=True, type=button_type):
                        st.session_state.selected_food = food['name']
            
            st.write("**飲み物を選んでね**")
            drink_cols = st.columns(len(question['drink_choices']))
            
            for i, drink in enumerate(question['drink_choices']):
                with drink_cols[i]:
                    # 飲み物の画像を表示
                    display_image("quiz_caries_drink", drink['name'].replace('ジュース', '_juice').replace('コーヒー', '_coffee').lower(), 
                                 caption=drink['name'], use_column_width=True)
                    
                    # 選択状態に応じてボタンの見た目を変更
                    button_type = "primary" if st.session_state.selected_drink == drink['name'] else "secondary"
                    if st.button(drink['name'], key=f"drink_{i}", use_container_width=True, type=button_type):
                        st.session_state.selected_drink = drink['name']
            
            if st.session_state.selected_food and st.session_state.selected_drink:
                st.write(f"**選択した組み合わせ:** {st.session_state.selected_food} + {st.session_state.selected_drink}")
                
                if st.button("この組み合わせで回答", use_container_width=True):
                    correct_food = st.session_state.selected_food in question['correct_combination']['food']
                    correct_drink = st.session_state.selected_drink in question['correct_combination']['drink']
                    correct = correct_food and correct_drink
                    
                    quiz_state['answers'].append({
                        'question_id': question['id'],
                        'food': st.session_state.selected_food,
                        'drink': st.session_state.selected_drink,
                        'correct': correct
                    })
                    
                    if correct:
                        st.success("正解！虫歯になりやすい組み合わせです。")
                    else:
                        st.error("違います。この組み合わせは虫歯になりにくいです。")
                    
                    st.info(question['explain'])
                    quiz_state['current_question'] += 1
                    
                    # 選択をリセット
                    st.session_state.selected_food = None
                    st.session_state.selected_drink = None
                    
                    time.sleep(2)
                    st.rerun()
    
    else:
        # クイズ完了
        if not quiz_state['completed']:
            correct_count = sum(1 for answer in quiz_state['answers'] if answer['correct'])
            
            st.markdown("### 🎉 クイズ完了！")
            st.write(f"正解数: {correct_count}/{len(caries_quiz)}")
            
            # 分岐判定
            if correct_count >= 1:  # 1問以上正解
                st.success("よくできました！虫歯予防の知識があるね！")
                st.session_state.game_state['branch_path'] = 'caries_pass'
            else:  # 全問不正解
                st.warning("虫歯について、もう少し勉強しようね。")
                st.session_state.game_state['branch_path'] = 'caries_fail'
            
            quiz_state['completed'] = True
            st.session_state.game_state['quiz_results']['caries'] = {
                'score': correct_count,
                'total': len(caries_quiz),
                'passed': correct_count >= 1
            }
            st.session_state.game_state['just_moved'] = False  # イベント完了後フラグをリセット
            
            return True
    
    return False

def handle_periodontitis_quiz():
    """歯周病クイズの処理"""
    st.markdown("### 🦷 歯周病クイズ")
    
    # 歯周病クイズのロジック（虫歯クイズと同様）
    try:
        with open('data/quizzes.json', 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
        perio_quiz = quiz_data['sets']['kids']['perio']
    except:
        st.error("クイズデータの読み込みに失敗しました。")
        return False
    
    if 'perio_quiz_state' not in st.session_state:
        st.session_state.perio_quiz_state = {
            'current_question': 0,
            'answers': [],
            'completed': False
        }
    
    quiz_state = st.session_state.perio_quiz_state
    
    if quiz_state['current_question'] < len(perio_quiz):
        question = perio_quiz[quiz_state['current_question']]
        
        st.write(f"**問題 {quiz_state['current_question'] + 1}/{len(perio_quiz)}**")
        st.write(question['text'])
        
        # 問題画像を表示
        display_image("quiz_periodontitis", f"question_{quiz_state['current_question'] + 1}", 
                     caption=f"歯周病クイズ {quiz_state['current_question'] + 1}", use_column_width=True)
        
        answer = st.radio("答えを選んでね", question['choices'], key=f"perio_q{quiz_state['current_question']}")
        
        if st.button("回答", use_container_width=True, key=f"perio_submit_{quiz_state['current_question']}"):
            correct = question['choices'].index(answer) == question['answer']
            quiz_state['answers'].append({
                'question_id': question['id'],
                'answer': answer,
                'correct': correct
            })
            
            if correct:
                st.success("正解！" + question['explain'])
            else:
                st.error(f"残念！正解は「{question['choices'][question['answer']]}」でした。")
                st.info(question['explain'])
            
            quiz_state['current_question'] += 1
            time.sleep(2)
            st.rerun()
    
    else:
        # クイズ完了
        if not quiz_state['completed']:
            correct_count = sum(1 for answer in quiz_state['answers'] if answer['correct'])
            
            st.markdown("### 🎉 歯周病クイズ完了！")
            st.write(f"正解数: {correct_count}/{len(perio_quiz)}")
            
            # 分岐判定
            if correct_count >= 1:  # 1問以上正解
                st.success("よくできました！歯周病予防の知識があるね！")
                st.session_state.game_state['branch_path'] = 'perio_pass'
            else:  # 全問不正解
                st.warning("歯周病について、もう少し勉強しようね。")
                st.session_state.game_state['branch_path'] = 'perio_fail'
            
            quiz_state['completed'] = True
            st.session_state.game_state['quiz_results']['periodontitis'] = {
                'score': correct_count,
                'total': len(perio_quiz),
                'passed': correct_count >= 1
            }
            st.session_state.game_state['just_moved'] = False  # イベント完了後フラグをリセット
            
            return True
    
    return False

def handle_dice_tooth_loss():
    """サイコロによる歯の脱落処理"""
    st.markdown("### 🎲 歯がぐらぐら...")
    st.write("大人の歯がぐらぐらしてきて、歯を抜かないといけなくなった！")
    st.write("サイコロを振って、出た目の数だけ歯を失います。")
    
    if st.button("サイコロを振る", use_container_width=True):
        dice_result = random.randint(1, 6)
        st.session_state.last_dice_result = dice_result
        
        # 歯を失う
        st.session_state.game_state['teeth_count'] -= dice_result
        # サイコロの出た目×2トゥースを払う
        tooth_cost = dice_result * 2
        st.session_state.game_state['tooth_count'] -= tooth_cost
        
        st.error(f"🎲 サイコロの目: {dice_result}")
        st.error(f"歯を{dice_result}本失いました...")
        st.error(f"治療費として{tooth_cost}トゥースを支払いました...")
        
        st.session_state.game_state['actions_taken'].append({
            'action': 'dice_tooth_loss',
            'dice_result': dice_result,
            'teeth_lost': dice_result,
            'tooth_cost': tooth_cost
        })
        st.session_state.game_state['just_moved'] = False  # イベント完了後フラグをリセット
        
        return True
    
    if hasattr(st.session_state, 'last_dice_result'):
        st.write(f"前回のサイコロ: {st.session_state.last_dice_result}")
        return True
    
    return False

def handle_job_experience():
    """職業体験処理"""
    st.markdown("### 👨‍⚕️ お仕事体験")
    st.write("歯科に関する職業を体験しよう！")
    
    # 職業体験の画像を表示
    display_image("events", "job_experience", caption="歯科のお仕事体験", use_column_width=True)
    
    jobs = [
        {"id": 1, "name": "歯科医師", "description": "歯の治療をする医師", "emoji": "👨‍⚕️"},
        {"id": 2, "name": "歯科衛生士", "description": "お口の中をきれいにする専門家", "emoji": "👩‍⚕️"},
        {"id": 3, "name": "歯科技工士", "description": "入れ歯や被せ物を作る職人", "emoji": "👨‍🔬"}
    ]
    
    st.write("どの職業を体験したい？")
    
    cols = st.columns(3)
    for i, job in enumerate(jobs):
        with cols[i]:
            # 各職業の画像を表示（もしあれば）
            display_image("events", f"job_{job['name'].replace('歯科', '').lower()}", 
                         caption=job['name'], use_column_width=True)
            
            if st.button(f"{job['emoji']} {job['name']}", use_container_width=True, key=f"job_{job['id']}"):
                st.success(f"{job['name']}の体験をしました！")
                st.write(job['description'])
                st.balloons()
                
                # 5トゥースもらう
                st.session_state.game_state['tooth_count'] += 5
                st.success("職業体験で5トゥースもらいました！")
                
                st.session_state.game_state['actions_taken'].append({
                    'action': 'job_experience',
                    'job': job['name'],
                    'reward': 5
                })
                st.session_state.game_state['just_moved'] = False  # イベント完了後フラグをリセット
                
                return True
    
    return False

def handle_cell_event(cell):
    """セルイベントの処理"""
    action = cell.get('action')
    
    if action == 'self_introduction':
        return handle_self_introduction()
    elif action == 'jump_exercise':
        return handle_jump_exercise()
    elif action == 'tooth_loss_story':
        return handle_tooth_loss_story()
    elif action == 'dice_tooth_loss':
        return handle_dice_tooth_loss()
    elif cell.get('type') == 'quiz':
        if cell.get('quiz_type') == 'caries':
            return handle_caries_quiz()
        elif cell.get('quiz_type') == 'periodontitis':
            return handle_periodontitis_quiz()
    elif cell.get('type') == 'job_experience':
        return handle_job_experience()
    
    return True  # その他のイベントは自動完了

def apply_cell_effects(cell):
    """セルの効果を適用"""
    game_state = st.session_state.game_state
    
    # トゥース変化
    if 'tooth_delta' in cell:
        game_state['tooth_count'] += cell['tooth_delta']
        if cell['tooth_delta'] > 0:
            st.success(f"🪙 {cell['tooth_delta']}トゥースを獲得しました！")
        else:
            st.warning(f"🪙 {abs(cell['tooth_delta'])}トゥースを支払いました...")
    
    # 歯数変化
    if 'teeth_delta' in cell:
        game_state['teeth_count'] += cell['teeth_delta']
        if cell['teeth_delta'] > 0:
            st.success(f"🦷 歯が{cell['teeth_delta']}本増えました！")
        else:
            st.error(f"🦷 歯を{abs(cell['teeth_delta'])}本失いました...")
    
    # 位置変化
    if 'step_delta' in cell:
        new_position = max(0, game_state['current_position'] + cell['step_delta'])
        game_state['current_position'] = new_position
        if cell['step_delta'] > 0:
            st.info(f"📍 {cell['step_delta']}マス進みました！")
        else:
            st.warning(f"📍 {abs(cell['step_delta'])}マス戻りました...")

def get_next_position(current_position, board_data, dice_result):
    """次の位置を計算（分岐を考慮）"""
    base_next = min(current_position + dice_result, len(board_data) - 1)
    
    # 分岐判定
    branch_path = st.session_state.game_state.get('branch_path')
    
    if branch_path and current_position < len(board_data):
        current_cell = board_data[current_position]
        
        # クイズセルの場合、結果に応じて分岐
        if current_cell.get('type') == 'quiz':
            if branch_path == 'caries_fail':
                return current_cell.get('branch_fail', base_next)
            elif branch_path == 'caries_pass':
                return current_cell.get('branch_pass', base_next)
            elif branch_path == 'perio_fail':
                return current_cell.get('branch_fail', base_next)
            elif branch_path == 'perio_pass':
                return current_cell.get('branch_pass', base_next)
    
    return base_next

def roll_dice():
    """サイコロを振る"""
    return random.randint(1, 6)

def main():
    st.title("🎲 お口の人生ゲーム - ゲームボード")
    
    # ゲーム状態の初期化
    initialize_new_game_state()
    
    # ボードデータの読み込み
    board_data = load_board_data()
    if not board_data:
        return
    
    # 現在の状態を表示
    game_state = st.session_state.game_state
    
    # プレイヤー情報表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="player-info">
            <h4>👤 プレイヤー情報</h4>
            <p><strong>名前:</strong> {st.session_state.get('participant_name', '未設定')}</p>
            <p><strong>年齢:</strong> {st.session_state.get('participant_age', '未設定')}歳</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="player-info">
            <h4>🎯 ゲーム状況</h4>
            <p><strong>現在位置:</strong> {game_state['current_position'] + 1}マス目</p>
            <p><strong>ターン数:</strong> {game_state['turn_count']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        play_time = calculate_play_time(game_state['start_time'])
        st.markdown(f"""
        <div class="player-info">
            <h4>⏰ ステータス</h4>
            <p><span class="status-badge teeth-count">🦷 {game_state['teeth_count']}本</span></p>
            <p><span class="status-badge tooth-count">🪙 {game_state['tooth_count']}トゥース</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    # ボード表示
    display_board(board_data, game_state['current_position'])
    
    # ゲーム終了チェック
    if game_state['current_position'] >= len(board_data) - 1:
        st.success("🎉 ゲームクリア！おめでとうございます！")
        
        # 結果表示
        st.markdown("### 📊 最終結果")
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            st.metric("残った歯", f"{game_state['teeth_count']}本")
            st.metric("残ったトゥース", f"{game_state['tooth_count']}トゥース")
        
        with result_col2:
            st.metric("総ターン数", game_state['turn_count'])
            st.metric("プレイ時間", play_time)
        
        if st.button("🏠 最初に戻る", use_container_width=True):
            # ゲーム状態をリセット
            for key in ['game_state', 'caries_quiz_state', 'perio_quiz_state']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("pages/0_受付_プロローグ.py")
        
        return
    
    # 現在のマス情報とイベント処理
    current_cell = board_data[game_state['current_position']]
    
    st.markdown("### 📍 現在のマス")
    st.info(f"**{current_cell.get('title', 'マス')}**\n\n{current_cell.get('desc', '特に何も起こりません。')}")
    
    # 現在のマスの画像を表示
    cell_number = game_state['current_position'] + 1
    display_image("board", f"cell_{cell_number:02d}", 
                 caption=f"マス{cell_number}: {current_cell.get('title', 'マス')}", use_column_width=True)
    
    # サイコロを振った直後かどうかをチェック
    just_moved = game_state.get('just_moved', False)
    
    # イベント処理
    event_completed = True
    cell_type = current_cell.get('type', 'event')
    
    # サイコロを振った直後、またはイベントがあるマスの場合は自動的にイベントを表示
    if (just_moved and cell_type in ['event', 'quiz', 'job_experience']) or (cell_type in ['event', 'quiz', 'job_experience'] and current_cell.get('action')):
        event_completed = handle_cell_event(current_cell)
        
        # 移動フラグをリセット
        if just_moved:
            game_state['just_moved'] = False
    
    # イベント完了後、またはイベントがない場合はサイコロエリアを表示
    if event_completed and not just_moved:
        # セル効果を適用
        apply_cell_effects(current_cell)
        
        st.markdown("### 🎲 サイコロを振ろう！")
        
        dice_col1, dice_col2, dice_col3 = st.columns([1, 2, 1])
        
        with dice_col2:
            st.markdown('<div class="dice-container">', unsafe_allow_html=True)
            
            # 最後のサイコロの目を表示
            if 'last_dice_roll' in st.session_state:
                dice_emoji = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"][st.session_state.last_dice_roll - 1]
                st.markdown(f'<div class="dice">{dice_emoji}</div>', unsafe_allow_html=True)
                st.markdown(f"**前回のサイコロ: {st.session_state.last_dice_roll}**")
            
            # サイコロを振るボタン
            if st.button("🎲 サイコロを振る", use_container_width=True, type="primary"):
                dice_result = roll_dice()
                st.session_state.last_dice_roll = dice_result
                
                # 次の位置を計算
                new_position = get_next_position(game_state['current_position'], board_data, dice_result)
                game_state['current_position'] = new_position
                
                # ターン数を増加
                game_state['turn_count'] += 1
                
                # 移動フラグを設定
                game_state['just_moved'] = True
                
                # 分岐パスをリセット
                game_state['branch_path'] = None
                
                # 結果を表示
                st.success(f"🎲 サイコロの目: {dice_result}")
                st.info(f"📍 {new_position + 1}マス目に移動しました！")
                
                # 状態を保存
                save_game_state(game_state)
                
                # ページを再読み込み
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 音声コントロール（現在のマスに音声がある場合）
    if current_cell.get('audio_id'):
        show_audio_controls(current_cell['audio_id'], f"🔊 {current_cell.get('title', 'マス')}の音声")
    
    # デバッグ情報（開発時のみ）
    if st.checkbox("🔧 デバッグ情報を表示"):
        st.json(game_state)

if __name__ == "__main__":
    main()
