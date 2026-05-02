import json
import os
from datetime import datetime

# Keep your existing tools (get_indian_datetime and get_stock_price) and IntentAnalyzer here

def save_interaction(tool_name, result, filename="agent_history.json"):
    """
    Saves the execution history to a JSON file.
    """
    history = {}
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            pass
            
    timestamp = datetime.now().isoformat()
    history[timestamp] = {
        "tool": tool_name,
        "result": result
    }
    
    with open(filename, "w") as f:
        json.dump(history, f, indent=4)


class AgentOrchestrator:
    def __init__(self):
        self.tools = {}
        self.analyzer = IntentAnalyzer()

    def register_tool(self, name, function_ref, description):
        self.tools[name] = {"function": function_ref, "description": description}

    def execute_tool(self, tool_name, arguments=None):
        tool = self.tools[tool_name]
        if arguments:
            return {"status": "success", "tool": tool_name, "result": tool["function"](**arguments)}
        return {"status": "success", "tool": tool_name, "result": tool["function"]()}

    def process_request(self, message: str):
        analysis = self.analyzer.analyze(message)
        if not analysis["tool"]:
            return {"status": "idle", "message": "I could not find a tool matching your request."}
            
        execution_result = self.execute_tool(analysis["tool"], analysis["arguments"])
        
        # Save execution data
        if execution_result["status"] == "success":
            save_interaction(execution_result["tool"], execution_result["result"])
            
        return execution_result
        
