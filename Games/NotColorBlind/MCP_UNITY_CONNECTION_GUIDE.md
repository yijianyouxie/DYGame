# Unity MCP 服务器连接与使用指南

## 📋 目录
- [环境配置](#环境配置)
- [MCP 服务器启动](#mcp-服务器启动)
- [Python 脚本连接 MCP](#python-脚本连接-mcp)
- [常用工具调用示例](#常用工具调用示例)
- [故障排查](#故障排查)

---

## 🔧 环境配置

### 软件版本
- **Unity**: Tuanjie 2022.3.2t13
- **IDE**: VS Code
- **MCP 插件**: 灵码 (Unity MCP 工具)
- **Python**: 3.13.5
- **MCP 服务器端口**: `8080`

### Unity MCP 插件安装
1. 在 Unity 中打开：Window > MCP for Unity
2. 点击 "Auto-Setup" 自动配置
3. 确保 Unity Bridge 状态为 "Running"
4. MCP 服务器会自动启动在 `http://127.0.0.1:8080`

---

## 🚀 MCP 服务器启动

### 方法 1：通过 Unity 自动启动
```
Unity Menu > Window > MCP for Unity > Start Local HTTP Server
```

### 方法 2：手动启动（使用项目中的脚本）
```powershell
# Windows PowerShell
.\init_mcp.ps1
```

或执行批处理文件：
```batch
init_mcp.bat
```

### 验证服务器运行状态
```bash
# 检查 8080 端口是否被占用
netstat -ano | findstr :8080
```

正常输出应显示：
```
TCP    127.0.0.1:8080         0.0.0.0:0              LISTENING       [PID]
```

---

## 🐍 Python 脚本连接 MCP

### 基础连接模板

```python
import asyncio
import aiohttp
import json

async def connect_to_mcp():
    """连接到 Unity MCP 服务器的基础模板"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # 步骤 1: 初始化并获取 Session ID
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "your-client-name",
                    "version": "1.0.0"
                }
            }
        }
        
        session_id = None
        async with session.post(url, headers=base_headers, json=init_message) as response:
            # 关键：从响应头中获取 Session ID
            session_id = response.headers.get('mcp-session-id')
            print(f"✅ Session ID: {session_id}")
            
            if not session_id:
                print("❌ 无法获取 Session ID")
                return
            
            # 等待初始化完成
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        # 步骤 2: 发送 initialized 通知
        headers_with_session = {**base_headers, 'mcp-session-id': session_id}
        initialized_message = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        async with session.post(url, headers=headers_with_session, json=initialized_message) as response:
            print(f"✅ Initialized: {response.status}")
        
        # 现在可以开始调用工具了
        # 示例：获取工具列表
        tools_list = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        async with session.post(url, headers=headers_with_session, json=tools_list) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        tools = data['result']['tools']
                        print(f"✅ 找到 {len(tools)} 个工具")
                        
                        # 打印所有工具名称
                        for i, tool in enumerate(tools, 1):
                            print(f"{i}. {tool['name']}")
                        break

if __name__ == "__main__":
    asyncio.run(connect_to_mcp())
```

### 关键要点

1. **Session ID 必须保存**：每次初始化的 Session ID 都不同，必须在初始化后立即保存
2. **所有后续请求都要携带 Session ID**：缺少会导致 400 错误
3. **SSE 流式响应**：MCP 使用 Server-Sent Events，需要异步读取流式数据
4. **参数名称必须精确**：不能使用近似名称（如 `asset_path` 应为 `path`）

---

## 🛠️ 常用工具调用示例

### 1. 创建场景

```python
create_scene_call = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "manage_scene",
        "arguments": {
            "action": "create",
            "name": "MyScene",
            "path": "Scenes/MyScene.unity"
        }
    }
}
```

### 2. 创建 GameObject（球体）

```python
create_sphere_call = {
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
        "name": "manage_gameobject",
        "arguments": {
            "action": "create",
            "name": "RedSphere",
            "primitive_type": "Sphere"
        }
    }
}
```

可用的 primitive_type:
- `Sphere` - 球体
- `Cube` - 立方体
- `Cylinder` - 圆柱体
- `Capsule` - 胶囊体
- `Plane` - 平面
- `Quad` - 四边形

### 3. 创建材质

```python
create_material_call = {
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
        "name": "manage_material",
        "arguments": {
            "action": "create",
            "material_path": "Materials/MyMaterial.mat"
        }
    }
}
```

### 4. 设置材质颜色

```python
set_color_call = {
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
        "name": "manage_material",
        "arguments": {
            "action": "set_material_color",
            "material_path": "Materials/MyMaterial.mat",
            "color": "#FF0000"  # 红色
        }
    }
}
```

颜色格式支持：
- Hex: `"#FF0000"`
- RGB: `"rgb(255, 0, 0)"`
- RGBA: `"rgba(255, 0, 0, 1.0)"`

### 5. 应用材质到 GameObject

```python
apply_material_call = {
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
        "name": "manage_material",
        "arguments": {
            "action": "assign_material_to_renderer",
            "target": "RedSphere",
            "search_method": "by_name",
            "material_path": "Materials/MyMaterial.mat"
        }
    }
}
```

注意：
- `action` 必须是 `"assign_material_to_renderer"`（不是 `"assign_material"`）
- `search_method` 必须是 `"by_name"`（不是 `"name"`）

### 6. 保存场景

```python
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
```

### 7. 删除资产

```python
delete_asset_call = {
    "jsonrpc": "2.0",
    "id": 9,
    "method": "tools/call",
    "params": {
        "name": "manage_asset",
        "arguments": {
            "action": "delete",
            "path": "Scenes/MyScene.unity"
        }
    }
}
```

注意：参数是 `path` 而不是 `asset_path`

### 8. 查找 GameObject

```python
find_objects_call = {
    "jsonrpc": "2.0",
    "id": 10,
    "method": "tools/call",
    "params": {
        "name": "find_gameobjects",
        "arguments": {
            "search_term": "Sphere",
            "search_method": "name"
        }
    }
}
```

可用的 search_method:
- `name` - 按名称搜索
- `tag` - 按标签搜索
- `layer` - 按层级搜索
- `component` - 按组件类型搜索
- `path` - 按路径搜索

---

## 📦 完整工作流程示例

### 创建场景 + 球体 + 红色材质

```python
import asyncio
import aiohttp
import json

async def create_scene_with_red_sphere():
    """完整示例：创建场景、球体和红色材质"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # 1. 初始化获取 Session ID
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "demo", "version": "1.0.0"}
            }
        }
        
        session_id = None
        async with session.post(url, headers=base_headers, json=init_message) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        if not session_id:
            print("❌ 无法获取 Session ID")
            return
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        # 2. 发送 initialized
        await session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })
        
        # 3. 创建场景
        await session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "manage_scene",
                "arguments": {"action": "create", "name": "TestScene", "path": "Scenes/TestScene.unity"}
            }
        })
        
        await asyncio.sleep(1)  # 等待场景加载
        
        # 4. 创建球体
        await session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "manage_gameobject",
                "arguments": {"action": "create", "name": "RedSphere", "primitive_type": "Sphere"}
            }
        })
        
        await asyncio.sleep(0.5)
        
        # 5. 创建红色材质
        await session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "manage_material",
                "arguments": {"action": "create", "material_path": "RedMaterial.mat"}
            }
        })
        
        await asyncio.sleep(0.5)
        
        # 6. 设置颜色
        await session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "manage_material",
                "arguments": {"action": "set_material_color", "material_path": "RedMaterial.mat", "color": "#FF0000"}
            }
        })
        
        await asyncio.sleep(0.5)
        
        # 7. 应用材质
        await session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "manage_material",
                "arguments": {
                    "action": "assign_material_to_renderer",
                    "target": "RedSphere",
                    "search_method": "by_name",
                    "material_path": "RedMaterial.mat"
                }
            }
        })
        
        # 8. 保存场景
        await session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "manage_scene",
                "arguments": {"action": "save"}
            }
        })
        
        print("✅ 完成！场景已创建并保存")

if __name__ == "__main__":
    asyncio.run(create_scene_with_red_sphere())
```

---

## 🔍 故障排查

### 问题 1: 400 Bad Request - Missing session ID

**原因**: 请求头中缺少 `mcp-session-id`

**解决方法**: 
```python
# 初始化时必须保存 Session ID
session_id = response.headers.get('mcp-session-id')

# 后续所有请求都要携带
headers = {**base_headers, 'mcp-session-id': session_id}
```

### 问题 2: 参数验证错误

**原因**: 使用了错误的参数名称或枚举值

**解决方法**:
1. 先查询工具定义确认参数名
2. 严格匹配枚举值（区分下划线和驼峰）

示例：
- ✅ `primitive_type` (正确)
- ❌ `primitiveType` (错误)

- ✅ `assign_material_to_renderer` (正确)
- ❌ `assign_material` (错误)

- ✅ `by_name` (正确)
- ❌ `name` (错误)

### 问题 3: 连接超时

**原因**: MCP 服务器未启动或端口被占用

**解决方法**:
```bash
# 检查端口
netstat -ano | findstr :8080

# 如果端口被占用，杀死进程
taskkill /F /PID [PID]

# 重新启动 MCP 服务器
```

### 问题 4: 工具调用失败 - Unknown tool

**原因**: 工具名称错误

**解决方法**: 先查询工具列表
```python
tools_list = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}
```

常见工具名称：
- ✅ `manage_gameobject` (不是 `manage_game_object`)
- ✅ `manage_scene`
- ✅ `manage_material`
- ✅ `manage_asset`

---

## 📝 快速参考卡片

### 连接流程
```
1. POST /mcp (initialize) → 获取 mcp-session-id
2. POST /mcp (notifications/initialized)
3. 开始调用工具...
```

### 请求头格式
```python
headers = {
    "Accept": "application/json,text/event-stream",
    "Content-Type": "application/json",
    "mcp-session-id": "你的 session-id"
}
```

### JSON-RPC 消息格式
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "工具名称",
    "arguments": {
      "参数名": "参数值"
    }
  }
}
```

### 响应格式（SSE）
```
event: message
data: {"jsonrpc":"2.0","id":1,"result":{...}}
```

---

## 🎯 新对话快速启动清单

在新对话中，只需提供以下信息即可快速开始：

- [ ] Unity MCP 服务器已在 `http://127.0.0.1:8080` 启动
- [ ] 使用上述 Python 模板代码
- [ ] 替换 `clientInfo` 中的客户端名称
- [ ] 保存返回的 Session ID
- [ ] 开始调用工具！

---

## 📚 相关资源

- 项目位置：`g:\DYGame\Games\NotColorBlind`
- Unity 版本：Tuanjie 2022.3.2t13
- MCP 插件：com.coplaydev.unity-mcp@d76a8df311
- Python 版本：3.13.5

---

*最后更新：2026-03-06*
