from flask import Flask, render_template, request, redirect, url_for, session, flash, current_app
from pymongo import errors
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import os
from bson import ObjectId

# Importation des schémas de validation de MongoDB
from create_bd import burger_validator, user_validator

# Création de l'application Flask
app = Flask(__name__)

# Définir la clé secrète pour sécuriser les sessions
app.secret_key = f'{os.urandom(26)}'  # Utilisez os.urandom(24) pour une clé aléatoire

# Connexion à MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017')
client.drop_database('burger_app')
db = client['burger_app']

# Créer les collections si elles n'existent pas, avec le validateur de schémas
try:
    db.create_collection('burgers', validator=burger_validator)
    db.create_collection('users', validator=user_validator)
    print("Collection 'burgers' et 'users' créées avec succès.")
except errors.CollectionInvalid:
    print("Les collections 'burgers' et 'users' existent déjà.")

# --------------------- ROUTES ---------------------

# Page d'accueil (affichage des burgers et des utilisateurs)
@app.route('/')
def index():
    burgers = db.burgers.find()
    return render_template('index.html', burgers=burgers)

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Recherche de l'utilisateur dans la base de données
        user_data = db.users.find_one({'username': username})

        if user_data and check_password_hash(user_data['password'], password):
            # Connexion réussie, stocker l'ID de l'utilisateur dans la session
            session['user_id'] = str(user_data['username'])
            flash('Connexion réussie', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')

    return render_template('login.html')

# Page d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Vérifier si l'utilisateur existe déjà
        if db.users.find_one({'username': username}):
            flash('Nom d\'utilisateur déjà pris', 'error')
            return redirect(url_for('signup'))

        # Insérer l'utilisateur dans la base de données
        db.users.insert_one({'username': username, 'password': hashed_password})
        flash('Compte créé avec succès, vous pouvez vous connecter', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Déconnexion
@app.route('/logout')
def logout():
    session.clear()  # Effacer la session
    flash('Vous êtes déconnecté', 'success')
    return redirect(url_for('index'))

# Page de création de burger
@app.route('/create_burger', methods=['GET', 'POST'])
def create_burger():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour créer un burger.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        burger_name = request.form['name']
        ingredients = request.form.getlist('ingredients')  # Liste des ingrédients
        user_id = session['user_id']

        if not burger_name:
            flash('Le nom du burger est requis', 'error')
            return render_template('create_burger.html')

        # Ajouter le burger à la base de données
        db.burgers.insert_one({
            'name': burger_name,
            'ingredients': ingredients,
            'creator': user_id,
            'ratings': [],  # Liste vide de notes
            'ratings_count': 0,  # Initialiser le nombre de votes à 0
            'rating': 0.0  # Initialiser la note moyenne
        })

        flash('Burger créé avec succès!', 'success')
        return redirect(url_for('index'))

    return render_template('create_burger.html')

# Supprimer un burger
@app.route('/delete_burger/<burger_id>', methods=['POST'])
def delete_burger(burger_id):
    # Vérifiez si l'utilisateur est connecté
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour supprimer un burger.', 'error')
        return redirect(url_for('login'))

    # Chercher le burger par son ID
    burger = db.burgers.find_one({'_id': ObjectId(burger_id)})

    if burger:
        # Vérifier si l'utilisateur est le créateur du burger
        if burger['creator_id'] == session['user_id']:
            db.burgers.delete_one({'_id': ObjectId(burger_id)})
            flash('Burger supprimé avec succès!', 'success')
        else:
            flash('Vous ne pouvez supprimer que vos propres burgers.', 'error')
    else:
        flash('Burger non trouvé.', 'error')

    return redirect(url_for('my_burgers'))

# Afficher les burgers de l'utilisateur
@app.route('/my_burgers')
def my_burgers():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour voir vos burgers.', 'error')
        return redirect(url_for('login'))

    # Récupérer les burgers créés par l'utilisateur
    user_burgers = db.burgers.find({'creator_id': session['user_id']})
    return render_template('my_burgers.html', burgers=user_burgers)

@app.route('/rate_burger/<burger_id>', methods=['POST'])
def rate_burger(burger_id):
    if 'user_id' not in session:
        flash('Vous devez être connecté pour voter.', 'error')
        return redirect(url_for('login'))

    burger_id = ObjectId(burger_id)
    user_id = session['user_id']  # ID de l'utilisateur connecté
    rating = float(request.form['rating'])  # La note donnée par l'utilisateur

    burger = db.burgers.find_one({'_id': burger_id})

    if burger:
        # Chercher si l'utilisateur a déjà voté
        existing_vote = next((vote for vote in burger['ratings'] if vote['user_id'] == user_id), None)

        if existing_vote:
            # Remplacer la note si l'utilisateur a déjà voté
            existing_vote['rating'] = rating
        else:
            # Ajouter la note si c'est la première fois que l'utilisateur vote
            burger['ratings'].append({'user_id': user_id, 'rating': rating})

        # Calculer la nouvelle note moyenne
        total_rating = sum(vote['rating'] for vote in burger['ratings'])
        ratings_count = len(burger['ratings'])
        new_avg_rating = total_rating / ratings_count if ratings_count > 0 else 0.0

        # Mettre à jour la note et le nombre de votes dans la base de données
        db.burgers.update_one(
            {'_id': burger_id},
            {'$set': {'rating': new_avg_rating, 'ratings': burger['ratings']}}
        )

        flash('Merci pour votre évaluation!', 'success')
    else:
        flash('Burger non trouvé', 'error')

    return redirect(url_for('index'))

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)
