#!/usr/bin/env python3

# ファイルを読み込み
with open('/Users/utsueito/oral_life_game/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 問題のある文字列リテラル部分を修正
# stop_message = "" の後の不正な文字列を修正
import re

# 正しい文字列リテラルに置換
problem_area = r'stop_message = ""\s*"\s*<div style.*?</div>\s*"""'
correct_area = '''stop_message = """
                                    <div style='background-color: #FFE4E1; padding: 15px; border-radius: 10px; border: 3px solid #FF6B6B; margin: 10px 0;'>
                                        <h3 style='color: #D2691E; margin: 5px 0;'>🏥 とくべつなマス</h3>
                                        <p style='color: #8B0000; font-weight: bold; margin: 5px 0;'>定期検診のマスに到着しました！</p>
                                    </div>
                                    """'''

content = re.sub(problem_area, correct_area, content, flags=re.DOTALL)

# ファイルに書き戻し
with open('/Users/utsueito/oral_life_game/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('文字列修正完了')
