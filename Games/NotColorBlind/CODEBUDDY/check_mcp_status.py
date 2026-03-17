import asyncio
import aiohttp
import json

async def init_session(session, url):
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': {}
    }
    
    async with session.post(url, headers={'Content-Type': 'application/json'}, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                if data.get('result', {}).get('session_id'):
                    return data['result']['session_id']
        return None

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
    async with aiohttp.ClientSession() as session:
        print("测试MCP连接...")
        try:
            session_id = await init_session(session, url)
            if session_id:
                print(f"[+] 连接成功，session_id: {session_id}")
            else:
                print("[!] 连接失败，无法获取session_id")
        except Exception as e:
            print(f"[!] 连接异常: {e}")

if __name__ == '__main__':
    asyncio.run(main())
