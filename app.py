#!venv/bin/python
import os
import settings
from flask import Flask, render_template, redirect, url_for, jsonify, send_from_directory, request
from flask_socketio import SocketIO, emit
import hashlib
import stripe
import requests
import json

app = Flask(__name__)
app.config.from_object('settings.Config')
socketio = SocketIO(app, logger=True, engineio_logger=True)

stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUB_KEY']
}

stripe.api_key = stripe_keys['secret_key']

@app.route('/', methods=['GET'])
def generic():
    return render_template('home.html', title = "Landing page")

@app.route('/process-give', methods=['POST'])
def process():
    print(request.form)
    item = request.form['item']
    player = request.form['player']
    count = request.form['count']
    key = os.environ['SECRET_KEY']
    string = "%s|%s|%s|%s" % (player, item, count, key)
    hash = hashlib.md5(string.encode('utf-8')).hexdigest()
    address = "%s/give" % os.environ['API_SERVER']
    headers = {'content-type': 'application/x-www-form-urlencoded', 'auth': hash}
    r = requests.post(address, data={'user': player, 'item': item, 'amount': count}, headers=headers)
    print(r.status_code, r.reason)

    return redirect(url_for('generic'))


@app.route('/assets/<path:path>', methods=['GET'])
def send_asset(path):
    return send_from_directory('assets', path)

@app.route('/item-images/<path:path>', methods=['GET'])
def send_item_image(path):
    return send_from_directory('assets/images/items', path)

@app.route('/purchase-page')
def purchase():
    return render_template('purchase.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 500

    customer = stripe.Customer.create(
        email='customer@example.com',
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

    return render_template('charge.html', amount=amount)

@app.route('/player', methods=['GET'])
def player():
  data = {
    'playerId': "76561198026242506",
    'playerName': "BadZombi",
    'avatar': "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/eb/ebf67636075f05f2b98e4085dad04c4e484da05a_full.jpg"
  }
  socketio.emit('user_connected', data)
  return "foo";

@app.route('/player/connect/<steamid>', methods=['GET'])
def player_connect(steamid):
  url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=%s&steamids=%s" % (os.environ.get('STEAM_KEY'), steamid)
  r = requests.get(url)
  data = json.loads(r.text)
  response = data['response']
  player = response['players'][0]

  new_user = {
    'steamid': player['steamid'],
    'personaname': player['personaname'],
    'avatar': player['avatar']
  }
  socketio.emit('user_connected', new_user)

  return "user connected."

@app.route('/player/disconnect/<steamid>', methods=['GET'])
def player_disconnect(steamid):

  socketio.emit('user_disconnected', {'steamid':steamid})

  return "user disconnected."

  # return url

@socketio.on('my event', namespace='/')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='/')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/')
def test_connect():
    emit('my response', {'data': 'Connected'})
    print('Connected')

@socketio.on('disconnect', namespace='/')
def test_disconnect():
    print('Client disconnected')



if __name__ == '__main__':
    socketio.run(app, port=5001)
