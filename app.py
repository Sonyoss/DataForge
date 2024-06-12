import streamlit as st
import sqlite3
import pandas as pd
import json
import random
from datetime import datetime
import pytz

# Création de la connexion à la base de données SQLite
conn = sqlite3.connect('jeu_de_donnees.db')
c = conn.cursor()


# Création de la table pour stocker les données avec une nouvelle table pour les validations
c.execute('''CREATE TABLE IF NOT EXISTS donnees
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              instruction TEXT,
              contenu TEXT,
              sortie TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS donnees_temp
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              instruction TEXT,
              contenu TEXT,
              sortie TEXT)''')

c.execute('''
INSERT INTO donnees_temp (id, instruction, contenu, sortie)
SELECT id, instruction, contenu, sortie FROM donnees
''')

c.execute('DROP TABLE donnees')

c.execute('ALTER TABLE donnees_temp RENAME TO donnees')

c.execute('''CREATE TABLE IF NOT EXISTS validations
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              id_entree INTEGER,
              valide BOOLEAN,
              explication TEXT,
              nom TEXT,
              date_de_validation TEXT,
              FOREIGN KEY(id_entree) REFERENCES donnees(id))''')

conn.commit()

# Fonction pour charger un jeu de données depuis un fichier jsonl
def charger_jeu_de_donnees(uploaded_file):
    data = json.loads(uploaded_file.getvalue().decode('utf-8'))
    
    # Supprimer les données existantes dans les tables
    c.execute('DELETE FROM donnees')
    c.execute('DELETE FROM validations')
    
    # Réinitialiser la séquence d'auto-incrémentation de la colonne id
    c.execute("DELETE FROM sqlite_sequence WHERE name='donnees'")
    c.execute("DELETE FROM sqlite_sequence WHERE name='validations'")

    for entry in data:
        instruction = entry['instruction']
        contenu = entry['input']
        sortie = entry['output']
        c.execute('''INSERT INTO donnees (instruction, contenu, sortie)
                      VALUES (?, ?, ?)''', (instruction, contenu, sortie))
    conn.commit()
    
# Fonction pour afficher le contenu du jeu de données
def afficher_donnees():
    st.set_option('deprecation.showfileUploaderEncoding', False)
    pd.set_option('display.max_rows', None)
    data = pd.read_sql('SELECT * FROM donnees', conn)
    st.write(data)

def afficher_donnees2():
    st.set_option('deprecation.showfileUploaderEncoding', False)
    pd.set_option('display.max_rows', None)
    data = pd.read_sql('SELECT * FROM validations', conn)
    st.write(data)

# Fonction pour valider une entrée
def valider_entree(id_entree, valide, explication, nom, date_de_validation):
    c.execute('''INSERT INTO validations (id_entree, valide, explication, nom, date_de_validation)
                 VALUES (?, ?, ?, ?, ?)''', (id_entree, valide, explication, nom,date_de_validation))
    conn.commit()

# Fonction pour choisir une entrée au hasard à valider
def choisir_entree_aleatoire():
    c.execute('SELECT id FROM donnees')
    entrees = c.fetchall()
    if entrees:
        id_entree = random.choice(entrees)[0]
        return id_entree
    else:
        return None

# Fonction pour exporter les données validées au format jsonl
def exporter_donnees(type_export):
    if type_export == "Données validées":
        query = '''
            SELECT d.id, d.instruction, d.contenu, d.sortie
            FROM donnees d
            JOIN validations v
            ON d.id = v.id_entree
            WHERE v.valide = 1
        '''
    else:  # type_export == "Toutes les données"
        query = 'SELECT * FROM donnees'
 
    data = pd.read_sql(query, conn)
    data_to_export = data.to_dict('records')
    json_lines = [json.dumps(record) + '\n' for record in data_to_export]
 
    with open('donnees_exportees.jsonl', 'w') as file:
        file.writelines(json_lines)
   
    return 'donnees_exportees.jsonl'


