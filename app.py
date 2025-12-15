from pulp import *
from flask import Flask, request, jsonify
from flask_cors import CORS


print("="*60)  # Affiche 60 fois le signe "="
print("TEXTILEOPTIM - KS Confection")
print("="*60)

produits = ['Laine', 'Coton', 'Soie']

profits = {
    'Laine': 7,   # Profit = 7 DTN (du Tableau 2)
    'Coton': 10,  # Profit = 10 DTN (du Tableau 2)
    'Soie': 12    # Profit = 12 DTN (du Tableau 2)
}
machines = ['Filature', 'Tissage', 'Ennoblissement']

disponibilites = {
    'Filature': 120,        # 120 heures disponibles
    'Tissage': 150,         # 150 heures disponibles
    'Ennoblissement': 100   # 100 heures disponibles
}

temps_fabrication = {
    # Machine de Filature (ligne 1 du Tableau 1)
    'Filature': {
        'Laine': 3,    # 3 heures (colonne Laine, ligne Filature)
        'Coton': 2,    # 2 heures (colonne Coton, ligne Filature)
        'Soie': 4      # 4 heures (colonne Soie, ligne Filature)
    },
    # Machine de Tissage (ligne 2 du Tableau 1)
    'Tissage': {
        'Laine': 8,    # 8 heures
        'Coton': 7,    # 7 heures
        'Soie': 4      # 4 heures
    },
    # Machine d'Ennoblissement (ligne 3 du Tableau 1)
    'Ennoblissement': {
        'Laine': 0.7,  # 0,7 heures (virgule = point en Python)
        'Coton': 0.6,  # 0,6 heures
        'Soie': 0.3    # 0,3 heures
    }
}


# PARTIE 2 : CRÉER LE MODÈLE MATHÉMATIQUE

probleme = LpProblem("KS_Confection_Optimisation", LpMaximize)
x = LpVariable.dicts("Quantite", produits, lowBound=0, cat='Continuous')
probleme += (
    lpSum([profits[p] * x[p] for p in produits]),
    "Profit_Total"  # Nom de l'objectif (optionnel)
)
probleme += (
    lpSum([temps_fabrication['Filature'][p] * x[p] for p in produits]) 
    <= disponibilites['Filature'],
    "Contrainte_Filature"  # Nom de la contrainte
)
probleme += (
    lpSum([temps_fabrication['Tissage'][p] * x[p] for p in produits]) 
    <= disponibilites['Tissage'],
    "Contrainte_Tissage"
)
probleme += (
    lpSum([temps_fabrication['Ennoblissement'][p] * x[p] for p in produits]) 
    <= disponibilites['Ennoblissement'],
    "Contrainte_Ennoblissement"
)
print("\n🔄 Calcul de la solution optimale...\n")

probleme.solve()




print("="*60)
print("RÉSULTATS")
print("="*60)

# LIGNE 16 : Vérifier si une solution a été trouvée
# probleme.status contient un code :
#   1 = Solution optimale trouvée
#   0 = Pas encore résolu
#  -1 = Pas de solution (problème infaisable)
#  -2 = Problème non borné

statut = LpStatus[probleme.status]  # Convertir le code en texte
print(f"\n📊 Statut : {statut}\n")

# LIGNE 17 : Si solution trouvée (status = 1)
if probleme.status == 1:
    
    print("✅ SOLUTION OPTIMALE TROUVÉE !\n")
    print("-" * 60)
    print("QUANTITÉS À PRODUIRE :")
    print("-" * 60)
    
    # LIGNE 18 : Afficher les quantités optimales
    # Pour chaque produit, afficher sa quantité optimale
    for produit in produits:
        # x[produit].varValue = la valeur optimale calculée pour ce produit
        quantite = x[produit].varValue
        # f"..." = format string (permet d'insérer des variables dans du texte)
        # {quantite:8.2f} = afficher quantite avec 8 caractères, 2 décimales
        print(f"  • {produit:15} : {quantite:8.2f} unités")
    
    # LIGNE 19 : Calculer et afficher le profit maximum
    # value(probleme.objective) = la valeur de la fonction objectif à l'optimum
    # C'est le profit total maximum
    profit_max = value(probleme.objective)
    print("\n" + "="*60)
    print(f"💰 PROFIT MAXIMUM : {profit_max:.2f} DTN")
    print("="*60)
    
    # LIGNE 20 : Calculer l'utilisation de chaque machine
    print("\n" + "-"*60)
    print("UTILISATION DES MACHINES :")
    print("-"*60)
    
    # Pour chaque machine
    for machine in machines:
        
        # Calculer le temps total utilisé sur cette machine
        # sum() = faire la somme
        # Pour chaque produit p :
        #   temps_fabrication[machine][p] = temps unitaire
        #   x[p].varValue = quantité optimale
        #   multiplier les deux
        # Additionner tout
        
        temps_utilise = sum(
            temps_fabrication[machine][p] * x[p].varValue 
            for p in produits
        )
        
        temps_dispo = disponibilites[machine]  # Temps disponible
        
        # Calculer le pourcentage d'utilisation
        pourcentage = (temps_utilise / temps_dispo) * 100
        
        # Afficher
        print(f"  • {machine:15} : {temps_utilise:6.2f} / {temps_dispo:6.2f} heures  ({pourcentage:5.1f}%)")
    
    # LIGNE 21 : Afficher la contribution de chaque produit au profit
    print("\n" + "-"*60)
    print("CONTRIBUTION AU PROFIT PAR PRODUIT :")
    print("-"*60)
    
    for produit in produits:
        quantite = x[produit].varValue  # Quantité optimale
        profit_produit = profits[produit] * quantite  # Profit de ce produit
        pourcentage_profit = (profit_produit / profit_max) * 100  # % du profit total
        
        print(f"  • {produit:15} : {profit_produit:8.2f} DTN  ({pourcentage_profit:5.1f}%)")
    
    print("\n" + "="*60)

else:
    # LIGNE 22 : Si pas de solution
    print("\n❌ ERREUR : Aucune solution trouvée !")

# =============================================================================
# FIN DU PROGRAMME
# =============================================================================

print("\n✅ Programme terminé !")
print("="*60)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pulp import *

app = Flask(__name__)
CORS(app)  # Autorise ton frontend à appeler le backend


@app.route('/')
def home():
    return render_template("index.html")


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
        
        # ===== MODÈLE D'OPTIMISATION (votre code) =====
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
                pourcentage_profit = round((profit_produit / profit_max) * 100, 1)
                
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
    print("📡 API accessible sur : http://127.0.0.1:5000")
    print("🌐 Testez l'API : http://127.0.0.1:5000")
    print("="*60)
    app.run(debug=True, port=5000)
