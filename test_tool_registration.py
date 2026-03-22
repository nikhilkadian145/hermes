import sys
from pathlib import Path
from nanobot.config.loader import load_config
from nanobot.agent.loop import AgentLoop
from nanobot.bus.queue import MessageBus
from nanobot.providers.litellm_provider import LiteLLMProvider

def test_tools():
    config_path = Path("test_customer/config.json")
    config = load_config(config_path)
    
    bus = MessageBus()
    provider = LiteLLMProvider(api_key="dummy", default_model="claude-3-haiku")
    
    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=config.workspace_path,
        exec_config=config.tools.exec,
        restrict_to_workspace=config.tools.restrict_to_workspace,
        mcp_servers=config.tools.mcp_servers,
    )
    
    print(f"Total tools registered: {len(agent.tools.tool_names)}")
    hermes_tools = [name for name in agent.tools.tool_names if name.startswith("Db")]
    print(f"HERMES DB tools registered: {len(hermes_tools)}")
    print(", ".join(hermes_tools[:5]) + " ...")
    
    if "DbGetMtdSummaryTool" in agent.tools.tool_names:
        print("SUCCESS: HERMES tools are successfully registered in the agent loop!")
    else:
        print("FAIL: DbGetMtdSummaryTool not found in registered tools.")
        sys.exit(1)

if __name__ == "__main__":
    test_tools()
