#!/usr/bin/env python3
import tkinter as tk
from cryptography.fernet import Fernet
from tkinter import simpledialog 
from tkinter import filedialog
from tkinter import messagebox
from tkinter.simpledialog import askstring
import re
import os
import csv

# Création de la clé
key = Fernet.generate_key()
fichiercle = open("macle.key", "wb")
fichiercle.write(key)
fichiercle.close()

# Ouvrir le fichier clé
fichiercle = open("macle.key", "rb")
key = fichiercle.read()

f = Fernet(key)

# Créer une liste pour stocker les données à crypter
donnees_a_crypter = []

# Variable pour maintenir le compteur de lignes
compteur_lignes = 0

# Fonction pour charger le compteur de lignes depuis un fichier
def charger_compteur():
    global compteur_lignes
    try:
        with open("compteur.txt", "r") as fichier_compteur:
            compteur_lignes = int(fichier_compteur.read())
    except FileNotFoundError:
        compteur_lignes = 0

# Fonction pour enregistrer le compteur de lignes dans un fichier
def enregistrer_compteur():
    with open("compteur.txt", "w") as fichier_compteur:
        fichier_compteur.write(str(compteur_lignes))

# Fonction pour déterminer le numéro de ligne actuel dans le fichier "liste.txt"
def determiner_numero_ligne_actuel():
    try:
        with open("liste.txt", "r") as fichier_liste:
            lignes = fichier_liste.readlines()
            return len(lignes)
    except FileNotFoundError:
        return 0

# Charger le compteur de lignes au démarrage
charger_compteur()

# Mettre à jour le compteur de lignes en fonction du numéro de ligne actuel
compteur_lignes = determiner_numero_ligne_actuel()

# Fonction de validation du code postal canadien
def valider_code_postal(code_postal):

    # Expression régulière pour le format A1A 1A1
    regex = r'^[A-Z]\d[A-Z]\d[A-Z]\d$'  # Modifié pour prendre en compte l'espace

    # Supprimer les espaces en trop et convertir en majuscules
    code_postal = code_postal.strip().upper()

    # Vérifier si le code postal correspond à l'expression régulière
    if re.match(regex, code_postal):
        # Insérer un trait '-' après les 3 premiers caractères
        code_postal = code_postal[:3] + '-' + code_postal[3:]
        return code_postal
    else:
        return False
    
# Fonction pour ajouter des données à la file et passer au champ suivant
def add_data_to_queue(event):
    global compteur_lignes  # Utilisation de la variable globale

    prenom = entry_prenom.get().upper()
    nom = entry_nom.get().upper()
    adresse = entry_adresse.get().upper()
    ville = entry_ville.get().upper()
    code_postal = valider_code_postal(entry_code_postal.get())
   
    if prenom and nom and adresse and ville and code_postal:
        compteur_lignes += 1  # Incrémenter le compteur de lignes

        donnees_a_crypter.append((prenom, nom, adresse, ville, code_postal))

        # Effacer les champs
        entry_prenom.delete(0, tk.END)
        entry_nom.delete(0, tk.END)
        entry_adresse.delete(0, tk.END)
        entry_ville.delete(0, tk.END)
        entry_code_postal.delete(0, tk.END)

        # Placer le focus sur le champ "prénom"
        entry_prenom.focus_set()

        # Écrire les données dans le fichier liste.txt avec le numéro de ligne
        with open("liste.txt", "a") as fichier_liste:
            fichier_liste.write(f"{compteur_lignes}:{prenom},{nom},{adresse},{ville},{code_postal}\n")

        # Enregistrer le compteur de lignes mis à jour
        enregistrer_compteur()

# Fonction pour demander la clé à l'utilisateur
def demander_cle():
    return askstring("Entrer la clé de chiffrement", "Veuillez entrer la clé de chiffrement :")

