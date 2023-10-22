import requests as requests
from flask import Flask, render_template, redirect
from markupsafe import escape
from datetime import datetime, date

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


app = Flask(__name__,template_folder='templates',static_folder='staticFolder')
app.secret_key = "WebPoke"


class PokemonForm(FlaskForm):
    nom = StringField("", validators=[DataRequired()])


@app.route("/", methods=['GET', 'POST'])
def index():
    pokedex_form = PokemonForm()
    if pokedex_form.validate_on_submit():
        print("test")
        response = requests.get(
            f'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{pokedex_form.nom.data}')
        reponse_data_json = response.json()
        print(reponse_data_json)
        if len(reponse_data_json)==2:
            return render_template('index.html', pokedex_json=None, form=pokedex_form)
        return render_template('index.html', pokedex_json=reponse_data_json)
    return render_template('index.html', pokedex_json=None, form=pokedex_form)


if __name__ == '__main__':
    app.run()
