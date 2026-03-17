import requests

MCP_SERVER_URL = "http://localhost:8080"
SESSION_ID = None

def init_session():
    global SESSION_ID
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", headers={
            "mcp-session-id": SESSION_ID
        } if SESSION_ID else {})
        
        if response.status_code == 200:
            print("✓ 使用现有会话")
            return True
            
        response = requests.post(f"{MCP_SERVER_URL}/initialize")
        if response.status_code == 200:
            SESSION_ID = response.headers.get("mcp-session-id")
            print(f"✓ 创建新会话：{SESSION_ID}")
            return True
            
    except Exception as e:
        print(f"✗ 连接失败：{e}")
        return False
    
    return False

def list_tools():
    """列出所有可用工具"""
    try:
        response = requests.get(
            f"{MCP_SERVER_URL}/tools",
            headers={"mcp-session-id": SESSION_ID}
        )
        
        if response.status_code == 200:
            tools = response.json().get("tools", [])
            print("\n=== 可用的 MCP 工具 ===\n")
            for tool in tools:
                print(f"工具名：{tool['name']}")
                print(f"描述：{tool.get('description', '无')}")
                if 'inputSchema' in tool:
                    params = tool['inputSchema'].get('properties', {})
                    if params:
                        print(f"参数：{list(params.keys())}")
                print("-" * 50)
            return tools
        else:
            print(f"✗ 获取工具列表失败：{response.text}")
            return []
            
    except Exception as e:
        print(f"✗ 异常：{e}")
        return []

if __name__ == "__main__":
    if init_session():
        list_tools()
