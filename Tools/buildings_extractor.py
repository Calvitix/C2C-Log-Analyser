
import os
import xml.etree.ElementTree as ET
from collections import defaultdict, deque


# Dossier contenant les fichiers XML
XML_FOLDER = "E:\C2CModding\Caveman2Cosmos\Assets\XML\Buildings"
OUTPUT_FOLDER = "building_chains_files"
VECTOR_FORMATS = ["svg", "pdf"]       # formats vectoriels souhaités


os.makedirs(OUTPUT_FOLDER, exist_ok=True)

NS = {'ns': 'x-schema:../Schema/C2C_CIV4BuildingsSchema.xml'}

# 1. Extraire toutes les relations
def parse_buildings(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    relations = []
    for b in root.findall(".//ns:BuildingInfo", NS):
        building_type_el = b.find("ns:Type", NS)
        if building_type_el is None or building_type_el.text is None:
            continue
        building_type = building_type_el.text

        obsoletes = b.find("ns:ObsoletesToBuilding", NS)
        if obsoletes is not None and obsoletes.text:
            relations.append((building_type, obsoletes.text, 'obsoletes'))

        replacements = b.find("ns:ReplacementBuildings", NS)
        if replacements is not None:
            for r in replacements.findall("ns:BuildingType", NS):
                if r.text:
                    relations.append((building_type, r.text, 'replacement'))
    return relations

# 2. Construire le graphe global
graph = defaultdict(list)
all_nodes = set()
for filename in os.listdir(XML_FOLDER):
    if filename.endswith(".xml"):
        file_path = os.path.join(XML_FOLDER, filename)
        for src, dst, rel_type in parse_buildings(file_path):
            graph[src].append((dst, rel_type))
            all_nodes.add(src)
            all_nodes.add(dst)

# 3. Trouver les ensembles connectés via BFS
visited_nodes = set()
ensemble_count = 0

for node in all_nodes:
    if node in visited_nodes:
        continue
    # BFS pour trouver tout l'ensemble connecté
    queue = deque([node])
    ensemble_nodes = set()
    ensemble_edges_set = set()  # pour éviter les doublons
    while queue:
        current = queue.popleft()
        if current in ensemble_nodes:
            continue
        ensemble_nodes.add(current)
        visited_nodes.add(current)
        # voisins descendants uniquement
        for neighbor, rel_type in graph.get(current, []):
            edge = (current, neighbor, rel_type)
            if edge not in ensemble_edges_set:
                ensemble_edges_set.add(edge)
            if neighbor not in ensemble_nodes:
                queue.append(neighbor)

    # Identifier le dernier bâtiment (nœud sans successeur)
    last_buildings = [n for n in ensemble_nodes if n not in graph or len(graph[n]) == 0]
    if last_buildings:
        last_name = last_buildings[0]
    else:
        last_name = f"ensemble_{ensemble_count}"
    filename = f"{last_name}.dot"
    path = os.path.join(OUTPUT_FOLDER, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("digraph BuildingEnsemble {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=box, style=rounded];\n")
        f.write("  splines=polyline;\n")
        for src, dst, rel_type in ensemble_edges_set:
            color = "red" if rel_type == "obsoletes" else "blue"
            f.write(f'  "{src}" -> "{dst}" [color={color}];\n')
        f.write("}\n")
    ensemble_count += 1

print(f"{ensemble_count} fichiers DOT générés dans {OUTPUT_FOLDER}")


# Générer un SVG (vectoriel, lisible dans les navigateurs)
#dot -Tsvg building_chains.dot -o building_chains.svg

# Générer un PDF (vectoriel, imprimable)
#dot -Tpdf building_chains.dot -o building_chains.pdf

# Générer EPS (vectoriel, compatible avec LaTeX)
#dot -Teps building_chains.dot -o building_chains.eps

import os
import subprocess

DOT_FOLDER = OUTPUT_FOLDER  # dossier contenant tous les .dot


for dot_file in os.listdir(DOT_FOLDER):
    if dot_file.endswith(".dot"):
        dot_path = os.path.join(DOT_FOLDER, dot_file)
        base_name = os.path.splitext(dot_file)[0]

        for fmt in VECTOR_FORMATS:
            output_path = os.path.join(DOT_FOLDER, f"{base_name}.{fmt}")
            subprocess.run(["dot", f"-T{fmt}", dot_path, "-o", output_path])
            print(f"Généré : {output_path}")

print("Conversion DOT -> vectoriel terminée !")
