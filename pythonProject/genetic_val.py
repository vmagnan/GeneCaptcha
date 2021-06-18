import json
import time
from datetime import datetime
from colorutils import *
from jellyfish import levenshtein_distance
from enum import Enum
from toolbox import *

TEXT_LENGTH = 8
WIDTH = 600
HEIGHT = 200
FONT_SIZE = 64


class OCR(Enum):
    EASY_OCR = 'EASY_OCR'
    TESSERACT = 'TESSERACT'


class CROSSCOLORVERSION(Enum):
    V1 = 'V1'
    V2 = 'V2'


class Captcha:
    def __init__(self, text, txt_color, bg_color, font, path):
        self.text = text
        self.txt_color = txt_color
        self.bg_color = bg_color
        self.font = font
        self.path = path
        self.ocr_value = -1


class Metadata:
    def __init__(self, _ocr: string, _size: int, _threshold: int, _path: string, _colors: list[string],
                 _fonts: list[string], _date: string):
        self.ocr = _ocr
        self.size = _size
        self.threshold = _threshold
        self.path = _path
        self.colors = _colors
        self.fonts = _fonts
        self.iterations = []
        self.total_time = 0
        self.date = _date

    def add_iteration(self, selected: int, iteration_time: float):
        """
        Append a new iteration to the attribute list called iterations
        :param selected: Number of selected individuals
        :param iteration_time: Time taken for the whole operation ==> Evaluation + Selection + Crossover(only when there are 2 individuals)
        :return:
        """
        self.iterations.append((selected, iteration_time))

    def set_total_time(self, total_time: float):
        self.total_time = total_time

    def save_as_json(self, path=None):
        """
        Save all attributes as JSON
        :param path: Path to the directory where to save the JSON
        :return: Nothing
        """
        if path is None:
            path = self.path
        with open(path + 'metadata.json', 'w', encoding='utf-8') as file:
            json.dump(self.__dict__, file, ensure_ascii=False, indent=4, default=str)


def initialise(_number: int, _colors: list[string], _fonts: list[string]) -> list[Captcha]:
    """
    Initialise N captcha, save them to ./Image and return the corresponding captcha list
    :param _number: Number of captcha
    :param _colors: Available colors
    :param _fonts: Available fonts
    :return: List of captchas
    """
    _captchas = []
    for _i in range(_number):
        _bg_color = random.choice(_colors)
        _txt_color = random.choice(_colors)
        while _bg_color == _txt_color:
            _txt_color = random.choice(_colors)
        _font = random.choice(_fonts)
        _text = get_random_string(TEXT_LENGTH)
        _path = "./Image/" + "_".join([_text, _txt_color, _bg_color, _font])
        get_new_captcha(_path, text=_text, color=_txt_color, background=_bg_color, font=_font, width=WIDTH,
                        height=HEIGHT,
                        font_size=FONT_SIZE)
        _captchas.append(Captcha(_text, _txt_color, _bg_color, _font, _path))
    return _captchas


def evaluate(_captchas: list[Captcha], _ocr: string, _reader):
    """
    Evaluate all captchas
    :param _ocr:
    :param _reader:
    :param _captchas: List of captchas
    :return: Nothing
    """
    for _captcha in _captchas:
        if _captcha.ocr_value == -1:
            _path = _captcha.path + '.png'
            _text = _captcha.text
            if _ocr == OCR.EASY_OCR:
                _ocr_string = get_string_ocr_easyocr(_path, _reader)
            elif _ocr == OCR.TESSERACT:
                _ocr_string = get_string_ocr_pytesseract(_path)
            else:
                _ocr_string = None
            _captcha.ocr_value = levenshtein_distance(_ocr_string, _text)


def cross_text(_text_1: string, _text_2: string) -> string:
    """
    Cross 2 text from their used characters
    :param _text_1: Text of the 1st captcha
    :param _text_2: Text of the 2nd captcha
    :return: Random text with allowed characters from _text_1 & _text_2
    """
    _union_chars = list(set(_text_1).union(set(_text_2)))
    return mutate_text(get_random_string(TEXT_LENGTH, _union_chars))


def mutate_text(_text: string) -> string:
    """
    Mutate a random single character of text by replacing it by one that doesn't exists in this string
    Idea of improvement : Add the union character set of the two parents as argument, and generates a random character that doesn't appear in this union
    :param _text: Text to mutate
    :return: Maybe a mutated text (1/10 chance)
    """
    if random.randint(1, 10) == 1:
        _position = random.randint(0, len(_text) - 1)
        _all_characters = string.ascii_letters + string.digits
        _allowed_characters = list(set(_all_characters).difference(set(_text)))
        # Turn string to list of char because strings are immutable
        _text_characters = list(_text)
        _text_characters[_position] = random.choice(_allowed_characters)
        _text = "".join(_text_characters)
    return _text


