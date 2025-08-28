import os
import xml.etree.ElementTree as ET
from collections import defaultdict, deque

import os
import xml.etree.ElementTree as ET
from collections import defaultdict, deque

XML_FOLDER = r"E:\C2CModding\Caveman2Cosmos\Assets\XML\Units"
OUTPUT_FOLDER = r"E:\C2CModding\C2C-Log-Analyser\C2C-Log-Analyser\Tools\unit_chains_files"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

NS = {'ns': 'x-schema:../Schema/C2C_CIV4UnitSchema.xml'}

def parse_units(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    relations = []
    all_units = set()

    for u in root.findall(".//ns:UnitInfos/ns:UnitInfo", NS):
        unit_type_el = u.find("ns:Type", NS)
        if unit_type_el is None or unit_type_el.text is None:
            continue
        unit_type = unit_type_el.text
        all_units.add(unit_type)

        upgrades = u.find("ns:UnitUpgrades", NS)
        if upgrades is not None:
            for tgt in upgrades.findall("ns:UnitType", NS):
                if tgt.text:
                    relations.append((unit_type, tgt.text))
                    all_units.add(tgt.text)

    return relations, all_units


# Construire le graphe
graph = defaultdict(list)
reverse_graph = defaultdict(list)
all_units_total = set()
all_nodes = set()

for filename in os.listdir(XML_FOLDER):
    if filename.endswith(".xml"):
        file_path = os.path.join(XML_FOLDER, filename)
        relations, units_in_file = parse_units(file_path)
        all_units_total.update(units_in_file)
        for src, dst in relations:
            graph[src].append(dst)
            reverse_graph[dst].append(src)
            all_nodes.add(src)
            all_nodes.add(dst)

# Générer les ensembles connectés (chaînes d’upgrades)
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

    # Nom du fichier = premier nœud de la chaîne (celui sans prédécesseur)
    first_nodes = [n for n in ensemble_nodes if n not in reverse_graph or len(reverse_graph[n]) == 0]
    first_name = first_nodes[0] if first_nodes else f"unit_chain_{ensemble_count}"
    filename = f"{first_name}.dot"
    path = os.path.join(OUTPUT_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write("digraph UnitEnsemble {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=box, style=rounded];\n")
        f.write("  splines=polyline;\n")
        for src, dst in ensemble_edges:
            f.write(f'  "{src}" -> "{dst}" [color=red];\n')
        f.write("}\n")

    ensemble_count += 1

# Graphe des unités solitaires (aucun upgrade ni target)
solitary_units = [u for u in all_units_total if u not in graph and u not in reverse_graph]

if solitary_units:
    path = os.path.join(OUTPUT_FOLDER, "solitary_units.dot")
    with open(path, "w", encoding="utf-8") as f:
        f.write("digraph SolitaryUnits {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=box, style=rounded, color=green];\n")
        for u in solitary_units:
            f.write(f'  "{u}";\n')
        f.write("}\n")

print(f"{ensemble_count} graphes DOT générés pour les chaînes d’unités.")


import os
import subprocess

DOT_FOLDER = r"E:\C2CModding\C2C-Log-Analyser\C2C-Log-Analyser\Tools\unit_chains_files"  # dossier contenant tous les .dot
VECTOR_FORMATS = ["svg", "pdf"]       # formats vectoriels souhaités

for dot_file in os.listdir(DOT_FOLDER):
    if dot_file.endswith(".dot"):
        dot_path = os.path.join(DOT_FOLDER, dot_file)
        base_name = os.path.splitext(dot_file)[0]

        for fmt in VECTOR_FORMATS:
            output_path = os.path.join(DOT_FOLDER, f"{base_name}.{fmt}")
            subprocess.run(["dot", f"-T{fmt}", dot_path, "-o", output_path])
            print(f"Généré : {output_path}")

print("Conversion DOT -> vectoriel terminée !")
