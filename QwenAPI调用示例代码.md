# Qwen API 调用示例代码

本文件提供了调用阿里云通义千问(Qwen)大模型API的示例代码。

## 使用前准备
1. 安装依赖：`pip install dashscope`
2. 获取API密钥：登录阿里云控制台获取
3. 配置环境变量或直接在代码中设置API密钥

## 代码示例

```python
from http import HTTPStatus
import dashscope


def call_with_messages():
    """调用Qwen模型进行对话"""
    # 构建对话消息
    messages = [
        {"role": "system", "content": "你是一个专业的食品安全助手，能够帮助用户分析食品成分和安全性。"},
        {"role": "user", "content": "请分析一下这个食品的营养成分和安全性。"}
    ]

    # 调用Qwen模型API
    responses = dashscope.Generation.call(
        model="qwen3-235B-A22",  # 模型名称
        api_key="sk-9e3579f390d5445a96030fdcd18f3e81",  # API密钥（请替换为您的密钥）
        messages=messages,  # 对话消息列表
        stream=True,  # 启用流式输出
        result_format='message',  # 返回结果格式设置为 message
        top_p=0.8,  # 核采样参数，控制生成文本的多样性
        temperature=0.7,  # 温度参数，控制生成文本的随机性
        enable_search=False,  # 是否启用搜索功能
        enable_thinking=False,  # 是否启用思考模式
        thinking_budget=4000  # 思考预算
    )

    # 处理响应结果
    for response in responses:
        if response.status_code == HTTPStatus.OK:
            # 成功响应，打印结果
            print(response.output.choices[0].message.content)
        else:
            # 错误响应，打印错误信息
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            break


if __name__ == '__main__':
    call_with_messages()
```

## 参数说明

- **model**: 模型名称，这里使用的是 `qwen3-235B-A22`
- **api_key**: 您的API密钥，需要从阿里云控制台获取
- **messages**: 对话消息列表，包含系统提示和用户输入
- **stream**: 是否启用流式输出，建议设为 `True` 以获得更好的用户体验
- **result_format**: 返回结果格式，设为 `message` 格式
- **top_p**: 核采样参数，范围 0-1，值越小生成越确定
- **temperature**: 温度参数，范围 0-2，值越高生成越随机
- **enable_search**: 是否启用联网搜索功能
- **enable_thinking**: 是否启用思考模式
- **thinking_budget**: 思考预算，仅在启用思考模式时有效

## 注意事项

1. **API密钥安全**: 请不要将API密钥硬编码在代码中，建议使用环境变量
2. **错误处理**: 务必处理API调用可能出现的各种错误情况
3. **流量控制**: 注意API调用频率限制，避免超出配额
4. **成本控制**: 大模型调用会产生费用，请合理使用

## 环境变量配置示例

```bash
# 设置环境变量
export DASHSCOPE_API_KEY="your-api-key-here"
```

```python
# 在代码中使用环境变量
import os
api_key = os.getenv('DASHSCOPE_API_KEY')
```