def cross_color_v1(_color_1_hex: string, _color_2_hex: string) -> string:
    """
    Cross colors V1
    By making the average of rgb values
    :param _color_2_hex: First color in hexadecimal string
    :param _color_1_hex: Second color in hexadecimal string
    :return: Average color in hexadecimal string
    """
    _r1, _g1, _b1 = hex_to_rgb(_color_1_hex)
    _r2, _g2, _b2 = hex_to_rgb(_color_2_hex)
    _rf = (_r1 + _r2) / 2
    _gf = (_g1 + _g2) / 2
    _bf = (_b1 + _b2) / 2
    _result_hex = rgb_to_hex((_rf, _gf, _bf))
    return mutate_color_v1(_result_hex)


def mutate_color_v1(_color_hex: string) -> string:
    """
    Mutate the color V1
    1/10 chance to mutate the color
    Offset of 20 for each element
    :param _color_hex: color to mutate in hexadecimal string
    :return: mutated color in hexadecimal string
    """
    if random.randint(1, 10) == 1:
        _tuple_rgb = hex_to_rgb(_color_hex)
        for _v in _tuple_rgb:
            _v = _v + random.randint(-10, 10)
            if _v < 0:
                _v = 0
            if _v > 255:
                _v = 255
        _color_hex = rgb_to_hex(_tuple_rgb)
    return _color_hex


def cross_color_v2(_color_1_hex: string, _color_2_hex: string, _colors: list[string]) -> string:
    """
    Cross colors V1
    By taking the color with the index in the middle of the 2 parents 
    :param _color_1_hex: First color in hexadecimal string
    :param _color_2_hex: Second color in hexadecimal string
    :param _colors: List of colors
    :return: 
    """
    _pos_color_1 = _colors.index(_color_1_hex)
    _pos_color_2 = _colors.index(_color_2_hex)
    # We get the colors between the two index into _sub_colors
    _sub_colors = []
    for _i in range(_pos_color_1, _pos_color_2):
        _sub_colors.append(_colors[_i])
    _size_sub_color = len(_sub_colors)
    # If the two colors are neighbours <==> _size_sub_color = 0, then choose randomly between the parents
    if _size_sub_color == 0:
        return mutate_color_v2(random.choice([_color_1_hex, _color_2_hex]), _colors)
    # Get the middle of the list
    # if length is pair there are two colors, we choose a random one between them, index len/2 or len/2 -1
    if _size_sub_color % 2 == 0:
        return mutate_color_v2(_sub_colors[int(_size_sub_color / 2) - random.choice([0, 1])], _colors)
    # Otherwise it's the int part of the length divided by 2
    else:
        return mutate_color_v2(_sub_colors[int(_size_sub_color / 2)], _colors)


def mutate_color_v2(_color_hex: string, _colors: list[string]) -> string:
    """
    Mutate the color V2
    1/10 chance to mutate the color
    Change the color by the one before or after the actual color index in the list
    :param _color_hex: Color to mutate
    :param _colors: List of colors
    :return:
    """
    if random.randint(1, 10) == 1:
        _pos_color = _colors.index(_color_hex)
        _new_index_color = _pos_color + random.choice([-1, 1])
        if _new_index_color > len(_colors) - 1:
            _color_hex = _colors[0]
        else:
            _color_hex = _colors[_new_index_color]
    return _color_hex


def cross_2_captcha(_captcha_1: Captcha, _captcha_2: Captcha, _colors: list[string],
                    _cross_color_version: CROSSCOLORVERSION = CROSSCOLORVERSION.V1, ) -> Captcha:
    """
    Cross 2 captcha attributes to create a new one
    :param _colors: List of colors, needed in the cross_color_v2
    :param _captcha_1: First parent captcha
    :param _captcha_2: Second parent captcha
    :param _cross_color_version: Version of crosscolor
    :return: Son captcha
    """
    _text = cross_text(_captcha_1.text, _captcha_2.text)
    if _cross_color_version == CROSSCOLORVERSION.V2:
        _txt_color = cross_color_v2(_captcha_1.txt_color, _captcha_2.txt_color, _colors)
        _bg_color = cross_color_v2(_captcha_1.bg_color, _captcha_2.bg_color, _colors)
    else:
        _txt_color = cross_color_v1(_captcha_1.txt_color, _captcha_2.txt_color)
        _bg_color = cross_color_v1(_captcha_1.bg_color, _captcha_2.bg_color)
    _font = random.choice([_captcha_1.font, _captcha_2.font])
    _path = "./Image/Crossed/" + "_".join([_text, _txt_color, _bg_color, _font])
    get_new_captcha(_path, text=_text, color=_txt_color, background=_bg_color, font=_font, width=WIDTH, height=HEIGHT,
                    font_size=FONT_SIZE)
    _captcha = Captcha(_text, _txt_color, _bg_color, _font, _path)
    return _captcha


