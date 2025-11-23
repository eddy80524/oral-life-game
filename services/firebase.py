"""
Firebase Firestoreサービス
"""
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime
import json

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Warning: firebase-admin not installed. Using local JSON fallback.")

class FirebaseService:
    """Firebase Firestoreサービス"""
    
    def __init__(self):
        self.initialized = False
        self.db = None
    
    def initialize(self) -> bool:
        """Firebase接続を初期化"""
        if not FIREBASE_AVAILABLE:
            return False
            
        if self.initialized:
            return True
            
        try:
            # Streamlit secrets から Firebase credentials を取得
            if "firebase" not in st.secrets:
                print("Firebase secrets not found in .streamlit/secrets.toml")
                return False
            
            # 既に初期化済みかチェック
            if not firebase_admin._apps:
                # secrets.toml から credentials を構築
                firebase_config = dict(st.secrets["firebase"])
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.initialized = True
            print("✓ Firebase Firestore initialized successfully")
            return True
            
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            return False
    
    def save_player_score(self, player_data: Dict) -> bool:
        """プレイヤースコアをFirestoreに保存"""
        if not self.initialize():
            return False
            
        try:
            # スコアを計算
            score = player_data.get("teeth_count", 0) * 10 + player_data.get("tooth_coins", 0)
            
            # Firestoreに保存するデータ
            doc_data = {
                "player_name": player_data.get("player_name", "匿名"),
                "age_group": player_data.get("age_group", ""),
                "teeth_count": player_data.get("teeth_count", 0),
                "tooth_coins": player_data.get("tooth_coins", 0),
                "play_time": player_data.get("play_time", "0分0秒"),
                "score": score,
                "timestamp": firestore.SERVER_TIMESTAMP
            }
            
            # scores コレクションに追加
            self.db.collection('scores').add(doc_data)
            return True
            
        except Exception as e:
            print(f"Firebase save error: {e}")
            return False
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """リーダーボードを取得"""
        if not self.initialize():
            return []
            
        try:
            # スコアの高い順に取得
            scores_ref = self.db.collection('scores')
            query = scores_ref.order_by('score', direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            leaderboard = []
            for doc in docs:
                data = doc.to_dict()
                # timestamp を文字列に変換
                if 'timestamp' in data and data['timestamp']:
                    data['timestamp'] = data['timestamp'].isoformat() if hasattr(data['timestamp'], 'isoformat') else str(data['timestamp'])
                leaderboard.append(data)
            
            return leaderboard
            
        except Exception as e:
            print(f"Firebase get leaderboard error: {e}")
            return []
    
    def increment_participant_count(self) -> int:
        """参加者数をインクリメント"""
        if not self.initialize():
            return 0
            
        try:
            stats_ref = self.db.collection('stats').document('participants')
            today = datetime.now().strftime("%Y-%m-%d")
            
            # トランザクションで安全に更新
            @firestore.transactional
            def  update_in_transaction(transaction, stats_ref):
                snapshot = stats_ref.get(transaction=transaction)
                
                if snapshot.exists:
                    data = snapshot.to_dict()
                    total_count = data.get('total_count', 0) + 1
                    daily_counts = data.get('daily_counts', {})
                    daily_counts[today] = daily_counts.get(today, 0) + 1
                else:
                    total_count = 1
                    daily_counts = {today: 1}
                
                transaction.set(stats_ref, {
                    'total_count': total_count,
                    'daily_counts': daily_counts
                })
                
                return total_count
            
            transaction = self.db.transaction()
            new_count = update_in_transaction(transaction, stats_ref)
            return new_count
            
        except Exception as e:
            print(f"Firebase increment count error: {e}")
            return 0
    
    def get_participant_stats(self) -> Dict:
        """参加者統計を取得"""
        if not self.initialize():
            return {"total": 0, "today": 0, "daily_counts": {}}
            
        try:
            stats_ref = self.db.collection('stats').document('participants')
            doc = stats_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                today = datetime.now().strftime("%Y-%m-%d")
                today_count = data.get('daily_counts', {}).get(today, 0)
                
                return {
                    "total": data.get('total_count', 0),
                    "today": today_count,
                    "daily_counts": data.get('daily_counts', {})
                }
            else:
                return {"total": 0, "today": 0, "daily_counts": {}}
                
        except Exception as e:
            print(f"Firebase get stats error: {e}")
            return {"total": 0, "today": 0, "daily_counts": {}}

# グローバルインスタンス
firebase_service = FirebaseService()

def get_firebase_service() -> FirebaseService:
    """Firebaseサービスインスタンスを取得"""
    return firebase_service

