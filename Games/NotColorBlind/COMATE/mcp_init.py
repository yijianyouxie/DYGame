"""
Unity MCP 初始化脚本
用于初始化与Unity MCP的连接
目录: COMATE
"""
import requests
import json
import os

# 配置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

MCP_URL = 'http://localhost:8080'
SESSION_FILE = os.path.join(BASE_DIR, 'mcp-session-id.txt')
CONFIG_FILE = os.path.join(BASE_DIR, 'mcp_config.json')

# 全局session ID
SESSION_ID = None

def init_session():
    """初始化MCP会话"""
    global SESSION_ID
    try:
        resp = requests.post(f'{MCP_URL}/initialize')
        SESSION_ID = resp.headers.get('mcp-session-id')
        print(f'[OK] Session ID: {SESSION_ID}')
        return SESSION_ID
    except Exception as e:
        print(f'[FAIL] 初始化失败: {e}')
        return None

def save_session():
    """保存session配置"""
    if SESSION_ID:
        with open(SESSION_FILE, 'w') as f:
            f.write(SESSION_ID)
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'server_url': MCP_URL,
                'session_id': SESSION_ID
            }, f, indent=2)
        print(f'[OK] 配置已保存')
        return True
    return False

def call_tool(tool_name, arguments):
    """调用MCP工具"""
    if not SESSION_ID:
        init_session()
    
    resp = requests.post(
        f'{MCP_URL}/tools/call',
        headers={
            'Content-Type': 'application/json',
            'mcp-session-id': SESSION_ID
        },
        json={
            'name': tool_name,
            'arguments': arguments
        }
    )
    return resp.json()

def get_tools():
    """获取可用工具列表"""
    if not SESSION_ID:
        init_session()
    
    resp = requests.get(
        f'{MCP_URL}/tools',
        headers={'mcp-session-id': SESSION_ID}
    )
    tools = resp.json().get('tools', [])
    return tools

if __name__ == '__main__':
    print('=== Unity MCP 初始化 ===')
    init_session()
    save_session()

    print('\n可用工具:')
    tools = get_tools()
    for t in tools:
        print(f'  - {t.get("name")}')

    print('\n[OK] 配置完成!')
