import asyncio
import aiohttp
import json

async def setup_fireworks_material():
    """为 FireworksEffect 创建并配置合适的材质球，然后重新生成 FireworksEffect Prefab"""
    
    url = "http://127.0.0.1:8080/mcp"
    
    # MCP 请求头 - 必须同时接受 JSON 和 SSE
    headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    session_id = None
    
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
                        "name": "fireworks-material-setup",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=init_message) as response:
                if response.status == 200:
                    # 获取 session ID
                    session_id = response.headers.get('mcp-session-id')
                    print(f"✅ 初始化成功，Session ID: {session_id}")
                    
                    # 添加 session ID 到后续请求头
                    headers['mcp-session-id'] = session_id
                    
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            break
            
            # 步骤 2: 发送 notifications/initialized
            initialized_message = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            async with session.post(url, headers=headers, json=initialized_message) as response:
                print(f"✅ 发送 initialized 通知：{response.status}")
            
            # 步骤 3: 使用 manage_asset 更新/创建材质球
            print("\n🎨 创建/更新 FireworksParticleMaterial 材质球...")
            
            manage_asset_message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_asset",
                    "arguments": {
                        "action": "create",
                        "asset_type": "material",
                        "path": "Assets/Effects/FireworksParticleMaterial.mat"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=manage_asset_message) as response:
                print(f"\n创建材质响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                result = data['result']
                                content = result.get('content', [{}])[0].get('text', '')
                                if content:
                                    try:
                                        content_data = json.loads(content)
                                        if content_data.get('success'):
                                            print(f"✅ 材质创建成功!")
                                            print(f"   路径：{content_data.get('data', {}).get('path')}")
                                            print(f"   GUID: {content_data.get('data', {}).get('guid')}")
                                            print(f"   名称：{content_data.get('data', {}).get('name')}")
                                            print(f"\n💡 提示：材质已创建，但需要通过 manage_vfx 工具在粒子系统中使用")
                                    except Exception as e:
                                        print(f"   结果：{content}")
                                    break
            
            # 步骤 4: 使用 manage_vfx 的 particle_create 来创建并自动赋值材质
            print("\n🎯 使用 manage_vfx 创建 FireworksEffect GameObject（会自动赋值材质）...")
            
            # 首先删除旧的 FireworksEffect（如果存在）
            delete_old_message = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "delete",
                        "target": "FireworksEffect"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=delete_old_message) as response:
                print(f"清理旧对象响应：{response.status}")
            
            # 创建新的 FireworksEffect
            create_vfx_message = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "manage_vfx",
                    "arguments": {
                        "target": "FireworksEffect",
                        "action": "particle_create",
                        "materialPath": "Assets/Effects/FireworksParticleMaterial.mat"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=create_vfx_message) as response:
                print(f"\n创建 ParticleSystem 响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print(f"创建结果：{json.dumps(data, indent=2, ensure_ascii=False)}")
                            
                            if 'result' in data and 'content' in data['result']:
                                content = data['result']['content'][0].get('text', '{}')
                                try:
                                    result_data = json.loads(content)
                                    if result_data.get('success'):
                                        print(f"\n✅ FireworksEffect 创建成功!")
                                        if result_data.get('assignedMaterial'):
                                            print(f"   已自动赋值材质：{result_data.get('assignedMaterial')}")
                                except:
                                    pass
                            break
            
            # 步骤 5: 配置粒子系统的主要参数
            print("\n⚙️ 配置粒子系统参数...")
            
            # 配置主模块
            config_main_message = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "manage_vfx",
                    "arguments": {
                        "target": "FireworksEffect",
                        "action": "particle_set_main",
                        "duration": 1.0,
                        "looping": False,
                        "startLifetime": {"min": 0.5, "max": 1.5},
                        "startSpeed": {"min": 5, "max": 15},
                        "startSize": {"min": 0.2, "max": 0.5},
                        "startColor": [1.0, 1.0, 1.0, 1.0],
                        "gravityModifier": 0.5,
                        "maxParticles": 200
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=config_main_message) as response:
                print(f"配置主模块响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                content = data['result'].get('content', [{}])[0].get('text', '{}')
                                try:
                                    result = json.loads(content)
                                    if result.get('success'):
                                        print(f"✅ 主模块配置完成：{result.get('message', '')}")
                                except:
                                    pass
                            break
            
            # 配置发射模块
            config_emission_message = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "manage_vfx",
                    "arguments": {
                        "target": "FireworksEffect",
                        "action": "particle_set_emission",
                        "rateOverTime": {"min": 0, "max": 100}
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=config_emission_message) as response:
                print(f"配置发射模块响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                content = data['result'].get('content', [{}])[0].get('text', '{}')
                                try:
                                    result = json.loads(content)
                                    if result.get('success'):
                                        print(f"✅ 发射模块配置完成：{result.get('message', '')}")
                                except:
                                    pass
                            break
            
            # 配置形状模块
            config_shape_message = {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {
                    "name": "manage_vfx",
                    "arguments": {
                        "target": "FireworksEffect",
                        "action": "particle_set_shape",
                        "shapeType": "Sphere",
                        "radius": 0.5
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=config_shape_message) as response:
                print(f"配置形状模块响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                content = data['result'].get('content', [{}])[0].get('text', '{}')
                                try:
                                    result = json.loads(content)
                                    if result.get('success'):
                                        print(f"✅ 形状模块配置完成：{result.get('message', '')}")
                                except:
                                    pass
                            break
            
            # 配置颜色渐变
            config_color_message = {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {
                    "name": "manage_vfx",
                    "arguments": {
                        "target": "FireworksEffect",
                        "action": "particle_set_color_over_lifetime",
                        "enabled": True,
                        "gradient": {
                            "colorKeys": [
                                {"color": [1.0, 0.8, 0.2, 1.0], "time": 0.0},  # 金黄色
                                {"color": [1.0, 0.4, 0.2, 1.0], "time": 0.5},  # 橙红色
                                {"color": [0.8, 0.2, 0.5, 1.0], "time": 1.0}   # 紫红色
                            ],
                            "alphaKeys": [
                                {"alpha": 1.0, "time": 0.0},
                                {"alpha": 0.8, "time": 0.5},
                                {"alpha": 0.0, "time": 1.0}
                            ]
                        }
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=config_color_message) as response:
                print(f"配置颜色渐变响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                content = data['result'].get('content', [{}])[0].get('text', '{}')
                                try:
                                    result = json.loads(content)
                                    if result.get('success'):
                                        print(f"✅ 颜色渐变配置完成：{result.get('message', '')}")
                                except:
                                    pass
                            break
            
            # 步骤 6: 使用 particle_set_renderer 显式赋值材质球
            print("\n🎯 为粒子系统赋值 FireworksParticleMaterial...")
            
            set_renderer_message = {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": "manage_vfx",
                    "arguments": {
                        "target": "FireworksEffect",
                        "action": "particle_set_renderer",
                        "materialPath": "Assets/Effects/FireworksParticleMaterial.mat"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=set_renderer_message) as response:
                print(f"\n设置 Renderer 响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print(f"Renderer 设置结果：{json.dumps(data, indent=2, ensure_ascii=False)}")
                            
                            if 'result' in data and 'content' in data['result']:
                                content = data['result']['content'][0].get('text', '{}')
                                try:
                                    result = json.loads(content)
                                    if result.get('success'):
                                        print(f"\n✅ 材质球已成功赋值给 FireworksEffect!")
                                        print(f"   消息：{result.get('message', '')}")
                                except Exception as e:
                                    print(f"解析结果时出错：{e}")
                            break
            
            print("\n✨ 完成！FireworksEffect 已创建并配置好材质球")
            print("\n📋 下一步操作:")
            print("1. 在 Unity Editor 中查看 Hierarchy 中的 FireworksEffect GameObject")
            print("2. 检查 ParticleSystemRenderer 组件的 Material 字段")
            print("3. 确认材质球显示为 FireworksParticleMaterial")
            print("4. 运行游戏测试烟花效果")
            print("\n💡 提示：如需保存为 Prefab，可在 Hierarchy 中右键 FireworksEffect > Prefab > Create")
            
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🎆 配置 FireworksEffect 材质球和粒子系统")
    print("=" * 60)
    asyncio.run(setup_fireworks_material())
