import os
import json
from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用静态缓存
app.secret_key = 'dev1234'  # 你可以换成任意字符串

client = OpenAI(
    api_key="sk-38d4bae37c72431992d3aee59dbe91db",
    base_url="https://api.deepseek.com"
)

@app.route('/')
def index():
    return render_template('index.html')

SESSION_FILE = 'chat_log.json'

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return []

def save_session(messages):
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    system_prompt = data.get('system_prompt', '你是一个聪明、有趣的AI助手。')
    user_input = data.get('user_input', '')

    # === 加载持久化消息 ===
    messages = load_session()

    # === 如果首次或 prompt 改了就重置 ===
    if not messages or messages[0]['content'] != system_prompt:
        messages = [{"role": "system", "content": system_prompt}]

    messages.append({"role": "user", "content": user_input})

    # === 模型调用 ===
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=1.5,
        top_p=1.0
    )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    # === 保存到本地 ===
    save_session(messages)

    # === 打印用于调试 ===
    print("📜 当前传入消息：", json.dumps(messages, indent=2, ensure_ascii=False))

    # === 信号生成（频率、强度）===
    freq = min(1.0, 0.2 + 0.1 * reply.count('！'))
    intensity = min(1.0, 0.1 + 0.1 * len(reply) / 20)

    return jsonify({
        'reply': reply,
        'signal': {
            'frequency': round(freq, 2),
            'intensity': round(intensity, 2)
        }
    })


@app.route('/reset', methods=['POST'])
def reset():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    return jsonify({'status': 'cleared'})


if __name__ == '__main__':
    app.run(debug=True)
