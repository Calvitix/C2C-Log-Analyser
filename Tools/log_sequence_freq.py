from collections import Counter
import re

# Paramètres : chemin du fichier log et taille de la séquence (n-gram)
LOG_FILE = r"E:\C2CModding\Input\Logs\BBAI.log"
N = 4  # nombre de mots par séquence (par ex. 2 = bigrammes, 3 = trigrammes)

print(f"[INFO] Ouverture du fichier : {LOG_FILE}")

# Lecture et nettoyage du log
with open(LOG_FILE, "r", encoding="latin-1", errors="ignore") as f:
    texte = f.read().lower()

print(f"[INFO] Taille du texte lu : {len(texte)} caractères")

# Extraction des mots (ici, uniquement lettres/chiffres)
mots = re.findall(r"\w+", texte)
print(f"[INFO] Nombre total de mots extraits : {len(mots)}")
print(f"[DEBUG] Extrait des 20 premiers mots : {mots[:20]}")

# Création des n-grammes
print(f"[INFO] Création des séquences de {N} mots...")
sequences = [" ".join(mots[i:i+N]) for i in range(len(mots) - N + 1)]
print(f"[INFO] Nombre total de séquences générées : {len(sequences)}")
print(f"[DEBUG] Exemple des 10 premières séquences : {sequences[:10]}")

# Comptage des fréquences
print("[INFO] Comptage des séquences...")
compte = Counter(sequences)


from collections import Counter
import re

# Paramètres : chemin du fichier log et taille de la séquence (n-gram)
LOG_FILE = r"E:\C2CModding\Input\Logs\AiEvaluation.log"
N = 4  # nombre de mots par séquence (par ex. 2 = bigrammes, 3 = trigrammes)

print(f"[INFO] Ouverture du fichier : {LOG_FILE}")

# Lecture et nettoyage du log
with open(LOG_FILE, "r", encoding="latin-1", errors="ignore") as f:
    texte = f.read().lower()

print(f"[INFO] Taille du texte lu : {len(texte)} caractères")

# Extraction des mots (ici, uniquement lettres/chiffres)
mots = re.findall(r"\w+", texte)
print(f"[INFO] Nombre total de mots extraits : {len(mots)}")
print(f"[DEBUG] Extrait des 20 premiers mots : {mots[:20]}")

# Création des n-grammes
print(f"[INFO] Création des séquences de {N} mots...")
sequences = [" ".join(mots[i:i+N]) for i in range(len(mots) - N + 1)]
print(f"[INFO] Nombre total de séquences générées : {len(sequences)}")
print(f"[DEBUG] Exemple des 10 premières séquences : {sequences[:10]}")

# Comptage des fréquences
print("[INFO] Comptage des séquences...")
compte2 = Counter(sequences)

# Affichage des 40 séquences les plus fréquentes
print("[INFO] Top 40 des séquences les plus fréquentes de BBAI ("+ str(N) + " mots):")
for seq, freq in compte.most_common(40):
    print(f"   {seq} -> {freq}")

# Affichage des 40 séquences les plus fréquentes
print("[INFO] Top 40 des séquences les plus fréquentes de AiEvaluation ("+ str(N) + " mots):")
for seq, freq in compte2.most_common(40):
    print(f"   {seq} -> {freq}")

print("[INFO] Fin du script")

