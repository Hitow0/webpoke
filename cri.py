from flask import render_template, Flask



app = Flask(__name__)
@app.route("/cri")
def cri_poke():
    return render_template('./templates/cri.html')


if __name__ == '__main__':
    app.run()

