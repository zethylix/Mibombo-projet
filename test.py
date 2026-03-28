import bcrypt
import pwinput
import json
import os

DB_FILE = "users.json"

def load_users():
    """Charge les utilisateurs depuis le fichier JSON."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_users(users):
    """Sauvegarde les utilisateurs dans le fichier JSON."""
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(role="user"):
    """Enregistre un nouvel utilisateur."""
    print(f"\n--- CRÉATION D'UN NOUVEL UTILISATEUR ({role.upper()}) ---")
    users = load_users()
    
    while True:
        username = input("Entrer un nom d'utilisateur : ")
        if username in users:
            print("Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre")
        elif not username:
            print("Le nom d'utilisateur ne peut pas être vide")
        else:
            break

    password = pwinput.pwinput("Créer un mot de passe : ", mask="*")
    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    # Le hash doit être décodé en string pour être stocké en JSON
    users[username] = {
        "hashed_password": hashed_password.decode("utf-8"),
        "role": role
    }
    
    save_users(users)
    print(f" Utilisateur '{username}' créé avec succès avec le rôle '{role}'.")

def login():
    """Gère la connexion d'un utilisateur."""
    print("\n--- CONNEXION ---")
    users = load_users()
    username = input("Entrer votre nom d'utilisateur : ")

    user_data = users.get(username)
    if not user_data:
        print("Cet utilisateur n'existe pas.")
        return None

    password = pwinput.pwinput("Entrer votre mot de passe : ", mask="*")

    # On doit encoder le mot de passe entré et le hash stocké pour la comparaison
    password_bytes = password.encode("utf-8")
    hashed_password_bytes = user_data["hashed_password"].encode("utf-8")
    
    if bcrypt.checkpw(password_bytes, hashed_password_bytes):
        print(f"Connexion réussie. Bienvenue {username} !")
        return {"username": username, "role": user_data["role"]}
    else:
        print("Mot de passe incorrect.")
        return None

def add_user_as_admin():
    """Permet à un admin d'ajouter un nouvel utilisateur ou admin."""
    print("\n--- AJOUTER UN UTILISATEUR (ADMIN) ---")
    while True:
        role = input("Quel rôle pour le nouvel utilisateur ? (user/admin) : ").lower()
        if role in ["user", "admin"]:
            break
        else:
            print("Rôle invalide. Veuillez choisir 'user' ou 'admin'.")
    
    register_user(role=role)

def change_user_role():
    """Permet à un admin de changer le rôle d'un utilisateur."""
    print("\n--- CHANGER LE RÔLE D'UN UTILISATEUR ---")
    users = load_users()
    username = input("Entrer le nom d'utilisateur à modifier : ")
    
    if username not in users:
        print("Cet utilisateur n'existe pas.")
        return
        
    print(f"Rôle actuel de {username} : {users[username]['role']}")
    while True:
        new_role = input("Nouveau rôle (user/admin) : ").lower()
        if new_role in ["user", "admin"]:
            break
        else:
            print("Rôle invalide. Veuillez choisir 'user' ou 'admin'.")
            
    users[username]["role"] = new_role
    save_users(users)
    print(f"Le rôle de '{username}' a été mis à jour avec succès vers '{new_role}'.")

def print_welcome_banner():
    """Affiche le logo et le nom de l'application au lancement."""
    # Efface la console 
    os.system('cls' if os.name == 'nt' else 'clear')

    banner = r"""
 ========================================================
   __  __  _  _                     _           
  |  \/  |(_)| |__   ___  _ __ ___ | |__   ___  
  | |\/| || || '_ \ / _ \| '_ ` _ \| '_ \ / _ \ 
  | |  | || || |_) | (_) | | | | | | |_) | (_) |
  |_|  |_||_||_.__/ \___/|_| |_| |_|_.__/ \___/ 
                                                
      🔒 Système de Gestion d'Authentification 🔒
 ========================================================
    """
    print(banner)

def main():
    """Fonction principale de l'application."""
    print_welcome_banner()

    # Si le fichier d'utilisateurs est vide, on force la création du premier admin
    if not load_users():
        print("Aucun utilisateur trouvé. Veuillez créer le premier compte administrateur.")
        register_user(role="admin")

    logged_in_user = None

    while True:
        if logged_in_user:
            # Menu pour utilisateur connecté
            print(f"\n--- MENU ({logged_in_user['username']} - {logged_in_user['role']}) ---")
            if logged_in_user['role'] == 'admin':
                print("1. Ajouter un utilisateur/admin")
                print("2. Changer le rôle d'un utilisateur")
                print("3. Se déconnecter")
                print("4. Quitter")

                choice = input("Votre choix : ")
                if choice == '1':
                    add_user_as_admin()
                elif choice == '2':
                    change_user_role()
                elif choice == '3':
                    logged_in_user = None
                    print("Déconnexion réussie.")
                elif choice == '4':
                    break
                else:
                    print("Choix invalide.")
            else:
                print("1. Se déconnecter")
                print("2. Quitter")
                
                choice = input("Votre choix : ")
                if choice == '1':
                    logged_in_user = None
                    print("Déconnexion réussie.")
                elif choice == '2':
                    break
                else:
                    print("Choix invalide.")

        else:
            # Menu pour utilisateur non connecté
            print("\n--- MENU PRINCIPAL ---")
            print("1. Se connecter")
            print("2. Quitter")
            
            choice = input("Votre choix : ")
            if choice == '1':
                logged_in_user = login()
            elif choice == '2':
                break
            else:
                print("Choix invalide.")

if __name__ == "__main__":
    main()
