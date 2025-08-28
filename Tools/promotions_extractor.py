import os
import xml.etree.ElementTree as ET
from collections import defaultdict, deque

XML_FOLDER = r"E:\C2CModding\Caveman2Cosmos\Assets\XML\Units"
OUTPUT_FOLDER = r"E:\C2CModding\C2C-Log-Analyser\C2C-Log-Analyser\Tools\promotion_chains_files"
VECTOR_FORMATS = ["svg", "pdf"]       # formats vectoriels souhaités

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

NS = {'ns': 'x-schema:../Schema/C2C_CIV4UnitSchema.xml'}

def parse_promotions(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    relations = []
    all_promotions = set()
    promotions = root.findall(".//ns:PromotionInfo", NS)
    print(f"Nombre de PromotionInfo : {len(promotions)}")
    for p in root.findall(".//ns:PromotionInfo", NS):
        promotion_type_el = p.find("ns:Type", NS)
        if promotion_type_el is None or promotion_type_el.text is None:
            continue
        promotion_type = promotion_type_el.text
        all_promotions.add(promotion_type)

        prereq = p.find("ns:PromotionPrereq", NS)
        if prereq is not None and prereq.text:
            relations.append((prereq.text, promotion_type))
    return relations, all_promotions

# Construire le graphe
graph = defaultdict(list)
reverse_graph = defaultdict(list)
all_nodes = set()
all_promotions_total = set()
for filename in os.listdir(XML_FOLDER):
    if filename.endswith(".xml"):
        file_path = os.path.join(XML_FOLDER, filename)
        relations, promotions_in_file = parse_promotions(file_path)
        all_promotions_total.update(promotions_in_file)
        for prereq, promo in relations:
            graph[prereq].append(promo)
            reverse_graph[promo].append(prereq)
            all_nodes.add(prereq)
            all_nodes.add(promo)

# Générer les ensembles connectés
visited_nodes = set()
ensemble_count = 0

for node in all_nodes:
    if node in visited_nodes:
        continue
    queue = deque([node])
    ensemble_nodes = set()
    ensemble_edges = set()
    while queue:
        current = queue.popleft()
        if current in ensemble_nodes:
            continue
        ensemble_nodes.add(current)
        visited_nodes.add(current)
        for neighbor in graph.get(current, []):
            ensemble_edges.add((current, neighbor))
            if neighbor not in ensemble_nodes:
                queue.append(neighbor)
        for neighbor in reverse_graph.get(current, []):
            ensemble_edges.add((neighbor, current))
            if neighbor not in ensemble_nodes:
                queue.append(neighbor)

    # Nommer le fichier avec le premier nœud (sans prereq)
    first_nodes = [n for n in ensemble_nodes if n not in reverse_graph or len(reverse_graph[n]) == 0]
    first_name = first_nodes[0] if first_nodes else f"ensemble_{ensemble_count}"
    filename = f"{first_name}.dot"
    path = os.path.join(OUTPUT_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write("digraph PromotionEnsemble {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=box, style=rounded];\n")
        f.write("  splines=polyline;\n")
        for src, dst in ensemble_edges:
            f.write(f'  "{src}" -> "{dst}" [color=blue];\n')
        f.write("}\n")
    ensemble_count += 1

# Graphe supplémentaire pour les promotions solitaires
solitary_promotions = [p for p in all_promotions_total
                       if p not in graph and p not in reverse_graph]

if solitary_promotions:
    path = os.path.join(OUTPUT_FOLDER, "solitary_promotions.dot")
    with open(path, "w", encoding="utf-8") as f:
        f.write("digraph SolitaryPromotions {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=box, style=rounded, color=green];\n")
        for promo in solitary_promotions:
            f.write(f'  "{promo}";\n')
        f.write("}\n")
    print(f"Graphe des promotions solitaires généré : {path}")

print(f"{ensemble_count} fichiers DOT pour les chaînes de promotions générés.")

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
