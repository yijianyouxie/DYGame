#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过Unity MCP检查编译错误
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
                'clientInfo': {'name': 'compile-error-checker', 'version': '1.0.0'}
            }
        }

        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status != 200:
                print(f"✗ 初始化失败: HTTP {response.status}")
                return

            print(f"✓ 会话初始化成功")
            print(f"  Session ID: {session_id}\n")

        # 添加session ID到headers
        headers['mcp-session-id'] = session_id

        # 发送initialized通知
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })

        # 1. 刷新Unity并触发编译
        print("=== 刷新Unity并触发编译 ===\n")
        refresh_request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'refresh_unity',
                'arguments': {
                    'import_assets': False,
                    'compile_scripts': True
                }
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
                                print("✓ 刷新完成:")
                                print(json.dumps(result, indent=2, ensure_ascii=False))
                            break
                        except json.JSONDecodeError:
                            continue

        # 2. 读取控制台错误
        print("\n=== 读取控制台编译错误 ===\n")
        console_request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'read_console',
                'arguments': {
                    'max_count': 50,
                    'message_type': 'error'
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
                                console_data = json.loads(result.get('text', '{}'))
                                messages = console_data.get('messages', [])

                                if not messages:
                                    print("✓ 未发现编译错误")
                                else:
                                    print(f"✓ 发现 {len(messages)} 条错误消息:\n")
                                    for i, msg in enumerate(messages, 1):
                                        msg_type = msg.get('type', 'unknown')
                                        message = msg.get('message', '')
                                        if 'CS' in message:  # 只显示编译错误
                                            print(f"  {i}. [{msg_type}] {message}\n")
                                        elif message:
                                            print(f"  {i}. [{msg_type}] {message}\n")
                            break
                        except json.JSONDecodeError:
                            continue

        # 3. 读取所有控制台消息
        print("\n=== 读取最近所有控制台消息 ===\n")
        all_console_request = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'read_console',
                'arguments': {
                    'max_count': 20
                }
            }
        }

        async with session.post(url, headers=headers, json=all_console_request) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        try:
                            data = json.loads(line_text[5:])
                            result = data.get('result', {})
                            if result:
                                console_data = json.loads(result.get('text', '{}'))
                                messages = console_data.get('messages', [])

                                print(f"✓ 最近 {len(messages)} 条消息:\n")
                                for i, msg in enumerate(messages, 1):
                                    msg_type = msg.get('type', 'unknown')
                                    message = msg.get('message', '')
                                    # 高亮显示错误
                                    if msg_type == 'error':
                                        print(f"  [ERROR] {message}")
                                    elif msg_type == 'warning':
                                        print(f"  [WARN]  {message}")
                                    else:
                                        if message:
                                            print(f"  [INFO]  {message}")
                            break
                        except json.JSONDecodeError:
                            continue

        print("\n" + "=" * 50)
        print("✓ 检查完成!")

asyncio.run(check_compile_errors())
