"""
修复 MCP Unity 配置错误
删除错误的 npm 包配置，使用正确的 Unity MCP 插件
"""
import json
import os
import platform
from pathlib import Path
import sys

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def find_claude_config():
    """查找 Claude Desktop 配置文件"""
    system = platform.system()

    if system == "Windows":
        # Windows: C:\Users\Username\AppData\Roaming\Claude\claude_desktop_config.json
        config_path = Path(os.path.expandvars(r"%APPDATA%\Claude\claude_desktop_config.json"))
    elif system == "Darwin":  # macOS
        # macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        # Linux: ~/.config/Claude/claude_desktop_config.json
        config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

    return config_path

def fix_mcp_config():
    """修复 MCP 配置"""
    print("=== MCP Unity 配置修复工具 ===\n")

    config_path = find_claude_config()
    print(f"配置文件路径: {config_path}\n")

    # 检查配置文件是否存在
    if not config_path.exists():
        print(f"✗ 配置文件不存在: {config_path}")
        print(f"  Claude Desktop 可能未安装")

        # 创建配置目录
        config_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"\n✓ 已创建配置目录: {config_path.parent}")

        # 创建新的配置
        new_config = {
            "mcpServers": {}
        }
    else:
        # 读取现有配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            print(f"✓ 找到现有配置文件")
            new_config = existing_config.copy()
        except Exception as e:
            print(f"✗ 读取配置文件失败: {e}")
            new_config = {"mcpServers": {}}

    # 检查是否有错误的 unity 服务器配置
    if "mcpServers" not in new_config:
        new_config["mcpServers"] = {}

    # 删除错误的 @modelcontextprotocol/server-unity 配置
    servers_to_remove = []
    for server_name, server_config in new_config["mcpServers"].items():
        if "unity" in server_name.lower():
            command = server_config.get("command", "")
            if "@modelcontextprotocol/server-unity" in command:
                servers_to_remove.append(server_name)
                print(f"✓ 找到错误配置: {server_name}")

    # 删除错误配置
    for server_name in servers_to_remove:
        del new_config["mcpServers"][server_name]
        print(f"  已删除: {server_name}")

    # 添加正确的 Unity MCP 配置
    # 使用 MCP 的 stdio 模式连接到 Unity 插件
    unity_server_name = "unity-mcp"
    if unity_server_name not in new_config["mcpServers"]:
        new_config["mcpServers"][unity_server_name] = {
            "command": "python",
            "args": [
                "g:/DYGame/Games/NotColorBlind/LINGMA/configure_unity_mcp.py"
            ]
        }
        print(f"\n✓ 添加正确的 Unity MCP 配置")
    else:
        print(f"\n✓ Unity MCP 配置已存在")

    # 保存配置
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        print(f"\n✓ 配置已保存到: {config_path}")
    except Exception as e:
        print(f"\n✗ 保存配置失败: {e}")
        return False

    # 显示当前配置
    print(f"\n=== 当前 MCP 服务器配置 ===")
    if new_config["mcpServers"]:
        for server_name, server_config in new_config["mcpServers"].items():
            print(f"\n服务器名称: {server_name}")
            print(f"  命令: {server_config.get('command', 'N/A')}")
            args = server_config.get('args', [])
            if args:
                print(f"  参数: {args[0]}...")
    else:
        print("(无配置)")

    return True

def verify_unity_mcp():
    """验证 Unity MCP 插件是否安装"""
    print("\n=== 验证 Unity MCP 插件 ===")

    unity_mcp_path = Path("g:/DYGame/Games/NotColorBlind/Library/PackageCache/com.coplaydev.unity-mcp")

    if unity_mcp_path.exists():
        print(f"✓ Unity MCP 插件已安装")
        print(f"  路径: {unity_mcp_path}")
        return True
    else:
        print(f"✗ Unity MCP 插件未找到")
        print(f"  请在 Unity Editor 中通过 Package Manager 安装:")
        print(f"  https://github.com/CoplayDev/Unity-MCP")
        return False

if __name__ == "__main__":
    print("MCP Unity 配置修复\n")

    # 1. 验证 Unity MCP 插件
    unity_ok = verify_unity_mcp()

    # 2. 修复 MCP 配置
    if fix_mcp_config():
        print("\n" + "=" * 50)
        print("✓ 配置修复完成!")
        print("\n下一步操作:")
        print("1. 确保 Unity Editor 已启动")
        print("2. 在 Unity 中启用 Unity MCP (菜单栏 > Tools > MCP Server)")
        print("3. 重启 Claude Desktop")
        print("4. 验证连接")
    else:
        print("\n✗ 配置修复失败")
