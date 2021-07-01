import cairosvg
import os
from glob import glob
import urllib
import requests
import pytesseract
import string
import random
import easyocr
from PIL import Image


def svg_to_png(_svg_path):
    """
    Transform svg to png and save the file to same folder
    :param _svg_path: Path to a svg file
    :return: Nothing
    """
    cairosvg.svg2png(url=_svg_path, write_to=_svg_path.replace(".svg", ".png"))


def get_paths_files_with_extension_from_folder(_folder, _extension='svg'):
    """
    :param _extension: Extension of the files you are searching, default is svg
    :param _folder: Folder in which searching files
    :return list of path to svg files without extension:
    """
    _list_paths_to_files = [y for x in os.walk(_folder) for y in glob(os.path.join(x[0], '*.' + _extension))]
    for _i in range(len(_list_paths_to_files)):
        _list_paths_to_files[_i] = _list_paths_to_files[_i].replace("\\", "/")
    return _list_paths_to_files


def delete_files_with_extension_from_path(_path, _extension: string):
    """
    Remove files with extension from a folder recursively
    :param _path: Path to the files to delete
    :param _extension: Extension type
    :return: Nothing
    """
    # Remove . if it exists in the extension string
    _extension.replace(".", "")
    for _file in get_paths_files_with_extension_from_folder(_path, _extension):
        os.remove(_file)


def clear_captcha_svg_string(_string):
    """
    Remove '\' everywhere and remove first and last characters
    :param _string:
    :return: string
    """
    _string_no_slash = _string.replace("\\", "")
    _string_remove_last_char = _string_no_slash[:-1]
    _string_remove_first_char = _string_remove_last_char[1:]
    return _string_remove_first_char


def get_new_captcha(_path, /, _no_color, **keywords):
    """
    Requête le serveur nodejs pour générer un captcha
    Exemple d'appel : get_new_captcha("./coucou"+font, text="A38hCNp8", color="green", font=font)
    :param _path: Le chemin de l'image à sauvegarder (Ne pas spécifier l'extension)
    :param keywords: Tableau de paramètres correspondant actuellement aux paramètres nommés : text, color, background, font, width, height, font_size, noise.
    :return: 0 = OK | 1 = Erreur
    """
    if len(keywords) > 0 and 'text' in keywords:
        if _no_color == True:
            keywords.pop('color')
            keywords.pop('background')
        url = "http://localhost:8080/captcha?" + urllib.parse.urlencode(keywords)
        # print(url)
        r = requests.get(url)
        if r.status_code == 200:
            byte_string = clear_captcha_svg_string(r.content.decode("utf8"))
            cairosvg.svg2png(bytestring=byte_string, write_to=_path + ".png")
            return 0
    return 1


def get_available_fonts():
    """
    Renvoie les polices disponibles sur le serveur nodejs
    :return: Tableau de font
    """
    _url = "http://localhost:8080/fonts"
    _r = requests.get(_url)
    if _r.status_code == 200:
        _array = _r.content.decode("utf8")
        _array = _array[:-1]
        _array = _array[1:]
        return _array.split("/")
    return None


def get_random_string(_length, _allowed_characters=string.ascii_letters + string.digits):
    """
    Generate random string from letters & digits
    :param _length: length of the random string
    :param _allowed_characters: Allowed characters in the string (ascii letters and digits if the argument is not provided)
    :return: random string
    """
    # With combination of lower and upper case
    _generated_string = "".join(random.choice(_allowed_characters) for i in range(8))
    return _generated_string


def get_string_ocr_pytesseract(_image_path):
    """
    Resolve the string inside an image with pytesseract OCR
    :param _image_path: Path to a png, bmp or jpg image
    :return: string
    """
    _raw_string = pytesseract.image_to_string(Image.open(_image_path))
    # Remove unwanted characters
    _beautified_string = _raw_string.replace("\n", "").replace("\x0c", "").replace(" ", "")
    return _beautified_string


def get_string_ocr_easyocr(_image_path, _reader):
    """
    Resolve the string inside an image with easyOCR
    :param _image_path: Path to a png, bmp or jpg image
    :param _reader: Initialized reader
    :return: string
    """
    _result = _reader.readtext(_image_path)
    _array = [x for elem in _result for x in elem]
    if len(_array) > 0:
        return _array[1].replace(" ", "")
    return ""


def add_trailing_slash_to_path(_path) -> str:
    # Add '/' at the end of the path when missing
    if _path[-1] != '/':
        _path = _path + '/'
    return _path


if __name__ == "__main__":
    fonts = get_available_fonts()
    captchas = []
    strings_ocr_pytesseract = []
    strings_ocr_easyocr = []
    reader = easyocr.Reader(['en'])
    for f in fonts:
        random_string = get_random_string(8)
        get_new_captcha("./" + random_string, text=random_string, color="green", background="white", font=f,
                        width=600, height=200,
                        font_size=64, noise=1)
        path_img = "./" + random_string + ".png"
        strings_ocr_pytesseract.append(get_string_ocr_pytesseract(path_img))
        strings_ocr_easyocr.append(get_string_ocr_easyocr(path_img, reader))
        captchas.append(random_string)
    print("Captcha   : {tab}".format(tab=captchas))
    print("Tesseract : {tab}".format(tab=strings_ocr_pytesseract))
    print("EasyOCR   : {tab}".format(tab=strings_ocr_easyocr))
