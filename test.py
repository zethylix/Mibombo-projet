import os
import bcrypt
import pwinput
import json

DB_FILE = "users.json"





def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nAppuyez sur Entrée pour continuer...")


def pause_and_clear():
    pause()
    clear_console()


def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_users(users):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def clean_username(username):
    return username.strip()


def print_welcome_banner():
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


def register_user(role="user"):
    clear_console()
    print_welcome_banner()
    print(f"\n--- CRÉATION D'UN NOUVEL UTILISATEUR ({role.upper()}) ---")

    users = load_users()

    while True:
        username = clean_username(input("Entrer un nom d'utilisateur : "))
        if not username:
            print("❌ Le nom d'utilisateur ne peut pas être vide.")
        elif username in users:
            print("❌ Ce nom d'utilisateur est déjà pris.")
        else:
            break

    password = pwinput.pwinput("Créer un mot de passe : ", mask="*")
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))

    users[username] = {
        "hashed_password": hashed_password.decode("utf-8"),
        "role": role
    }

    save_users(users)
    print(f"\n✅ Utilisateur '{username}' créé avec succès avec le rôle '{role}'.")
    pause_and_clear()


def login():
    clear_console()
    print_welcome_banner()
    print("\n--- CONNEXION ---")

    users = load_users()
    username = clean_username(input("Entrer votre nom d'utilisateur : "))

    user_data = users.get(username)
    logged_user = None

    if not user_data:
        print("\n❌ Cet utilisateur n'existe pas.")
    else:
        password = pwinput.pwinput("Entrer votre mot de passe : ", mask="*")
        if bcrypt.checkpw(password.encode("utf-8"), user_data["hashed_password"].encode("utf-8")):
            print(f"\n✅ Connexion réussie. Bienvenue {username} !")
            logged_user = {"username": username, "role": user_data["role"]}
        else:
            print("\n❌ Mot de passe incorrect.")

    pause_and_clear()
    return logged_user


def add_user_as_admin(current_user):
    clear_console()
    print_welcome_banner()
    print("\n--- AJOUTER UN UTILISATEUR ---")

    allowed_roles = ["user", "admin"] if current_user["role"] == "owner" else ["user"]

    while True:
        role = input(f"Quel rôle pour le nouvel utilisateur ? ({'/'.join(allowed_roles)}) : ").strip().lower()
        if role in allowed_roles:
            break
        print("❌ Rôle invalide.")

    register_user(role=role)


def change_user_role(current_user):
    clear_console()
    print_welcome_banner()
    print("\n--- CHANGER LE RÔLE D'UN UTILISATEUR ---")

    users = load_users()
    username = clean_username(input("Entrer le nom d'utilisateur à modifier : "))
    allowed = True

    if username not in users:
        print("\n❌ Cet utilisateur n'existe pas.")
        allowed = False

    if allowed and username == current_user["username"]:
        print("\n❌ Vous ne pouvez pas modifier votre propre rôle.")
        allowed = False

    if allowed:
        target_role = users[username]["role"]
        current_role = current_user["role"]

        if target_role == "owner":
            print("\n❌ Le owner ne peut pas être modifié.")
            allowed = False

        if current_role == "admin" and target_role == "admin":
            print("\n❌ Seul le owner peut modifier un admin.")
            allowed = False

    if allowed:
        allowed_new_roles = ["user", "admin"] if current_user["role"] == "owner" else ["user"]
        print(f"Rôle actuel de {username} : {users[username]['role']}")

        while True:
            new_role = input(f"Nouveau rôle ({'/'.join(allowed_new_roles)}) : ").strip().lower()
            if new_role in allowed_new_roles:
                break
            print("❌ Rôle invalide.")

        users[username]["role"] = new_role
        save_users(users)
        print(f"\n✅ Le rôle de '{username}' a été mis à jour vers '{new_role}'.")

    pause_and_clear()


def delete_user(current_user):
    clear_console()
    print_welcome_banner()
    print("\n--- SUPPRIMER UN UTILISATEUR ---")

    users = load_users()
    username = clean_username(input("Entrer le nom d'utilisateur à supprimer : "))
    allowed = True

    if username not in users:
        print("\n❌ Cet utilisateur n'existe pas.")
        allowed = False

    if allowed and username == current_user["username"]:
        print("\n❌ Vous ne pouvez pas vous supprimer vous-même.")
        allowed = False

    if allowed:
        target_role = users[username]["role"]
        current_role = current_user["role"]

        if target_role == "owner":
            print("\n❌ Le owner ne peut pas être supprimé.")
            allowed = False

        if current_role == "admin" and target_role == "admin":
            print("\n❌ Seul le owner peut supprimer un admin.")
            allowed = False

    if allowed:
        confirm = input(f"Confirmer la suppression de '{username}' ? (oui/non) : ").strip().lower()

        if confirm == "oui":
            del users[username]
            save_users(users)
            print(f"\n✅ Utilisateur '{username}' supprimé avec succès.")
        else:
            print("\nSuppression annulée.")

    pause_and_clear()


def show_logged_menu(logged_in_user):
    clear_console()
    print_welcome_banner()
    print(f"\n--- MENU ({logged_in_user['username']} - {logged_in_user['role']}) ---")

    if logged_in_user["role"] in ["admin", "owner"]:
        print("1. Ajouter un utilisateur")
        print("2. Changer le rôle d'un utilisateur")
        print("3. Supprimer un utilisateur")
        print("4. Se déconnecter")
        print("5. Quitter")
    else:
        print("1. Se déconnecter")
        print("2. Quitter")


def show_main_menu():
    clear_console()
    print_welcome_banner()
    print("\n--- MENU PRINCIPAL ---")
    print("1. Se connecter")
    print("2. Quitter")


def main():
    if not load_users():
        clear_console()
        print_welcome_banner()
        print("Aucun utilisateur trouvé.")
        print("Veuillez créer le premier compte administrateur (OWNER).")
        pause_and_clear()
        register_user(role="owner")

    logged_in_user = None

    while True:
        if logged_in_user:
            show_logged_menu(logged_in_user)

            if logged_in_user["role"] in ["admin", "owner"]:
                choice = input("\nVotre choix : ").strip()

                if choice == "1":
                    add_user_as_admin(logged_in_user)
                elif choice == "2":
                    change_user_role(logged_in_user)
                elif choice == "3":
                    delete_user(logged_in_user)
                elif choice == "4":
                    print("\n✅ Déconnexion réussie.")
                    logged_in_user = None
                    pause_and_clear()
                elif choice == "5":
                    clear_console()
                    print("Au revoir.")
                    break
                else:
                    print("\n❌ Choix invalide.")
                    pause_and_clear()
            else:
                choice = input("\nVotre choix : ").strip()

                if choice == "1":
                    print("\n✅ Déconnexion réussie.")
                    logged_in_user = None
                    pause_and_clear()
                elif choice == "2":
                    clear_console()
                    print("Au revoir.")
                    break
                else:
                    print("\n❌ Choix invalide.")
                    pause_and_clear()
        else:
            show_main_menu()
            choice = input("\nVotre choix : ").strip()

            if choice == "1":
                logged_in_user = login()
            elif choice == "2":
                clear_console()
                print("Au revoir.")
                break
            else:
                print("\n❌ Choix invalide.")
                pause_and_clear()


if __name__ == "__main__":
    main()