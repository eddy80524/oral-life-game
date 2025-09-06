#!/usr/bin/env python3

# ファイルを読み込み
with open('/Users/utsueito/oral_life_game/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 問題のある領域全体を正しいコードで置換
problem_start = "                            with col_b:"
problem_end = "st.markdown(f\"\"\""

# 問題領域を見つけて置換
start_idx = content.find(problem_start)
end_idx = content.find(problem_end, start_idx)

if start_idx != -1 and end_idx != -1:
    # 正しいコードブロック
    correct_block = '''                            with col_b:
                                # 強制停止マスに到着した場合の特別表示
                                stop_message = ""
                                if new_position in stop_positions:
                                    if new_position == 4 or new_position == 15:
                                        stop_message = """
                                        <div style='background-color: #FFE4E1; padding: 15px; border-radius: 10px; border: 3px solid #FF6B6B; margin: 10px 0;'>
                                            <h3 style='color: #D2691E; margin: 5px 0;'>🏥 とくべつなマス</h3>
                                            <p style='color: #8B0000; font-weight: bold; margin: 5px 0;'>定期検診のマスに到着しました！</p>
                                        </div>
                                        """
                                    elif new_position == 13:
                                        stop_message = """
                                        <div style='background-color: #FFE4E1; padding: 15px; border-radius: 10px; border: 3px solid #FF6B6B; margin: 10px 0;'>
                                            <h3 style='color: #D2691E; margin: 5px 0;'>🏥 とくべつなマス</h3>
                                            <p style='color: #8B0000; font-weight: bold; margin: 5px 0;'>定期検診のマスに到着しました！</p>
                                        </div>
                                        """
                            
                                '''
    
    # 置換実行
    new_content = content[:start_idx] + correct_block + content[end_idx:]
    
    # ファイルに書き戻し
    with open('/Users/utsueito/oral_life_game/app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('領域全体修正完了')
else:
    print('問題領域が見つかりませんでした')
