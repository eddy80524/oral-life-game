"""
音声再生サービス
"""
import json
import streamlit as st
import os

def load_audio_manifest():
    """音声マニフェストを読み込む"""
    try:
        with open('data/audio_manifest.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning("音声マニフェストファイルが見つかりません")
        return {}

def play_audio(audio_id: str, autoplay: bool = False) -> bool:
    """音声を再生"""
    if not audio_id:
        return False
    
    manifest = load_audio_manifest()
    audio_path = manifest.get(audio_id)
    
    if not audio_path:
        st.info(f"音声ID '{audio_id}' が見つかりません")
        return False
    
    if not os.path.exists(audio_path):
        st.info(f"音声ファイル '{audio_path}' が見つかりません（実装時に追加予定）")
        return False
    
    try:
        # Streamlitの音声プレイヤーを使用
        with open(audio_path, 'rb') as audio_file:
            st.audio(audio_file.read(), format='audio/mp3', start_time=0)
        return True
    except Exception as e:
        st.error(f"音声再生エラー: {e}")
        return False

def show_audio_controls(audio_id: str, label: str = "🔊 音声ガイド"):
    """音声コントロールを表示"""
    if audio_id:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(label, key=f"audio_{audio_id}"):
                play_audio(audio_id)
        with col2:
            st.info("💡 タップで再生")
    else:
        st.info("音声ガイドはありません")

def create_placeholder_audio():
    """プレースホルダー音声ファイルを作成（開発用）"""
    # TODO: 実際の音声ファイルが用意された時に削除
    audio_dir = "assets/audio"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    # 空のMP3ファイルを作成（実際の音声ファイルのプレースホルダー）
    manifest = load_audio_manifest()
    for audio_id, path in manifest.items():
        if not os.path.exists(path):
            # 簡単なプレースホルダーファイルを作成
            with open(path, 'w') as f:
                f.write(f"# Placeholder for {audio_id}")
