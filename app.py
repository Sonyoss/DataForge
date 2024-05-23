import streamlit as st
import sqlite3
import pandas as pd
import json
import random


# Création de la connexion à la base de données SQLite
conn = sqlite3.connect('jeu_de_donnees.db')
c = conn.cursor()

# Création de la table pour stocker les données
c.execute('''CREATE TABLE IF NOT EXISTS donnees
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              instruction TEXT,
              contenu TEXT,
              sortie TEXT,
              valide BOOLEAN,
              explication TEXT)''')
conn.commit()

# Fonction pour charger un jeu de données depuis un fichier jsonl
def charger_jeu_de_donnees(uploaded_file):
    data = json.loads(uploaded_file.getvalue().decode('utf-8'))
    
    # Supprimer les données existantes dans la table
    c.execute('DELETE FROM donnees')
    
    # Réinitialiser la séquence d'auto-incrémentation de la colonne id
    c.execute("DELETE FROM sqlite_sequence WHERE name='donnees'")

    for entry in data:
        instruction = entry['instruction']
        contenu = entry['input']
        sortie = entry['output']
        c.execute('''INSERT INTO donnees (instruction, contenu, sortie, valide, explication)
                      VALUES (?, ?, ?, NULL, NULL)''', (instruction, contenu, sortie))
    conn.commit()
    
# Fonction pour afficher le contenu du jeu de données
def afficher_donnees():
    # Avant d'afficher les données, essayez de définir une option pour afficher toutes les lignes avec Streamlit
    st.set_option('deprecation.showfileUploaderEncoding', False)

    # Définir l'option de Pandas pour afficher toutes les lignes
    pd.set_option('display.max_rows', None)
    data = pd.read_sql('SELECT * FROM donnees', conn)
    st.write(data)

# Fonction pour valider une entrée
def valider_entree(id_entree, valide, explication):
    c.execute('''UPDATE donnees
                 SET valide = ?,
                     explication = ?
                 WHERE id = ?''', (valide, explication, id_entree))
    conn.commit()

# Fonction pour choisir une entrée au hasard à valider
def choisir_entree_aleatoire():
    c.execute('SELECT id FROM donnees WHERE valide IS NULL')
    entrees = c.fetchall()
    if entrees:
        id_entree = random.choice(entrees)[0]
        return id_entree
    else:
        return None

# Fonction pour exporter les données validées au format jsonl
def exporter_donnees():
    data = pd.read_sql('SELECT * FROM donnees WHERE valide = 1', conn)
    data_to_export = data['contenu'].tolist()
    with open('donnees_exportees.jsonl', 'w') as file:
        for entry in data_to_export:
            file.write(json.dumps({'contenu': entry}) + '\n')

    

