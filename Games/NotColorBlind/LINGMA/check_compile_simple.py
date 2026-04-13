"""
通过MCP Unity检查编译错误
"""
import requests
import json

MCP_SERVER = "http://127.0.0.1:8080/mcp"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

def check_compile_errors():
    """检查Unity编译错误"""
    print("=== 检查Unity编译错误 ===\n")
    
    try:
        # 1. 初始化并获取session
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "compile-check",
                    "version": "1.0"
                }
            }
        }
        
        response = requests.post(
            MCP_SERVER,
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        print(f"初始化响应状态: {response.status_code}")
        
        # 2. 获取工具列表
        tools_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        tools_response = requests.post(
            MCP_SERVER,
            json=tools_payload,
            headers=HEADERS,
            timeout=10
        )
        
        print(f"工具列表响应状态: {tools_response.status_code}")
        if tools_response.status_code == 200 and tools_response.text.strip():
            tools_result = tools_response.json()
            tools = tools_result.get("result", {}).get("tools", [])
            print(f"\n找到 {len(tools)} 个工具")
            
            # 查找相关的编译检查工具
            compile_tools = [t for t in tools if "console" in t.get("name", "").lower() or "compile" in t.get("name", "").lower() or "error" in t.get("name", "").lower()]
            print(f"\n编译相关工具:")
            for tool in compile_tools:
                print(f"  - {tool.get('name')}: {tool.get('description', 'N/A')}")
            
            # 尝试调用第一个合适的工具
            if compile_tools:
                tool_name = compile_tools[0].get("name")
                print(f"\n尝试调用工具: {tool_name}")
                
                call_payload = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": {}
                    }
                }
                
                call_response = requests.post(
                    MCP_SERVER,
                    json=call_payload,
                    headers=HEADERS,
                    timeout=10
                )
                
                print(f"\n工具调用响应状态: {call_response.status_code}")
                if call_response.status_code == 200 and call_response.text.strip():
                    print(f"\n编译结果:")
                    print(call_response.text[:2000])
                else:
                    print(f"工具调用失败: {call_response.text}")
            
            # 如果没有找到编译工具，列出所有工具
            if not compile_tools:
                print(f"\n所有可用工具:")
                for tool in tools:
                    print(f"  - {tool.get('name')}: {tool.get('description', 'N/A')}")
        else:
            print(f"获取工具列表失败: {tools_response.text}")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_compile_errors()
