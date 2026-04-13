#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查指定的编译错误
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def check_compile_errors():
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json, text/event-stream',
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        # 初始化
        print("=== 初始化MCP会话 ===\n")
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'error-checker', 'version': '1.0.0'}
            }
        }

        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status != 200:
                print(f"✗ 初始化失败: HTTP {response.status}")
                return

            print(f"✓ 会话初始化成功")
            print(f"  Session ID: {session_id}\n")

        headers['mcp-session-id'] = session_id

        # 发送initialized通知
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })

        # 刷新Unity以获取最新的编译状态
        print("=== 刷新Unity ===\n")
        refresh_request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'refresh_unity',
                'arguments': {}
            }
        }

        async with session.post(url, headers=headers, json=refresh_request) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        try:
                            data = json.loads(line_text[5:])
                            result = data.get('result', {})
                            if result:
                                print("✓ 刷新完成\n")
                            break
                        except json.JSONDecodeError:
                            continue

        # 验证脚本
        print("=== 验证LeaderboardManager.cs ===\n")
        validate_request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'validate_script',
                'arguments': {
                    'uri': 'Assets/Scripts/LeaderboardManager.cs'
                }
            }
        }

        async with session.post(url, headers=headers, json=validate_request) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        try:
                            data = json.loads(line_text[5:])
                            result = data.get('result', {})
                            if result:
                                result_text = result.get('text', '')
                                print(f"验证结果:\n{result_text}\n")
                            break
                        except json.JSONDecodeError:
                            continue

        # 读取控制台所有消息
        print("=== 读取控制台所有消息 ===\n")
        console_request = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'read_console',
                'arguments': {
                    'max_count': 100
                }
            }
        }

        async with session.post(url, headers=headers, json=console_request) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        try:
                            data = json.loads(line_text[5:])
                            result = data.get('result', {})
                            if result:
                                console_text = result.get('text', '')
                                console_data = json.loads(console_text)
                                messages = console_data.get('messages', [])

                                print(f"共 {len(messages)} 条消息:\n")

                                for i, msg in enumerate(messages, 1):
                                    msg_type = msg.get('type', 'unknown')
                                    message = msg.get('message', '')

                                    if message:
                                        if msg_type == 'error':
                                            print(f"  [ERROR {i}] {message}\n")
                                        elif msg_type == 'warning':
                                            print(f"  [WARN {i}] {message}\n")
                                        else:
                                            if 'error' in message.lower() or 'CS' in message:
                                                print(f"  [INFO {i}] {message}\n")

                            break
                        except json.JSONDecodeError:
                            continue

        print("\n" + "=" * 50)
        print("✓ 检查完成!")

if __name__ == "__main__":
    asyncio.run(check_compile_errors())
