from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import os
from bson import ObjectId


# Création de l'application Flask
app = Flask(__name__)

# Définir la clé secrète pour sécuriser les sessions (vous pouvez remplacer cela par une clé générée)
app.secret_key = f'{os.urandom(26)}'  # Par exemple, utilisez os.urandom(24) pour une clé aléatoire

# Connexion à MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017')

client.drop_database('burger_app')

db = client['burger_app']

# Vérifiez si la base de données est correctement connectée
try:
    db.burgers.find_one()
    print("Ok")
except Exception as e:
    print(f"Erreur de connexion à la base de données: {e}")

# Page d'accueil
@app.route('/')
def index():
    burgers = db.burgers.find()
    return render_template('index.html', burgers=burgers)

# Route pour la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Recherche de l'utilisateur dans la base de données
        user_data = db.users.find_one({'username': username})

        if user_data and check_password_hash(user_data['password'], password):
            # Connexion réussie, stocker l'ID de l'utilisateur dans la session
            session['user_id'] = str(user_data['_id'])
            flash('Connexion réussie', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')

    return render_template('login.html')

# Route pour la page d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Vérifier si l'utilisateur existe déjà
        existing_user = db.users.find_one({'username': username})
        if existing_user:
            flash('Nom d\'utilisateur déjà pris', 'error')
            return redirect(url_for('signup'))

        # Insérer l'utilisateur dans la base de données
        db.users.insert_one({'username': username, 'password': hashed_password})
        flash('Compte créé avec succès, vous pouvez vous connecter', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Route pour se déconnecter
@app.route('/logout')
def logout():
    session.clear()  # Effacer la session
    flash('Vous êtes déconnecté', 'success')
    return redirect(url_for('index'))

@app.route('/create_burger', methods=['GET', 'POST'])
def create_burger():
    # Vérification que l'utilisateur est connecté
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour créer un burger.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Récupérer les données du formulaire
        burger_name = request.form['name']
        ingredients = request.form.getlist('ingredients')  # Liste des ingrédients
        user_id = session['user_id']  # ID de l'utilisateur connecté

        # Vérification que le nom du burger est fourni
        if not burger_name:
            flash('Le nom du burger est requis', 'error')
            return render_template('create_burger.html')

        # Ajouter le burger à la base de données
        db.burgers.insert_one({
            'name': burger_name,
            'ingredients': ingredients,
            'creator_id': user_id
        })

        flash('Burger créé avec succès!', 'success')
        return redirect(url_for('index'))

    return render_template('create_burger.html')

@app.route('/delete_burger/<burger_id>', methods=['POST'])
def delete_burger(burger_id):
    # Vérifiez si l'utilisateur est connecté
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour supprimer un burger.', 'error')
        return redirect(url_for('login'))

    # Cherchez le burger par son ID dans la base de données
    burger = db.burgers.find_one({'_id': ObjectId(burger_id)})

    if burger:
        # Vérifiez si le burger appartient à l'utilisateur connecté
        if burger['creator_id'] == session['user_id']:
            # Supprimez le burger de la base de données
            db.burgers.delete_one({'_id': ObjectId(burger_id)})
            flash('Burger supprimé avec succès!', 'success')
        else:
            flash('Vous ne pouvez supprimer que vos propres burgers.', 'error')
    else:
        flash('Burger non trouvé.', 'error')

    return redirect(url_for('my_burgers'))

@app.route('/my_burgers')
def my_burgers():
    # Vérifiez si l'utilisateur est connecté
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour voir vos burgers.', 'error')
        return redirect(url_for('login'))

    # Récupérer les burgers créés par l'utilisateur connecté
    user_burgers = db.burgers.find({'creator_id': session['user_id']})
    return render_template('my_burgers.html', burgers=user_burgers)


# Exécution de l'application Flask
if __name__ == '__main__':
    app.run(debug=True)
