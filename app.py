from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI

app = Flask(__name__)
app.secret_key = 'dev1234'  # 你可以换成任意字符串

client = OpenAI(
    api_key="sk-38d4bae37c72431992d3aee59dbe91db",
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

    # 初始化历史
    if 'messages' not in session:
        session['messages'] = [{"role": "system", "content": system_prompt}]
    
    # 如果已经存在，但 system_prompt 不一致，重新开始
    elif session['messages'][0]['content'] != system_prompt:
        session['messages'] = [{"role": "system", "content": system_prompt}]

    # 加入用户输入
    session['messages'].append({"role": "user", "content": user_input})

    # 调用 API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=session['messages'],
        temperature=1.5,
        top_p=1.0
    )

    reply = response.choices[0].message.content
    session['messages'].append({"role": "assistant", "content": reply})

    return jsonify({'reply': reply})

@app.route('/reset', methods=['POST'])
def reset():
    session.pop('messages', None)
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)
