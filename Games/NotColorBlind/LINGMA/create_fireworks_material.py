import asyncio
import aiohttp
import json

async def create_fireworks_material():
    """通过 MCP Unity 在 Assets/Materials 下创建 FireworksMaterial 材质球"""
    
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
                        "name": "material-creator",
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
            
            # 步骤 3: 使用 manage_asset 工具创建材质
            print("\n🎨 使用 manage_asset 创建材质球...")
            
            # 尝试使用 manage_asset 创建材质
            manage_asset_message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_asset",
                    "arguments": {
                        "action": "create",
                        "asset_type": "material",
                        "path": "Assets/Materials/FireworksMaterial.mat"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=manage_asset_message) as response:
                print(f"\n调用 manage_asset 响应：{response.status}")
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print(f"结果：{json.dumps(data, indent=2, ensure_ascii=False)}")
                            
                            if 'result' in data and 'content' in data['result']:
                                content = data['result']['content'][0]
                                if 'text' in content:
                                    result_text = content['text']
                                    print(f"\n详细信息：{result_text}")
                            break
            
            print("\n✨ 完成！")
            
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🎨 创建 FireworksMaterial 材质球")
    print("=" * 60)
    asyncio.run(create_fireworks_material())
