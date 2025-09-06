"""
QRコード検出・処理サービス
"""
import json
import cv2
import numpy as np
import streamlit as st
from typing import Dict, Optional, Tuple
import uuid

def decode_qr_from_frame(frame: np.ndarray) -> Optional[str]:
    """フレームからQRコードをデコード"""
    try:
        # QRコード検出器を初期化
        qr_detector = cv2.QRCodeDetector()
        
        # QRコードを検出・デコード
        data, points, _ = qr_detector.detectAndDecode(frame)
        
        if data:
            return data
        return None
    except Exception as e:
        st.error(f"QR読み取りエラー: {e}")
        return None

def decode_qr_payload(payload: Dict) -> bool:
    """QRペイロードをデコードして検証"""
    try:
        # 必須フィールドの確認
        required_fields = ['t', 'v', 'cell', 'nonce']
        for field in required_fields:
            if field not in payload:
                return False
        
        # タイプ確認
        if payload['t'] != 'tooth_delta':
            return False
        
        # 値の型確認
        if not isinstance(payload['v'], (int, float)):
            return False
        
        if not isinstance(payload['cell'], int):
            return False
        
        if not isinstance(payload['nonce'], str):
            return False
        
        return True
    
    except Exception:
        return False

def is_valid_nonce(nonce: str) -> bool:
    """nonceが未使用かチェック"""
    if 'used_nonces' not in st.session_state:
        st.session_state.used_nonces = []
    
    return nonce not in st.session_state.used_nonces

def add_nonce(nonce: str) -> bool:
    """使用済みnonceに追加"""
    try:
        if 'used_nonces' not in st.session_state:
            st.session_state.used_nonces = []
        
        if nonce not in st.session_state.used_nonces:
            st.session_state.used_nonces.append(nonce)
            return True
        
        return False
    
    except Exception:
        return False

def generate_sample_qr(cell: int, value: int) -> Dict:
    """サンプルQRペイロードを生成"""
    return {
        't': 'tooth_delta',
        'v': value,
        'cell': cell,
        'nonce': f'sample-{cell}-{str(uuid.uuid4())[:8]}'
    }

def validate_qr_for_cell(payload: Dict, target_cell: int) -> bool:
    """特定のセルに対してQRが有効かチェック"""
    if not decode_qr_payload(payload):
        return False
    
    if payload['cell'] != target_cell:
        return False
    
    if not is_valid_nonce(payload['nonce']):
        return False
    
    return True
