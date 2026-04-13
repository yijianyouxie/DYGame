"""
等待编译完成并检查错误
"""
import requests
import json
import time

MCP_SERVER = "http://127.0.0.1:8080/mcp"
BASE_HEADERS = {
    "Accept": "application/json,text/event-stream",
    "Content-Type": "application/json"
}

def wait_for_compile_and_check():
    """等待编译完成并检查错误"""
    print("=== 初始化 ===\n")

    # 初始化获取session
    init_response = requests.post(
        MCP_SERVER,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "compile-check", "version": "1.0"}
            }
        },
        headers=BASE_HEADERS,
        timeout=10
    )

    session_id = init_response.headers.get('mcp-session-id')
    print(f"[OK] Session ID: {session_id}")

    headers = {**BASE_HEADERS, 'mcp-session-id': session_id}

    # 发送 initialized
    requests.post(
        MCP_SERVER,
        json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        headers=headers,
        timeout=10
    )

    # 触发编译
    print("\n=== 触发编译 ===\n")
    refresh_response = requests.post(
        MCP_SERVER,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "refresh_unity",
                "arguments": {
                    "force_script_compile": True
                }
            }
        },
        headers=headers,
        timeout=10
    )

    print(f"刷新响应状态: {refresh_response.status_code}")

    # 等待编译完成（10秒）
    print("\n等待编译完成 (10秒)...\n")
    for i in range(10):
        time.sleep(1)
        print(f".", end="", flush=True)
    print()

    # 检查编译错误
    print("\n=== 检查编译错误 ===\n")
    console_response = requests.post(
        MCP_SERVER,
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "read_console",
                "arguments": {
                    "action": "get",
                    "types": ["error"]
                }
            }
        },
        headers=headers,
        timeout=10
    )

    print(f"控制台响应状态: {console_response.status_code}")

    if console_response.status_code == 200:
        for line in console_response.iter_lines():
            if line:
                line_text = line.decode('utf-8').strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    if 'result' in data:
                        result = data['result']
                        structuredContent = result.get('structuredContent', {})
                        error_data = structuredContent.get('data', [])

                        if error_data:
                            print(f"\n{'='*60}")
                            print(f"发现 {len(error_data)} 个编译错误:")
                            print(f"{'='*60}\n")
                            for error in error_data:
                                print(f"  - {error}\n")
                        else:
                            print("\n[SUCCESS] 没有编译错误！编译成功！")
                        break

if __name__ == "__main__":
    wait_for_compile_and_check()