# Créer une fonction pour chiffrer le contenu de liste.txt et le sauvegarder dans filecrypt.txt
def chiffrer_fichier():

    # Demander à l'utilisateur la clé de chiffrement
    key_input = demander_cle()
    if not key_input:
        return

    try:
        key = key_input.encode()
        #f = Fernet(key)

        # Lire le contenu de liste.txt
        with open("liste.txt", "r") as fichier_liste:
            donnees_a_chiffrer = fichier_liste.read()

        # Chiffrer le contenu
        nom_fichier = f.encrypt(donnees_a_chiffrer.encode())

        enr_fichier = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Fichiers texte chiffrés", "*.txt")])
        
        if enr_fichier:
            with open(enr_fichier, 'wb') as fichier:
                fichier.write(nom_fichier)
            print("Texte chiffré sauvegardé avec succès dans", nom_fichier)
        
        messagebox.showinfo("Chiffrement réussi", "Contenu de liste.txt chiffré avec succès.", icon='info')
    except Exception as e:
        messagebox.showerror("Erreur de chiffrement", "Le chiffrement du contenu de liste.txt a échoué.")

# Fonction pour sélectionner un fichier à décrypter
def selectionner_fichier_a_dechiffrer():
    nom_fichier = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Fichiers texte chiffrés", "*.txt")])
    if nom_fichier:
        cle_texte = demander_cle()  # Demande la clé de déchiffrement à l'utilisateur
        if cle_texte:
            dechiffrer_fichier(nom_fichier, cle_texte)

# Fonction pour décrypter le texte et l'écrire dans un fichier decrypt.txt
def dechiffrer_fichier(nom_fichier, cle_texte):
    try:
        with open(nom_fichier, 'rb') as fichier:
            texte_chiffre = fichier.read()
            f = Fernet(cle_texte.encode())  # Crée un nouvel objet Fernet avec la clé de déchiffrement
            texte_dechiffre = f.decrypt(texte_chiffre)  # Déchiffre le texte
            # Écrit le texte déchiffré dans un fichier decrypt.txt
            with open("decrypt.txt", 'w') as fichier_decrypt:
                fichier_decrypt.write(texte_dechiffre.decode())

        messagebox.showinfo("Déchiffrement réussi", "Contenu déchiffré avec succès decrypt.txt.", icon='info')
    except Exception as e:
        label_result.config(text=f"Erreur lors du déchiffrement : {str(e)}")

# Fonction pour supprimer une ligne spécifique de liste.txt et ajuster les autres numéros de ligne
def supprimer_ligne():
    try:
        numero_ligne = simpledialog.askinteger("Supprimer une ligne", "Entrez le numéro de la ligne à supprimer:")
        if not numero_ligne:
            return

        with open("liste.txt", "r") as fichier_liste:
            lignes = fichier_liste.readlines()

        if 1 <= numero_ligne <= len(lignes):
            lignes.pop(numero_ligne - 1)

            # Ajuster les numéros de ligne restants
            for i in range(len(lignes)):
                ligne = lignes[i].split(":", 1)
                ligne[0] = str(i + 1)
                lignes[i] = ":".join(ligne)

            with open("liste.txt", "w") as fichier_liste:
                fichier_liste.writelines(lignes)

            messagebox.showinfo("Suppression réussie", "Ligne supprimée avec succès.", icon='info')

            # Réduire le compteur de 1
            global compteur_lignes
            if compteur_lignes > 0:
                compteur_lignes -= 1

            # Enregistrer le compteur de lignes mis à jour
            enregistrer_compteur()
            
            # Vérifier si le fichier est vide, et le supprimer si nécessaire
            if not lignes:
                os.remove("liste.txt")
                os.remove("compteur.txt")
        else:
            messagebox.showerror("Erreur de suppression", "Le numéro de ligne n'est pas valide.")
    except Exception as e:
        messagebox.showerror("Erreur de suppression", "La suppression de la ligne a échoué.")

