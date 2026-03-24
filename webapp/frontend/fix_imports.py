import os
import re

src_dir = r"d:\HERMES\webapp\frontend\src"
for root, _, files in os.walk(src_dir):
    for f in files:
        if f.endswith('.tsx') or f.endswith('.ts'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            if 'import { apiFetch } from' in content:
                # Correct relative depth
                depth = root.count(os.sep) - src_dir.count(os.sep)
                if depth == 0:
                    correct_prefix = './'
                else:
                    correct_prefix = '../' * depth
                correct_import = f"import {{ apiFetch }} from '{correct_prefix}api/client';"
                
                # Replace the wrong one
                new_content = re.sub(r"import \{ apiFetch \} from '[\./]+api/client';", correct_import, content)
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    print(f'Fixed {f}')
