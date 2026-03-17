# MCP 工具使用最终结论

## 🔍 问题根源分析

### 用户提供的修复方案 ❌ 不完全正确

用户指出：
- 工具名应该是 `manage_gameobject` ❌ **错误**
- 参数应该是 `name` 而不是 `search_term` ❌ **错误**

### 实际 MCP 服务器的响应 ✅

```
❌ 错误：Missing required parameter 'action'. 
Valid actions: create, modify, delete, duplicate, move_relative. 
To SEARCH for GameObjects use the find_gameobjects tool. 
To manage COMPONENTS use the manage_components tool.
```

**正确理解**：
1. **搜索对象** → 使用 `find_gameobjects` 工具 ✅
2. **管理对象结构** → 使用 `manage_gameobject` 工具（需要 action 参数）
3. **管理组件** → 使用 `manage_components` 工具

---

##  正确的工具使用方式

### 1. find_gameobjects - 用于搜索对象

```python
{
  "name": "find_gameobjects",
  "arguments": {
    "search_term": "Canvas",
    "search_method": "by_name"  # 或 by_path
  }
}
```

**返回格式**（实际测试）：
```json
{
  "success": true,
  "data": {
    "instanceIDs": [24836],  // ← 只返回 IDs，不返回 gameObjects
    "pageSize": 50,
    "cursor": 0
  }
}
```

**问题**：返回的数据**不包含** `gameObjects` 字段！

### 2. manage_gameobject - 用于操作对象结构

```python
{
  "name": "manage_gameobject",
  "arguments": {
    "action": "duplicate",  // ← 必需参数
    "target": "Canvas/Button",
    "search_method": "by_path"
  }
}
```

**用途**：
- `create` - 创建新对象
- `duplicate` - 复制对象 ✅（已验证有效）
- `modify` - 修改对象
- `delete` - 删除对象
- `move_relative` - 移动对象

### 3. manage_components - 用于操作组件

```python
{
  "name": "manage_components",
  "arguments": {
    "action": "set_property",
    "target": "LeaderboardButton",
    "search_method": "by_name",
    "component_type": "RectTransform",
    "property": "sizeDelta",
    "value": {"x": 80, "y": 40}
  }
}
```

**用途**：
- `add` - 添加组件
- `remove` - 移除组件
- `set_property` - 设置属性 ✅（已验证有效）
- `get_property` - 获取属性

---

## 💡 为什么之前的脚本"看起来"有效？

### ✅ 已验证成功的操作

```python
# 1. 复制按钮
manage_gameobject.duplicate(
  target="Canvas/Button",      # ← 使用 by_path
  search_method="by_path"
)

# 2. 设置属性
manage_components.set_property(
  target="LeaderboardButton",  # ← 使用 by_name
  search_method="by_name"
)
```

这些操作**确实有效**，因为：
1. 使用了正确的工具（`manage_gameobject`、`manage_components`）
2. 使用了正确的参数结构
3. 路径是精确的（`by_path`）

### ❌ 失败的搜索操作

```python
# 尝试搜索对象
find_gameobjects(
  search_term="Canvas",
  search_method="by_name"
)
# 返回：{"instanceIDs": [24836]}  ← 只有 ID，没有详细信息
```

**问题**：
- `find_gameobjects` 只返回 `instanceIDs`
- 代码期望 `gameObjects` 字段
- 无法获取对象的详细信息（名称、路径等）

---

## 📋 实际测试结果

### 测试 1：使用 find_gameobjects 搜索
```
🔍 搜索：'Canvas'
❌ 响应：{"instanceIDs": [24836]}
⚠️ 问题：没有 gameObjects 字段，无法获取详细信息
```

### 测试 2：使用 manage_gameobject.duplicate
```
📋 复制：Canvas/Button
✅ 成功：创建了 LeaderboardButton
```

### 测试 3：使用 manage_components.set_property
```
📋 设置属性：LeaderboardButton
✅ 成功：修改了 RectTransform.sizeDelta
```

---

## 🎯 最终结论

### MCP 工具能力

**✅ 可行的操作**：
1. 使用 `manage_gameobject` + `by_path` 进行结构操作
2. 使用 `manage_components` + `by_name`/`by_path` 设置组件属性
3. 使用 `find_gameobjects` 获取对象 instanceID

**❌ 不可行的操作**：
1. 使用 `find_gameobjects` 获取对象详细信息（只有 IDs）
2. 列出场景中的所有对象
3. 遍历场景层级结构

### 推荐工作流程

1. **用户在 Unity 中查看 Hierarchy**
2. **提供精确路径给 MCP**
3. **MCP 使用 `manage_gameobject` 或 `manage_components` 操作**

```python
# ✅ 标准工作流程
manage_gameobject.duplicate(
  target="Canvas/Button",      # 用户提供的精确路径
  search_method="by_path"
)

manage_components.set_property(
  target="LeaderboardButton",
  search_method="by_name",
  component_type="RectTransform",
  property="sizeDelta",
  value={"x": 80, "y": 40}
)
```

---

## 🔧 对于排行榜按钮 Text 修改

由于 MCP 无法自动找到 Text 子对象，建议：

### 方案 A：手动修改（推荐）
1. 在 Unity 中选中 `Canvas/LeaderboardButton/Text`
2. 在 Inspector 中修改 Text 为"排行榜"

### 方案 B：提供精确路径
如果知道 Text 的确切路径：
```python
manage_components.set_property(
  target="Canvas/LeaderboardButton/Text",
  search_method="by_path",
  component_type="Text",
  property="text",
  value="排行榜"
)
```

---

*创建时间：2026-03-16*
*结论：MCP 工具能正常操作对象，但搜索功能有限，需要用户提供精确路径*