# Fonction pour modifier une ligne spécifique dans liste.txt sans affecter le reste
def modifier_ligne():
    try:
        numero_ligne = simpledialog.askinteger("Modifier une ligne", "Entrez le numéro de la ligne à modifier:")
        if not numero_ligne:
            return

        with open("liste.txt", "r") as fichier_liste:
            lignes = fichier_liste.readlines()

        if 1 <= numero_ligne <= len(lignes):
            ligne_a_modifier = lignes[numero_ligne - 1]
            prenom, nom, adresse, ville, code_postal = ligne_a_modifier.split(":")[1].split(",")

            choix_modification = simpledialog.askstring("Modifier une ligne", f"Que souhaitez-vous modifier pour la ligne {numero_ligne} ? \n(P)rénom (N)om (A)dresse (V)ille (C)ode-postal")
            if choix_modification == "p" or choix_modification == "P":
                nouveau_prenom = simpledialog.askstring("Modifier une ligne", f"Entrez le nouveau prénom pour la ligne {numero_ligne}:")
                ligne_modifiee = f"{numero_ligne}:{nouveau_prenom.upper()},{nom},{adresse},{ville},{code_postal}"
            elif choix_modification == "n" or choix_modification == "N":
                nouveau_nom = simpledialog.askstring("Modifier une ligne", f"Entrez le nouveau nom pour la ligne {numero_ligne}:")
                ligne_modifiee = f"{numero_ligne}:{prenom},{nouveau_nom.upper()},{adresse},{ville},{code_postal}"
            elif choix_modification == "a" or choix_modification == "A":
                nouveau_adresse = simpledialog.askstring("Modifier une ligne", f"Entrez la nouvelle adresse pour la ligne {numero_ligne}:")
                ligne_modifiee = f"{numero_ligne}:{prenom},{nom},{nouveau_adresse.upper()},{ville},{code_postal}"
            elif choix_modification == "v" or choix_modification == "V":
                nouveau_ville = simpledialog.askstring("Modifier une ligne", f"Entrez la nouvelle ville pour la ligne {numero_ligne}:")
                ligne_modifiee = f"{numero_ligne}:{prenom},{nom},{adresse},{nouveau_ville.upper()},{code_postal}"
            elif choix_modification == "c" or choix_modification == "C":
                while True:
                    nouveau_code_postal = simpledialog.askstring("Modifier une ligne", f"Entrez le nouveau code-postal pour la ligne {numero_ligne}:")
                    if nouveau_code_postal is None:
                        break
                    else:
                        nouveau_code_postal = valider_code_postal(nouveau_code_postal)
                        if nouveau_code_postal:
                            break
                if nouveau_code_postal is not None:
                    ligne_modifiee = f"{numero_ligne}:{prenom},{nom},{adresse},{ville},{nouveau_code_postal}"
                else:
                    return
            else:
                messagebox.showerror("Erreur de modification", "Choix de modification invalide.")
                return
            
            # Vérifier si la ligne d'origine contenait un saut de ligne, puis ajouter ou ne pas ajouter le saut de ligne
            if ligne_modifiee.endswith("\n"):
                lignes[numero_ligne - 1] = ligne_modifiee  # Ne pas ajouter de saut de ligne
            else:
                lignes[numero_ligne - 1] = ligne_modifiee + "\n" # Ajouter le saut de ligne
                
            with open("liste.txt", "w") as fichier_liste:
                fichier_liste.writelines(lignes)

            messagebox.showinfo("Modification réussie", "Ligne modifiée avec succès.", icon='info')
        else:
            messagebox.showerror("Erreur de modification", "Le numéro de ligne n'est pas valide.")
    except Exception as e:
        messagebox.showerror("Erreur de modification", "La modification de la ligne a échoué.")

# Fonction pour afficher le contenu actuel du fichier liste.txt
def afficher_contenu_liste():
    try:
        with open("liste.txt", "r") as fichier_liste:
            contenu = fichier_liste.read()

        # Créer une nouvelle fenêtre
        affichage_window = tk.Toplevel(window)
        affichage_window.title("Contenu de liste.txt")

        # Créer un widget d'édition de texte (Text)
        text_widget = tk.Text(affichage_window)
        text_widget.insert(tk.END, contenu)
        text_widget.pack()

        # Ajouter un bouton pour fermer la fenêtre
        fermer_button = tk.Button(affichage_window, text="Fermer", command=affichage_window.destroy)
        fermer_button.pack()

    except FileNotFoundError:
        messagebox.showerror("Erreur", "Le fichier liste.txt n'existe pas.")

