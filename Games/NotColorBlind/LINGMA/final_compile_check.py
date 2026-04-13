#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过Unity MCP检查编译错误（最终版）
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

        # 读取控制台错误
        print("=== 读取Unity控制台错误 ===\n")
        console_request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'read_console',
                'arguments': {}
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

                                # 统计错误
                                errors = [m for m in messages if m.get('type') == 'error']
                                warnings = [m for m in messages if m.get('type') == 'warning']
                                infos = [m for m in messages if m.get('type') == 'info']

                                print(f"控制台消息统计:")
                                print(f"  错误: {len(errors)}")
                                print(f"  警告: {len(warnings)}")
                                print(f"  信息: {len(infos)}\n")

                                if errors:
                                    print("发现编译错误:")
                                    for i, err in enumerate(errors, 1):
                                        print(f"\n  错误 {i}:")
                                        print(f"  {err.get('message', 'Unknown error')}")
                                else:
                                    print("✓ 未发现编译错误")

                                # 显示编译相关的错误（包含CS的）
                                compile_errors = [m for m in messages if 'CS' in m.get('message', '')]
                                if compile_errors:
                                    print(f"\n✓ 发现 {len(compile_errors)} 条编译错误:")
                                    for i, err in enumerate(compile_errors, 1):
                                        print(f"\n  {i}. {err.get('message', 'Unknown')}")

                                break
                        except json.JSONDecodeError:
                            continue

        # 尝试验证一个脚本
        print("\n=== 验证LeaderboardManager.cs ===\n")
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
                                validation_data = json.loads(result_text)
                                diagnostics = validation_data.get('diagnostics', [])

                                print(f"诊断信息: {len(diagnostics)} 条")

                                if diagnostics:
                                    print("\n诊断结果:")
                                    for diag in diagnostics:
                                        severity = diag.get('severity', 'unknown')
                                        message = diag.get('message', '')
                                        print(f"  [{severity}] {message}")
                                else:
                                    print("✓ 脚本验证通过，无诊断信息")

                                break
                        except json.JSONDecodeError:
                            continue

        print("\n" + "=" * 50)
        print("✓ 检查完成!")

if __name__ == "__main__":
    asyncio.run(check_compile_errors())
