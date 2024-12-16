# Définir le validateur pour la collection 'burgers'
burger_validator = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['name', 'creator'],
        'properties': {
            'name': {
                'bsonType': 'string',
                'description': 'Le nom du burger doit être une chaîne de caractères.'
            },
            'creator': {
                'bsonType': 'string',
                'description': 'L\'identifiant du créateur doit être une chaîne de caractères.'
            },
            'ingredients': {
                'bsonType': 'array',
                'items': {
                    'bsonType': 'string',
                    'description': 'Chaque ingrédient doit être une chaîne de caractères.'
                },
                'description': 'Les ingrédients doivent être un tableau de chaînes de caractères.'
            },
            'rating': {
                'bsonType': 'double',
                'description': 'La note du burger, un nombre flottant entre 0 et 5.',
                'minimum': 0,
                'maximum': 5
            },
            'ratings': {
                'bsonType': 'array',
                'items': {
                    'bsonType': 'object',
                    'required': ['user_id', 'rating'],
                    'properties': {
                        'user_id': {
                            'bsonType': 'string',
                            'description': 'L\'identifiant de l\'utilisateur ayant voté.'
                        },
                        'rating': {
                            'bsonType': 'double',
                            'description': 'Une note individuelle entre 0 et 5.',
                            'minimum': 0,
                            'maximum': 5
                        }
                    }
                },
                'description': 'Liste des notes données au burger sous forme d\'objets contenant un identifiant d\'utilisateur et une note.'
            }
        }
    }
}

# Définir le validateur pour la collection 'users'
user_validator = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['username', 'password'],
        'properties': {
            'username': {
                'bsonType': 'string',
                'description': 'Le nom d\'utilisateur doit être une chaîne de caractères.'
            },
            'password': {
                'bsonType': 'string',
                'description': 'Le mot de passe doit être une chaîne de caractères.'
            }
        }
    }
}