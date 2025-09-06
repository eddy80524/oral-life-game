"""
QRスキャンページ - お口の人生ゲーム
"""
import streamlit as st
import sys
import os
import json
import cv2
import numpy as np
from datetime import datetime

# servicesディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.qr import decode_qr_payload, is_valid_nonce, add_nonce
from services.game_logic import apply_tooth_delta
from services.store import save_game_state

# ページ設定
st.set_page_config(
    page_title="QRスキャン - お口の人生ゲーム",
    page_icon="📱",
    layout="wide"
)

def main():
    st.title("📱 QRコードスキャン")
    
    if 'game_state' not in st.session_state:
        st.error("ゲーム状態が見つかりません。ゲームボードからやり直してください。")
        if st.button("🎲 ゲームボードに戻る"):
            st.switch_page("pages/1_ゲームボード.py")
        return
    
    game_state = st.session_state.game_state
    current_cell = game_state['current_position']
    
    st.markdown("""
    ### 📋 QRスキャンの使い方
    1. 現在のマスに対応するQRコードをカメラでスキャン
    2. トゥースコインの増減が自動で反映されます
    3. 同じQRコードは一度しか使用できません
    """)
    
    # 現在の状態表示
    col1, col2 = st.columns(2)
    with col1:
        st.metric("現在のマス", f"{current_cell + 1}マス目")
    with col2:
        st.metric("トゥースコイン", game_state['tooth_coins'])
    
    # QRコード入力エリア
    st.markdown("### 📷 QRコードをスキャン")
    
    # カメラ入力（簡易版）
    camera_input = st.camera_input("QRコードをカメラで撮影")
    
    # テキスト入力（デバッグ用）
    st.markdown("#### またはQRコードの内容を直接入力")
    qr_text = st.text_area("QRコードの内容", placeholder='{"t":"tooth_delta","v":5,"cell":4,"nonce":"demo-0001"}')
    
    if st.button("🔍 QRコードを処理", use_container_width=True, type="primary"):
        payload_text = None
        
        # カメラ画像からQR読み取り
        if camera_input is not None:
            # 画像を読み込んでQRデコード
            file_bytes = np.asarray(bytearray(camera_input.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            
            # QR検出
            detector = cv2.QRCodeDetector()
            retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(image)
            
            if retval and decoded_info:
                payload_text = decoded_info[0]
                st.success("📱 QRコードを検出しました！")
            else:
                st.warning("QRコードが見つかりませんでした。")
        
        # テキスト入力からの処理
        if not payload_text and qr_text.strip():
            payload_text = qr_text.strip()
        
        # ペイロード処理
        if payload_text:
            try:
                payload = json.loads(payload_text)
                
                # ペイロード検証
                if not decode_qr_payload(payload):
                    st.error("❌ 無効なQRコードです")
                    return
                
                # セル一致チェック
                if payload.get('cell') != current_cell:
                    st.error(f"❌ このQRコードは{payload.get('cell', '?')}マス目用です。現在は{current_cell + 1}マス目です。")
                    return
                
                # nonce重複チェック
                nonce = payload.get('nonce', '')
                if not is_valid_nonce(nonce):
                    st.error("❌ このQRコードは既に使用済みです")
                    return
                
                # トゥース増減適用
                tooth_delta = payload.get('v', 0)
                if apply_tooth_delta(game_state, tooth_delta):
                    add_nonce(nonce)
                    save_game_state(game_state)
                    
                    if tooth_delta > 0:
                        st.success(f"🎉 +{tooth_delta}トゥースコインを獲得！")
                    elif tooth_delta < 0:
                        st.warning(f"💸 {abs(tooth_delta)}トゥースコインを支払いました")
                    else:
                        st.info("ℹ️ 特別なイベントが発生しました")
                    
                    # 少し待ってからゲームボードに戻る
                    st.balloons()
                    st.markdown("**3秒後にゲームボードに戻ります...**")
                    
                    # 自動でゲームボードに戻る処理
                    if st.button("🎲 ゲームボードに戻る", use_container_width=True):
                        st.switch_page("pages/1_ゲームボード.py")
                
            except json.JSONDecodeError:
                st.error("❌ QRコードの形式が正しくありません")
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
    
    # サンプルQRコード表示
    with st.expander("📖 サンプルQRコード（テスト用）"):
        st.markdown("**現在のマス用サンプル:**")
        sample_payload = {
            "t": "tooth_delta",
            "v": 5,
            "cell": current_cell,
            "nonce": f"sample-{current_cell}-{datetime.now().strftime('%H%M%S')}"
        }
        st.code(json.dumps(sample_payload, ensure_ascii=False, indent=2))
        
        st.markdown("**説明:**")
        st.markdown("""
        - `t`: タイプ（tooth_delta = トゥースコイン増減）
        - `v`: 値（正数で増加、負数で減少）
        - `cell`: 対象マス番号（0から開始）
        - `nonce`: 重複防止ID（一意である必要があります）
        """)
    
    # 戻るボタン
    if st.button("⬅️ ゲームボードに戻る", use_container_width=True):
        st.switch_page("pages/1_ゲームボード.py")

if __name__ == "__main__":
    main()
