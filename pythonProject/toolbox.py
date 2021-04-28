"""
To install cairoSVG please follow these instructions : https://cairosvg.org/documentation/#installation
"""
import cairosvg
import os
from glob import glob
import urllib
import requests
import time


def svg_to_png(svg_path):
    """
    :param svg_path: Path to a svg file
    :return: Nothing
    """
    cairosvg.svg2png(url=svg_path, write_to=svg_path.replace(".svg", ".png"))


def get_paths_files_with_extension_from_folder(folder, extension='svg'):
    """
    :param extension: Extension of the files you are searching, default is svg
    :param folder: Folder in which searching files
    :return list of path to svg files without extension:
    """
    list_paths_to_files = [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.' + extension))]
    for i in range(len(list_paths_to_files)):
        list_paths_to_files[i] = list_paths_to_files[i].replace("\\", "/")
    return list_paths_to_files


def beautify_string(string):
    string_no_slash = string.replace("\\", "")
    string_remove_last_char = string_no_slash[:-1]
    string_remove_first_char = string_remove_last_char[1:]
    return string_remove_first_char


def get_new_captcha(path, /, **keywords):
    """
    Requête le serveur nodejs pour générer un captcha
    Exemple d'appel : get_new_captcha("./coucou"+font, text="A38hCNp8", color="green", font=font)
    :param path: Le chemin de l'image à sauvegarder (Ne pas spécifier l'extension)
    :param keywords: Tableau de paramètres correspondant actuellement aux paramètres nommés : text, color, font, width, height, font_size, noise.
    :return: 0 = OK | 1 = Erreur
    """
    if len(keywords) > 0 and 'text' in keywords:
        url = "http://localhost:8080/captcha?" + urllib.parse.urlencode(keywords)
        print(url)
        r = requests.get(url)
        if r.status_code == 200:
            byte_string = beautify_string(r.content.decode("utf8"))
            cairosvg.svg2png(bytestring=byte_string, write_to=path + ".png")
            return 0
    return 1


def get_available_fonts():
    """
    Renvoie les polices disponibles sur le serveur nodejs
    :return: Tableau de font
    """
    url = "http://localhost:8080/fonts"
    r = requests.get(url)
    if r.status_code == 200:
        array = r.content.decode("utf8")
        array = array[:-1]
        array = array[1:]
        return array.split("/")
    return None


if __name__ == "__main__":
    fonts = get_available_fonts()
    for font in fonts:
        get_new_captcha("./coucou" + font, text="A38hCNp8", color="green", font=font, width=600, height=200, font_size=64)
