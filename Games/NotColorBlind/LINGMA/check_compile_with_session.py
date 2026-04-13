"""
通过MCP Unity获取session并检查编译错误（正确版本）
根据官方文档，session ID应该从响应头中获取
"""
import requests
import json
import time

MCP_SERVER = "http://127.0.0.1:8080/mcp"

BASE_HEADERS = {
    "Accept": "application/json,text/event-stream",
    "Content-Type": "application/json"
}

class MCPUnityClient:
    def __init__(self):
        self.session_id = None
        self.initialized = False

    def initialize(self):
        """初始化并获取session ID"""
        print("=== 初始化MCP Unity Server ===\n")

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
            headers=BASE_HEADERS,
            timeout=10
        )

        print(f"初始化响应状态: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")

        # 关键：从响应头中获取session ID
        self.session_id = response.headers.get('mcp-session-id')

        if self.session_id:
            print(f"[OK] Session ID: {self.session_id}")
        else:
            print("[ERROR] 无法从响应头获取 Session ID")
            return False

        # 等待初始化完成
        if response.status_code == 200:
            # 读取流式响应
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        if 'result' in data:
                            result = data['result']
                            print(f"[OK] 初始化成功")
                            print(f"服务器: {result.get('serverInfo', {})}")
                            self.initialized = True

                            # 发送 initialized 通知
                            self.send_initialized()
                            return True

        return False

    def send_initialized(self):
        """发送 initialized 通知"""
        print("\n=== 发送 Initialized 通知 ===\n")

        headers = {**BASE_HEADERS, 'mcp-session-id': self.session_id}

        payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }

        response = requests.post(
            MCP_SERVER,
            json=payload,
            headers=headers,
            timeout=10
        )

        print(f"Initialized 通知响应状态: {response.status_code}")
        return response.status_code == 200

    def list_tools(self):
        """列出可用工具"""
        print("\n=== 列出可用工具 ===\n")

        headers = {**BASE_HEADERS, 'mcp-session-id': self.session_id}

        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        response = requests.post(
            MCP_SERVER,
            json=payload,
            headers=headers,
            timeout=10
        )

        print(f"工具列表响应状态: {response.status_code}")

        if response.status_code == 200:
            tools = []
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        if 'result' in data and 'tools' in data['result']:
                            tools = data['result']['tools']
                            print(f"[OK] 找到 {len(tools)} 个工具:\n")

                            # 分类显示工具
                            for tool in tools:
                                name = tool.get('name', 'Unknown')
                                description = tool.get('description', 'No description')
                                print(f"  - {name}")
                                print(f"    描述: {description[:80]}")

                                # 如果是编译相关工具，显示参数
                                if any(keyword in name.lower() for keyword in ['console', 'compile', 'error', 'log']):
                                    input_schema = tool.get('inputSchema', {})
                                    properties = input_schema.get('properties', {})
                                    if properties:
                                        print(f"    参数: {', '.join(properties.keys())}")
                                print()

                            break

            return tools

        return []

    def call_tool(self, tool_name, arguments=None):
        """调用工具"""
        print(f"\n=== 调用工具: {tool_name} ===\n")

        headers = {**BASE_HEADERS, 'mcp-session-id': self.session_id}

        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }

        response = requests.post(
            MCP_SERVER,
            json=payload,
            headers=headers,
            timeout=10
        )

        print(f"响应状态: {response.status_code}")

        if response.status_code == 200:
            print(f"响应内容:")
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        if 'result' in data:
                            result = data['result']
                            # 格式化输出
                            if isinstance(result, str):
                                print(result[:3000])
                            else:
                                print(json.dumps(result, indent=2, ensure_ascii=False)[:3000])
                        elif 'error' in data:
                            print(f"错误: {data['error']}")
                        break
        else:
            print(f"请求失败: {response.text}")

        return response.status == 200

def check_compile_errors():
    """检查Unity编译错误"""
    client = MCPUnityClient()

    # 1. 初始化
    if not client.initialize():
        print("[ERROR] 初始化失败")
        return

    # 2. 列出工具
    tools = client.list_tools()

    if not tools:
        print("[ERROR] 无法获取工具列表")
        return

    # 3. 查找编译相关工具
    compile_tools = [t for t in tools if any(keyword in t.get('name', '').lower()
                     for keyword in ['console', 'compile', 'error', 'log'])]

    print(f"\n{'='*50}")
    print(f"找到 {len(compile_tools)} 个编译相关工具")
    print(f"{'='*50}")

    # 4. 调用编译检查工具
    for tool in compile_tools[:5]:  # 最多调用5个工具
        tool_name = tool['name']
        description = tool.get('description', '')

        print(f"\n\n{'='*60}")
        print(f"工具: {tool_name}")
        print(f"描述: {description}")
        print(f"{'='*60}")

        client.call_tool(tool_name, {})

    print(f"\n\n{'='*60}")
    print("[OK] 检查完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    check_compile_errors()
