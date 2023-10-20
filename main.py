import requests as requests
from flask import Flask, render_template, redirect
from markupsafe import escape
from datetime import datetime, date

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = "Pokedex !"

class PokemonForm(FlaskForm):
    nom = StringField("nom", validators=[DataRequired()])


@app.route("/index", methods=['GET', 'POST'])
def index():
    pokemon_form = PokemonForm()
    if pokemon_form.validate_on_submit():
        response = requests.get('https://api-pokemon-fr.vercel.app/api/v1/pokemon/argouste')
        response_data_json = response.json()
        return render_template('index.html', adresse_json=response_data_json)
    return render_template('index.html', form=pokemon_form)


if __name__ == '__main__':
    app.run()
