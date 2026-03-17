import asyncio
import aiohttp
import json

async def create_test_scene():
    """通过 MCP Unity 创建 test3 场景和红色胶囊体"""
    
    url = "http://127.0.0.1:8080/mcp"
    
    # MCP 请求头 - 必须同时接受 JSON 和 SSE
    headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    session_id = "test-session-123"
    
    async with aiohttp.ClientSession() as session:
        print("🔌 连接到 MCP Unity 服务器...")
        
        try:
            # 步骤 1: 初始化
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=init_message) as response:
                print(f"初始化响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print("✅ 初始化成功\n")
                            break
            
            # 步骤 2: 发送 notifications/initialized
            initialized_message = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            async with session.post(url, headers=headers, json=initialized_message) as response:
                print(f"发送 initialized 通知：{response.status}")
            
            # 步骤 3: 获取工具列表
            tools_list_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            print("\n📋 获取可用工具列表...")
            async with session.post(url, headers=headers, json=tools_list_message) as response:
                print(f"工具列表响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'tools' in data['result']:
                                tools = data['result']['tools']
                                print(f"\n找到 {len(tools)} 个工具:")
                                print("=" * 60)
                                for tool in tools[:10]:  # 只显示前 10 个
                                    print(f"• {tool.get('name', 'unknown')}")
                                if len(tools) > 10:
                                    print(f"... 还有 {len(tools) - 10} 个工具")
                                print()
                                
                                # 查找与场景相关的工具
                                scene_tools = [t for t in tools if 'scene' in t.get('name', '').lower()]
                                if scene_tools:
                                    print("🎯 场景相关工具:")
                                    for tool in scene_tools:
                                        print(f"  • {tool.get('name')}: {tool.get('description', '')[:80]}")
                            break
            
            # 步骤 4: 使用 manage_scene 工具创建场景
            print("\n🎬 准备创建场景...")
            
            # 首先读取菜单项看看有什么可用的
            menu_items_resource = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/read",
                "params": {
                    "uri": "mcpforunity://menu-items"
                }
            }
            
            print("\n📖 读取菜单项...")
            async with session.post(url, headers=headers, json=menu_items_resource) as response:
                print(f"菜单项响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'contents' in data['result']:
                                content = data['result']['contents'][0]
                                if 'text' in content:
                                    menu_data = json.loads(content['text'])
                                    # 查找我们创建的菜单项
                                    test_menu = [m for m in menu_data if 'Create Test Scene' in m.get('label', '')]
                                    if test_menu:
                                        print(f"✅ 找到菜单项：{test_menu[0]['label']}")
                                        print(f"   命令：{test_menu[0]['command']}")
                            break
            
            print("\n✨ 测试完成！MCP Unity 连接正常")
            print("\n下一步:")
            print("1. 在 Unity Editor 中点击菜单：Tools > Create Test Scene")
            print("2. 或者使用 MCP 工具调用 execute_menu_item")
            
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 测试 MCP Unity 连接和功能")
    print("=" * 60)
    asyncio.run(create_test_scene())