def crossover(_captchas: list[Captcha], _population_size: int, _colors: list[string],
              _cross_color_version: CROSSCOLORVERSION = CROSSCOLORVERSION.V1, ) -> list[Captcha]:
    """
    Shuffle the list, cross the two last captchas, add the parents and the son to the new list
    For each available couple : select 2 random captchas from the list, cross them and add the three captchas to the return list
    And then remove the 2 parents from the initial list
    :param _captchas: List of captchas
    :param _population_size: Size of the population
    :param _colors: List of colors, needed in the cross_color_v2
    :param _cross_color_version: Version of the cross color function
    :return:
    """
    if not _captchas:
        print("crossover : Population passed is empty")
        return []
    _new_population = []
    # Add all parents to new_population to keep previous selected captchas
    for _captcha in _captchas:
        _new_population.append(_captcha)
    # Add crossed sons
    while len(_captchas) >= 2 and len(_new_population) < _population_size:
        random.shuffle(_captchas)
        _parent_1 = _captchas.pop()
        _parent_2 = _captchas.pop()
        _son = cross_2_captcha(_parent_1, _parent_2, _colors, _cross_color_version)
        if len(_new_population) < _population_size:
            _new_population.append(_son)
    return _new_population


def selection(_captchas: list[Captcha], _threshold: int) -> list[Captcha]:
    """
    Select all captcha with a levenshtein distance > THRESHOLD & with a different text color from its background
    :param _threshold: Threshold
    :param _captchas: List of captchas
    :return: List of Selected captchas
    """
    _selected_captchas = []
    for _captcha in _captchas:
        if _captcha.ocr_value >= _threshold:
            if _captcha.txt_color != _captcha.bg_color:
                _selected_captchas.append(_captcha)
    return _selected_captchas


def is_population_converged(_captchas: list[Captcha], _population_size: int, _threshold) -> bool:
    """
    Return true when the population is full and their EasyOCR values are >= THRESHOLD
    :param _threshold: Threshold
    :param _population_size: Size of the population
    :param _captchas: List of Captchas
    :return:
    """
    if len(_captchas) < _population_size:
        return False
    for _captcha in _captchas:
        if _captcha.ocr_value < _threshold:
            return False
    return True


def save_converged_population(_captchas: list[Captcha], _path: string):
    """
    Save all captchas as png to a path
    Be careful, this function also delete the png already located to the path !
    Idea of improvement : Only move the files, don't duplicate
    :param _captchas: List of captchas
    :param _path: Path
    :return:
    """
    # Delete previous files if exists
    delete_files_with_extension_from_path(_path, 'png')
    for _captcha in _captchas:
        _captcha.path = _path + "_".join([_captcha.text, _captcha.txt_color, _captcha.bg_color, _captcha.font])
        get_new_captcha(_captcha.path, text=_captcha.text, color=_captcha.txt_color, background=_captcha.bg_color,
                        font=_captcha.font, width=WIDTH,
                        height=HEIGHT,
                        font_size=FONT_SIZE)


def sort_dic_by_value_descending(_dic: dict) -> dict:
    """
    Sort dictionary by value and descending
    :param _dic: Dictionary to sort
    :return: Sorted dictionary
    """
    return dict(sorted(_dic.items(), key=lambda item: item[1], reverse=True))


