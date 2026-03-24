import os
import re

FRONTEND_PAGES_DIR = r"d:\HERMES\webapp\frontend\src\pages"
COMPONENTS_DIR = r"d:\HERMES\webapp\frontend\src\components"

# Matches: fetch("http://localhost:8000/api/..." ) or fetch(`http://localhost:8000/api/...`) or fetch(API)
# But we also have to add the import carefully.

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip files that don't have fetch
    if "fetch(" not in content:
        return

    # Check if we should ignore this file because we want to manually rewrite it entirely (like Dashboard.tsx)
    if "Dashboard.tsx" in filepath:
        return

    new_content = content

    # Replace absolute URLs with relative paths for apiFetch
    new_content = re.sub(
        r'fetch\(\s*["\']http://localhost:8000/api(.*?)(["\'])',
        r'apiFetch("\1"',
        new_content
    )
    new_content = re.sub(
        r'fetch\(\s*`http://localhost:8000/api(.*?)`',
        r'apiFetch(`\1`',
        new_content
    )
    
    # Handle fetch(API) or fetch(`${API}/...`) where API was defined
    new_content = re.sub(
        r'fetch\(\s*`\$\{API\}(.*?)`',
        r'apiFetch(`\1`',
        new_content
    )
    new_content = re.sub(
        r'fetch\(\s*API\s*\)',
        r'apiFetch("")',
        new_content
    )
    new_content = re.sub(
        r'fetch\(\s*API\s*,',
        r'apiFetch("",',
        new_content
    )
    
    # Handle file download endpoints - we keep normal fetch for those, or use window.open / anchor tags anyway.
    # Actually wait - we might have some specialized fetch for files. We can blindly replace, but `apiFetch` 
    # assumes JSON response. If they expect blob, apiFetch might fail. But looking at the grep earlier:
    # Most file downloads use window.open(). The fetches were for JSON APIs.

    # If we changed anything, add the import
    if new_content != content:
        # Determine relative path to src/api/client
        depth = filepath.count(os.sep) - r"d:\HERMES\webapp\frontend\src".count(os.sep)
        # e.g., pages -> depth 1 -> ../api/client
        # components/layout -> depth 2 -> ../../api/client
        rel_prefix = "../" * depth
        import_stmt = f"import {{ apiFetch }} from '{rel_prefix}api/client';\n"
        
        # Insert import after the React imports
        if "import React" in new_content or "import {" in new_content:
            lines = new_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import ') and 'react' not in line.lower():
                    lines.insert(i, import_stmt.strip())
                    new_content = '\n'.join(lines)
                    break
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {os.path.basename(filepath)}")

def main():
    for root, _, files in os.walk(FRONTEND_PAGES_DIR):
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts'):
                process_file(os.path.join(root, f))
                
    for root, _, files in os.walk(COMPONENTS_DIR):
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts'):
                process_file(os.path.join(root, f))

if __name__ == "__main__":
    main()
