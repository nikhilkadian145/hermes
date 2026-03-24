import os

routers = [
    'dashboard', 'invoices', 'bills', 'contacts', 'payments',
    'accounts', 'reports', 'anomalies', 'audit', 'notifications',
    'search', 'files', 'settings', 'system', 'chat'
]

os.makedirs('backend/routers', exist_ok=True)

with open('backend/routers/__init__.py', 'w') as f:
    pass

for r in routers:
    content = f'''from fastapi import APIRouter

router = APIRouter(prefix=\"/api/{r}\", tags=[\"{r}\"])

@router.get(\"/health\")
def health():
    return {{\"status\": \"ok\", \"router\": \"{r}\"}}
'''
    with open(f'backend/routers/{r}.py', 'w') as f:
        f.write(content)

print("Created all routers successfully.")
