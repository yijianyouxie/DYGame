#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过Unity MCP连接并检查编译错误
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class UnityMCPClient:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = f"{base_url}/mcp"
        self.session_id = None
        self.headers = {
            'Accept': 'application/json, text/event-stream',
            'Content-Type': 'application/json'
        }

    async def initialize(self):
        """初始化MCP会话"""
        print("=== 初始化Unity MCP会话 ===\n")

        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'compile-checker', 'version': '1.0.0'}
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=self.headers, json=init_msg) as response:
                if response.status != 200:
                    print(f"✗ 初始化失败: HTTP {response.status}")
                    return False

                # 从响应头获取session ID
                self.session_id = response.headers.get('mcp-session-id')
                if not self.session_id:
                    print("✗ 无法获取session ID")
                    return False

                print(f"✓ 会话初始化成功")
                print(f"  Session ID: {self.session_id}\n")

                # 发送initialized通知
                await session.post(
                    self.base_url,
                    headers={**self.headers, 'mcp-session-id': self.session_id},
                    json={
                        'jsonrpc': '2.0',
                        'method': 'notifications/initialized',
                        'params': {}
                    }
                )

                return True

    async def list_tools(self):
        """列出可用工具"""
        print("=== 列出可用工具 ===\n")

        request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/list',
            'params': {}
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                headers={**self.headers, 'mcp-session-id': self.session_id},
                json=request
            ) as response:
                if response.status != 200:
                    print(f"✗ 获取工具列表失败: HTTP {response.status}")
                    return None

                # 读取SSE响应
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        try:
                            data = json.loads(line_text[5:])
                            tools = data.get('result', {}).get('tools', [])
                            print(f"✓ 找到 {len(tools)} 个工具:\n")
                            for i, tool in enumerate(tools, 1):
                                name = tool.get('name', '未知')
                                desc = tool.get('description', '无描述')[:80]
                                print(f"  {i}. {name}")
                                print(f"     {desc}...\n")
                            return tools
                        except json.JSONDecodeError:
                            continue

        return None

    async def get_compile_errors(self):
        """获取编译错误"""
        print("=== 获取Unity编译错误 ===\n")

        # 先尝试直接获取编译状态
        request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'get_console',
                'arguments': {
                    'mode': 'compile_errors'
                }
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                headers={**self.headers, 'mcp-session-id': self.session_id},
                json=request
            ) as response:
                if response.status != 200:
                    print(f"✗ 获取编译错误失败: HTTP {response.status}")
                    print(f"  响应: {await response.text()[:200]}")
                    return None

                # 读取SSE响应
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        try:
                            data = json.loads(line_text[5:])
                            result = data.get('result', {})

                            if not result:
                                print("✓ 未发现编译错误")
                            else:
                                print("✓ 编译错误信息:")
                                print(json.dumps(result, indent=2, ensure_ascii=False))

                            return result
                        except json.JSONDecodeError:
                            continue

        return None

    async def check_compilation_status(self):
        """检查编译状态"""
        print("=== 检查编译状态 ===\n")

        request = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'compile_project',
                'arguments': {}
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                headers={**self.headers, 'mcp-session-id': self.session_id},
                json=request
            ) as response:
                if response.status != 200:
                    print(f"✗ 检查编译状态失败: HTTP {response.status}")
                    print(f"  响应: {await response.text()[:200]}")
                    return None

                # 读取SSE响应
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        try:
                            data = json.loads(line_text[5:])
                            result = data.get('result', {})

                            print("✓ 编译状态:")
                            print(json.dumps(result, indent=2, ensure_ascii=False))

                            return result
                        except json.JSONDecodeError:
                            continue

        return None

async def main():
    client = UnityMCPClient()

    # 初始化
    if not await client.initialize():
        print("\n✗ 无法连接到Unity MCP服务器")
        print("请确保:")
        print("  1. Unity Editor已启动")
        print("  2. Unity MCP插件已加载")
        print("  3. MCP服务器正在运行 (http://127.0.0.1:8080)")
        return

    # 列出工具
    tools = await client.list_tools()

    # 获取编译错误
    compile_errors = await client.get_compile_errors()

    # 检查编译状态
    status = await client.check_compilation_status()

    print("\n" + "=" * 50)
    print("✓ 检查完成!")

if __name__ == "__main__":
    asyncio.run(main())
