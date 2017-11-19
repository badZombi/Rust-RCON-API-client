#!venv/bin/python
import os
import settings
from flask import Flask, render_template, redirect, url_for, jsonify, send_from_directory, request
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import hashlib
import stripe
import requests
import json

app = Flask(__name__)
app.config.from_object('settings.Config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://rustard_u:password@localhost/rustard'
socketio = SocketIO(app, logger=True, engineio_logger=True)
db = SQLAlchemy(app)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steamid = db.Column(db.String(), unique=True, nullable=False)
    avatar_m = db.Column(db.String(), unique=False, nullable=True)
    avatar_l = db.Column(db.String(), unique=False, nullable=True)
    personaname = db.Column(db.String(), unique=False, nullable=True)
    realname = db.Column(db.String(), unique=False, nullable=True)
    online = db.Column(db.Boolean())

    def __init__(self, steamid, avatar_m, avatar_l, personaname, realname, online=True):
      self.steamid = steamid
      self.avatar_m = avatar_m
      self.avatar_l = avatar_l
      self.personaname = personaname
      self.realname = realname
      self.online = online

    def __repr__(self):
      return '<User %r>' % self.steamid


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

def getSteamDetails(steamid):
  url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=%s&steamids=%s" % (os.environ.get('STEAM_KEY'), steamid)
  r = requests.get(url)
  data = json.loads(r.text)
  response = data['response']
  player = response['players'][0]



  return player

@app.route('/player/connect/<steamid>', methods=['GET'])
def player_connect(steamid):
  # check for user in DB:
  existingPlayer = Player.query.filter_by(steamid=steamid).first()

  if existingPlayer:
    if existingPlayer.online == True:
      new_user = {
        'steamid': existingPlayer.steamid,
        'personaname': existingPlayer.personaname,
        'avatar': existingPlayer.avatar_m
      }
    else:
      # get latest info from steam
      steam_data = getSteamDetails(steamid)
      new_user = {
        'steamid': steam_data['steamid'],
        'personaname': steam_data['personaname'],
        'avatar': steam_data['avatar']
      }
      existingPlayer.avatar_m = steam_data['avatarmedium']
      existingPlayer.avatar_l = steam_data['avatarfull']
      existingPlayer.personaname = steam_data['personaname']
      existingPlayer.realname = steam_data['realname']
      existingPlayer.online = True

      # update existing user
  else:
    # get latest info from steam
    steam_data = getSteamDetails(steamid)
    new_user = {
      'steamid': steam_data['steamid'],
      'personaname': steam_data['personaname'],
      'avatar': steam_data['avatar']
    }

    player = Player(steam_data['steamid'], steam_data['avatarmedium'], steam_data['avatarfull'], steam_data['personaname'], steam_data['realname'], True)

    db.session.add(player)

  db.session.commit()

  socketio.emit('user_connected', new_user)

  return "user connected."

@app.route('/player/disconnect/<steamid>', methods=['GET'])
def player_disconnect(steamid):
  existingPlayer = Player.query.filter_by(steamid=steamid).first()

  if existingPlayer:
    existingPlayer.online = False
    db.session.commit()

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
