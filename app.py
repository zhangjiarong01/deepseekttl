from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用静态缓存
app.secret_key = 'dev1234'  # 你可以换成任意字符串

client = OpenAI(
    api_key="",
    base_url="https://api.deepseek.com"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    system_prompt = data.get('system_prompt', '你是一个聪明、有趣的AI助手。')
    user_input = data.get('user_input', '')

    if 'messages' not in session:
        session['messages'] = [{"role": "system", "content": system_prompt}]
    elif session['messages'][0]['content'] != system_prompt:
        session['messages'] = [{"role": "system", "content": system_prompt}]
    
    session['messages'].append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=session['messages'],
        temperature=1.5,
        top_p=1.0
    )

    reply = response.choices[0].message.content
    session['messages'].append({"role": "assistant", "content": reply})

    # 简单规则生成 frequency 和 intensity（未来可替换为模型输出）
    freq = min(1.0, 0.2 + 0.1 * reply.count('！'))  # 感叹号越多，频率越高
    intensity = min(1.0, 0.1 + 0.1 * len(reply) / 20)  # 回复越长，强度越强

    return jsonify({
        'reply': reply,
        'signal': {
            'frequency': round(freq, 2),
            'intensity': round(intensity, 2)
        }
    })


@app.route('/reset', methods=['POST'])
def reset():
    session.pop('messages', None)
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)
