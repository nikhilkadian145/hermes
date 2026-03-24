import os

tool_code = """
class WebChatPollTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "web_chat_poll"

    @property
    def description(self) -> str:
        return (
            "Check if a user has sent a message via the HERMES web dashboard chat. "
            "This tool is called automatically by the system — not by the user. "
            "Returns the pending message if one exists."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    async def execute(self, **kwargs) -> Any:
        try:
            msg = db.get_pending_web_chat_message(self.db_path)
            if not msg:
                return json.dumps({"has_message": False})
            db.mark_web_chat_message_processing(self.db_path, msg["id"])
            return json.dumps({
                "has_message": True,
                "message_id": msg["id"],
                "conversation_id": msg["conversation_id"],
                "content": msg["content"],
                "metadata": msg["metadata"]
            })
        except Exception as e:
            return f"Error: {e}"


class WebChatRespondTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "web_chat_respond"

    @property
    def description(self) -> str:
        return (
            "Send your response to the user on the web dashboard chat. "
            "Call this after processing a web chat message — "
            "pass the message_id from web_chat_poll and your response content."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message_id":      {"type": "integer", "description": "The id returned by web_chat_poll"},
                "conversation_id": {"type": "string"},
                "content":         {"type": "string", "description": "Your response text"},
                "metadata":        {"type": "string", "description": "Optional JSON: linked invoice_id, bill_id, etc."}
            },
            "required": ["message_id", "conversation_id", "content"]
        }

    async def execute(self, message_id: int, conversation_id: str,
                content: str, metadata: str = None, **kwargs) -> Any:
        try:
            db.mark_web_chat_message_done(self.db_path, message_id)
            db.write_web_chat_assistant_message(self.db_path, conversation_id, content, metadata)
            return json.dumps({"success": True})
        except Exception as e:
            return f"Error: {e}"
"""

with open(r'd:\HERMES\nanobot\agent\tools\hermes_tools.py', 'a', encoding='utf-8') as f:
    f.write('\n\n' + tool_code + '\n')

print('Success')
