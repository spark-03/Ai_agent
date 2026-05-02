from datetime import datetime
from zoneinfo import ZoneInfo
import json

def get_indian_datetime():
    """
    Fetches the current real-time date and time specifically for India (Asia/Kolkata).
    """
    ist_tz = ZoneInfo("Asia/Kolkata")
    now = datetime.now(ist_tz)

    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timestamp": now.isoformat(),
        "year": now.year,
        "month": now.month,
        "day": now.day
    }

class AgentOrchestrator:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name, function_ref, description):
        """
        Registers an external tool or utility in the orchestrator's registry.
        """
        self.tools[name] = {
            "function": function_ref,
            "description": description
        }
        print(f"Tool registered: '{name}'")

    def execute_tool(self, tool_name, arguments=None):
        """
        Executes the requested tool with the provided arguments.
        """
        if tool_name not in self.tools:
            return {"status": "error", "message": f"Tool '{tool_name}' not found."}
        
        tool = self.tools[tool_name]
        try:
            if arguments:
                result = tool["function"](**arguments)
            else:
                result = tool["function"]()
                
            return {
                "status": "success",
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Initialize and test the base orchestrator
if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    
    # Register our time engine as the first tool
    orchestrator.register_tool(
        name="get_indian_datetime",
        function_ref=get_indian_datetime,
        description="Fetches current date and time in Indian Standard Time (IST)."
    )
    
    # Test execution
    output = orchestrator.execute_tool("get_indian_datetime")
    print(json.dumps(output, indent=4))
      
