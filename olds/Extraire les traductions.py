import sys
import lxml

print("Python version:", sys.version)
print("lxml version:", lxml.__version__)

from lxml import etree
print("lxml version:", etree.LXML_VERSION)


# Extraire les traductions d'un fichier XML et les enregistrer dans un fichier CSV
import csv
import re

def extract_texts_from_xml(in_xml_file, in_new_only=False):


    try:
        # Charger le fichier XML
        encodeStr = 'utf-8'
        #encodeStr = 'ISO-8859-1'

        with open(in_xml_file, encoding=encodeStr) as f:
            xml_content = f.read()
            # Supprimer les tabulations et retours à la ligne pour éviter les problèmes de parsing
            xml_content_clean = xml_content.replace('\t', '').replace('\n', '').replace(' xmlns="http://www.firaxis.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.firaxis.com ../Schema/Civ4Gametext.xsd"','' )
            #.replace('&#','ETCETCCAR')
            # Supprimer dynamiquement l'attribut xsi:schemaLocation avec n'importe quel chemin relatif
            # Enlève tous les xmlns et xsi:schemaLocation, peu importe le nombre de ../
            xml_content_clean = re.sub(
                r' xmlns="http://www\.firaxis\.com" xmlns:xsi="http://www\.w3\.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www\.firaxis\.com\s+[^"]+"',
                '', 
                xml_content_clean
            )
            xml_content_clean = xml_content_clean.replace(' xmlns="http://www.firaxis.com"','')
            
            if 'encoding="ISO-8859-1"'in xml_content_clean :
                encodeStr = 'ISO-8859-1'


            tree = etree.fromstring(xml_content_clean.encode(encodeStr))
            # Pour garder la même interface que etree.parse
            tree = etree.ElementTree(tree)
        root = tree.getroot()

        # Vérifier la structure du fichier XML, qui doit ressembler à : 
        """
        <Civ4GameText>
            <TEXT>
                <Tag>TXT_KEY_APPIAN_BUILT</Tag>
                <English>The [COLOR_UNIT_TEXT]Via Appia[COLOR_REVERT] connects your cities.</English>
                <French>La [COLOR_UNIT_TEXT]Via Appia[COLOR_REVERT] connecte entre-elles toutes vos Villes.</French>
                <Italian>La [COLOR_UNIT_TEXT]Via Appia[COLOR_REVERT] connette tutte le tue città.</Italian>
                <Russian>[COLOR_UNIT_TEXT]Аппиева дорога[COLOR_REVERT] соединяет ваши города.</Russian>
            </TEXT>
            <TEXT>
                <Tag>TXT_KEY_BUILDING_10000_YEAR_CLOCK</Tag>
                <English>10,000 Year Clock</English>
                <French>Horloge de 10000 ans</French>
                <German>
                    <Text>10000-Jahre-Uhr:10000-Jahre-Uhr:10000-Jahre-Uhr:10000-Jahre-Uhr</Text>
                    <Gender>Female</Gender>
                    <Plural>0</Plural>
                </German>
                <Italian>Orologio dei 10000 anni</Italian>
                <Spanish>Reloj de 10000 años</Spanish>
                <Russian>10000-летние часы</Russian>
            </TEXT>
            ...
        </Civ4GameText>    
        """
        if root.tag != 'Civ4GameText':
            raise ValueError("Le fichier XML n'a pas la structure attendue. La racine doit être 'Civ4GameText'.")   

        # Préparer le CSV pour l'export, même nom que le fichier XML d'entrée + _extract, avec extension .csv
        csv_file = in_xml_file.replace('.xml', '_extract.csv')

        with open(csv_file, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['tag', 'original_text', 'text_to_translate']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Utiliser le bon namespace pour xpath
            for text_element in root.xpath('TEXT'):
                # Récupérer le tag au même niveau que French
                tag_element = text_element.find('Tag')
                tag_content = tag_element.text.strip() if tag_element is not None and tag_element.text else "N/A"

                english_tag = text_element.find('English')
                original_text = english_tag.text if english_tag is not None and english_tag.text else ""

                french_tag = text_element.find('French')
                french_text = french_tag.text if french_tag is not None and french_tag.text else ""

                # Si le texte original est vide, on passe à l'itération suivante
                if not original_text:
                    continue  # Si on ne veut que les nouvelles traductions, on ignore les textes vides

                # Si la balise French n'existe pas, on la crée

                if french_tag is not None and french_text == "":
                    # Si la balise French est vide, on cherche une sous balise Text
                    french_text_tag = french_tag.find('Text')
                    if french_text_tag is not None:
                        french_text = french_text_tag.text if french_text_tag.text else ""                    
                    else:
                        french_text = ""

                # Si le texte est vide, on passe à l'itération suivante
                if not french_text:
                    if in_new_only:
                        text_to_translate = ""
                else:
                    if in_new_only:
                        continue  # Si on ne veut que les nouvelles traductions, on ignore les textes vides

                    # Vérifier si le texte commence par "Traduction :"
                    if french_text.startswith("Traduction :"):
                        # Extrait le texte à traduire
                        text_to_translate = french_text[len("Traduction :"):].strip()
                    else:
                        text_to_translate = french_text

                #pour original_text et text_to_translate, convrtir les " en \", et ajouter des guillemets autour
                original_text = original_text.replace('"', '\\"')
                text_to_translate = text_to_translate.replace('"', '\\"')
                original_text = f'"{original_text}"'
                if in_new_only and not text_to_translate:
                    # Si on ne veut que les nouvelles traductions et qu'il n'y a pas de texte à traduire, on continue
                    text_to_translate = original_text
                text_to_translate = f'"{text_to_translate}"'
                tag_content = f'"{tag_content}"'

                # Si le texte à traduire est trop long, on passe à l'itération suivante
                #if len(text_to_translate) > 500:
                #    print(f"Le texte à traduire pour le tag {tag_content} est trop long ({len(text_to_translate)} caractères). Il sera ignoré.")
                #    continue

                #if not 'A traduire - ' in text_to_translate :
                #    print(f"Ne contient pas : A traduire -  pour le tag {tag_content}.")
                #    continue


                # Écrire dans le CSV
                writer.writerow({
                    'tag': tag_content,
                    'original_text': original_text,
                    'text_to_translate': text_to_translate
                })

                print(f"Extraction du tag : {tag_content}")

        print("Extraction terminée, fichier CSV : " + csv_file)
    except Exception as e:
        print(f"Erreur lors de l'extraction du fichier {in_xml_file} : {e}")



def inject_translations_into_xml(in_csv_file,in_xml_file = None):    
    """
    Injecte les traductions d'un fichier CSV dans un fichier XML.   
    Le fichier CSV doit contenir les colonnes suivantes : tag, french_translation, text_to_translate, original_text.
    Le fichier XML doit être au format Civ4GameText.
    Si le fichier XML n'est pas spécifié, on prend le fichier XML du même nom que le CSV, mais avec l'extension .xml, en enlevant _extract.csv
    """
    
    # Charger le fichier XML

    #si le fichier XML n'existe pas, on prendra le fichier XML du même nom que le CSV, mais avec l'extension .xml, en enlevant _extract.csv
    if in_xml_file is None:
        in_xml_file = ""

    if not in_xml_file.endswith('.xml'):
        in_xml_file = in_csv_file.replace('_extract.csv', '.xml')
    if not in_xml_file.endswith('.xml'):
        raise ValueError("Le fichier XML doit avoir l'extension .xml")
    if not in_csv_file.endswith('.csv'):
        raise ValueError("Le fichier CSV doit avoir l'extension .csv")
        
    if in_xml_file is None:
        raise ValueError("Le fichier XML doit être spécifié")

    encodeStr = 'utf-8'
    #encodeStr = 'ISO-8859-1'
    with open(in_xml_file, encoding=encodeStr) as f:
        xml_content = f.read()
        # Supprimer les tabulations et retours à la ligne pour éviter les problèmes de parsing
        xml_content_clean = xml_content.replace('\t', '').replace('\n', '').replace('&#','ETCETCCAR').replace(' xmlns="http://www.firaxis.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.firaxis.com ../Schema/Civ4Gametext.xsd"','' )
        xml_content_clean = re.sub(
            r' xmlns="http://www\.firaxis\.com" xmlns:xsi="http://www\.w3\.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www\.firaxis\.com\s+[^"]+"',
            '', 
            xml_content_clean
        )
        xml_content_clean = xml_content_clean.replace(' xmlns="http://www.firaxis.com"','')
                   
        parser = etree.XMLParser(resolve_entities=False)
        tree = etree.fromstring(xml_content_clean.encode(encodeStr),parser)
        # Pour garder la même interface que etree.parse
        tree = etree.ElementTree(tree)
    root = tree.getroot()

    if root.tag != 'Civ4GameText':
        raise ValueError("Le fichier XML n'a pas la structure attendue. La racine doit être 'Civ4GameText'.")   


    with open(in_csv_file, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # Pour chaque ligne dans le CSV
        for row in reader:
            tag_content = row['tag']
            translated_text = row['french_translation']  # Assurez-vous que la nouvelle colonne a ce nom
            translated_text_backup = row['text_to_translate']  # Assurez-vous que la nouvelle colonne a ce nom
            original_text = row['original_text']  # Assurez-vous que la nouvelle colonne a ce nom

            if original_text == translated_text:
                # Si le texte original est identique à la traduction, on ne fait rien
                print(f"Aucune modification nécessaire pour le tag : {tag_content}")
                continue

            if translated_text == "" or translated_text is None : 
                # Si aucune traduction n'est fournie, on utilise le texte original
                if original_text != translated_text_backup:
                    translated_text = translated_text_backup
                else :
                    print(f"Aucune traduction fournie pour le tag : {tag_content}")
                    continue
            # Chercher la balise TEXT correspondante par <Tag>
            for text_element in root.xpath('TEXT'):
                tag_element = text_element.find('Tag')
                if tag_element is not None and tag_element.text.strip() == tag_content:
                    # Chercher la balise <French> et mettre à jour avec la traduction
                    french_tag = text_element.find('French')
                    if french_tag is not None:
                        french_tag.text = translated_text
                    else:
                        # Si la balise <French> n'existe pas, on la crée, en la placant dans la balise TEXT juste après la balise existente English
                        french_tag = etree.SubElement(text_element, 'French',)
                        french_tag.text = translated_text
                        comment = None
                        # Récupérer les enfants
                        children = list(text_element)
                        for child in children:
                            #Si child est un commentaire, on le supprime
                            if isinstance(child, etree._Comment):
                                # Si un enfant contient un commentaire, on le supprime, et on le garde pour l'ajouter à la fin
                                comment = child
                                children.remove(child)  

                        # Trier les enfants par ordre alphabétique du tag
                        children.sort(key=lambda x: x.tag)

                        # Effacer tous les enfants
                        text_element.clear()                        

                        # Ajouter les enfants triés
                        for child in children:
                            if child.tag == 'Tag':
                                # Ajouter la balise French en premier
                                text_element.insert(0, tag_element)
                            else:
                                # Ajouter les autres balises après
                                text_element.append(child)
                        if comment is not None:
                            # Ajouter le commentaire à la fin
                            text_element.append(comment)


                    print(f"Traduction injectée pour le tag : {tag_content}")



    # Sauvegarder le XML avec les traductions mises à jour
    updatedfile = in_xml_file.replace('.xml', '_updated.xml')
    result = etree.tostring(root, encoding='unicode', with_tail=False).replace('ETCETCCAR','&#').replace('<Civ4GameText>',' xmlns="<Civ4GameText http://www.firaxis.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.firaxis.com ../Schema/Civ4Gametext.xsd">')
    # Écrire le résultat dans un nouveau fichier XML
    with open(updatedfile, 'w', encoding='utf-8') as f:
        f.write(result)     
    print("Mise à jour des traductions terminée, fichier XML : " + updatedfile)



def extract_texts_from_repo(in_xml_repo, in_new_only=False):
    """
    lance de manière récursive extract_texts_from_xml pour tous les fichiers xml du répertoire
    """
    
    import os
    import re

    # Parcourir tous les fichiers du répertoire
    for root, dirs, files in os.walk(in_xml_repo):
        for file in files:
            if file.endswith('.xml'):
                full_path = os.path.join(root, file)
                print(f"Extraction des textes de {full_path}...")
                extract_texts_from_xml(full_path, in_new_only=in_new_only)


def inject_translations_from_repo(in_csv_repo, in_xml_repo=None):
    """
    lance de manière récursive inject_translations_into_xml pour tous les fichiers csv du répertoire
    """
    

    import os
    import re

    # Parcourir tous les fichiers du répertoire
    for root, dirs, files in os.walk(in_csv_repo):
        for file in files:
            if file.endswith('_extract.csv'):
                full_path = os.path.join(root, file)

                #si in_xml_repo n'est pas spécifié, on prend le répertoire du même nom que in_csv_repo, mais avec l'extension .xml
                if in_xml_repo is None:
                    xml_file = os.path.join(os.path.dirname(full_path), os.path.basename(full_path).replace('_extract.csv', '.xml'))

                #lance l'injection si la date du fichier XML est plus ancienne que celle du fichier CSV
                if not os.path.exists(xml_file) or os.path.getmtime(full_path) > os.path.getmtime(xml_file):
                    if not os.path.exists(xml_file):
                        print(f"Le fichier XML {xml_file} n'existe pas, il sera créé.") 
                    else:
                        print(f"Le fichier XML {xml_file} est plus ancien que le fichier CSV {full_path}, il sera mis à jour.") 
                else:
                    print(f"Le fichier XML {xml_file} est plus récent que le fichier CSV {full_path}, il ne sera pas mis à jour.") 
                    continue

                print(f"Injection des traductions de {full_path} dans {xml_file}...")
                inject_translations_into_xml(full_path, xml_file)




#extract_texts_from_xml('.\\Civ4_GameText\\Units_CIV4GameText.xml', in_new_only=True)
#inject_translations_from_repo('.\\Civ4_GameText', in_xml_repo='.\\Civ4_GameText')
#C:\Data\personnel\Jeux\C2C Trad\Civ4_GameText\Events_CIV4GameText_extract.csv
#extract_texts_from_repo('.\\Civ4_GameText', in_new_only=True)
inject_translations_into_xml('.\\Civ4_GameText\\Modules\\Alt_Timelines\\Megafauna\\Megafauna_CIV4GameText_extract.csv')
#extract_texts_from_repo('E:\\C2CModding\\DuneWars_Revival-v.1.10\\DuneWars Revival\\Assets\\XML\\Text', in_new_only=False)
#extract_texts_from_xml(".\\Civ4_GameText\\Strategy_CIV4GameText.xml",False)