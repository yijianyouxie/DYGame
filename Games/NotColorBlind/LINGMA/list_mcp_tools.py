"""
通过MCP Unity列出可用工具并检查编译错误
"""
import requests
import json

MCP_SERVER = "http://127.0.0.1:8080/mcp"

# 强制使用JSON格式
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

def list_tools():
    """列出MCP可用工具"""
    print("=== 列出MCP可用工具 ===\n")
    
    try:
        # 使用MCP协议格式调用initialize
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
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
        print(f"响应内容: {response.text[:500]}")
        
        if response.status_code == 200 and response.text.strip():
            result = response.json()
            print(f"初始化成功: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 获取工具列表
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
            
            print(f"\n工具列表响应状态: {tools_response.status_code}")
            if tools_response.status_code == 200 and tools_response.text.strip():
                tools_result = tools_response.json()
                print(f"\n可用工具: {json.dumps(tools_result, indent=2, ensure_ascii=False)}")
            else:
                print(f"获取工具列表失败: {tools_response.text}")
        else:
            print(f"初始化失败: {response.text}")
            
    except Exception as e:
        print(f"错误: {e}")

def get_compile_errors():
    """获取Unity编译错误"""
    print("\n=== 获取Unity编译错误 ===\n")
    
    try:
        # 调用获取控制台的工具
        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_console",
                "arguments": {
                    "mode": "compile_errors"
                }
            }
        }
        
        response = requests.post(
            MCP_SERVER,
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        print(f"获取编译错误响应状态: {response.status_code}")
        if response.status_code == 200 and response.text.strip():
            result = response.json()
            print(f"\n编译错误: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取编译错误失败: {response.text}")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    list_tools()
    get_compile_errors()
