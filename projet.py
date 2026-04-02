import os
import json
import bcrypt
import pwinput

FICHIER_UTILISATEURS = "utilisateurs.json"


def effacer_console():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nAppuyez sur Entrée pour continuer...")


def pause_et_effacer():
    pause()
    effacer_console()


def afficher_logo():
    banner = r"""
 ========================================================
   __  __  _  _                     _
  |  \/  |(_)| |__   ___  _ __ ___ | |__   ___
  | |\/| || || '_ \ / _ \| '_ ` _ \| '_ \ / _ \
  | |  | || || |_) | (_) | | | | | | |_) | (_) |
  |_|  |_||_||_.__/ \___/|_| |_| |_|_.__/ \___/

      🔒 Application de Gestion d'adresses IP 🔒
 ========================================================
    """
    print(banner)


def charger_utilisateurs():
    if not os.path.exists(FICHIER_UTILISATEURS):
        return {}

    try:
        with open(FICHIER_UTILISATEURS, "r", encoding="utf-8") as fichier:
            utilisateurs = json.load(fichier)

        for _, donnees in utilisateurs.items():
            if "actif" not in donnees:
                donnees["actif"] = True

        return utilisateurs

    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def sauvegarder_utilisateurs(utilisateurs):
    with open(FICHIER_UTILISATEURS, "w", encoding="utf-8") as fichier:
        json.dump(utilisateurs, fichier, indent=4, ensure_ascii=False)


def nettoyer_nom_utilisateur(nom_utilisateur):
    return nom_utilisateur.strip()


