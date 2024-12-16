import subprocess
import sys

def install_requirements():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dépendances installées avec succès !")
    except subprocess.CalledProcessError as e:
        print(f"Une erreur s'est produite lors de l'installation : {e}")
    except FileNotFoundError:
        print("Le fichier requirements.txt est introuvable.")

if __name__ == "__main__":
    install_requirements()
