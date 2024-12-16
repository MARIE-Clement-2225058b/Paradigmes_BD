from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connexion à MongoDB (modifie l'URL selon ton cas, ici on utilise une connexion locale)
client = MongoClient('mongodb://localhost:27017/')
db = client['burger_builder']  # Nom de la base de données

# Collection MongoDB pour les burgers
burgers_collection = db['burgers']

@app.route('/')
def index():
    # Récupérer tous les burgers de la base de données
    burgers = list(burgers_collection.find({}, {"_id": 0}))  # Exclure l'_id de MongoDB
    return render_template('index.html', burgers=burgers)

@app.route('/add_burger', methods=['POST'])
def add_burger():
    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form.getlist('ingredients')  # Liste des ingrédients
        creator = request.form['creator']

        # Ajouter un nouveau burger dans la collection
        burger = {
            'name': name,
            'ingredients': ingredients,
            'creator': creator,
            'ratings': [],
            'average_rating': 0
        }

        burgers_collection.insert_one(burger)
        return redirect(url_for('index'))

@app.route('/rate_burger/<string:name>', methods=['POST'])
def rate_burger(name):
    rating = int(request.form['rating'])

    # Trouver le burger à partir du nom
    burger = burgers_collection.find_one({'name': name})

    # Ajouter la note au burger
    burger['ratings'].append(rating)

    # Calculer la nouvelle note moyenne
    burger['average_rating'] = sum(burger['ratings']) / len(burger['ratings'])

    # Mettre à jour le burger dans la base de données
    burgers_collection.update_one({'name': name}, {'$set': burger})

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
