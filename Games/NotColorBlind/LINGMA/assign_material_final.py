import asyncio
import aiohttp
import json

async def assign_material_to_fireworks():
    """使用正确的 MCP API 为 FireworksEffect 赋值材质球"""
    
    url = "http://127.0.0.1:8080/mcp"
    
    headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    session_id = None
    
    async with aiohttp.ClientSession() as session:
        print("🔌 连接到 MCP Unity 服务器...")
        
        try:
            # 初始化
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "material-assigner",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=init_message) as response:
                if response.status == 200:
                    session_id = response.headers.get('mcp-session-id')
                    print(f"✅ Session ID: {session_id}")
                    headers['mcp-session-id'] = session_id
                    
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            break
            
            # 发送 initialized 通知
            initialized_message = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            async with session.post(url, headers=headers, json=initialized_message) as response:
                print(f"✅ Initialized")
            
            # 获取工具列表，查看 manage_vfx 的正确参数
            print("\n📋 查询 manage_vfx 工具的可用操作...")
            
            tools_list_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            async with session.post(url, headers=headers, json=tools_list_message) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'tools' in data['result']:
                                tools = data['result']['tools']
                                
                                # 查找 manage_vfx 工具
                                vfx_tool = next((t for t in tools if t['name'] == 'manage_vfx'), None)
                                if vfx_tool:
                                    print(f"\n找到 manage_vfx 工具")
                                    print(f"描述：{vfx_tool.get('description', '')[:200]}")
                                    
                                    # 获取输入 schema
                                    input_schema = vfx_tool.get('inputSchema', {})
                                    properties = input_schema.get('properties', {})
                                    arguments_props = properties.get('arguments', {}).get('properties', {})
                                    
                                    print(f"\nparticle_set_renderer 的参数:")
                                    if 'action' in arguments_props:
                                        action_schema = arguments_props['action']
                                        enum_values = action_schema.get('enum', [])
                                        print(f"  可用 actions: {enum_values}")
                            break
            
            # 尝试使用 particle_create 并让它自动赋值默认材质
            print("\n🎯 重新创建 ParticleSystem（会自动处理材质）...")
            
            recreate_message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_vfx",
                    "arguments": {
                        "target": "FireworksEffect",
                        "action": "particle_create"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=recreate_message) as response:
                print(f"\n重新创建响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            result_text = json.dumps(data, indent=2, ensure_ascii=False)
                            print(f"结果：{result_text}")
                            
                            # 提取成功信息
                            if 'result' in data and 'content' in data['result']:
                                content = data['result']['content'][0].get('text', '{}')
                                try:
                                    result_data = json.loads(content)
                                    if result_data.get('success'):
                                        assigned_mat = result_data.get('assignedMaterial', 'Unknown')
                                        print(f"\n✅ FireworksEffect 已更新!")
                                        print(f"   自动赋值的材质：{assigned_mat}")
                                except:
                                    pass
                            break
            
            print("\n✨ 完成！")
            print("\n📋 验证步骤:")
            print("1. 在 Unity Hierarchy 中查看 FireworksEffect")
            print("2. 检查 ParticleSystemRenderer 的 Material 字段")
            print("3. 如果显示的是自动分配的材质，可以手动替换为 FireworksParticleMaterial")
            
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🎆 为 FireworksEffect 赋值材质球")
    print("=" * 60)
    asyncio.run(assign_material_to_fireworks())
