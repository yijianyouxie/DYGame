#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Unity MCP - 创建testa场景和黄色球体
"""
import asyncio
import aiohttp
import json
import sys
import io

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_unity_mcp():
    """测试Unity MCP连接并创建场景和黄色球体"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # 步骤 1: 初始化获取 Session ID
        print("🔄 步骤1: 初始化连接...")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "unity-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        session_id = None
        async with session.post(url, headers=base_headers, json=init_message) as response:
            session_id = response.headers.get('mcp-session-id')
            print(f"✅ Session ID: {session_id}")
            
            if not session_id:
                print("❌ 无法获取 Session ID")
                return
            
            # 读取响应内容
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        # 步骤 2: 发送 initialized 通知
        print("🔄 步骤2: 发送 initialized 通知...")
        async with session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }) as response:
            print(f"✅ Initialized: {response.status}")
        
        # 步骤 3: 获取工具列表
        print("🔄 步骤3: 获取可用工具列表...")
        async with session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        tools = data.get('result', {}).get('tools', [])
                        print(f"✅ 找到 {len(tools)} 个工具")
                        
                        # 打印所有工具名称
                        for i, tool in enumerate(tools, 1):
                            print(f"  {i}. {tool['name']}")
                        break
        
        # 步骤 4: 创建testa场景
        print("\n🔄 步骤4: 创建testa场景...")
        await asyncio.sleep(0.5)
        
        create_scene_call = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "manage_scene",
                "arguments": {
                    "action": "create",
                    "name": "testa",
                    "path": "Scenes/testa.unity"
                }
            }
        }
        
        async with session.post(url, headers=headers, json=create_scene_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        print(f"✅ 场景创建响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                        break
        
        # 等待场景加载
        print("⏳ 等待场景加载...")
        await asyncio.sleep(1)
        
        # 步骤 5: 创建黄色球体
        print("\n🔄 步骤5: 创建黄色球体...")
        create_sphere_call = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "manage_gameobject",
                "arguments": {
                    "action": "create",
                    "name": "YellowSphere",
                    "primitive_type": "Sphere"
                }
            }
        }
        
        async with session.post(url, headers=headers, json=create_sphere_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        print(f"✅ 球体创建响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                        break
        
        # 等待球体创建
        await asyncio.sleep(0.5)
        
        # 步骤 6: 创建黄色材质
        print("\n🔄 步骤6: 创建黄色材质...")
        create_material_call = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "manage_material",
                "arguments": {
                    "action": "create",
                    "material_path": "Materials/YellowMaterial.mat"
                }
            }
        }
        
        async with session.post(url, headers=headers, json=create_material_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        print(f"✅ 材质创建响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                        break
        
        await asyncio.sleep(0.5)
        
        # 步骤 7: 设置材质颜色为黄色
        print("\n🔄 步骤7: 设置材质颜色为黄色...")
        set_color_call = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "manage_material",
                "arguments": {
                    "action": "set_material_color",
                    "material_path": "Materials/YellowMaterial.mat",
                    "color": "#FFFF00"  # 黄色
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_color_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        print(f"✅ 颜色设置响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                        break
        
        await asyncio.sleep(0.5)
        
        # 步骤 8: 应用材质到球体
        print("\n🔄 步骤8: 应用材质到球体...")
        apply_material_call = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "manage_material",
                "arguments": {
                    "action": "assign_material_to_renderer",
                    "target": "YellowSphere",
                    "search_method": "by_name",
                    "material_path": "Materials/YellowMaterial.mat"
                }
            }
        }
        
        async with session.post(url, headers=headers, json=apply_material_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        print(f"✅ 材质应用响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                        break
        
        # 步骤 9: 保存场景
        print("\n🔄 步骤9: 保存场景...")
        save_scene_call = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "manage_scene",
                "arguments": {
                    "action": "save"
                }
            }
        }
        
        async with session.post(url, headers=headers, json=save_scene_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        print(f"✅ 场景保存响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                        break
        
        print("\n✅ 完成！testa场景已创建，包含一个黄色球体")

if __name__ == "__main__":
    asyncio.run(test_unity_mcp())
