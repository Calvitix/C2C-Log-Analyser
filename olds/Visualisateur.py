from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox,
    QTextEdit, QFileDialog, QMessageBox, QLineEdit, QLabel
)
import xml.etree.ElementTree as ET
import re

def load_xml(file_path):
    tree = ET.parse(file_path)
    return tree.getroot()

def get_tags(root):
    ns = {'ns': 'http://www.firaxis.com'}
    tags = {}
    for text_elem in root.findall('.//ns:TEXT', ns):
        tag_elem = text_elem.find('ns:Tag', ns)
        if tag_elem is not None:
            tag_name = tag_elem.text
            tags[tag_name] = text_elem
    return tags

def get_text_for_lang(text_elem, lang):
    ns = {'ns': 'http://www.firaxis.com'}
    lang_tag = text_elem.find(f'ns:{lang}', ns)
    if lang_tag is not None:
        return lang_tag.text
    return "Texte non disponible pour cette langue."


def parse_special_tags(text):
    color_stack = []
    current_color = None
    result = ""

    # Pattern pour détecter les balises
    pattern = re.compile(r'\[((\\|/)?[\w=:]+)\]')
    pos = 0

    for match in pattern.finditer(text):
        start, end = match.span()
        tag = match.group(1)

        result += text[pos:start]

        # Gestion ouverture
        if not (tag.startswith('/') or tag.startswith('\\') or tag.startswith('COLOR_REVERT')):
            # Balises avec paramètre
            if '=' in tag:
                tag_name, arg = tag.split('=', 1)
                if tag_name == 'LINK':
                    # Créer un lien
                    result += f'<a href="myapp://tag/{arg}">'
                elif tag_name.startswith('PARAGRAPH'):
                    # Pas de fermeture directe
                    result += '<br>'
                    level = tag.split(':',1)[1] if ':' in tag else ''
                    result += f'<b>[{level}]</b><br>'
                # Ajoutez autres si besoin
            else:
                # Balises sans paramètre
                if tag == 'COLOR_UNIT_TEXT':
                    color_stack.append('red')
                    current_color = 'red'
                    result += f'<span style="color:{current_color}">'
                elif tag == 'COLOR_GREEN':
                    color_stack.append('green')
                    current_color = 'green'
                    result += f'<span style="color:{current_color}">'
                elif tag == 'COLOR_HIGHLIGHT_TEXT':
                    color_stack.append('blue')
                    current_color = 'blue'
                    result += f'<span style="color:{current_color}">'
                elif tag == 'NEWLINE':
                    result += '<br>'
                elif tag == 'ICON_BULLET':
                    result += '<br>&bull; '
                elif tag == 'BOLD':
                    result += '<b>'
                elif tag == 'H1':
                    result += '<h1>'
                elif tag == 'H2':
                    result += '<h2>'
                elif tag.startswith('PARAGRAPH'):
                    # Pas de fermeture directe
                    result += '<br>'

        else:
            # Gestion fermeture
            t = tag[1:]
            if t.startswith('LINK'):
                result += '</a>'
            elif t == 'BOLD':
                result += '</b>'
            elif t == 'H1':
                result += '</h1>'
            elif t == 'H2':
                result += '</h2>'
            elif t == 'COLOR_REVERT':
                if color_stack:
                    color_stack.pop()
                current_color = color_stack[-1] if color_stack else None
                result += '</span>'
            # Ajoutez autres fermetures si nécessaires

        pos = end

    result += text[pos:]

    # Fermer toutes les spans ouvertes
    while color_stack:
        result += '</span>'
        color_stack.pop()

    # Wrap tout dans une structure HTML avec style global
    html_final = '''
<html>
<head>
<style>
body { font-family: Arial; font-size: 16pt; }
</style>
</head>
<body>''' + result + '</body></html>'
    return html_final


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lecture de fichier XML (PySide6) avec filtre")
        self.setGeometry(100, 100, 600, 500)

        self.root = None
        self.tags = {}
        self.filtered_tags = []

        layout = QVBoxLayout()

        # Bouton de chargement
        self.load_button = QPushButton("Charger le fichier XML")
        self.load_button.clicked.connect(self.load_file)
        layout.addWidget(self.load_button)

        # Champ de filtrage
        self.filter_label = QLabel("Filtrer par texte :")
        layout.addWidget(self.filter_label)
        self.filter_edit = QLineEdit()
        self.filter_edit.textChanged.connect(self.filter_tags)
        layout.addWidget(self.filter_edit)

        # ComboBox des tags
        self.tag_combo = QComboBox()
        self.tag_combo.currentIndexChanged.connect(self.display_text)
        layout.addWidget(self.tag_combo)

        # ComboBox des langues
        self.lang_combo = QComboBox()
        self.languages = ['English', 'French', 'Italian', 'Russian', 'German', 'Spanish']
        self.lang_combo.addItems(self.languages)
        self.lang_combo.currentIndexChanged.connect(self.display_text)
        layout.addWidget(self.lang_combo)

        # Zone de texte pour affichage stylé
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier XML", filter="XML Files (*.xml)")
        if file_path:
            try:
                self.root = load_xml(file_path)
                self.tags = get_tags(self.root)
                self.filtered_tags = list(self.tags.keys())
                self.update_tag_list()
                if self.filtered_tags:
                    self.tag_combo.setCurrentIndex(0)
                    self.display_text()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {e}")

    def update_tag_list(self):
        self.tag_combo.clear()
        self.tag_combo.addItems(self.filtered_tags)

    def filter_tags(self):
        filter_text = self.filter_edit.text().lower()
        self.filtered_tags = [tag for tag in self.tags if filter_text in tag.lower()]
        self.update_tag_list()

    def display_text(self):
        selected_tag = self.tag_combo.currentText()
        language = self.lang_combo.currentText()
        self.text_edit.clear()
        if selected_tag in self.tags:
            text_elem = self.tags[selected_tag]
            raw_text = get_text_for_lang(text_elem, language)
            html_text = parse_special_tags(raw_text)
            self.text_edit.setHtml(html_text)
            #self.text_edit.setOpenExternalLinks(True)
            #self.text_edit.anchorClicked.connect(self.handle_link_click)            
        else:
            self.text_edit.setPlainText("Balise non trouvée.")


def handle_link_click(self, url):
    # Exemple : url = QUrl("myapp://tag/TXT_KEY_APPIAN_BUILT")
    if url.scheme() == 'myapp':
        # On extrait le tag
        path = url.path()  # ex : /tag/TXT_KEY_APPIAN_BUILT
        tag_name = path[len('/tag/'):]

        # Vérifier si le tag est dans la liste
        if tag_name in self.tags:
            # Mettre à jour la sélection du combobox
            index = self.tag_combo.findText(tag_name)
            if index != -1:
                self.tag_combo.setCurrentIndex(index)
                # Si besoin, appeler la fonction pour afficher le texte
                # self.display_text()

# Si vous utilisez la version avec la fonction corrigée `parse_special_tags`, intégrez-la !

if __name__ == "__main__":
    app = QApplication([])
    window = App()
    window.show()
    app.exec()