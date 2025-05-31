import os
import json
import re
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# === 加载配置 ===
with open('./secrets/config.sample.json', 'r', encoding='utf-8-sig') as f:
    config = json.load(f)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'dev1234'

client = OpenAI(
    api_key=config['api_key'],
    base_url=config['base_url']
)

@app.route('/')
def index():
    return render_template('model.html')

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

# === 指令解析工具 ===
def parse_target_instruction(text):
    time_match = re.search(r'(\d+)\s*秒', text)
    count_match = re.search(r'(\d+)\s*次', text)

    time = int(time_match.group(1)) if time_match else 30  # 默认时间设为30秒更合理
    count = int(count_match.group(1)) if count_match else 10
    return {'time': time, 'count': count}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    system_prompt = data.get('system_prompt', '你是一个聪明、有趣的AI助手。')
    user_input = data.get('user_input', '')
    motion_count = data.get('motion_count', 0)
    is_auto = data.get('auto', False)

    messages = load_session()

    # 如果系统设定不一致或首次对话，重新初始化
    if not messages or messages[0]['content'] != system_prompt:
        messages = [{"role": "system", "content": system_prompt}]

    # 自动提交 vs 用户输入
    if is_auto:
        summary_msg = f"⏱ 本轮挑战结束，完成了 {motion_count} 次动作。"
        messages.append({"role": "user", "content": summary_msg})
    else:
        messages.append({"role": "user", "content": user_input})

    print("🤖 接收到的 motion_count：", motion_count)

    # 调用大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=1.5,
        top_p=1.0
    )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    save_session(messages)

    # 自动提交也可解析新挑战目标（推荐）
    target = parse_target_instruction(reply)

    print("📜 当前对话内容：", json.dumps(messages, indent=2, ensure_ascii=False))
    print("🎯 当前目标要求：", target)

    return jsonify({
        'reply': reply,
        'target': target
    })

@app.route('/result', methods=['POST'])
def result():
    data = request.json
    motion_count = data.get('motion_count')
    motion_time = data.get('motion_time')

    summary_msg = f"本轮完成了 {motion_count} 次运动，用时 {motion_time} 秒。"
    messages = load_session()
    messages.append({"role": "user", "content": summary_msg})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=1.5,
        top_p=1.0
    )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    save_session(messages)

    return jsonify({
        'reply': reply
    })

@app.route('/reset', methods=['POST'])
def reset():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)