# Interface utilisateur avec Streamlit
def main():
    if "id_entree" not in st.session_state:
        st.session_state.id_entree = choisir_entree_aleatoire()

    st.title("Application de gestion de jeu de données")

    menu = st.sidebar.selectbox("Menu", ["Accueil", "Visualisation", "Modification", "Validation", "Import/Export"])

    if menu == "Accueil":
        st.write("Bienvenue dans l'application de gestion de jeu de données.")

    elif menu == "Visualisation":
        # Fonction pour rechercher des données dans la base de données
        def rechercher_donnees(recherche):
            query = f"SELECT * FROM donnees WHERE instruction LIKE '%{recherche}%' OR contenu LIKE '%{recherche}%' OR sortie LIKE '%{recherche}%'"
            data = pd.read_sql(query, conn)
            st.write(data)

        # Demander à l'utilisateur de saisir une recherche
        recherche = st.text_input("Rechercher dans la base de données :")
        if st.button("Rechercher"):
            rechercher_donnees(recherche)
            if st.button("Afficher toutes les données"):
                afficher_donnees()
        else :
            afficher_donnees()
        
        
    
    elif menu == "Modification":
        st.subheader("Modification d'une entrée")
        id_entree = st.number_input("ID de l'entrée :", min_value=1, max_value=100, step=1)
        
        if st.button("Changer d'entrée"):
            st.session_state.id_entree = id_entree
            
        if id_entree:
            instruction = c.execute('SELECT instruction FROM donnees WHERE id = ?', (id_entree,)).fetchone()
            contenu = c.execute('SELECT contenu FROM donnees WHERE id = ?', (id_entree,)).fetchone()
            sortie = c.execute('SELECT sortie FROM donnees WHERE id = ?', (id_entree,)).fetchone()
            
            if contenu is None or sortie is None:
                st.write("L'entrée spécifiée n'existe pas.")
            else:
                contenu = contenu[0]
                sortie = sortie[0]
                
                # Afficher la description de l'entrée et son id
                st.write(f"ID de l'entrée : {id_entree}")
                st.write(f"Instruction de l'entrée : {instruction}")
                st.write(f"Contenu de l'entrée : {contenu}")
                st.write(f"Sortie de l'entrée : {sortie}")
                
                # Utiliser des champs de texte pour modifier le contenu et la sortie
                nouvelle_instruction = st.text_input("Nouvelle instruction de l'entrée :")
                nouveau_contenu = st.text_input("Nouveau contenu de l'entrée :")
                nouvelle_sortie = st.text_input("Nouvelle sortie de l'entrée :")
                
                if st.button("Modifier"):
                    if not nouvelle_instruction :
                        nouvelle_instruction = instruction[0] if instruction else ""
                    if not nouveau_contenu:
                        nouveau_contenu = contenu if contenu else ""
                    if not nouvelle_sortie:
                        nouvelle_sortie = sortie if sortie else ""
                    c.execute('''UPDATE donnees
                                 SET instruction = ?,
                                     contenu = ?,
                                     sortie = ?
                                 WHERE id = ?''', (nouvelle_instruction, nouveau_contenu, nouvelle_sortie, id_entree))
                    conn.commit()
                    st.write("Entrée modifiée avec succès.")
                    st.experimental_rerun()
        if st.session_state.id_entree:
            id_entree = st.session_state.id_entree
            instruction = c.execute('SELECT instruction FROM donnees WHERE id = ?', (id_entree,)).fetchone()
            contenu = c.execute('SELECT contenu FROM donnees WHERE id = ?', (id_entree,)).fetchone()
            sortie = c.execute('SELECT sortie FROM donnees WHERE id = ?', (id_entree,)).fetchone()
            
            if contenu is None or sortie is None:
                st.write("L'entrée spécifiée n'existe pas.")
            else:
                contenu = contenu[0]
                sortie = sortie[0]

    elif menu == "Validation":
        st.subheader("Validation d'une entrée")
        st.session_state.id_entree = choisir_entree_aleatoire()

        if st.button("Changer d'entrée"):
            st.session_state.id_entree = choisir_entree_aleatoire()
        
        if st.session_state.id_entree:
            id_entree = st.session_state.id_entree
            contenu = c.execute('SELECT contenu FROM donnees WHERE id = ?', (id_entree,)).fetchone()[0]
            explication = st.text_input("Explication de la validation :")
            
            # Afficher la description de l'entrée et son id
            st.write(f"ID de l'entrée : {id_entree}")
            st.write(f"Description de l'entrée : {contenu}")
            
            # Utiliser des boutons radio pour la validation
            valide_oui = st.radio("Valider l'entrée ?", ("Oui", "Non"))
            if st.button("Valider"):
                if valide_oui == "Oui":
                    valider_entree(id_entree, True, explication)
                    st.write("Entrée validée avec succès.")
                    st.session_state.id_entree = choisir_entree_aleatoire()
                    st.experimental_rerun()
                elif valide_oui == "Non":
                    valider_entree(id_entree, False, explication)
                    st.write("Entrée non validée avec succès.")
                    st.session_state.id_entree = choisir_entree_aleatoire()
                    st.experimental_rerun()
            else:
                st.write("Toutes les entrées ont été validées.")
        

    elif menu == "Import/Export":
        st.subheader("Import/Export de données")
        fichier_import = st.file_uploader("Importer un fichier jsonl")
        if fichier_import:
            charger_jeu_de_donnees(fichier_import)
            st.success("Jeu de données importé avec succès.")

        if st.button("Exporter les données validées au format jsonl"):
            exporter_donnees()
            st.success("Données exportées avec succès.")

if __name__ == '__main__':
    main()