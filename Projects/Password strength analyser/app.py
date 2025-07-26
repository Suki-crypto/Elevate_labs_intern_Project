from flask import Flask, render_template, request, send_file
from zxcvbn import zxcvbn
import os

app = Flask(__name__)
os.makedirs("wordlists", exist_ok=True)

def generate_wordlist(user_inputs):
    base_words = user_inputs.split()
    variations = []

    for word in base_words:
        variations.extend([
            word,
            word.lower(),
            word.upper(),
            word.capitalize(),
            word + "123",
            word + "2025",
            word.replace('a', '@').replace('o', '0').replace('e', '3')
        ])

    return list(set(variations))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    password = request.form['password']
    info = request.form['info']
    result = zxcvbn(password)

    wordlist = generate_wordlist(info)
    filename = f"wordlists/wordlist.txt"
    with open(filename, 'w') as f:
        for word in wordlist:
            f.write(word + '\n')

    score = result['score']
    feedback = result['feedback']['warning'] or "Looks good!"

    return {
        "score": score,
        "feedback": feedback,
        "download": "/download"
    }

@app.route('/download')
def download():
    return send_file("wordlists/wordlist.txt", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
