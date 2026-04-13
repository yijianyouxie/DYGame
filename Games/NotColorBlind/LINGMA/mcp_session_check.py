"""
通过MCP Unity获取session并检查编译错误（修复版本）
"""
import requests
import json
import time
import uuid

MCP_SERVER = "http://127.0.0.1:8080/mcp"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

class MCPClient:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.initialized = False

    def send_request(self, method, params=None, request_id=None):
        """发送MCP请求"""
        if request_id is None:
            request_id = int(time.time() * 1000)

        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        # 尝试在URL中添加session参数
        url_with_session = f"{MCP_SERVER}?session={self.session_id}"

        response = requests.post(
            url_with_session,
            json=payload,
            headers=HEADERS,
            timeout=10
        )

        return response

    def parse_sse_response(self, text):
        """解析Server-Sent Events格式的响应"""
        lines = text.strip().split('\n')
        result = None
        error = None

        for line in lines:
            line = line.strip()
            if line.startswith('data: '):
                data_str = line[6:]  # 去掉 'data: ' 前缀
                try:
                    data = json.loads(data_str)
                    if 'result' in data:
                        result = data['result']
                    elif 'error' in data:
                        error = data['error']
                except json.JSONDecodeError:
                    pass

        return result, error

    def initialize(self):
        """初始化"""
        print("=== 初始化MCP Unity Server ===\n")

        response = self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "compile-check",
                "version": "1.0"
            }
        })

        print(f"初始化响应状态: {response.status_code}")
        print(f"响应内容（前500字符）: {response.text[:500]}")

        result, error = self.parse_sse_response(response.text)

        if error:
            print(f"初始化错误: {error}")
            return False

        if result:
            print(f"\n初始化成功!")
            print(f"服务器信息: {result.get('serverInfo', {})}")

            # 发送initialized通知
            initialized_resp = self.send_request("notifications/initialized", request_id=None)
            print(f"Initialized通知响应: {initialized_resp.status_code}")

            self.initialized = True
            return True

        return False

    def list_tools(self):
        """列出可用工具"""
        print("\n=== 列出可用工具 ===\n")

        response = self.send_request("tools/list", {})

        print(f"工具列表响应状态: {response.status_code}")

        result, error = self.parse_sse_response(response.text)

        if error:
            print(f"获取工具列表错误: {error}")
            return []

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

    def call_tool(self, tool_name, arguments=None):
        """调用工具"""
        print(f"\n=== 调用工具: {tool_name} ===\n")

        payload = {
            "name": tool_name,
            "arguments": arguments or {}
        }

        response = self.send_request("tools/call", payload)

        print(f"响应状态: {response.status_code}")
        print(f"响应内容（前3000字符）:")
        print(response.text[:3000])

        result, error = self.parse_sse_response(response.text)

        if error:
            print(f"\n工具调用错误: {error}")

        if result:
            print(f"\n工具返回结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        return result, error

def main():
    client = MCPClient()

    # 初始化
    if client.initialize():
        # 列出工具
        tools = client.list_tools()

        if tools:
            # 查找编译相关工具
            compile_tools = [t for t in tools if 'console' in t.get('name', '').lower() or
                            'compile' in t.get('name', '').lower() or
                            'error' in t.get('name', '').lower() or
                            'log' in t.get('name', '').lower()]

            print(f"\n=== 编译相关工具 ===\n")
            print(f"找到 {len(compile_tools)} 个编译相关工具")

            # 调用编译相关工具
            for tool in compile_tools[:3]:  # 最多调用前3个工具
                tool_name = tool['name']
                print(f"\n{'='*50}")
                client.call_tool(tool_name, {})

    print("\n" + "="*50)
    print("检查完成")

if __name__ == "__main__":
    main()