def get_simple_stats(_captchas: list[Captcha]):
    """
    Print the occurrence of each captcha parameter : Letter, text color, background color, font
    :param _captchas: List of captchas
    :return: Nothing
    """
    _characters_apparition = {}
    _fonts_apparition = {}
    _txt_color_apparition = {}
    _bg_color_apparition = {}
    for _captcha in _captchas:
        # Calculate the sum of all char used in all captchas
        for _char in _captcha.text:
            if _char in _characters_apparition:
                _characters_apparition[_char] += 1
            else:
                _characters_apparition[_char] = 1
        # Calculate the sum of all fonts used in all captchas
        if _captcha.font in _fonts_apparition:
            _fonts_apparition[_captcha.font] += 1
        else:
            _fonts_apparition[_captcha.font] = 1
        # Calculate the sum of all txt colors used in all captchas
        if _captcha.txt_color in _txt_color_apparition:
            _txt_color_apparition[_captcha.txt_color] += 1
        else:
            _txt_color_apparition[_captcha.txt_color] = 1
        # Calculate the sum of all bg colors used in all captchas
        if _captcha.bg_color in _bg_color_apparition:
            _bg_color_apparition[_captcha.bg_color] += 1
        else:
            _bg_color_apparition[_captcha.bg_color] = 1
    # Sort apparitions by value and descending
    _characters_apparition = sort_dic_by_value_descending(_characters_apparition)
    _fonts_apparition = sort_dic_by_value_descending(_fonts_apparition)
    _txt_color_apparition = sort_dic_by_value_descending(_txt_color_apparition)
    _bg_color_apparition = sort_dic_by_value_descending(_bg_color_apparition)
    print("""\
    ----------------------------------------------------
    Number of captchas : {nb}
    Characters apparition : {chs}
    Fonts apparition : {fts}
    Text-Color apparition : {txtcos}
    Background-Color apparition : {bgcos}
    ----------------------------------------------------""".format(nb=len(_captchas), chs=_characters_apparition,
                                                                   fts=_fonts_apparition,
                                                                   txtcos=_txt_color_apparition,
                                                                   bgcos=_bg_color_apparition))


def summarize(_captchas: list[Captcha], _data_list):
    # Not working, get doesn't exist on lists
    for _captcha in _captchas:
        for _letter in _captcha.text:
            if _data_list.get([_letter][_captcha.bg_color][_captcha.font]) is not None:
                _data_list[_letter][_captcha.bg_color][_captcha.font] += 1
            else:
                _data_list[_letter][_captcha.bg_color][_captcha.font] = 1


def retrieve_captcha_from_path(_path: string) -> list[Captcha]:
    """
    Retrieve the list of captcha located in a specific path
    :param _path: Path
    :return: List of captchas
    """
    # Add '/' at the end of the path when missing
    if _path[-1] != '/':
        _path = _path + '/'
    _captchas = []
    _files = get_paths_files_with_extension_from_folder(_path, "png")
    for _file in _files:
        _file_beautified = _file.replace(".png", "").replace(_path, "").replace("/", "")
        (_text, _txt_color, _bg_color, _font) = tuple(map(str, _file_beautified.split('_')))
        if _text != "" and _txt_color != "" and _bg_color != "" and _font != "":
            _captchas.append(Captcha(_text, _txt_color, _bg_color, _font, _file))
    return _captchas


def generate_converged_population(_ocr: OCR, _size: int, _threshold: int, _path: string, _colors: list[string],
                                  _fonts: list[string],
                                  _cross_color_version: CROSSCOLORVERSION = CROSSCOLORVERSION.V1) -> \
        list[Captcha]:
    """
    Generate a converged population with a genetic algorithm
    :param _ocr: OCR you want to choose (OCR.EASY_OCR or OCR.TESSERACT)
    :param _size: Size of the population
    :param _threshold: Threshold, all captcha with their levenshtein distance >= threshold will be selected
    :param _path: Path to save the generated population
    :param _colors: Allowed colors
    :param _fonts: Allowed fonts
    :param _cross_color_version: Version of the cross color function (V1 or V2, check enum)
    :return: List of captchas
    """
    _reader = None
    # Delete all images from the processing folder
    delete_files_with_extension_from_path("./Image/", 'png')
    # Initialize EasyOCR Reader if it's the chosen one
    if _ocr == OCR.EASY_OCR:
        _reader = easyocr.Reader(['en'])
    # Add '/' at the end of the path when missing
    if _path[-1] != '/':
        _path = _path + '/'
    # Initialize metadata
    _metadata = Metadata(_ocr.value, _size, _threshold, _path, _colors, _fonts, datetime.now())
    _starting_time = time.time()
    _population = initialise(_size, _colors, _fonts)
    _iterations = 0
    while not is_population_converged(_population, _size, _threshold):
        _starting_time_iteration = time.time()
        # Evaluate the crossed population
        evaluate(_population, _ocr, _reader)
        print("Iteration = {iter}".format(iter=_iterations))
        # Select individuals accordingly to a Threshold
        _selected_population = selection(_population, _threshold)
        _number_selected = len(_selected_population)
        print("{nb} Selected captcha".format(nb=_number_selected))
        # If population has totally converged, we get out of the loop
        if _number_selected >= _size:
            _population = _selected_population
            _metadata.add_iteration(_number_selected, time.time() - _starting_time_iteration)
            break
        # If there are at least 2 selected individuals, we reproduce them
        if _number_selected > 1:
            _crossed_population = crossover(_selected_population, _size, _colors, _cross_color_version)
        # Otherwise, we generate new individuals, and append the one selected if it exists
        else:
            _new_population = initialise(_size - _number_selected, _colors, _fonts)
            if _number_selected == 1:
                _new_population.append(_selected_population.pop())
            _crossed_population = _new_population
        # And so on !
        _population = _crossed_population
        _metadata.add_iteration(_number_selected, time.time() - _starting_time_iteration)
        _iterations += 1
    _metadata.set_total_time(time.time() - _starting_time)
    _metadata.save_as_json()
    print("""\
    Convergence of the population :
    Iteration required = {iter}
    Time required = {time} seconds
    """.format(iter=_iterations, time=_metadata.total_time))
    save_converged_population(_population, _path)
    return _population


