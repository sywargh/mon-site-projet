from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pulp import *
import os

app = Flask(__name__, static_folder='.')  # ← MODIFICATION ICI
CORS(app)

print("="*60)
print("TEXTILEOPTIM - KS Confection")
print("="*60)

@app.route('/')
def home():
    """Page d'accueil - Affiche le fichier HTML à la racine"""
    return send_from_directory('.', 'index.html')  # ← MODIFICATION ICI

@app.route('/optimiser', methods=['POST'])
def optimiser():
    """
    Endpoint pour résoudre le problème d'optimisation
    Reçoit les données en JSON et retourne la solution optimale
    """
    try:
        # Récupérer les données envoyées par le frontend
        data = request.get_json()
        
        # Extraire les données
        profits = data.get('profits', {'Laine': 7, 'Coton': 10, 'Soie': 12})
        disponibilites = data.get('disponibilites', {
            'Filature': 120,
            'Tissage': 150,
            'Ennoblissement': 100
        })
        temps_fabrication = data.get('temps_fabrication', {
            'Filature': {'Laine': 3, 'Coton': 2, 'Soie': 4},
            'Tissage': {'Laine': 8, 'Coton': 7, 'Soie': 4},
            'Ennoblissement': {'Laine': 0.7, 'Coton': 0.6, 'Soie': 0.3}
        })
        
        # Listes des produits et machines
        produits = ['Laine', 'Coton', 'Soie']
        machines = ['Filature', 'Tissage', 'Ennoblissement']
        
        # ===== MODÈLE D'OPTIMISATION =====
        probleme = LpProblem("KS_Confection_Optimisation", LpMaximize)
        
        # Variables de décision
        x = LpVariable.dicts("Quantite", produits, lowBound=0, cat='Continuous')
        
        # Fonction objectif : maximiser le profit
        probleme += lpSum([profits[p] * x[p] for p in produits]), "Profit_Total"
        
        # Contraintes de disponibilité des machines
        for machine in machines:
            probleme += (
                lpSum([temps_fabrication[machine][p] * x[p] for p in produits]) 
                <= disponibilites[machine],
                f"Contrainte_{machine}"
            )
        
        # Résoudre le problème
        probleme.solve()
        
        # ===== PRÉPARER LES RÉSULTATS =====
        if probleme.status == 1:  # Solution optimale trouvée
            
            # Quantités optimales
            quantites = {p: round(x[p].varValue, 2) for p in produits}
            
            # Profit maximum
            profit_max = round(value(probleme.objective), 2)
            
            # Utilisation des machines
            utilisation_machines = {}
            for machine in machines:
                temps_utilise = sum(
                    temps_fabrication[machine][p] * x[p].varValue 
                    for p in produits
                )
                temps_dispo = disponibilites[machine]
                pourcentage = round((temps_utilise / temps_dispo) * 100, 1)
                
                utilisation_machines[machine] = {
                    'temps_utilise': round(temps_utilise, 2),
                    'temps_disponible': temps_dispo,
                    'pourcentage': pourcentage
                }
            
            # Contribution au profit par produit
            contributions = {}
            for produit in produits:
                profit_produit = round(profits[produit] * x[produit].varValue, 2)
                pourcentage_profit = round((profit_produit / profit_max) * 100, 1) if profit_max > 0 else 0
                
                contributions[produit] = {
                    'profit': profit_produit,
                    'pourcentage': pourcentage_profit
                }
            
            # Réponse JSON
            return jsonify({
                'success': True,
                'statut': 'Optimal',
                'quantites': quantites,
                'profit_maximum': profit_max,
                'utilisation_machines': utilisation_machines,
                'contributions': contributions
            })
        
        else:
            return jsonify({
                'success': False,
                'message': 'Aucune solution optimale trouvée',
                'statut': LpStatus[probleme.status]
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur : {str(e)}'
        }), 500

@app.route('/donnees-defaut', methods=['GET'])
def donnees_defaut():
    """
    Retourne les données par défaut du TP (Tableau 1 et 2)
    """
    return jsonify({
        'profits': {
            'Laine': 7,
            'Coton': 10,
            'Soie': 12
        },
        'disponibilites': {
            'Filature': 120,
            'Tissage': 150,
            'Ennoblissement': 100
        },
        'temps_fabrication': {
            'Filature': {'Laine': 3, 'Coton': 2, 'Soie': 4},
            'Tissage': {'Laine': 8, 'Coton': 7, 'Soie': 4},
            'Ennoblissement': {'Laine': 0.7, 'Coton': 0.6, 'Soie': 0.3}
        }
    })

if __name__ == '__main__':
    print("="*60)
    print("🧵 TEXTILEOPTIM - Serveur démarré")
    print("="*60)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)