# Fonction pour afficher le contenu du fichier "resultats.txt" dans une fenêtre Tkinter
def afficher_resultats_recherche():
    # Créez une fenêtre Tkinter
    fenetre = tk.Tk()
    fenetre.title("Résultats de la recherche")

    # Créez un widget de texte pour afficher le contenu du fichier
    texte_resultats = tk.Text(fenetre)
    texte_resultats.pack()

    # Ouvrir le fichier "resultats.txt" en mode lecture
    with open("resultats.txt", "r") as fichier_resultats:
        contenu = fichier_resultats.read()
        texte_resultats.insert(tk.END, contenu)

    # Démarrez la boucle principale de Tkinter pour afficher la fenêtre
    fenetre.mainloop()

# Définition de la fonction demander_type_recherche
def demander_type_recherche():
    choix = askstring("Choisir le type de recherche", "(P)rénom, (N)om, (A)dresse, (V)ille ou (C)ode postal:")

    # Chemin vers le fichier
    chemin_fichier = "liste.txt"  # Assurez-vous de mettre le bon chemin

    # Vérifiez le choix de l'utilisateur et demandez la valeur correspondante
    if choix:
        choix = choix.lower()
        if choix in ('p', 'n', 'a', 'v', 'c'):

            if choix == 'p':
                valeur_rechercher = askstring("Entrez le Prénom".format(choix), choix.capitalize()+"rénom")
            elif choix == 'n':
                valeur_rechercher = askstring("Entrez le Nom".format(choix), choix.capitalize()+"om")
            elif choix == 'a':
                valeur_rechercher = askstring("Entrez l'Adresse".format(choix), choix.capitalize()+"dresse")
            elif choix == 'v':
                valeur_rechercher = askstring("Entrez la Ville".format(choix), choix.capitalize()+"ille")
            elif choix == 'c':
                valeur_rechercher = askstring("Entrez le Code-Postal".format(choix), choix.capitalize()+"ode-Postal avec -")
            if valeur_rechercher:
                rechercher(valeur_rechercher.upper(), choix)
        else:
            print("Option invalide")
    
# Définition de la fonction rechercher
def rechercher(valeur_recherchee, colonne_recherchee):
    # Chemin vers le fichier
    chemin_fichier = "liste.txt"  # Assurez-vous de mettre le bon chemin

    # Initialisation d'un drapeau pour vérifier si la valeur a été trouvée
    valeur_trouvee = False

    # Dictionnaire de correspondance entre les choix de l'utilisateur et les colonnes
    choix_colonnes = {
        'p': 0,   # Index de la colonne "Prénom"
        'n': 1,      # Index de la colonne "Nom"
        'a': 2,  # Index de la colonne "Adresse"
        'v': 3,    # Index de la colonne "Ville"
        'c': 4  # Index de la colonne "Code postal"
    }

    # Ouvrir un fichier de sortie pour enregistrer les lignes trouvées
    fichier_sortie = open("resultats.txt", "w")

    # Vérifiez si le choix de colonne est valide
    if colonne_recherchee.lower() in choix_colonnes:
        colonne_index = choix_colonnes[colonne_recherchee.lower()]

        # Ouvrir le fichier en mode lecture
        with open(chemin_fichier, mode='r') as fichier:

            # Lire chaque ligne du fichier
            for ligne in fichier:
                # Supprimez le numéro suivi de deux points
                contenu_sans_numero = ligne.split(':', 1)[1]

                # Divisez le contenu après les deux points en utilisant ',' comme séparateur
                colonnes = contenu_sans_numero.strip().split(',')

                # Assurez-vous qu'il y a au moins 5 colonnes
                if len(colonnes) == 5:
                    # Vérifiez si la valeur correspondante à la colonne spécifiée contient la valeur recherchée
                    if valeur_recherchee.lower() in colonnes[colonne_index].strip().lower():
                        # Afficher les résultats dans la zone de texte
                        resultat = "{}\n".format(ligne.strip())
                        valeur_trouvee = True
                        # Écrivez le résultat dans le fichier de sortie
                        fichier_sortie.write(resultat)

    # Fermez le fichier de sortie
    fichier_sortie.close()
    afficher_resultats_recherche()

    # Vérifiez si la valeur a été trouvée
    if not valeur_trouvee:
        print("Aucune correspondance trouvée dans la colonne '{}'.".format(colonne_recherchee))

