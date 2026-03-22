import sys
from pathlib import Path
from nanobot.config.loader import load_config

def test_load():
    config_path = Path("test_customer/config.json")
    config = load_config(config_path)
    
    workspace_path = config.workspace_path
    print(f"Parsed workspace path: {workspace_path}")
    
    soul_file = workspace_path / "SOUL.md"
    if not soul_file.exists():
        print(f"FAIL: SOUL.md not found at {soul_file}")
        sys.exit(1)
        
    content = soul_file.read_text(encoding="utf-8")
    print("=== Loaded SOUL.md ===")
    print(content[:200].encode('ascii', errors='ignore').decode('ascii') + "...\n")
    if "You are HERMES," in content:
        print("SUCCESS: HERMES SOUL.md loaded correctly via workspace config!")
    else:
        print("FAIL: Wrong SOUL.md content.")
        sys.exit(1)

if __name__ == "__main__":
    test_load()
