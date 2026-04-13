"""
通过MCP Unity获取session并检查编译错误
"""
import requests
import json
import time

MCP_SERVER = "http://127.0.0.1:8080/mcp"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

def parse_sse_response(text):
    """解析Server-Sent Events格式的响应"""
    lines = text.strip().split('\n')
    result = None

    for line in lines:
        if line.startswith('data: '):
            data_str = line[6:]  # 去掉 'data: ' 前缀
            try:
                data = json.loads(data_str)
                if 'result' in data:
                    result = data['result']
                elif 'error' in data:
                    print(f"错误: {data['error']}")
            except json.JSONDecodeError:
                pass

    return result

def get_session_and_tools():
    """初始化并获取session信息"""
    print("=== 初始化MCP Unity Server ===\n")

    # 初始化
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
    print(f"响应内容（前500字符）: {response.text[:500]}")

    # 解析响应
    result = parse_sse_response(response.text)
    if result:
        print(f"\n初始化成功!")
        print(f"服务器信息: {result.get('serverInfo', {})}")
        return True

    return False

def list_tools():
    """列出可用工具"""
    print("\n=== 列出可用工具 ===\n")

    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }

    response = requests.post(
        MCP_SERVER,
        json=payload,
        headers=HEADERS,
        timeout=10
    )

    print(f"工具列表响应状态: {response.status_code}")

    result = parse_sse_response(response.text)
    if result and 'tools' in result:
        tools = result['tools']
        print(f"\n找到 {len(tools)} 个工具:\n")

        # 分类显示工具
        for tool in tools:
            name = tool.get('name', 'Unknown')
            description = tool.get('description', 'No description')
            print(f"  - {name}")
            print(f"    描述: {description[:100]}")

            # 如果是编译相关工具，显示参数
            if 'console' in name.lower() or 'compile' in name.lower() or 'error' in name.lower():
                input_schema = tool.get('inputSchema', {})
                properties = input_schema.get('properties', {})
                if properties:
                    print(f"    参数: {', '.join(properties.keys())}")
            print()

        return tools

    return []

def check_compile_errors(tools):
    """检查编译错误"""
    print("\n=== 检查编译错误 ===\n")

    # 查找编译相关工具
    compile_tools = [t for t in tools if 'console' in t.get('name', '').lower() or
                     'compile' in t.get('name', '').lower() or
                     'error' in t.get('name', '').lower()]

    if not compile_tools:
        print("未找到编译相关工具")
        return

    # 尝试每个工具
    for tool in compile_tools:
        tool_name = tool['name']
        print(f"\n尝试调用工具: {tool_name}")

        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": {}
            }
        }

        try:
            response = requests.post(
                MCP_SERVER,
                json=payload,
                headers=HEADERS,
                timeout=10
            )

            print(f"响应状态: {response.status_code}")
            print(f"响应内容（前2000字符）:")
            print(response.text[:2000])

            # 解析结果
            result = parse_sse_response(response.text)
            if result:
                print(f"\n工具返回结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"调用失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 初始化
    if get_session_and_tools():
        # 列出工具
        tools = list_tools()
        # 检查编译错误
        if tools:
            check_compile_errors(tools)
