#!/usr/bin/env python3

# ファイルを読み込み
with open('/Users/utsueito/oral_life_game/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 問題のある行を特定して修正
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # col_a, col_b, col_c を含む行を見つけた場合
    if 'col_a, col_b, col_c = st.columns([1,' in line:
        # 行を2つに分割：st.columns の部分と with col_b: の部分
        if '2, 1])' in line and 'with col_b:' in line:
            # 1行に両方が含まれている場合
            fixed_lines.append('                            col_a, col_b, col_c = st.columns([1, 2, 1])\n')
            fixed_lines.append('                            with col_b:\n')
        elif i + 1 < len(lines) and '2, 1])' in lines[i + 1]:
            # 2行に分かれている場合
            fixed_lines.append('                            col_a, col_b, col_c = st.columns([1, 2, 1])\n')
            i += 1  # 次の行をスキップ
            fixed_lines.append('                            with col_b:\n')
        else:
            fixed_lines.append(line)
    elif 'with col_b:' in line and not line.strip().startswith('with col_b:'):
        # with col_b: が他のコードと同じ行にある場合
        fixed_lines.append('                            with col_b:\n')
    else:
        fixed_lines.append(line)
    
    i += 1

# with col_b: ブロック内の行のインデントを修正
in_with_block = False
for i, line in enumerate(fixed_lines):
    if '                            with col_b:' in line:
        in_with_block = True
        continue
    elif in_with_block:
        if line.strip() == '':
            continue
        elif line.startswith('                            ') and line.strip():
            # with ブロック内なので追加インデント
            fixed_lines[i] = '                                ' + line.strip() + '\n'
        elif not line.startswith(' '):
            # ブロック終了
            in_with_block = False

# ファイルに書き戻し
with open('/Users/utsueito/oral_life_game/app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('構文修正完了')
