from flask import Flask
from flask import render_template
from flask import url_for
from flask import request

import os

app = Flask(__name__)


import os
from dotenv import load_dotenv
load_dotenv()


from openai import OpenAI
 
client = OpenAI(
    api_key=os.environ['API_KEY'],
    base_url=os.environ['BASE_URL'],
)


@app.route("/")
def index():
    return render_template("index.html")


 
 
# MODEL = "gpt-3.5-turbo"

# response = client.chat.completions.create(
#     model=MODEL,
#    messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#     {"role": "user", "content": "Where was it played?"}
#   ],
#     temperature=0,
#     )



@app.route('/question', methods=['POST'])
def question():

    question = request.form.get('text')

    # Получаем файл изображения
    image = request.files.get('image')

    if image:
        # Сохраняем изображение на диск или обрабатываем его
        image.save(f'uploads/{image.filename}')


    MODEL = "gpt-3.5-turbo"
    # question = request.json['question']

    chat_completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        temperature=0,
        )
    
    answer = chat_completion.choices[0].message.content

    # answer = 'Ответ бота'
    return {'answer': answer}

 

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')  
    port = 5000
    app.run(host='0.0.0.0', port=port, debug=True)
