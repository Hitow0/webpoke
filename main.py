import requests as requests
from flask import Flask, render_template, redirect, url_for


from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


app = Flask(__name__, template_folder='templates', static_folder='staticFolder')
app.secret_key = "WebPoke"


class PokemonForm(FlaskForm):
    nom = StringField("nom", validators=[DataRequired()])

@app.route("/", methods=['GET', 'POST'])
def index():
    pokedex_form = PokemonForm()
    if pokedex_form.validate_on_submit():
        return redirect(url_for('pokemon_info', name=pokedex_form.nom.data))
    return render_template('pokedex.html', pokedex_json=None, form=pokedex_form)

@app.route('/pokemon/<name>')
def pokemon_info(name):
    pokedex_form = PokemonForm()
    response = requests.get(
        f'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{name}')
    reponse_data_json = response.json()
    if len(reponse_data_json) == 2:
        return render_template('pokedex.html', pokedex_json=None, form=pokedex_form, msg="Le pokemon n'existe pas.")
    return render_template('pokedex.html', pokedex_json=reponse_data_json, form=pokedex_form)


if __name__ == '__main__':
    app.run()