from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Connexion MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['burger_builder']  # Nom de la base de données

@app.route('/')
def home():
    return "Bienvenue sur Build-A-Burger!"

if __name__ == '__main__':
    app.run(debug=True)
