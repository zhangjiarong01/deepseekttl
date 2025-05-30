import requests
import json
from volcengine.auth.SignerV4 import SignerV4
from volcengine.Credentials import Credentials

# 替换为你的密钥
ak = '你的AK'
sk = '你的SK'
region = 'cn-north-1'
service = 'volc_tts'

# 创建 Credentials 对象（必须传 3 个参数）
credentials = Credentials(ak, sk, region)

# 创建签名器
signer = SignerV4(credentials, service, region)

# 构造请求体
payload = {
    "Text": "你好，这是我生成的语音。",
    "Speaker": "chinese_zhixuan_female",  # 可换别的音色
    "AudioFormat": "mp3",
    "SampleRate": 16000,
    "EnableSubtitle": False
}
body = json.dumps(payload)

# 构造签名前 headers
host = "tts.volcengineapi.com"
url = f"https://{host}/"
headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Host": host
}

# 签名（你这个版本的 sign() 用这种方式）
signed_headers = signer.sign(
    method="POST",
    url=url,
    headers=headers,
    body=body
)

# 发起 POST 请求
response = requests.post(url, headers=signed_headers, data=body)

# 保存音频或打印错误
if response.status_code == 200:
    with open("output.mp3", "wb") as f:
        f.write(response.content)
    print("✅ 语音合成成功，保存为 output.mp3")
else:
    print(f"❌ 合成失败（{response.status_code}）：{response.text}")
