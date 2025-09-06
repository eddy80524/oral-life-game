#!/usr/bin/env python3

# ファイルを読み込み
with open('/Users/utsueito/oral_life_game/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 問題のある領域を特定して修正
fixed_lines = []
skip_until_line = -1

for i, line in enumerate(lines):
    if skip_until_line > i:
        continue
        
    # with col_b: の行を見つけた場合
    if 'with col_b:' in line and 'col_a, col_b, col_c' not in line:
        fixed_lines.append('                            with col_b:\n')
        
        # 次の行から正しいブロックを追加
        fixed_lines.append('                                # 強制停止マスに到着した場合の特別表示\n')
        fixed_lines.append('                                stop_message = ""\n')
        fixed_lines.append('                                if new_position in stop_positions:\n')
        fixed_lines.append('                                    if new_position == 4 or new_position == 15:\n')
        fixed_lines.append('                                        stop_message = """\n')
        fixed_lines.append('                                        <div style=\'background-color: #FFE4E1; padding: 15px; border-radius: 10px; border: 3px solid #FF6B6B; margin: 10px 0;\'>\n')
        fixed_lines.append('                                            <h3 style=\'color: #D2691E; margin: 5px 0;\'>🏥 とくべつなマス</h3>\n')
        fixed_lines.append('                                            <p style=\'color: #8B0000; font-weight: bold; margin: 5px 0;\'>定期検診のマスに到着しました！</p>\n')
        fixed_lines.append('                                        </div>\n')
        fixed_lines.append('                                        """\n')
        fixed_lines.append('                                    elif new_position == 13:\n')
        
        # 元の壊れたブロックをスキップ
        j = i + 1
        while j < len(lines) and ('elif new_position == 13:' not in lines[j] or lines[j].count('elif new_position == 13:') < 1):
            if 'elif new_position == 13:' in lines[j]:
                break
            j += 1
        skip_until_line = j
        
    else:
        fixed_lines.append(line)

# ファイルに書き戻し
with open('/Users/utsueito/oral_life_game/app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('ブロック全体修正完了')
