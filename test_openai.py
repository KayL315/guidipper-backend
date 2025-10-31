import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 初始化新版 OpenAI 客户端
client = OpenAI(api_key=api_key)

# 发起请求
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "你好，简单介绍一下北京故宫"}
    ]
)

print("ChatGPT 回复：")
print(response.choices[0].message.content)