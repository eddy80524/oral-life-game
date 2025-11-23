"""
ゲームロジックの中核機能
"""
import random
import json
import streamlit as st
from typing import Dict, Tuple, Optional
import uuid
from datetime import datetime

from . import teeth as teeth_service

def initialize_game_state():
    """ゲーム状態の初期化"""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'current_position': 0,
            'turn_count': 0,
            'start_time': datetime.now(),
            'total_points': 0,
            'teeth_count': 20,
            'tooth_coins': 10000,  # Updated to 10,000
            'caries_correct_count': 0,
            'perio_correct_count': 0,
            'scanned_nonces': [],
            'reached_goal': False,
            'job_experience_done': False
        }
    
    # 従来の変数も維持（互換性のため）
    if 'player_name' not in st.session_state:
        st.session_state.player_name = ""
    if 'age_group' not in st.session_state:
        st.session_state.age_group = ""
    if 'age_under_5' not in st.session_state:
        st.session_state.age_under_5 = False
    if 'teeth_count' not in st.session_state:
        st.session_state.teeth_count = 20
    if 'tooth_coins' not in st.session_state:
        st.session_state.tooth_coins = 10000  # Updated to 10,000
    if 'current_cell' not in st.session_state:
        st.session_state.current_cell = 0
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'turn_id' not in st.session_state:
        st.session_state.turn_id = None
    if 'caries_correct_count' not in st.session_state:
        st.session_state.caries_correct_count = 0
    if 'perio_correct_count' not in st.session_state:
        st.session_state.perio_correct_count = 0
    if 'scanned_nonces' not in st.session_state:
        st.session_state.scanned_nonces = []
    if 'photo_consent' not in st.session_state:
        st.session_state.photo_consent = False
    if 'reached_goal' not in st.session_state:
        st.session_state.reached_goal = False
    if 'job_experience_done' not in st.session_state:
        st.session_state.job_experience_done = False

    teeth_service.ensure_tooth_state(st.session_state.game_state)
    st.session_state.teeth_count = st.session_state.game_state.get("teeth_count", 20)

def roll_1to3() -> int:
    """1-3のサイコロを振る"""
    return random.randint(1, 3)

def generate_turn_id() -> str:
    """ターンIDを生成（重複防止用）"""
    return str(uuid.uuid4())[:8]

def load_board_data() -> list:
    """ボードデータを読み込む"""
    # Both files are now identical, but keeping the logic for now
    board_file = "data/board_main_under5.json" if st.session_state.age_under_5 else "data/board_main_5plus.json"
    try:
        with open(board_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"ボードファイル {board_file} が見つかりません")
        return []

def move_player(steps: int) -> int:
    """プレイヤーを移動させる"""
    old_cell = st.session_state.current_cell
    new_cell = max(0, old_cell + steps)
    
    # ボードの長さを取得
    board_data = load_board_data()
    max_cell = len(board_data) - 1
    
    if new_cell > max_cell:
        new_cell = max_cell
        st.session_state.reached_goal = True
    
    st.session_state.current_cell = new_cell
    # Sync with game_state
    if 'game_state' in st.session_state:
        st.session_state.game_state['current_position'] = new_cell
        
    return new_cell

def apply_delta(tooth_delta: int = 0, teeth_delta: int = 0) -> Dict[str, int]:
    """歯の本数とToothコインの増減を適用"""
    old_teeth = st.session_state.teeth_count
    old_coins = st.session_state.tooth_coins
    
    # 歯の本数の更新（0-28の範囲）
    new_teeth = max(0, min(28, old_teeth + teeth_delta))
    st.session_state.teeth_count = new_teeth
    if 'game_state' in st.session_state:
        st.session_state.game_state['teeth_count'] = new_teeth
    
    # Toothコインの更新（負の値も許可）
    new_coins = old_coins + tooth_delta
    st.session_state.tooth_coins = new_coins
    if 'game_state' in st.session_state:
        st.session_state.game_state['tooth_coins'] = new_coins
    
    return {
        'old_teeth': old_teeth,
        'new_teeth': new_teeth,
        'old_coins': old_coins,
        'new_coins': new_coins,
        'teeth_delta': teeth_delta,
        'coins_delta': tooth_delta
    }

def apply_tooth_delta(game_state, delta):
    """トゥースコインの増減を適用"""
    game_state['tooth_coins'] = max(0, game_state['tooth_coins'] + delta)
    # Sync with session_state
    st.session_state.tooth_coins = game_state['tooth_coins']
    return True

def apply_teeth_delta(game_state, delta):
    """歯の本数の増減を適用"""
    game_state['teeth_count'] = max(0, min(28, game_state['teeth_count'] + delta))
    # Sync with session_state
    st.session_state.teeth_count = game_state['teeth_count']
    return True

