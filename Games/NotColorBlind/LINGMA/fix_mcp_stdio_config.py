"""
修复 MCP Unity 配置错误 - 使用正确的 stdio 模式
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
        config_path = Path(os.path.expandvars(r"%APPDATA%\Claude\claude_desktop_config.json"))
    elif system == "Darwin":  # macOS
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

    return config_path

def fix_mcp_config():
    """修复 MCP 配置"""
    print("=== MCP Unity 配置修复工具 ===\n")

    config_path = find_claude_config()
    print(f"配置文件路径: {config_path}\n")

    # 检查配置文件是否存在
    if not config_path.exists():
        print(f"✓ 配置文件不存在，将创建新配置")
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

    # 确保有 mcpServers 字段
    if "mcpServers" not in new_config:
        new_config["mcpServers"] = {}

    # 删除所有旧的 unity 相关配置
    servers_to_remove = []
    for server_name in list(new_config["mcpServers"].keys()):
        if "unity" in server_name.lower():
            servers_to_remove.append(server_name)

    for server_name in servers_to_remove:
        del new_config["mcpServers"][server_name]
        print(f"✓ 已删除旧配置: {server_name}")

    # 添加正确的 Unity MCP 配置
    # 根据文档，使用 uvx 命令启动 MCP 服务器
    unity_server_name = "unity-mcp"

    # 检查 uvx 是否可用
    import shutil
    uvx_path = shutil.which("uvx")

    if uvx_path:
        print(f"\n✓ 找到 uvx: {uvx_path}")
        # 使用 uvx 从 git 安装并运行
        unity_config = {
            "command": "uvx",
            "args": [
                "--from", "mcp-for-unity", "mcp-for-unity"
            ]
        }
    else:
        print(f"\n⚠ 未找到 uvx，尝试使用本地 Python 脚本")
        # 回退到本地 Python 脚本
        python_path = sys.executable
        unity_config = {
            "command": python_path,
            "args": [
                "g:/DYGame/Games/NotColorBlind/LINGMA/configure_unity_mcp.py"
            ]
        }

    new_config["mcpServers"][unity_server_name] = unity_config
    print(f"✓ 添加 Unity MCP 配置")
    print(f"  命令: {unity_config['command']}")
    print(f"  参数: {' '.join(unity_config['args'])}")

    # 保存配置
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        print(f"\n✓ 配置已保存到: {config_path}")
    except Exception as e:
        print(f"\n✗ 保存配置失败: {e}")
        return False

    return True

def main():
    print("MCP Unity 配置修复 (使用 stdio 模式)\n")
    print("=" * 50)

    if fix_mcp_config():
        print("\n" + "=" * 50)
        print("✓ 配置修复完成!")
        print("\n下一步操作:")
        print("1. 确保 Unity Editor 已启动")
        print("2. 在 Unity 中打开 Window > MCP for Unity")
        print("3. 确保状态显示为 'Running'")
        print("4. 重启 Claude Desktop")
        print("5. 验证连接")
        print("\n注意: Unity MCP 插件已安装在项目中:")
        print("  com.coplaydev.unity-mcp@d76a8df311")
    else:
        print("\n✗ 配置修复失败")

if __name__ == "__main__":
    main()