def creer_utilisateur(role="user"):
    effacer_console()
    afficher_logo()
    print(f"--- CRÉATION D'UN UTILISATEUR ({role.upper()}) ---\n")

    utilisateurs = charger_utilisateurs()

    while True:
        nom_utilisateur = nettoyer_nom_utilisateur(input("Nom d'utilisateur : "))
        if not nom_utilisateur:
            print("Le nom d'utilisateur ne peut pas être vide.")
        elif nom_utilisateur in utilisateurs:
            print("Ce nom d'utilisateur existe déjà.")
        else:
            break

    while True:
        mot_de_passe = pwinput.pwinput("Mot de passe : ", mask="*")
        confirmation = pwinput.pwinput("Confirmer le mot de passe : ", mask="*")

        if not mot_de_passe:
            print("Le mot de passe ne peut pas être vide.")
        elif mot_de_passe != confirmation:
            print("Les mots de passe ne correspondent pas.")
        else:
            break

    mot_de_passe_hache = bcrypt.hashpw(
        mot_de_passe.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    utilisateurs[nom_utilisateur] = {
        "mot_de_passe": mot_de_passe_hache,
        "role": role,
        "actif": True
    }

    sauvegarder_utilisateurs(utilisateurs)
    print(f"\nUtilisateur '{nom_utilisateur}' créé avec succès.")
    pause_et_effacer()


def se_connecter():
    effacer_console()
    afficher_logo()
    print("--- CONNEXION ---\n")

    utilisateurs = charger_utilisateurs()
    nom_utilisateur = nettoyer_nom_utilisateur(input("Nom d'utilisateur : "))

    if nom_utilisateur not in utilisateurs:
        print("\nUtilisateur introuvable.")
        pause_et_effacer()
        return None

    mot_de_passe = pwinput.pwinput("Mot de passe : ", mask="*")
    donnees_utilisateur = utilisateurs[nom_utilisateur]

    if not donnees_utilisateur.get("actif", True):
        print("\nCe compte est inactif. Connexion impossible.")
        pause_et_effacer()
        return None

    if bcrypt.checkpw(
        mot_de_passe.encode("utf-8"),
        donnees_utilisateur["mot_de_passe"].encode("utf-8")
    ):
        print(f"\nConnexion réussie. Bienvenue {nom_utilisateur}.")
        pause_et_effacer()
        return {
            "nom_utilisateur": nom_utilisateur,
            "role": donnees_utilisateur["role"]
        }

    print("\nMot de passe incorrect.")
    pause_et_effacer()
    return None


def ajouter_utilisateur(utilisateur_connecte):
    effacer_console()
    afficher_logo()
    print("--- AJOUTER UN UTILISATEUR ---\n")

    if utilisateur_connecte["role"] not in ["admin", "owner"]:
        print("Accès refusé.")
        pause_et_effacer()
        return

    roles_autorises = ["user", "admin"] if utilisateur_connecte["role"] == "owner" else ["user"]

    while True:
        role = input(f"Rôle du nouvel utilisateur ({'/'.join(roles_autorises)}) : ").strip().lower()
        if role in roles_autorises:
            break
        print("Rôle invalide.")

    creer_utilisateur(role)


def afficher_utilisateurs(utilisateur_connecte):
    effacer_console()
    afficher_logo()
    print("--- LISTE DES UTILISATEURS ---\n")

    if utilisateur_connecte["role"] not in ["admin", "owner"]:
        print("Accès refusé.")
        pause_et_effacer()
        return

    utilisateurs = charger_utilisateurs()

    if not utilisateurs:
        print("Aucun utilisateur trouvé.")
        pause_et_effacer()
        return

    print(f"{'Nom':<20} {'Rôle':<10} {'État':<10}")
    print("-" * 42)

    def cle_tri(item):
        nom, donnees = item
        priorite_role = {"owner": 0, "admin": 1, "user": 2}
        return (priorite_role.get(donnees.get("role", "user"), 99), nom.lower())

    for nom_utilisateur, donnees in sorted(utilisateurs.items(), key=cle_tri):
        role = donnees.get("role", "user")
        etat = "actif" if donnees.get("actif", True) else "inactif"
        print(f"{nom_utilisateur:<20} {role:<10} {etat:<10}")

    pause_et_effacer()


def modifier_role_utilisateur(utilisateur_connecte):
    effacer_console()
    afficher_logo()
    print("--- MODIFIER LE RÔLE D'UN UTILISATEUR ---\n")

    utilisateurs = charger_utilisateurs()
    nom_utilisateur = nettoyer_nom_utilisateur(input("Nom de l'utilisateur à modifier : "))

    if nom_utilisateur not in utilisateurs:
        print("Utilisateur introuvable.")
        pause_et_effacer()
        return

    if nom_utilisateur == utilisateur_connecte["nom_utilisateur"]:
        print("Vous ne pouvez pas modifier votre propre rôle.")
        pause_et_effacer()
        return

    if not utilisateurs[nom_utilisateur].get("actif", True):
        print("Impossible de modifier le rôle d'un utilisateur inactif.")
        pause_et_effacer()
        return

    role_cible = utilisateurs[nom_utilisateur]["role"]
    role_courant = utilisateur_connecte["role"]

    if role_cible == "owner":
        print("Le owner ne peut pas être modifié.")
        pause_et_effacer()
        return

    if role_courant == "admin" and role_cible == "admin":
        print("Seul le owner peut modifier un admin.")
        pause_et_effacer()
        return

    nouveaux_roles_autorises = ["user", "admin"] if role_courant == "owner" else ["user"]

    print(f"Rôle actuel : {role_cible}")
    print("État actuel : actif")

    while True:
        nouveau_role = input(f"Nouveau rôle ({'/'.join(nouveaux_roles_autorises)}) : ").strip().lower()
        if nouveau_role in nouveaux_roles_autorises:
            break
        print("Rôle invalide.")

    utilisateurs[nom_utilisateur]["role"] = nouveau_role
    sauvegarder_utilisateurs(utilisateurs)

    print(f"\nLe rôle de '{nom_utilisateur}' a été modifié en '{nouveau_role}'.")
    pause_et_effacer()


def desactiver_utilisateur(utilisateur_connecte):
    effacer_console()
    afficher_logo()
    print("--- DÉSACTIVER UN UTILISATEUR ---\n")

    utilisateurs = charger_utilisateurs()
    nom_utilisateur = nettoyer_nom_utilisateur(input("Nom de l'utilisateur à désactiver : "))

    if nom_utilisateur not in utilisateurs:
        print("Utilisateur introuvable.")
        pause_et_effacer()
        return

    if nom_utilisateur == utilisateur_connecte["nom_utilisateur"]:
        print("Vous ne pouvez pas vous désactiver vous-même.")
        pause_et_effacer()
        return

    role_cible = utilisateurs[nom_utilisateur]["role"]
    role_courant = utilisateur_connecte["role"]

    if role_cible == "owner":
        print("Le owner ne peut pas être désactivé.")
        pause_et_effacer()
        return

    if role_courant == "admin" and role_cible == "admin":
        print("Seul le owner peut désactiver un admin.")
        pause_et_effacer()
        return

    if not utilisateurs[nom_utilisateur].get("actif", True):
        print("Cet utilisateur est déjà inactif.")
        pause_et_effacer()
        return

    confirmation = input(f"Confirmer la désactivation de '{nom_utilisateur}' ? (oui/non) : ").strip().lower()

    if confirmation != "oui":
        print("Opération annulée.")
        pause_et_effacer()
        return

    utilisateurs[nom_utilisateur]["actif"] = False
    sauvegarder_utilisateurs(utilisateurs)

    print(f"\nUtilisateur '{nom_utilisateur}' désactivé.")
    pause_et_effacer()


def reactiver_utilisateur(utilisateur_connecte):
    effacer_console()
    afficher_logo()
    print("--- RÉACTIVER UN UTILISATEUR ---\n")

    if utilisateur_connecte["role"] not in ["admin", "owner"]:
        print("Accès refusé.")
        pause_et_effacer()
        return

    utilisateurs = charger_utilisateurs()
    nom_utilisateur = nettoyer_nom_utilisateur(input("Nom de l'utilisateur à réactiver : "))

    if nom_utilisateur not in utilisateurs:
        print("Utilisateur introuvable.")
        pause_et_effacer()
        return

    role_cible = utilisateurs[nom_utilisateur]["role"]
    role_courant = utilisateur_connecte["role"]

    if utilisateurs[nom_utilisateur].get("actif", True):
        print("Cet utilisateur est déjà actif.")
        pause_et_effacer()
        return

    if role_cible == "owner":
        print("Le owner ne nécessite pas de réactivation.")
        pause_et_effacer()
        return

    if role_courant == "admin" and role_cible == "admin":
        print("Seul le owner peut réactiver un admin.")
        pause_et_effacer()
        return

    confirmation = input(f"Confirmer la réactivation de '{nom_utilisateur}' ? (oui/non) : ").strip().lower()

    if confirmation != "oui":
        print("Opération annulée.")
        pause_et_effacer()
        return

    utilisateurs[nom_utilisateur]["actif"] = True
    sauvegarder_utilisateurs(utilisateurs)

    print(f"\nUtilisateur '{nom_utilisateur}' réactivé.")
    pause_et_effacer()


def est_ipv4_valide(adresse_ip):
    parties = adresse_ip.strip().split(".")

    if len(parties) != 4:
        return False

    for partie in parties:
        if not partie.isdigit():
            return False

        valeur = int(partie)

        if valeur < 0 or valeur > 255:
            return False

        if str(valeur) != partie:
            return False

    return True


def ip_vers_liste(adresse_ip):
    return [int(partie) for partie in adresse_ip.split(".")]


def determiner_classe_ip(adresse_ip):
    octets = ip_vers_liste(adresse_ip)
    premier_octet = octets[0]

    if 1 <= premier_octet <= 126:
        return "A"
    if premier_octet == 127:
        return "A (réservée : machine locale)"
    if 128 <= premier_octet <= 191:
        return "B"
    if 192 <= premier_octet <= 223:
        return "C"
    if 224 <= premier_octet <= 239:
        return "D (réservée : multicast)"
    if 240 <= premier_octet <= 255:
        return "E (réservée : jamais utilisée pour les adresses IP)"
    return "Inconnue"


def obtenir_masque_classe(adresse_ip):
    classe = determiner_classe_ip(adresse_ip)

    if classe.startswith("A"):
        return "255.0.0.0"
    if classe.startswith("B"):
        return "255.255.0.0"
    if classe.startswith("C"):
        return "255.255.255.0"
    return "Pas de masque de classe standard"


def est_ip_privee(adresse_ip):
    octets = ip_vers_liste(adresse_ip)

    if octets[0] == 10:
        return True
    if octets[0] == 172 and 16 <= octets[1] <= 31:
        return True
    if octets[0] == 192 and octets[1] == 168:
        return True

    return False


def obtenir_infos_reservees(adresse_ip):
    octets = ip_vers_liste(adresse_ip)
    informations = []

    if octets[0] == 0:
        informations.append("0.0.0.0/8 : réservée")
    if octets[0] == 100 and 64 <= octets[1] <= 127:
        informations.append("100.64.0.0/10 : réservé pour certains opérateurs")
    if octets[0] == 127:
        informations.append("127.0.0.0/8 : machine locale")
    if octets[0] == 169 and octets[1] == 254:
        informations.append("169.254.0.0/16 : IP automatique")
    if octets[0] == 192 and octets[1] == 0 and octets[2] == 2:
        informations.append("192.0.2.0/24 : documentation")
    if octets[0] == 198 and octets[1] == 51 and octets[2] == 100:
        informations.append("198.51.100.0/24 : documentation")
    if octets[0] == 203 and octets[1] == 0 and octets[2] == 113:
        informations.append("203.0.113.0/24 : documentation")
    if 224 <= octets[0] <= 239:
        informations.append("Classe D : multicast")
    if 240 <= octets[0] <= 255:
        informations.append("Classe E : réservée, jamais utilisée pour les adresses IP")
    if adresse_ip == "255.255.255.255":
        informations.append("255.255.255.255 : broadcast")

    return informations


def masque_depuis_cidr(cidr):
    bits = "1" * cidr + "0" * (32 - cidr)
    groupes_binaires = [bits[i:i + 8] for i in range(0, 32, 8)]
    groupes_decimaux = [str(int(groupe, 2)) for groupe in groupes_binaires]
    return ".".join(groupes_binaires), ".".join(groupes_decimaux)


def afficher_tableau_masques():
    effacer_console()
    afficher_logo()
    print("--- TABLEAU DES MASQUES DE /8 À /30 ---\n")
    print(f"{'CIDR':<6} {'Binaire':<39} {'Décimal pointé':<18}")
    print("-" * 70)

    for cidr in range(8, 31):
        masque_binaire, masque_decimal = masque_depuis_cidr(cidr)
        print(f"/{cidr:<5} {masque_binaire:<39} {masque_decimal:<18}")

    pause_et_effacer()


def analyser_adresse_ip():
    effacer_console()
    afficher_logo()
    print("--- ANALYSE D'UNE ADRESSE IPv4 ---\n")

    adresse_ip = input("Entrez une adresse IPv4 : ").strip()

    if not est_ipv4_valide(adresse_ip):
        print("\nLe format de l'adresse IP est invalide.")
        pause_et_effacer()
        return

    classe = determiner_classe_ip(adresse_ip)
    masque_classe = obtenir_masque_classe(adresse_ip)
    privee = "Oui" if est_ip_privee(adresse_ip) else "Non"
    infos_reservees = obtenir_infos_reservees(adresse_ip)

    print("\nRésultat")
    print("--------")
    print(f"Adresse IP         : {adresse_ip}")
    print(f"Format valide      : Oui")
    print(f"Classe             : {classe}")
    print(f"Masque de classe   : {masque_classe}")
    print(f"Adresse privée     : {privee}")

    if infos_reservees:
        print("Adresse réservée   : Oui")
        for info in infos_reservees:
            print(f" - {info}")
    else:
        print("Adresse réservée   : Non")

    pause_et_effacer()


def afficher_menu_principal():
    effacer_console()
    afficher_logo()
    print("--- MENU PRINCIPAL ---\n")
    print("1. Se connecter")
    print("2. Quitter")


def afficher_menu_utilisateur(utilisateur_connecte):
    effacer_console()
    afficher_logo()
    print(f"--- MENU ({utilisateur_connecte['nom_utilisateur']} - {utilisateur_connecte['role']}) ---\n")
    print("1. Afficher le tableau des masques")
    print("2. Analyser une adresse IPv4")

    if utilisateur_connecte["role"] in ["admin", "owner"]:
        print("3. Afficher les utilisateurs")
        print("4. Ajouter un utilisateur")
        print("5. Modifier le rôle d'un utilisateur")
        print("6. Désactiver un utilisateur")
        print("7. Réactiver un utilisateur")
        print("8. Se déconnecter")
        print("9. Quitter")
    else:
        print("3. Se déconnecter")
        print("4. Quitter")


def programme_principal():
    if not charger_utilisateurs():
        effacer_console()
        afficher_logo()
        print("Aucun utilisateur trouvé.")
        print("Création du premier compte administrateur (owner).")
        pause_et_effacer()
        creer_utilisateur(role="owner")

    utilisateur_connecte = None

    while True:
        if utilisateur_connecte is None:
            afficher_menu_principal()
            choix = input("\nVotre choix : ").strip()

            if choix == "1":
                utilisateur_connecte = se_connecter()
            elif choix == "2":
                effacer_console()
                print("Au revoir.")
                break
            else:
                print("Choix invalide.")
                pause_et_effacer()
        else:
            afficher_menu_utilisateur(utilisateur_connecte)
            choix = input("\nVotre choix : ").strip()

            if utilisateur_connecte["role"] in ["admin", "owner"]:
                if choix == "1":
                    afficher_tableau_masques()
                elif choix == "2":
                    analyser_adresse_ip()
                elif choix == "3":
                    afficher_utilisateurs(utilisateur_connecte)
                elif choix == "4":
                    ajouter_utilisateur(utilisateur_connecte)
                elif choix == "5":
                    modifier_role_utilisateur(utilisateur_connecte)
                elif choix == "6":
                    desactiver_utilisateur(utilisateur_connecte)
                elif choix == "7":
                    reactiver_utilisateur(utilisateur_connecte)
                elif choix == "8":
                    print("\nDéconnexion réussie.")
                    utilisateur_connecte = None
                    pause_et_effacer()
                elif choix == "9":
                    effacer_console()
                    print("Au revoir.")
                    break
                else:
                    print("Choix invalide.")
                    pause_et_effacer()
            else:
                if choix == "1":
                    afficher_tableau_masques()
                elif choix == "2":
                    analyser_adresse_ip()
                elif choix == "3":
                    print("\nDéconnexion réussie.")
                    utilisateur_connecte = None
                    pause_et_effacer()
                elif choix == "4":
                    effacer_console()
                    print("Au revoir.")
                    break
                else:
                    print("Choix invalide.")
                    pause_et_effacer()


if __name__ == "__main__":
    programme_principal()