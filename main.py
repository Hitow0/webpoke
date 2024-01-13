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


def retrait_espace(nom):
    return nom.replace(" ", "")


class PokemonForm(FlaskForm):
    nom = StringField("nom", validators=[DataRequired()])


class WhosThatPokemon(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])


class FavorisForm(FlaskForm):
    nom = StringField('nom')


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
    if retrait_espace(remove_accents(name)).lower() == "MimeJr.".lower():
        data = 439
    elif [retrait_espace(remove_accents("Nidoran♀")).lower(),
          retrait_espace(remove_accents("nidoran femelle")).lower()].__contains__(
          retrait_espace(remove_accents(name)).lower()):
        data = 29
    elif [retrait_espace(remove_accents("Nidoran♂")).lower(),
          retrait_espace(remove_accents("nidoran mâle")).lower()].__contains__(
          retrait_espace(remove_accents(name)).lower()):
        data = 32
    else:
        data = retrait_espace(remove_accents(name))
    regions = ["Paldea", "Alola", "Hisui", "Galar"]
    response = requests.get(
        f'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{data}')
    reponse_data_json = response.json()

    for region in regions:
        if name.lower().__contains__(region.lower()):
            newName = name.split(" ")
            data = remove_accents(newName[0])
            response = requests.get(
                f'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{data}/{region.lower()}')
            reponse_data_json = response.json()

    if len(reponse_data_json) == 2:
        return render_template('pokedex.html', pokedex_json=None, form=pokedex_form, msg="Le pokemon n'existe pas.")

    # tab = []
    # for i in range(1,722):
    #     pokemon_info = requests.get(
    #             f'https://api-pokemon-fr.vercel.app/api/v1/pokemon/{i}').json()
    #     pokemon_gen = pokemon_info['generation']
    #     pokemon_name = pokemon_info['name']['fr']
    #     audio_url = f'http://127.0.0.1:5000/staticFolder/CrisPokemon/génération%20{pokemon_gen}/{i}%20-%20{pokemon_name.lower()}.ogg'
    #     audio_response = requests.get(audio_url)
    #
    #     if audio_response.status_code == 404:
    #         tab.append(i)
    # print(tab)
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
        if retrait_espace(remove_accents(game_form.nom.data.lower())) == retrait_espace(remove_accents(reponse_data_json['name']['fr'].lower())) or (retrait_espace(remove_accents(game_form.nom.data.lower())) == retrait_espace(remove_accents("nidoran femelle".lower())) and retrait_espace(remove_accents(reponse_data_json['name']['fr'].lower())) == retrait_espace(remove_accents("Nidoran♀".lower()))) or (retrait_espace(remove_accents(game_form.nom.data.lower())) == retrait_espace(remove_accents("nidoran mâle".lower())) and retrait_espace(remove_accents(reponse_data_json['name']['fr'].lower())) == retrait_espace(remove_accents("Nidoran♂".lower()))):
            add_csv(reponse_data_json["pokedexId"], reponse_data_json["name"]['fr'])

            session['current_msg'] = "Bravo ! Vous avez trouvé le Pokémon !"

            session.pop('current_pokemon_id', None)
        else:
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


def add_csv(id, name, filename='data.csv'):
    if not os.path.isfile(filename):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Name'])

    if not is_duplicate(id, name, filename):
        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([id, name])
        return True
    else:
        return False


def is_duplicate(id, name, filename='data.csv'):
    existing_data = read_csv(filename)
    return str(id) in existing_data


def read_csv(filename='data.csv'):
    data = {}
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data[row['ID']] = row['Name']
    return data


def sort_dict_by_id(data):
    sorted_data = dict(sorted(data.items(), key=lambda item: int(item[0])))
    return sorted_data


@app.route('/pokedex', methods=['GET', 'POST'])
def pokedex():
    favoris_form = FavorisForm()

    if not os.path.exists("data.csv"):
        data = {}
        return render_template('favoris.html', data=data, form=favoris_form, message="File not found: data.csv")

    if favoris_form.validate_on_submit():
        all_data = read_csv("data.csv")
        filtered_data = {}
        for id, name in all_data.items():
            if name.lower().startswith(favoris_form.nom.data.lower()):
                filtered_data[id] = name
        return render_template('favoris.html', data=filtered_data, form=favoris_form)

    data = sort_dict_by_id(read_csv("data.csv"))
    return render_template('favoris.html', data=data, form=favoris_form)


if __name__ == '__main__':
    app.run()
