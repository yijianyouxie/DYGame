import aiohttp
import asyncio
import json

async def query_mcp_tools():
    async with aiohttp.ClientSession() as session:
        # List available tools
        response = await session.post(
            'http://localhost:39880/mcp',
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
        )
        
        tools = await response.json()
        
        # Find manage_scene and manage_gameobject tools
        manage_scene = None
        manage_gameobject = None
        manage_components = None
        
        for tool in tools['result']['tools']:
            if tool['name'] == 'manage_scene':
                manage_scene = tool
            elif tool['name'] == 'manage_gameobject':
                manage_gameobject = tool
            elif tool['name'] == 'manage_components':
                manage_components = tool
        
        print("=" * 80)
        print("MANAGE_SCENE TOOL PARAMETERS:")
        print("=" * 80)
        print(json.dumps(manage_scene, indent=2))
        
        print("\n" + "=" * 80)
        print("MANAGE_GAMEOBJECT TOOL PARAMETERS:")
        print("=" * 80)
        print(json.dumps(manage_gameobject, indent=2))
        
        print("\n" + "=" * 80)
        print("MANAGE_COMPONENTS TOOL PARAMETERS:")
        print("=" * 80)
        print(json.dumps(manage_components, indent=2))

if __name__ == "__main__":
    asyncio.run(query_mcp_tools())