def quitter():
    if messagebox.askyesno("Confirmation", "Êtes-vous sûr\nde vouloir quitter ? "):
        window.destroy()  # Fermer la fenêtre principale

# Fonction pour passer au champ "Nom" lorsque la touche Entrée est pressée dans le champ "Prénom"
def focus_on_nom(event):
    entry_nom.focus_set()

# Fonction pour passer au champ "ville" lorsque la touche Entrée est pressée dans le champ "nom"
def focus_on_adresse(event):
    entry_adresse.focus_set()

# Fonction pour passer au champ "adresse" lorsque la touche Entrée est pressée dans le champ "ville"
def focus_on_ville(event):
    entry_ville.focus_set()

# Fonction pour passer au champ "ville" lorsque la touche Entrée est pressée dans le champ "code-postal"
def focus_on_code_postal(event):
    entry_code_postal.focus_set()
    
# Créer la fenêtre principale
window = tk.Tk()
window.title("Base de données (DLC)")
window.geometry('800x600')
window.resizable(width=False, height=False)

label_prenom = tk.Label(window, text="Prénom:")
label_prenom.pack()
#champ prénom
entry_prenom = tk.Entry(window, width=25)
entry_prenom.pack()

label_nom = tk.Label(window, text="Nom:")
label_nom.pack()
#champ nom
entry_nom = tk.Entry(window, width=25)
entry_nom.pack()

label_adresse = tk.Label(window, text="Adresse:")
label_adresse.pack()
#champ adresse
entry_adresse = tk.Entry(window, width=25)
entry_adresse.pack()

label_ville = tk.Label(window, text="Ville:")
label_ville.pack()
#champ ville
entry_ville = tk.Entry(window, width=25)
entry_ville.pack()

label_code_postal = tk.Label(window, text="Code-Postal:")
label_code_postal.pack()
# Entrée pour le code postal
entry_code_postal = tk.Entry(window)
entry_code_postal.pack()

# Créer un bouton pour afficher le contenu de liste.txt
afficher_contenu_button = tk.Button(window, text="Afficher Contenu Liste", command=afficher_contenu_liste)
afficher_contenu_button.pack()
afficher_contenu_button.place(x=320, y=300)

# Créer un bouton pour modifier une ligne de liste.txt
modifier_ligne_button = tk.Button(window, text="Modifier Ligne", command=modifier_ligne)
modifier_ligne_button.pack()
modifier_ligne_button.place(x=260, y=350)

# Créer un bouton pour supprimer une ligne de liste.txt
supprimer_ligne_button = tk.Button(window, text="Supprimer Ligne", command=supprimer_ligne)
supprimer_ligne_button.pack()
supprimer_ligne_button.place(x=420, y=350)

encrypt_button = tk.Button(window, text="Chiffrer la liste", command=chiffrer_fichier)
encrypt_button.pack()
encrypt_button.place(x=260, y=400)

decrypt_button = tk.Button(window, text="Déchiffrer la liste", command=selectionner_fichier_a_dechiffrer)
decrypt_button.pack()
decrypt_button.place(x=420, y=400)

recherche_nom_button = tk.Button(window, text="Rechercher", command=demander_type_recherche)
recherche_nom_button.pack()
recherche_nom_button.place(x=260, y=450)

# Créer un bouton "Quitter"
bouton_quitter = tk.Button(window, text="Quitter", command=quitter)
bouton_quitter.place(x=690, y=550)

# Lier la fonction à l'événement Entrée dans le champ "Prénom"
entry_prenom.bind("<Return>", focus_on_nom)
entry_nom.bind("<Return>", focus_on_adresse)
entry_adresse.bind("<Return>", focus_on_ville)
entry_ville.bind("<Return>", focus_on_code_postal)
entry_code_postal.bind("<Return>", add_data_to_queue)

# Associer la demande de confirmation de quitter à la fermeture de la fenêtre
window.protocol("WM_DELETE_WINDOW", quitter)

label_result = tk.Label(window, text="")
label_result.pack()


window.mainloop()
