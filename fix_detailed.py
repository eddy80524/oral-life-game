#!/usr/bin/env python3

# ファイルを読み込み
with open('/Users/utsueito/oral_life_game/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 問題のある長い行を分割
import re

# 複数のコマンドが1行に結合されているパターンを修正
fixes = [
    # パターン1: stop_message = "" が他のコードと結合
    (r'(.*?)stop_message = ""(.*)', r'\1stop_message = ""\n\2'),
    
    # パターン2: if文が結合
    (r'(.*?)if new_position in stop_positions:(.*)', r'\1if new_position in stop_positions:\n\2'),
    
    # パターン3: if文の条件が結合
    (r'(.*?)if new_position == 4 or new_position == 15:(.*)', r'\1if new_position == 4 or new_position == 15:\n\2'),
    
    # パターン4: HTMLの開始が結合
    (r'(.*?)stop_message = """(.*)', r'\1stop_message = """\n\2'),
]

for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# 行ごとに分割して、インデントを修正
lines = content.split('\n')
fixed_lines = []

for line in lines:
    # 空行や適切にインデントされた行はそのまま
    if not line.strip() or line.startswith('                                    '):
        fixed_lines.append(line)
    # with col_b: ブロック内の行で、適切なインデントでない場合
    elif line.strip() and '                            with col_b:' in '\n'.join(fixed_lines[-10:]):
        # with ブロック内なので、適切なインデントを追加
        if line.startswith('                                '):
            fixed_lines.append(line)
        else:
            fixed_lines.append('                                ' + line.strip())
    else:
        fixed_lines.append(line)

# ファイルに書き戻し
with open('/Users/utsueito/oral_life_game/app.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print('詳細修正完了')
