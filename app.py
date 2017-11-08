#!venv/bin/python
import os
import settings
from flask import Flask, render_template, redirect, url_for, jsonify, send_from_directory

app = Flask(__name__)
app.config.from_object('settings.Config')

@app.route('/', methods=['GET'])
def generic():
    return render_template('home.html', title = "Landing page")

@app.route('/assets/<path:path>', methods=['GET'])
def send_asset(path):
    return send_from_directory('assets', path)

@app.route('/item-images/<path:path>', methods=['GET'])
def send_item_image(path):
    return send_from_directory('assets/images/items', path)

if __name__ == '__main__':
    app.run(debug=True)
