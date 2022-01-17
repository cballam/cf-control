from flask import Flask
from flask.json import jsonify
from flask.templating import render_template
from ..solver.server import Server

app = Flask(__name__)

# Note: very dodgy way to do things, but it works. Should find better way to do it.
#def state():
#    return jsonify({'state' : S._state_traj})

@app.route('/')
def page():
    return render_template('index.html')
