import asyncio
import aiohttp
import json

async def create_button_correct():
    """使用正确的 MCP 方法创建排行榜按钮"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 使用正确的 MCP 方法创建排行榜按钮 ===\n")
        
        try:
            # ========== 初始化连接 ==========
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "button-creator",
                        "version": "1.0.0"
                    }
                }
            }
            
            session_id = None
            async with session.post(url, headers=base_headers, json=init_message) as response:
                session_id = response.headers.get('mcp-session-id')
                print(f"✅ Session ID: {session_id}")
                
                if not session_id:
                    return
                
                if response.status == 200:
                    async for line in response.content:
                        if line.decode('utf-8').strip().startswith('data:'):
                            break
            
            headers_with_session = {**base_headers, 'mcp-session-id': session_id}
            
            await session.post(url, headers=headers_with_session, json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            
            # ========== 步骤 1: 创建 GameObject（使用 create 动作） ==========
            print("\n📐 步骤 1: 创建空 GameObject...")
            
            create_empty_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "LeaderboardButton",
                        "parent": "Canvas"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_empty_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            
                            if 'result' in data:
                                tools_result = data['result']
                                content_list = tools_result.get('content', [])
                                
                                if content_list and len(content_list) > 0:
                                    content_item = content_list[0]
                                    text_content = content_item.get('text', '')
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ 空 GameObject 创建成功!")
                                            print(f"   📍 路径：Canvas/LeaderboardButton")
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ⚠️ 创建失败：{error_msg}")
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                                        print(f"   原始响应：{text_content[:200]}")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 2: 添加 Button 组件 ==========
            print("\n🔧 步骤 2: 添加 Button 组件...")
            
            add_button_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "add",
                        "target": "LeaderboardButton",
                        "search_method": "by_name",
                        "component_type": "Button"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_button_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            
                            if 'result' in data:
                                tools_result = data['result']
                                content_list = tools_result.get('content', [])
                                
                                if content_list and len(content_list) > 0:
                                    content_item = content_list[0]
                                    text_content = content_item.get('text', '')
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ Button 组件添加成功!")
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ⚠️ 添加失败：{error_msg}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.5)
            
            print("\n=== ✅ 按钮基础结构创建完成 ===")
            print("\n⚠️ 由于 MCP 工具的限制，需要手动完成以下步骤:")
            print("\n📋 手动配置步骤:")
            print("1. 在 Unity Hierarchy 中:")
            print("   • 展开 Canvas")
            print("   • 应该能看到 LeaderboardButton")
            print()
            print("2. 为 LeaderboardButton 添加子对象 Text:")
            print("   • 右键 LeaderboardButton → UI → Text")
            print("   • 重命名为 Text")
            print()
            print("3. 设置按钮属性:")
            print("   • 选中 LeaderboardButton")
            print("   • 在 Inspector 的 RectTransform 中:")
            print("     - Anchor: Top Right (1, 1)")
            print("     - Pivot: (0.5, 0.5)")
            print("     - Pos X: -50, Pos Y: -30")
            print("     - Width: 80, Height: 40")
            print()
            print("4. 设置 Text 属性:")
            print("   • Text: 排行榜")
            print("   • Font: FZLTH-GBK (Assets/Font/FZLTH-GBK.TTF)")
            print("   • Font Size: 18")
            print("   • Alignment: Center")
            print()
            print("5. 在 MainMenuController 中绑定按钮:")
            print("   • 选中 Canvas（挂载 MainMenuController 的对象）")
            print("   • 在 Inspector 的 MainMenuController 组件中")
            print("   • 将 LeaderboardButton 拖入 leaderboardButton 字段")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_button_correct())