def apply_branch_after_quiz(game_state, quiz_type, correct_count):
    """クイズ後の分岐処理"""
    # Note: The actual branching (changing cells) happens in the UI/Board component.
    # This function handles side effects (points, flags).
    
    if quiz_type == "caries":  # 虫歯クイズ (Cell 7)
        st.session_state.caries_correct_count = correct_count
        if correct_count >= 1:
            # 正解ルート: Cell 8-2 (Floss)
            game_state['caries_result'] = 'correct'
            # No points mentioned for 8-2 in new spec, but keeping logic structure
        else:
            # 不正解ルート: Cell 8-1 (Caries)
            game_state['caries_result'] = 'incorrect'
            # Points are handled by the cell definition itself usually, 
            # but if we need immediate effect:
            # -2000 is defined in the cell 8-1 JSON.
            pass
    
    elif quiz_type == "perio":  # 歯周病クイズ (Cell 17)
        st.session_state.perio_correct_count = correct_count
        if correct_count >= 1:
            # 正解ルート: Cell 18-2 (Salary Up)
            game_state['perio_result'] = 'correct'
            # +5000 is defined in cell 18-2 JSON
        else:
            # 不正解ルート: Cell 18-1 (Loose Teeth)
            game_state['perio_result'] = 'incorrect'
            # -2000 is defined in cell 18-1 JSON

def lose_teeth_and_pay() -> Dict[str, int]:
    """歯周病不正解の動的処理：出た数の歯を失い、-2000 Tooth"""
    dice_roll = roll_1to3()
    current_teeth = st.session_state.game_state.get("teeth_count", st.session_state.teeth_count)
    teeth_lost = min(dice_roll, current_teeth)  # 現在の歯数を超えない
    
    # New spec: (-2000 Tooth) regardless of dice? 
    # "出た目の数だけ歯を失う (-2000トゥース)" -> Fixed -2000.
    payment = 2000 
    
    # Note: apply_delta takes positive for gain, negative for loss.
    # So we pass -2000.
    result = apply_delta(tooth_delta=-payment, teeth_delta=-teeth_lost)
    result['dice_roll'] = dice_roll
    result['teeth_lost'] = teeth_lost
    result['payment'] = payment
    
    if teeth_lost > 0:
        lost_ids = teeth_service.lose_random_teeth(
            st.session_state.game_state,
            count=teeth_lost,
            permanent=True,
        )
        result['lost_tooth_ids'] = lost_ids
        teeth_service.sync_teeth_count(st.session_state.game_state)
    
    return result

def get_current_cell_info() -> Dict:
    """現在のマス情報を取得"""
    board_data = load_board_data()
    current_cell = st.session_state.current_cell
    
    for cell_info in board_data:
        if cell_info['cell'] == current_cell:
            return cell_info
    
    # マス情報が見つからない場合はデフォルト
    return {
        'cell': current_cell,
        'type': 'event',
        'title': f'マス {current_cell}',
        'desc': '何かが起こります...',
        'audio_id': None
    }

def is_stop_cell(cell_info: Dict) -> bool:
    """ストップマス（強制停止）かどうか判定"""
    return cell_info.get('type') in ['stop', 'quiz'] or cell_info.get('route') in ['caries_quiz', 'perio_quiz']

def calculate_play_time(start_time=None) -> str:
    """プレイ時間を計算"""
    if start_time is None:
        start_time = st.session_state.start_time
    
    if start_time:
        elapsed = datetime.now() - start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{minutes}分{seconds}秒"
    return "0分0秒"

def handle_cell_action(cell_data, game_state):
    """セルアクションを処理"""
    if not cell_data:
        return None
    
    cell_type = cell_data.get('type', 'normal')
    action_message = None
    
    # Note: This might be redundant if we use apply_delta directly in the UI loop,
    # but keeping for compatibility if used elsewhere.
    
    if cell_type == 'teeth_gain':
        gain = cell_data.get('teeth_change', 1)
        game_state['teeth_count'] += gain
        action_message = f"歯が{gain}本増えました！"
    
    elif cell_type == 'teeth_loss':
        loss = abs(cell_data.get('teeth_change', 1))
        game_state['teeth_count'] = max(0, game_state['teeth_count'] - loss)
        action_message = f"歯が{loss}本減りました..."
    
    elif cell_type == 'coins_gain':
        gain = cell_data.get('coins_change', 1)
        game_state['tooth_coins'] += gain
        action_message = f"歯コインを{gain}枚獲得！"
    
    elif cell_type == 'coins_loss':
        loss = abs(cell_data.get('coins_change', 1))
        game_state['tooth_coins'] = max(0, game_state['tooth_coins'] - loss)
        action_message = f"歯コインを{loss}枚失いました..."
    
    elif cell_type == 'quiz':
        action_message = "クイズが始まります！"
    
    elif cell_type == 'event':
        action_message = cell_data.get('description', "何かが起こりました！")
    
    return action_message

def is_game_finished(game_state, board_size):
    """ゲーム終了判定"""
    return game_state['current_position'] >= board_size - 1

def add_scanned_nonce(nonce: str):
    """スキャン済みnonceを追加"""
    if nonce not in st.session_state.scanned_nonces:
        st.session_state.scanned_nonces.append(nonce)

def is_nonce_used(nonce: str) -> bool:
    """nonceが使用済みかチェック"""
    return nonce in st.session_state.scanned_nonces
