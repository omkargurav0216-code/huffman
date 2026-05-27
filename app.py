from flask import Flask, render_template, request
import subprocess
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():

    text = request.form['text']

    executable = './huffman'

    if os.name == 'nt':
        executable = './huffman.exe'

    result = subprocess.run(
        [executable, text],
        capture_output=True,
        text=True
    )

    output = result.stdout

    with open('tree.json') as f:
        tree_data = json.load(f)

    return render_template(
        'index.html',
        output=output,
        tree=tree_data,
        text=text
    )

if __name__ == '__main__':
    app.run(debug=True)