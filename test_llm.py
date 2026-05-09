import requests
import json
import sys

API_KEY = sys.argv[1] if len(sys.argv) > 1 else input('请输入API Key: ').strip()
CHAT_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'

prompt = '你好，请介绍一下你自己。'
headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
data = {
    'model': 'qwen3.5-plus',
    'input': {'messages': [{'role': 'user', 'content': prompt}]},
    'parameters': {'temperature': 0.5, 'result_format': 'message'}
}

print(f'请求URL: {CHAT_URL}')
print(f'模型: qwen3.5-plus')
print(f'请求中...')
res = requests.post(CHAT_URL, json=data, headers=headers, verify=False, timeout=120)
print(f'状态码: {res.status_code}')
print(f'响应: {json.dumps(res.json(), ensure_ascii=False)[:1000]}')