if __name__ == "__main__":
    # Pour supprimer rapidement les images/json de certains dossiers
    # for i in range(25,30):
    #     delete_files_with_extension_from_path("./Results/" + str(i) + '/', 'png')
    #     delete_files_with_extension_from_path("./Results/" + str(i) + '/', 'json')
    colors = ["red", "pink", "purple", "blue", "cyan", "green", "yellow", "orange"]
    colors_extended = ["MediumVioletRed", "DeepPink", "PaleVioletRed", "HotPink", "LightPink", "Pink", "DarkRed", "Red",
                       "Firebrick", "Crimson", "IndianRed", "LightCoral", "Salmon", "DarkSalmon", "LightSalmon",
                       "OrangeRed", "Tomato", "DarkOrange", "Coral", "Orange", "DarkKhaki", "Gold", "Khaki",
                       "PeachPuff", "Yellow", "PaleGoldenrod", "Moccasin", "PapayaWhip", "LightGoldenrodYellow",
                       "LemonChiffon", "LightYellow", "Maroon", "Brown", "SaddleBrown", "Sienna", "Chocolate",
                       "DarkGoldenrod", "Peru", "RosyBrown", "Goldenrod", "SandyBrown", "Tan", "Burlywood", "Wheat",
                       "NavajoWhite", "Bisque", "BlanchedAlmond", "Cornsilk", "DarkGreen", "Green", "DarkOliveGreen",
                       "ForestGreen", "SeaGreen", "Olive", "OliveDrab", "MediumSeaGreen", "LimeGreen", "Lime",
                       "SpringGreen", "MediumSpringGreen", "DarkSeaGreen", "MediumAquamarine", "YellowGreen",
                       "LawnGreen", "Chartreuse", "LightGreen", "GreenYellow", "PaleGreen", "Teal", "DarkCyan",
                       "LightSeaGreen", "CadetBlue", "DarkTurquoise", "MediumTurquoise", "Turquoise", "Aqua", "Cyan",
                       "Aquamarine", "PaleTurquoise", "LightCyan", "Navy", "DarkBlue", "MediumBlue", "Blue",
                       "MidnightBlue", "RoyalBlue", "SteelBlue", "DodgerBlue", "DeepSkyBlue", "CornflowerBlue",
                       "SkyBlue", "LightSkyBlue", "LightSteelBlue", "LightBlue", "PowderBlue", "Indigo", "Purple",
                       "DarkMagenta", "DarkViolet", "DarkSlateBlue", "BlueViolet", "DarkOrchid", "Fuchsia", "Magenta",
                       "SlateBlue", "MediumSlateBlue", "MediumOrchid", "MediumPurple", "Orchid", "Violet", "Plum",
                       "Thistle", "Lavender", "MistyRose", "AntiqueWhite", "Linen", "Beige", "WhiteSmoke",
                       "LavenderBlush", "OldLace", "AliceBlue", "Seashell", "GhostWhite", "Honeydew", "FloralWhite",
                       "Azure", "MintCream", "Snow", "Ivory", "White", "Black", "DarkSlateGray", "DimGray", "SlateGray",
                       "Gray", "LightSlateGray", "DarkGray", "Silver", "LightGray", "Gainsboro"]
    # fonts = get_available_fonts()
    for i in range(7, 11):
        get_simple_stats(retrieve_captcha_from_path("./Results/" + str(i)))
    # for i in range(12, 13):
    #     generate_converged_population(OCR.EASY_OCR, 10, 8, "./Results/" + str(i), colors_extended, fonts,
    #                                   CROSSCOLORVERSION.V2)