# Interface utilisateur avec Streamlit
def main():
    
    hide_img_fs = '''
    <style>
    button[title="View fullscreen"]{
        visibility: hidden;}
    </style>
    '''
 
    st.markdown(hide_img_fs, unsafe_allow_html=True)
 
 
    if "id_entree" not in st.session_state:
        st.session_state.id_entree = choisir_entree_aleatoire()
 
    logo_url = "./img/Logo.png"
    logo_url2 = "./img/LogoText.png"
 
    col1, col2 = st.columns(2)
    with col1:
        st.image(logo_url2, use_column_width=True)
 
    
    st.sidebar.image(logo_url)
    menu = st.sidebar.selectbox("Menu", ["Accueil", "Visualisation","Ajout", "Modification", "Validation", "Import/Export"])
    
 
    if menu == "Accueil":
        st.write("Bienvenue dans DataForge, une application de gestion de jeu de données.")
        st.write("Pour une meilleure expérience, utilisez le mode sombre.")
 
        st.markdown("<hr>", unsafe_allow_html=True)
 
        st.write("Cette application vous permet de gérer un jeu de données en effectuant les actions suivantes :")
        st.write("- Importer un jeu de données au format jsonl.")
        st.write("- Visualiser les données existantes.")
        st.write("- Modifier les données existantes.")
        st.write("- Valider les données existantes.")
        st.write("- Ajouter des nouvelles données.")
        st.write("- Exporter les données validées au format jsonl.")
 
        st.markdown("<hr>", unsafe_allow_html=True)
 
        st.write("Tutoriel :")  
 
        st.write("1. Cliquez sur le menu de gauche pour choisir une action.")
        col1, col2 = st.columns(2)
        with col1:
            st.image("img/Etape1.png", use_column_width=True)
 
        st.write("2. Pour importer un jeu de données, cliquez sur le menu 'Import/Export', puis importez le fichier. ")
 
        col1, col2, col3 = st.columns(3)
 
        with col1:
            st.image("img/Etape2_1.png", use_column_width=True)
 
        with col2:
            st.image("img/Etape2_2.png", use_column_width=True)
 
        st.write("3. Pour valider une entrée, cliquez sur le bouton 'Changer d'entrée', puis remplissez les champs.")
 
        col1, col2, col3 = st.columns(3)
 
        with col1:
            st.image("img/Etape3_1.png", use_column_width=True)
        with col2:
            st.image("img/Etape3_2.png", use_column_width=True)
        with col3:
            st.image("img/Etape3_3.png", use_column_width=True)
 
        st.write("4. Pour modifier une entrée, saisissez l'ID de l'entrée, puis les nouvelles valeurs.")
 
        col1, col2, col3 = st.columns(3)
 
        with col1:
            st.image("img/Etape4_1.png", use_column_width=True)
        with col2:
            st.image("img/Etape4_2.png", use_column_width=True)
        with col3:
            st.image("img/Etape4_3.png", use_column_width=True)
 
        st.write("6. Pour visualiser les données, cliquez sur le menu 'Visualisation'.")
 
        col1, col2, col3 = st.columns(3)
 
        with col1:
            st.image("img/Etape5_1.png", use_column_width=True)
 
        with col2:
            st.image("img/Etape5_2.png", use_column_width=True)
        
        st.write("7. Pour ajouter une entrée, cliquez sur le menu 'Ajout', puis remplissez les champs.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.image("img/Etape7_1.png", use_column_width=True)
 
        with col2:
            st.image("img/Etape7_2.png", use_column_width=True)
 
        st.write("8. Pour exporter les données validées, cliquez sur le menu 'Import/Export'.")
 
        col1, col2, col3 = st.columns(3)
 
        with col1:
            st.image("img/Etape6_1.png", use_column_width=True)
 
        with col2:
            st.image("img/Etape6_2.png", use_column_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.write("A propos :")
        st.write("Cette application a été développé dans le cadre d'un projet universitaire du BUT Informatique de Nevers par DURAND Romain, SCHEER Corentin, LESPLINGUIES Tristan et CHANFI MARI Yram.")

    elif menu == "Visualisation":
        def rechercher_donnees(recherche):
            query = f"SELECT * FROM donnees WHERE instruction LIKE '%{recherche}%' OR contenu LIKE '%{recherche}%' OR sortie LIKE '%{recherche}%'"
            data = pd.read_sql(query, conn)
            st.write(data)

        recherche = st.text_input("Rechercher dans la base de données :")
        if st.button("Rechercher"):
            rechercher_donnees(recherche)
            if st.button("Afficher toutes les données"):
                st.markdown("<hr>", unsafe_allow_html=True)
                st.write("Eensemble du jeu de données : ")
                afficher_donnees()
                st.markdown("<hr>", unsafe_allow_html=True)
                st.write("Voici les entrées validées avec la personne ayant validé et les explications")
                afficher_donnees2()
        else:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.write("Ensemble du jeu de données : ")
            afficher_donnees()
            st.markdown("<hr>", unsafe_allow_html=True)
            st.write("Voici les entrées validées avec la personne ayant validé et les explications")
            afficher_donnees2()

    elif menu == "Ajout":
        st.subheader("Ajouter une entrée")          
        nouvelle_instruction = st.text_input("Nouvelle instruction de l'entrée :")
        nouveau_contenu = st.text_input("Nouveau contenu de l'entrée :")
        nouvelle_sortie = st.text_input("Nouvelle sortie de l'entrée :")
       
        if st.button("Ajouter"):
                if not nouvelle_instruction:
                    st.error("L'instruction est obligatoire.")
                elif not nouveau_contenu:
                    st.error("Le contenu est obligatoire.")
                elif not nouvelle_sortie:
                    st.error("La sortie est obligatoire.")
                else:
                    c.execute('''INSERT INTO donnees (instruction, contenu, sortie)
                        VALUES (?, ?, ?)''', (nouvelle_instruction, nouveau_contenu, nouvelle_sortie))
                    conn.commit()
                    st.write("Entrée ajouter avec succès.")
                    st.experimental_rerun()


    elif menu == "Modification":
        st.subheader("Modification d'une entrée")
        id_entree = st.number_input("ID de l'entrée :", min_value=1, step=1)
        
        if st.button("Changer d'entrée"):
            st.session_state.id_entree = id_entree
            
        if st.session_state.id_entree:
            id_entree = st.session_state.id_entree
            instruction = c.execute('SELECT instruction FROM donnees WHERE id = ?', (id_entree,)).fetchone()
            contenu = c.execute('SELECT contenu FROM donnees WHERE id = ?', (id_entree,)).fetchone()
            sortie = c.execute('SELECT sortie FROM donnees WHERE id = ?', (id_entree,)).fetchone()
            
            if contenu is None or sortie is None:
                st.write("L'entrée spécifiée n'existe pas.")
            else:
                instruction = instruction[0] if instruction else ""
                contenu = contenu[0] if contenu else ""
                sortie = sortie[0] if sortie else ""

                st.write(f"ID de l'entrée : {id_entree}")
                st.write(f"Instruction de l'entrée : {instruction}")
                st.write(f"Contenu de l'entrée : {contenu}")
                st.write(f"Sortie de l'entrée : {sortie}")
                st.markdown("<hr>", unsafe_allow_html=True)

                
                nouvelle_instruction = st.text_input("Nouvelle instruction de l'entrée :", value=instruction)
                nouveau_contenu = st.text_input("Nouveau contenu de l'entrée :", value=contenu)
                nouvelle_sortie = st.text_input("Nouvelle sortie de l'entrée :", value=sortie)
                
                if st.button("Modifier"):
                    c.execute('''UPDATE donnees
                                 SET instruction = ?,
                                     contenu = ?,
                                     sortie = ?
                                 WHERE id = ?''', (nouvelle_instruction, nouveau_contenu, nouvelle_sortie, id_entree))
                    conn.commit()
                    st.write("Entrée modifiée avec succès.")
                    st.experimental_rerun()

    elif menu == "Validation":
        if 'x' not in st.session_state:
            st.session_state.x = False

        st.subheader("Validation d'une entrée")
        if st.button("Générer une entrée"):
            st.session_state.id_entree = choisir_entree_aleatoire()
            st.session_state.x = True
        
        if st.session_state.id_entree and st.session_state.x == True:
            id_entree = st.session_state.id_entree
            instruction = c.execute('SELECT instruction FROM donnees WHERE id = ?', (id_entree,)).fetchone()[0]
            contenu = c.execute('SELECT contenu FROM donnees WHERE id = ?', (id_entree,)).fetchone()[0]
            sortie = c.execute('SELECT sortie FROM donnees WHERE id = ?', (id_entree,)).fetchone()[0]
            date_de_validation = datetime.now(pytz.timezone('Europe/Paris')).strftime("%Y-%m-%d %H:%M:%S")

            explication = st.text_input("Explication de la validation :", key="explication")
            nom = st.text_input("Votre nom :")
            st.markdown("<hr>", unsafe_allow_html=True)
            
            st.write(f"ID de l'entrée : {id_entree}")
            st.write(f"Instruction de l'entrée : {instruction}")
            st.write(f"Contenu de l'entrée : {contenu}")
            st.write(f"Sortie de l'entrée : {sortie}")
            
            valide_oui = st.radio("Valider l'entrée ?", ("Oui", "Non"))
            if st.button("Valider"):
                if not explication:
                    st.error("L'explication de la validation est obligatoire.")
                elif not nom:
                    st.error("Le nom est obligatoire.")
                else:
                    valide = True if valide_oui == "Oui" else False
                    valider_entree(id_entree, valide, explication, nom, date_de_validation)
                    st.write("Entrée validée avec succès.")
                    st.session_state.id_entree = choisir_entree_aleatoire()
                    st.experimental_rerun()

    elif menu == "Import/Export":
        st.subheader("Import/Export de données")
        fichier_import = st.file_uploader("Importer un fichier jsonl")
        if fichier_import:
            charger_jeu_de_donnees(fichier_import)
            st.success("Jeu de données importé avec succès.")

        type_export = st.selectbox("Choisissez le type de données à exporter :", ["Toutes les données", "Données validées"])

        if st.button("Exporter les données au format jsonl"):
            fichier_export = exporter_donnees(type_export)
            with open(fichier_export, 'r') as file:
                st.download_button('Télécharger le fichier', file, file_name=fichier_export)
            st.success("Données exportées avec succès.")

if __name__ == '__main__':
    main()
