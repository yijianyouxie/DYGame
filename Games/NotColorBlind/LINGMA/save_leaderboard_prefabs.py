import asyncio
import aiohttp
import json

async def save_prefabs():
    """将 Hierarchy 中的 GameObject 保存为 Prefab 文件"""
    
    url = "http://127.0.0.1:8080/mcp"
    
    headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 开始保存预制件 ===\n")
        
        try:
            # 步骤 1: 初始化
            print("🔌 连接到 MCP Unity 服务器...")
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "prefab-saver",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=init_message) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print("✅ 连接成功\n")
                            break
            
            # 步骤 2: 发送 initialized 通知
            initialized_message = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            async with session.post(url, headers=headers, json=initialized_message) as response:
                pass
            
            # 步骤 3: 检查 Prefabs 文件夹是否存在
            print("📁 检查 Assets/Prefabs 文件夹...")
            check_folder_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manage_asset",
                    "arguments": {
                        "action": "exists",
                        "path": "Assets/Prefabs"
                    }
                }
            }
            
            folder_exists = False
            async with session.post(url, headers=headers, json=check_folder_message) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'content' in data['result']:
                                folder_exists = True
                                print("✅ Assets/Prefabs 文件夹已存在")
                            else:
                                print("❌ Assets/Prefabs 文件夹不存在")
                            break
            
            # 如果文件夹不存在，创建它
            if not folder_exists:
                print("\n📁 创建 Assets/Prefabs 文件夹...")
                create_folder_message = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_asset",
                        "arguments": {
                            "action": "create_folder",
                            "path": "Assets/Prefabs"
                        }
                    }
                }
                
                async with session.post(url, headers=headers, json=create_folder_message) as response:
                    if response.status == 200:
                        print("✅ Assets/Prefabs 文件夹创建成功")
            
            # 步骤 4: 将 LeaderboardPanel 保存为预制件
            print("\n💾 保存 LeaderboardPanel 为预制件...")
            save_panel_message = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "save_as_prefab",
                        "path": "LeaderboardPanel",
                        "asset_path": "Assets/Prefabs/LeaderboardPanel.prefab"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=save_panel_message) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"⚠️ 保存 LeaderboardPanel 失败：{data['error']}")
                                print("提示：请在 Unity 中手动操作")
                            else:
                                print("✅ LeaderboardPanel.prefab 保存成功")
                            break
                else:
                    print(f"⚠️ 保存失败：{response.status}")
            
            # 步骤 5: 将 RankItemPrefab 保存为预制件
            print("\n💾 保存 RankItemPrefab 为预制件...")
            save_item_message = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "save_as_prefab",
                        "path": "RankItemPrefab",
                        "asset_path": "Assets/Prefabs/RankItemPrefab.prefab"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=save_item_message) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"⚠️ 保存 RankItemPrefab 失败：{data['error']}")
                                print("提示：请在 Unity 中手动操作")
                            else:
                                print("✅ RankItemPrefab.prefab 保存成功")
                            break
                else:
                    print(f"⚠️ 保存失败：{response.status}")
            
            # 步骤 6: 验证预制件是否创建成功
            print("\n🔍 验证预制件是否创建成功...")
            
            for prefab_name in ["LeaderboardPanel.prefab", "RankItemPrefab.prefab"]:
                prefab_path = f"Assets/Prefabs/{prefab_name}"
                check_message = {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_asset",
                        "arguments": {
                            "action": "exists",
                            "path": prefab_path
                        }
                    }
                }
                
                async with session.post(url, headers=headers, json=check_message) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'result' in data and 'content' in data['result']:
                                    print(f"✅ {prefab_name} 已成功创建")
                                else:
                                    print(f"❌ {prefab_name} 未找到")
                                break
            
            print("\n=== ✅ 预制件保存完成 ===\n")
            print("📋 检查结果：")
            print("1. 在 Unity Project 窗口中查看 Assets/Prefabs 目录")
            print("2. 应该看到以下预制件文件:")
            print("   • LeaderboardPanel.prefab")
            print("   • RankItemPrefab.prefab")
            print()
            print("如果预制件未自动创建，请使用 Unity 编辑器手动操作：")
            print("方法 1: 在 Hierarchy 中右键 GameObject → Create Prefab")
            print("方法 2: 直接拖拽 GameObject 到 Project 窗口的 Assets/Prefabs 文件夹")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(save_prefabs())
