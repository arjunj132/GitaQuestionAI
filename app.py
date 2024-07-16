from flask import Flask
from ai import generate
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return generate()

@app.route('/about')
def about():
    return 'GitaQuestionAI is a Llama3 and Mixtral-8x7B-Instruct-v0.1 based AI program designed to make 10 shlokas question (can be very unreliable). By GitaGuru'
