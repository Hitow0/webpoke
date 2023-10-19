import requests as requests
from flask import Flask, render_template, redirect
from markupsafe import escape
from datetime import datetime, date

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


app = Flask(__name__)

class PokemonForm(FlaskForm):
    nom = StringField("nom", validators=[DataRequired()])

@app.route("/")
def index():
    pass

if __name__ == '__main__':
    app.run()
