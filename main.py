import random

import requests as requests
from flask import Flask, render_template, redirect, url_for, session, jsonify
import unicodedata

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__, template_folder='templates', static_folder='staticFolder')
app.secret_key = "WebPoke"


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def retrait_espace(nom):
    return nom.replace(" ", "")


class PokemonForm(FlaskForm):
    nom = StringField("nom", validators=[DataRequired()])


class WhosThatPokemon(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('accueil.html')


@app.route("/pokemon", methods=['GET', 'POST'])
def pokemon_index():
    pokedex_form = PokemonForm()
    if pokedex_form.validate_on_submit():
        return redirect(url_for('pokemon_info', name=remove_accents(pokedex_form.nom.data)))
    return render_template('pokedex.html', pokedex_json=None, form=pokedex_form)


@app.route('/pokemon/<name>')
def pokemon_info(name):
    pokedex_form = PokemonForm()
    data = retrait_espace(remove_accents(name))
    regions = ["Paldea", "Alola", "Hisui", "Galar"]
    response = requests.get(
        f'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{data}')
    reponse_data_json = response.json()

    for region in regions:
        if name.__contains__(region):
            newName = name.split(" ")
            data = remove_accents(newName[0])
            response = requests.get(
                f'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{data}/{region.lower()}')
            print(region)
            reponse_data_json = response.json()

    if len(reponse_data_json) == 2:
        return render_template('pokedex.html', pokedex_json=None, form=pokedex_form, msg="Le pokemon n'existe pas.")
    return render_template('pokedex.html', pokedex_json=reponse_data_json, form=pokedex_form)


@app.route("/game", methods=['GET', 'POST'])
def game():
    game_form = WhosThatPokemon()

    current_pokemon_id = session.get('current_pokemon_id')
    msg = session.get('current_msg')

    if current_pokemon_id is None:
        current_pokemon_id = obtenir_id_pokemon_aleatoire()
        session['current_pokemon_id'] = current_pokemon_id

    response = requests.get(
        f'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{current_pokemon_id}'
    )
    reponse_data_json = response.json()

    if game_form.validate_on_submit():
        if remove_accents(game_form.nom.data.lower()) == remove_accents(reponse_data_json['name']['fr'].lower()):
            print("Bravo ! Vous avez trouvé le Pokémon !")
            session['current_msg'] = "Bravo ! Vous avez trouvé le Pokémon !"

            # Procéder à l'ajout dans la base de données

            session.pop('current_pokemon_id', None)
        else:
            print("Erreur !")
            session['current_msg'] = "Erreur ! Vous n'avez pas trouvé le pokemon !"

            session.pop('current_pokemon_id', None)
        return redirect('/game')
    else:
        session.pop('current_msg', None)
    return render_template('game.html', form=game_form, msg=msg, pokemon=reponse_data_json)


@app.route('/game/skip', methods=['GET'])
def skip():
    session.pop('current_pokemon_id', None)
    return redirect(url_for('game'))


def obtenir_id_pokemon_aleatoire():
    return random.randint(1, 1017)


@app.route('/get_sprite_url', methods=['GET'])
def get_sprite_url():
    # Utilisez votre fonction pour obtenir un nouvel ID aléatoire et retournez l'URL du sprite
    sprite_url = 'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{obtenir_id_pokemon_aleatoire()}'
    return jsonify({'sprite_url': sprite_url})


if __name__ == '__main__':
    app.run()
