# お口の人生ゲーム - デジタル版

スマートフォン・PCブラウザで楽しめる歯科保健教育ゲームアプリです。

## 🎯 概要

子ども（5歳〜）と保護者が楽しみながら、クイズを通じて虫歯・歯周病予防を学習するゲームです。
ルーレットで進み、QRスキャンでToothコインを貯め、音声ガイド付きで各マスを体験できます。

## 🛠️ 技術スタック

- **言語**: Python 3.10+
- **フレームワーク**: Streamlit
- **主要ライブラリ**:
  - streamlit-webrtc (カメラ/QR機能)
  - opencv-python (QR検出)
  - pandas, numpy
  - pydub (音声処理)
- **データ保存**: ローカルJSON (将来Firebase対応)

## 📁 プロジェクト構成

```
oral_life_game/
├── app.py                      # メインアプリケーション
├── requirements.txt            # 依存関係
├── data/                       # ゲームデータ
│   ├── board_main_5plus.json   # 5歳以上用ボード
│   ├── board_main_under5.json  # 5歳未満用ボード
│   ├── quizzes.json            # クイズデータ
│   ├── audio_manifest.json     # 音声ファイルマップ
│   └── coloring_pages.json     # 塗り絵データ
├── assets/                     # 静的アセット
│   ├── images/                 # 画像ファイル
│   ├── audio/                  # 音声ファイル
│   └── qr_samples/             # サンプルQR
├── services/                   # サービスモジュール
│   ├── game_logic.py           # ゲームロジック
│   ├── audio.py                # 音声制御
│   ├── store.py                # データ保存
│   ├── qr.py                   # QR処理
│   └── firebase.py             # Firebase連携(モック)
└── pages/                      # Streamlitページ
    ├── 0_受付_プロローグ.py
    ├── 1_ゲームボード.py
    ├── 2_QRスキャン.py
    ├── 3_虫歯クイズ.py
    ├── 4_職業体験.py
    ├── 5_定期健診.py
    ├── 6_歯周病クイズ.py
    ├── 7_ゴール_ランキング.py
    ├── 8_スタッフ管理.py
    └── 9_LINE_塗り絵.py
```

## 🚀 セットアップと起動

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd oral_life_game
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. アプリケーションの起動
```bash
streamlit run app.py
```

### 4. ブラウザでアクセス
```
http://localhost:8501
```

## 🎮 ゲームフロー

1. **受付・プロローグ** - 参加者登録、撮影同意、基本説明
2. **ゲームボード** - 1〜3のサイコロで進行
3. **虫歯クイズ** - 2問出題、正答数で分岐
4. **職業体験** - 歯科関連職業体験（5歳以上のみ）
5. **歯周病クイズ** - 2問出題、正答数で分岐
6. **ゴール・ランキング** - 最終スコア発表

## 📱 QRコード仕様

QRペイロード例:
```json
{
  "t": "tooth_bonus",
  "v": 10,
  "cell": 4,
  "nonce": "demo-001"
}
```

- `t`: タイプ (tooth_bonus/tooth_penalty/stamp)
- `v`: 増減値
- `cell`: 対応マス番号
- `nonce`: 重複防止ID

## 🔧 スタッフ管理

PIN: `0418` でスタッフ管理画面にアクセス
- 参加者統計表示
- データリセット
- ボード設定切替

## 📊 データ管理

### ローカル保存
- `data/leaderboard.json` - ランキングデータ
- `data/participants.json` - 参加者統計
- `data/settings.json` - アプリ設定

### Firebase連携（将来実装）
- services/firebase.py でFirestore連携
- リアルタイムランキング
- クラウドバックアップ

## 🎨 カスタマイズ

### ボードの変更
`data/board_main_*.json` を編集してマス構成を変更

### クイズの追加
`data/quizzes.json` に新しいクイズを追加

### 音声の追加
1. `assets/audio/` に音声ファイルを配置
2. `data/audio_manifest.json` にマッピング追加

## 🐛 トラブルシューティング

### 音声が再生されない
- ブラウザの自動再生ポリシーを確認
- 音声ファイルの存在確認

### QRスキャンが動作しない
- カメラ権限の許可確認
- HTTPS環境での動作確認

### データが保存されない
- ファイル書き込み権限の確認
- `data/` ディレクトリの存在確認

## 📝 TODO

- [ ] 音声ファイルの実装
- [ ] 画像アセットの追加
- [ ] Firebase連携の実装
- [ ] モバイルUI最適化
- [ ] 多言語対応

## 📄 ライセンス

このプロジェクトは教育目的で作成されています。

## 👥 貢献

プルリクエストや課題報告をお待ちしています。

---

**お口の人生ゲーム** - 楽しく学ぶ歯科保健教育
