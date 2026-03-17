# MCP find_gameobjects 调试报告

## 🎯 问题根源

**发现关键问题**：MCP 的 `find_gameobjects` 工具返回的数据结构**不包含 `gameObjects` 字段**！

### 实际响应格式
```json
{
  "success": true,
  "message": "Found GameObjects",
  "data": {
    "instanceIDs": [24836],  // ← 只有这个字段
    "pageSize": 50,
    "cursor": 0,
    "nextCursor": null,
    "totalCount": 1,
    "hasMore": false
  }
}
```

### 期望的响应格式（代码中）
```json
{
  "success": true,
  "message": "Found GameObjects",
  "data": {
    "gameObjects": [  // ← 期望这个字段
      {
        "name": "Canvas",
        "path": "Canvas",
        "instanceID": 24836
      }
    ]
  }
}
```

---

## ✅ 已验证的功能

### 1. find_gameobjects 能正常工作
```python
# ✅ 成功找到对象
search_term: "Canvas"
search_method: "by_path"
# 返回：{"instanceIDs": [24836]}
```

### 2. 支持多种 search_method
```python
# ✅ 已测试有效
"by_name"   # 按名称搜索
"by_path"   # 按路径搜索（最可靠）
```

### 3. manage_gameobject 能操作对象
```python
# ✅ 之前成功复制了按钮
manage_gameobject.duplicate(
  target="Canvas/Button",
  search_method="by_path"
)
```

---

## ❌ 问题所在

### 代码解析错误

之前的代码期望响应包含 `gameObjects` 字段：
```python
objects = result.get('data', {}).get('gameObjects', [])  # ❌ 这个字段不存在！
```

实际应该解析 `instanceIDs`：
```python
instance_ids = result.get('data', {}).get('instanceIDs', [])  # ✅ 正确
```

---

## 💡 解决方案

### 方案 1：使用 instanceIDs 进行后续操作

既然 `find_gameobjects` 返回 `instanceIDs`，可以使用这些 ID 进行后续操作：

```python
# 步骤 1：查找对象获取 instanceID
find_call = {
  "name": "find_gameobjects",
  "arguments": {
    "search_term": "Canvas/Button",
    "search_method": "by_path"
  }
}
# 返回：{"instanceIDs": [24856]}

# 步骤 2：使用 manage_gameobject 操作
# 但问题是：manage_gameobject 不支持 by_instance_id 搜索方式
```

**问题**：`manage_gameobject` 不支持 `by_instance_id` 搜索方式

### 方案 2：继续使用 by_path（推荐）

既然 `by_path` 已经能正常工作，应该继续使用：

```python
# ✅ 已经验证有效
manage_gameobject.duplicate(
  target="Canvas/Button",
  search_method="by_path"
)

manage_components.set_property(
  target="LeaderboardButton",
  search_method="by_name"  # 或 by_path
)
```

---

## 📊 测试结果汇总

### 步骤 1：获取可用工具 ✅
```
✅ 可用工具 (31 个):
   • find_gameobjects
   • manage_gameobject
   • manage_components
   • manage_asset
   • manage_scene
   ... 等
```

### 步骤 2：使用 by_path 访问已知对象 ✅
```
✅ Canvas        → instanceIDs: [24836]
✅ Canvas/Button → instanceIDs: [24856]
✅ Main Camera   → instanceIDs: [24828]
✅ Directional Light → instanceIDs: [24806]
✅ EventSystem   → instanceIDs: [24812]
```

### 步骤 3：使用 by_name 搜索 ✅
```
✅ Main Camera → instanceIDs: [24828]
✅ Canvas      → instanceIDs: [24836]
✅ Button      → instanceIDs: [24856]
```

### 步骤 4：获取所有对象 ❌
```
❌ search_term: "", search_method: "all" 
   → JSON 解析错误
❌ search_term: "", search_method: "by_name"
   → 缺少必需的 search_term 参数
```

---

## 🎯 结论

### MCP 工具能力

**✅ 可行的操作**：
1. 使用 `by_path` 精确定位对象
2. 使用 `by_name` 搜索对象
3. 使用 `manage_gameobject` 进行结构操作（create/duplicate/move_relative）
4. 使用 `manage_components` 设置组件属性

**❌ 不可行的操作**：
1. 获取场景中所有对象的列表
2. 遍历场景层级结构
3. 使用 `instanceIDs` 进行后续操作（因为不支持 `by_instance_id`）
4. 获取对象的详细信息（名称、路径等）

### 推荐工作流程

1. **用户在 Unity 中查看 Hierarchy**
2. **提供精确路径给 MCP**
3. **MCP 使用 `by_path` 进行操作**

```python
# ✅ 标准工作流程
manage_gameobject.duplicate(
  target="Canvas/Button",      # 用户提供的精确路径
  search_method="by_path"      # 使用 by_path 确保精确匹配
)

manage_components.set_property(
  target="LeaderboardButton",  # 新创建的对象
  search_method="by_name",     # 使用 by_name 查找
  component_type="RectTransform",
  property="sizeDelta",
  value={"x": 80, "y": 40}
)
```

---

## 📝 对于排行榜按钮 Text 修改的建议

由于 MCP 无法自动找到 Text 子对象，建议：

### 方案 A：手动修改（推荐）
1. 在 Unity 中选中 `Canvas/LeaderboardButton/Text`
2. 在 Inspector 中修改 Text 为"排行榜"

### 方案 B：提供精确路径
如果知道 Text 的确切路径，可以直接使用：
```python
manage_components.set_property(
  target="Canvas/LeaderboardButton/Text",  # 精确路径
  search_method="by_path",
  component_type="Text",
  property="text",
  value="排行榜"
)
```

---

*调试时间：2026-03-16*
*调试结论：MCP 能正常操作对象，但无法列出场景层级，需要用户提供精确路径*
