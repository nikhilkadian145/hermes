import sys
from pathlib import Path
from nanobot.agent.context import ContextBuilder

def test_skills_loaded():
    # Use the local workspace directory where skills are placed
    workspace = Path(r"d:\HERMES\build\workspace")
    ctx = ContextBuilder(workspace)
    
    prompt = ctx.build_system_prompt()
    
    expected_skills = [
        "invoice-create",
        "expense-log",
        "report-pl"
    ]
    
    missing = []
    for skill in expected_skills:
        if skill not in prompt:
            missing.append(skill)
            
    if missing:
        print(f"FAILED: Missing skills in prompt: {missing}")
        sys.exit(1)
    
    print("SUCCESS: Skills are successfully loaded into the prompt context by ContextBuilder.")
    
if __name__ == "__main__":
    test_skills_loaded()
