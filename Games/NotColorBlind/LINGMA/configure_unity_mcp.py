"""
Unity MCP 配置和连接脚本
用于配置Unity MCP并建立连接
"""
import requests
import json
import sys

# Unity MCP 配置
MCP_CONFIG = {
    "server_url": "http://localhost:8080",
    "timeout": 10,
    "session_id": None
}

def check_server_status():
    """检查MCP服务器状态"""
    print("=== 检查Unity MCP服务器状态 ===")
    try:
        response = requests.get(
            f"{MCP_CONFIG['server_url']}/health",
            timeout=MCP_CONFIG['timeout']
        )
        if response.status_code == 200:
            print(f"✓ MCP服务器运行正常")
            print(f"  响应: {response.text[:100]}")
            return True
        else:
            print(f"✗ MCP服务器响应异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ 无法连接到MCP服务器 {MCP_CONFIG['server_url']}")
        print(f"  请确认Unity MCP已启动并监听端口8080")
        return False
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

def initialize_session():
    """初始化MCP会话"""
    print("\n=== 初始化MCP会话 ===")
    try:
        response = requests.post(
            f"{MCP_CONFIG['server_url']}/initialize",
            timeout=MCP_CONFIG['timeout']
        )

        if response.status_code == 200:
            session_id = response.headers.get('mcp-session-id')
            if session_id:
                MCP_CONFIG['session_id'] = session_id
                print(f"✓ 会话初始化成功")
                print(f"  Session ID: {session_id}")

                # 保存session ID到文件
                with open('mcp-session-id.txt', 'w') as f:
                    f.write(session_id)
                print(f"  Session ID已保存到 mcp-session-id.txt")

                return True
            else:
                print(f"✗ 响应中未找到Session ID")
                return False
        else:
            print(f"✗ 初始化失败: HTTP {response.status_code}")
            print(f"  响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return False

def get_available_tools():
    """获取可用的工具列表"""
    print("\n=== 获取可用工具 ===")
    if not MCP_CONFIG['session_id']:
        print("✗ 需要先初始化会话")
        return False

    try:
        response = requests.get(
            f"{MCP_CONFIG['server_url']}/tools",
            headers={"mcp-session-id": MCP_CONFIG['session_id']},
            timeout=MCP_CONFIG['timeout']
        )

        if response.status_code == 200:
            tools_data = response.json()
            tools = tools_data.get('tools', [])
            print(f"✓ 成功获取 {len(tools)} 个工具:")
            for i, tool in enumerate(tools, 1):
                name = tool.get('name', '未知')
                desc = tool.get('description', '无描述')[:60]
                print(f"  {i}. {name}: {desc}...")
            return True
        else:
            print(f"✗ 获取工具列表失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 获取工具列表失败: {e}")
        return False

def test_connection():
    """测试连接并获取场景信息"""
    print("\n=== 测试连接 ===")
    if not MCP_CONFIG['session_id']:
        print("✗ 需要先初始化会话")
        return False

    try:
        # 尝试列出游戏对象
        response = requests.post(
            f"{MCP_CONFIG['server_url']}/tools/call",
            headers={
                "Content-Type": "application/json",
                "mcp-session-id": MCP_CONFIG['session_id']
            },
            json={
                "name": "manage_gameobject",
                "arguments": {
                    "action": "list",
                    "path": ""
                }
            },
            timeout=MCP_CONFIG['timeout']
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ 连接测试成功")
            print(f"  成功获取场景中的游戏对象列表")
            return True
        else:
            print(f"✗ 连接测试失败: HTTP {response.status_code}")
            print(f"  响应: {response.text[:300]}")
            return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False

def save_config():
    """保存配置到文件"""
    config_file = "mcp_config.json"
    try:
        with open(config_file, 'w') as f:
            json.dump({
                "server_url": MCP_CONFIG['server_url'],
                "timeout": MCP_CONFIG['timeout'],
                "session_id": MCP_CONFIG['session_id']
            }, f, indent=2)
        print(f"✓ 配置已保存到 {config_file}")
        return True
    except Exception as e:
        print(f"✗ 保存配置失败: {e}")
        return False

def main():
    """主配置流程"""
    print("Unity MCP 配置工具")
    print("=" * 50)

    # 1. 检查服务器状态
    if not check_server_status():
        print("\n✗ 配置失败: MCP服务器未运行")
        print("  请在Unity Editor中启动Unity MCP")
        sys.exit(1)

    # 2. 初始化会话
    if not initialize_session():
        print("\n✗ 配置失败: 无法初始化会话")
        sys.exit(1)

    # 3. 获取可用工具
    if not get_available_tools():
        print("\n⚠ 警告: 无法获取工具列表，但会话可能正常")

    # 4. 测试连接
    if not test_connection():
        print("\n⚠ 警告: 连接测试失败，但会话已初始化")

    # 5. 保存配置
    save_config()

    print("\n" + "=" * 50)
    print("✓ Unity MCP 配置完成!")
    print(f"  服务器地址: {MCP_CONFIG['server_url']}")
    print(f"  Session ID: {MCP_CONFIG['session_id']}")
    print("\n现在可以使用MCP与Unity进行交互了")

if __name__ == "__main__":
    main()
