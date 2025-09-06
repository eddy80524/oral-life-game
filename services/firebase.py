"""
Firebase Firestoreサービス（将来実装用のモック）
"""
import streamlit as st
from typing import Dict, List, Optional

# TODO: 実際の実装時にpyrebase4を使用
# import pyrebase

class FirebaseService:
    """Firebase Firestoreサービスのモック実装"""
    
    def __init__(self):
        self.initialized = False
        # TODO: Firebase設定を追加
        # config = {
        #     "apiKey": "your-api-key",
        #     "authDomain": "your-project.firebaseapp.com",
        #     "databaseURL": "https://your-project.firebaseio.com",
        #     "projectId": "your-project-id",
        #     "storageBucket": "your-project.appspot.com",
        #     "messagingSenderId": "your-sender-id"
        # }
        # firebase = pyrebase.initialize_app(config)
        # self.db = firebase.database()
    
    def initialize(self) -> bool:
        """Firebase接続を初期化"""
        # TODO: 実際のFirebase初期化
        st.info("Firebase接続はモック実装です")
        self.initialized = True
        return True
    
    def save_player_score(self, player_data: Dict) -> bool:
        """プレイヤースコアをFirestoreに保存"""
        try:
            # TODO: 実際のFirestore保存
            # self.db.child("scores").push(player_data)
            st.info("スコアはローカルJSONに保存されました（Firebase実装待ち）")
            return True
        except Exception as e:
            st.error(f"Firebase保存エラー: {e}")
            return False
    
    def get_leaderboard(self, limit: int = 5) -> List[Dict]:
        """リーダーボードを取得"""
        try:
            # TODO: 実際のFirestore取得
            # scores = self.db.child("scores").order_by_child("score").limit_to_last(limit).get()
            st.info("リーダーボードはローカルJSONから取得されました（Firebase実装待ち）")
            return []
        except Exception as e:
            st.error(f"Firebase取得エラー: {e}")
            return []
    
    def increment_participant_count(self) -> int:
        """参加者数をインクリメント"""
        try:
            # TODO: 実際のFirestore更新
            # current = self.db.child("stats").child("participants").get().val() or 0
            # new_count = current + 1
            # self.db.child("stats").child("participants").set(new_count)
            st.info("参加者数はローカルJSONに保存されました（Firebase実装待ち）")
            return 1
        except Exception as e:
            st.error(f"Firebase更新エラー: {e}")
            return 0
    
    def backup_local_data(self) -> bool:
        """ローカルデータをFirebaseにバックアップ"""
        try:
            # TODO: ローカルJSONファイルの内容をFirebaseに移行
            st.info("バックアップはローカル実装のみです（Firebase実装待ち）")
            return True
        except Exception as e:
            st.error(f"バックアップエラー: {e}")
            return False

# グローバルインスタンス
firebase_service = FirebaseService()

def get_firebase_service() -> FirebaseService:
    """Firebaseサービスインスタンスを取得"""
    return firebase_service
