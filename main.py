import csv
import os
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
    data = remove_accents(name)
    response = requests.get(
        f'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{data}')
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
        if game_form.nom.data.lower() == reponse_data_json['name']['fr'].lower():

            add_csv(reponse_data_json["pokedexId"], reponse_data_json["name"]['fr'])

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

def add_csv(id, name, filename='data.csv'):
    # Vérifier si le fichier CSV existe
    if not os.path.isfile(filename):
        # Si le fichier n'existe pas, le créer avec un en-tête
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Name'])

    # Ajouter la nouvelle ligne avec l'ID et le nom
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([id, name])



if __name__ == '__main__':
    app.run()
