"""
Unity MCP 示例 - 创建UI元素
演示如何使用MCP在Unity中创建按钮和文本框
目录: COMATE
"""
import requests
import json
import os

# 导入初始化模块
from mcp_init import init_session, call_tool, SESSION_ID

def list_scene_objects(path=''):
    """列出场景中的对象"""
    result = call_tool('manage_gameobject', {
        'action': 'list',
        'path': path
    })
    return result

def create_button(name='MyButton', parent_path=''):
    """
    创建UI按钮
    
    参数:
        name: 按钮名称
        parent_path: 父对象路径（空=根目录）
    """
    print(f'创建按钮: {name}')
    result = call_tool('manage_gameobject', {
        'action': 'create',
        'path': parent_path,
        'name': name,
        'type': 'Button'  # Unity Button类型
    })
    return result

def create_text(name='MyText', parent_path=''):
    """
    创建UI文本
    
    参数:
        name: 文本对象名称
        parent_path: 父对象路径
    """
    print(f'创建文本: {name}')
    result = call_tool('manage_gameobject', {
        'action': 'create',
        'path': parent_path,
        'name': name,
        'type': 'Text'  # Unity Text类型
    })
    return result

def set_property(path, property_name, value):
    """设置对象属性"""
    result = call_tool('manage_gameobject', {
        'action': 'set_property',
        'path': path,
        'property': property_name,
        'value': value
    })
    return result

def get_object_info(path):
    """获取对象信息"""
    result = call_tool('manage_gameobject', {
        'action': 'get',
        'path': path
    })
    return result

if __name__ == '__main__':
    print('=== Unity MCP 示例 - 创建UI元素 ===\n')
    
    # 1. 初始化
    init_session()
    
    # 2. 列出当前场景对象
    print('\n--- 当前场景对象 ---')
    objects = list_scene_objects()
    print(json.dumps(objects, indent=2, ensure_ascii=False))
    
    # 3. 创建按钮示例
    print('\n--- 创建按钮 ---')
    btn_result = create_button('TestButton')
    print(json.dumps(btn_result, indent=2, ensure_ascii=False))
    
    # 4. 创建文本示例
    print('\n--- 创建文本 ---')
    txt_result = create_text('TestText')
    print(json.dumps(txt_result, indent=2, ensure_ascii=False))
    
    print('\n✓ 示例执行完成!')
