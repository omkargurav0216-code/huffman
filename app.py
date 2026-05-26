from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():

    text = request.form['text']

    executable = './huffman.exe'

    if os.name != 'nt':
        executable = './huffman'

    result = subprocess.run(
        [executable, text],
        capture_output=True,
        text=True
    )

    output = result.stdout

    return render_template(
        'index.html',
        output=output,
        text=text
    )

if __name__ == '__main__':
    app.run(debug=True)