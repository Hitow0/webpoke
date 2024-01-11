from flask import render_template, Flask



app = Flask(__name__)
@app.route("/cri")
def cri_poke():
    return render_template('./templates/cri.html')

@app.route('/getFileName')
def getFileName():
    return './CrisPokemon/génération1/1-bulbizarre.ogg'

if __name__ == '__main__':
    app.run()

