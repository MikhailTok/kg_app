from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
import base64
import os

app = Flask(__name__)

import time


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

def encode_image(image):
    return base64.b64encode(image).decode('utf-8')


@app.route('/question', methods=['POST'])
def question():
    question = request.form.get('text')
    image = request.files.get('image')

    content = [{"type": "text", "text": question}]

    if image:
        base64_image = encode_image(image.read())
        image = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "low"}}]
        content += image

    MODEL = 'gpt-4o-mini-2024-07-18' or "gpt-3.5-turbo"
    chat_completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": content}],
        temperature=0,
        )
    answer = chat_completion.choices[0].message.content

    # time.sleep(1)
    # answer = 'Ответ бота'
    return {'answer': answer}

 

if __name__ == '__main__':
    port = 5000
    app.run(host='0.0.0.0', port=port, debug=True)
