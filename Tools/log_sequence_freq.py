from collections import Counter
import re

# Paramètres : chemin du fichier log et taille de la séquence (n-gram)
LOG_FILE = r"E:\C2CModding\Input\Logs\BBAI.log"
N = 3  # nombre de mots par séquence (par ex. 2 = bigrammes, 3 = trigrammes)

# Lecture et nettoyage du log
with open(LOG_FILE, "r", encoding="latin-1", errors="ignore") as f:
    texte = f.read().lower()

# Extraction des mots (ici, uniquement lettres/chiffres)
mots = re.findall(r"\w+", texte)

# Création des n-grammes
sequences = [" ".join(mots[i:i+N]) for i in range(len(mots) - N + 1)]

# Comptage des fréquences
compte = Counter(sequences)

# Affichage des 20 séquences les plus fréquentes
for seq, freq in compte.most_common(20):
    print(f"{seq} -> {freq}")
