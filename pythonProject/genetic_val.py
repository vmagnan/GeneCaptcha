import json
import time
import textwrap
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


class Stats:
    def __init__(self, characters_apparition, fonts_apparition, txt_color_apparition, bg_color_apparition):
        self.characters_apparition = characters_apparition
        self.fonts_apparition = fonts_apparition
        self.txt_color_apparition = txt_color_apparition
        self.bg_color_apparition = bg_color_apparition

    def print_stats(self):
        print(textwrap.dedent("""\
            ----------------------------------------------------
            Characters apparition : {chs}
            Fonts apparition : {fts}
            Text-Color apparition : {txtcos}
            Background-Color apparition : {bgcos}
            ----------------------------------------------------""".format(chs=self.characters_apparition,
                                                                           fts=self.fonts_apparition,
                                                                           txtcos=self.txt_color_apparition,
                                                                           bgcos=self.bg_color_apparition)))


class Captcha:
    def __init__(self, text, txt_color, bg_color, font, path, generation):
        self.text = text
        self.txt_color = txt_color
        self.bg_color = bg_color
        self.font = font
        self.path = path
        self.ocr_value = -1
        self.prob_max = 0
        self.generation = generation


class Metadata:
    def __init__(self, **kwargs):
        self.ocr = kwargs.get('ocr')
        self.size = kwargs.get('size')
        self.threshold = kwargs.get('threshold')
        self.path = kwargs.get('path')
        self.colors = kwargs.get('colors')
        self.fonts = kwargs.get('fonts')
        self.iterations = []
        self.total_time = 0
        self.date = kwargs.get('date')
        self.stats = None

    def add_iteration(self, mean_values: float, iteration_time: float):
        """
        Append a new iteration to the attribute list called iterations
        :param mean_values: Number of selected individuals
        :param iteration_time: Time taken for the whole operation ==> Evaluation + Selection + Crossover(only when there are 2 individuals)
        :return:
        """
        self.iterations.append((mean_values, iteration_time))

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

    def load_from_json(self, path):
        """
        Save all attributes as JSON
        :param path: Path to the directory where to save the JSON
        :return: Nothing
        """
        with open(path + 'metadata.json', 'r', encoding='utf-8') as file:
            json_object = json.load(file)
            for k in json_object.keys():
                if k == 'ocr':
                    if json_object[k] == 'EASY_OCR':
                        self.__dict__[k] = OCR.EASY_OCR
                    else:
                        self.__dict__[k] = OCR.TESSERACT
                elif k == 'stats':
                    stats = None
                    if len(json_object[k]) == 4:
                        stats = Stats(json_object[k][0], json_object[k][1], json_object[k][2], json_object[k][3])
                    self.__dict__[k] = stats
                else:
                    self.__dict__[k] = json_object[k]


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
        get_new_captcha(_path, _no_color=1, text=_text, color=_txt_color, background=_bg_color, font=_font, width=WIDTH,
                        height=HEIGHT,
                        font_size=FONT_SIZE)
        _captchas.append(Captcha(_text, _txt_color, _bg_color, _font, _path, 0))
    return _captchas


def evaluate_single_captcha(_captcha: Captcha, _ocr: string, _reader):
    if _captcha.ocr_value == -1:
        if _captcha.path[-3:] != "png":
            _path = _captcha.path + '.png'
        else:
            _path = _captcha.path
        _text = _captcha.text
        if _ocr == OCR.EASY_OCR:
            _ocr_string = get_string_ocr_easyocr(_path, _reader)
        elif _ocr == OCR.TESSERACT:
            _ocr_string = get_string_ocr_pytesseract(_path)
        else:
            _ocr_string = None
        _captcha.ocr_value = levenshtein_distance(_ocr_string, _text)


def evaluate(_captchas: list[Captcha], _ocr: string, _reader):
    """
    Evaluate all captchas
    :param _ocr:
    :param _reader:
    :param _captchas: List of captchas
    :return: Nothing
    """
    for _captcha in _captchas:
        evaluate_single_captcha(_captcha, _ocr, _reader)


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


def cross_font(_font1: string, _font2: string) -> string:
    font_name: list = [_font1.split("-")[0], _font2.split("-")[0]]
    font_type: list = [_font1.split("-")[1], _font2.split("-")[1]]
    return random.choice(font_name) + "-" + random.choice(font_type)


def mutate_font() -> string:
    if random.randint(1, 1) == 1:
        font_list = get_available_fonts()
        return random.choice(font_list)


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


def cross_color_v2(_color_1: string, _color_2: string, _colors: list[string], _forbidden_color: string = "") -> string:
    """
    Cross colors V2
    By taking the color with the index in the middle of the 2 parents
    :param _color_1: First color in string
    :param _color_2: Second color in string
    :param _colors: List of colors
    :param _forbidden_color: Forbidden color, in order to get different color for the text and background
    :return: 
    """
    _pos_color_1 = _colors.index(_color_1)
    _pos_color_2 = _colors.index(_color_2)
    # We get the colors between the two index into _sub_colors
    _sub_colors = []
    for _i in range(_pos_color_1, _pos_color_2):
        _sub_colors.append(_colors[_i])
    _size_sub_color = len(_sub_colors)
    # If the two colors are neighbours <==> _size_sub_color = 0, then choose randomly between the parents
    if _size_sub_color == 0:
        _return_color = mutate_color_v2(random.choice([_color_1, _color_2]), _colors)
    # Get the middle of the list
    # if length is pair there are two colors, we choose a random one between them, index len/2 or len/2 -1
    elif _size_sub_color % 2 == 0:
        _return_color = mutate_color_v2(_sub_colors[int(_size_sub_color / 2) - random.choice([0, 1])], _colors)
    # Otherwise it's the int part of the length divided by 2
    else:
        _return_color = mutate_color_v2(_sub_colors[int(_size_sub_color / 2)], _colors)

    # _return_color is returned only if != than forbidden color
    # Otherwise : If _color_1 && _color_2 != forbidden, return random one between them
    # Otherwise : Return the one different from forbidden
    if _return_color != _forbidden_color:
        return _return_color
    else:
        if _color_1 != _forbidden_color and _color_2 != _forbidden_color:
            return random.choice([_color_1, _color_2])
        else:
            if _color_1 != _forbidden_color:
                return _color_1
            else:
                return _color_2


def mutate_color_v2(_color: string, _colors: list[string]) -> string:
    """
    Mutate the color V2
    1/10 chance to mutate the color
    Change the color by the one before or after the actual color index in the list
    :param _color: Color to mutate
    :param _colors: List of colors
    :return:
    """
    if random.randint(1, 10) == 1:
        _pos_color = _colors.index(_color)
        _new_index_color = _pos_color + random.choice([-1, 1])
        if _new_index_color > len(_colors) - 1:
            _color = _colors[0]
        else:
            _color = _colors[_new_index_color]
    return _color


def cross_2_captcha(_parents: tuple[Captcha, Captcha], _colors: list[string],
                    _cross_color_version: CROSSCOLORVERSION = CROSSCOLORVERSION.V1, ) -> Captcha:
    """
    Cross 2 captcha attributes to create a new one
    :param _parents: Tuple of parents
    :param _colors: List of colors, needed in the cross_color_v2
    :param _cross_color_version: Version of crosscolor
    :return: Son captcha
    """
    _text = cross_text(_parents[0].text, _parents[1].text)
    if _cross_color_version == CROSSCOLORVERSION.V2:
        _txt_color = cross_color_v2(_parents[0].txt_color, _parents[1].txt_color, _colors)
        _bg_color = cross_color_v2(_parents[0].bg_color, _parents[1].bg_color, _colors, _txt_color)

    else:
        _txt_color = cross_color_v1(_parents[0].txt_color, _parents[1].txt_color)
        _bg_color = cross_color_v1(_parents[0].bg_color, _parents[1].bg_color)
    _font = random.choice([_parents[0].font, _parents[1].font])
    _path = "./Image/Crossed/" + "_".join([_text, _txt_color, _bg_color, _font])
    get_new_captcha(_path, _no_color=1, text=_text, color=_txt_color, background=_bg_color, font=_font, width=WIDTH,
                    height=HEIGHT,
                    font_size=FONT_SIZE)
    _captcha = Captcha(_text, _txt_color, _bg_color, _font, _path,
                       max([_parents[0].generation, _parents[1].generation]) + 1)
    return _captcha


def crossover(_captchas: list[Captcha], _population_size: int, _colors: list[string],
              _cross_color_version: CROSSCOLORVERSION = CROSSCOLORVERSION.V1) -> list[Captcha]:
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
        _son = cross_2_captcha((_parent_1, _parent_2), _colors, _cross_color_version)
        if len(_new_population) < _population_size:
            _new_population.append(_son)
    return _new_population


def selection(_captchas: list[Captcha]) -> (Captcha, Captcha):
    """
    Select 2 different parents with Fitness proportionate selection
    :param _captchas: List of captchas
    :return: Tuple of 2 parents captcha
    """
    _probs = []
    _previous_prob = 0
    _selected_captchas = []
    _parent_1 = _parent_2 = None
    _sorted_captchas = sorted(_captchas, key=lambda _captcha: _captcha.ocr_value)
    _sum_values = sum(_c.ocr_value for _c in _sorted_captchas)
    # Calcul max proba for each captcha    
    for _c in _sorted_captchas:
        _c.prob_max = _previous_prob + (_c.ocr_value / _sum_values)
        _previous_prob = _c.prob_max
    # Select parent 1, the parent_2 == parent 1 to get two different parents in next loop
    random_number = random.random()
    for _c in _sorted_captchas:
        if random_number < _c.prob_max:
            _parent_1 = _c
            _parent_2 = _c
            break
    # Select parent 2, while parent 2 == parent 1 in case the probabilities gives the same parent
    while _parent_1 == _parent_2:
        random_number = random.random()
        for _c in _sorted_captchas:
            if random_number < _c.prob_max:
                _parent_2 = _c
                break
    return _parent_1, _parent_2


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
        get_new_captcha(_captcha.path, _no_color=1, text=_captcha.text, color=_captcha.txt_color,
                        background=_captcha.bg_color,
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


def get_simple_stats(_captchas: list[Captcha]) -> Stats:
    """
    Print the occurrence of each captcha parameter : Letter, text color, background color, font
    :param _captchas: List of captchas
    :return: Stats object
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
    _stats = Stats(_characters_apparition, _fonts_apparition, _txt_color_apparition, _bg_color_apparition)
    _stats.print_stats()
    return _stats


def summarize(_captchas: list[Captcha], _data_dict):
    # Not working, get doesn't exist on lists
    for _captcha in _captchas:
        for _letter in _captcha.text:
            if _data_dict.get(_letter) is not None:
                if _data_dict[_letter].get(_captcha.bg_color) is not None:
                    if _data_dict[_letter][_captcha.bg_color].get(_captcha.font) is not None:
                        _data_dict[_letter][_captcha.bg_color][_captcha.font] += 1
                    else:
                        font_add = {_captcha.font: 1}
                        _data_dict[_letter][_captcha.bg_color].update(font_add)
                else:
                    font_add = {_captcha.font: 1}
                    color_add = {_captcha.bg_color: font_add}
                    _data_dict[_letter].update(color_add)
            else:
                font_add = {_captcha.font: 1}
                color_add = {_captcha.bg_color: font_add}
                letter_add = {_letter: color_add}
                _data_dict.update(letter_add)
    # print(_data_dict)
    return _data_dict


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
            _captchas.append(Captcha(_text, _txt_color, _bg_color, _font, _file, -1))
    return _captchas


def retrieve_metadata_from_path(_path: string) -> Metadata:
    """
    Retrieve the list of captcha located in a specific path
    :param _path: Path
    :return: List of captchas
    """
    # Add '/' at the end of the path when missing
    if _path[-1] != '/':
        _path = _path + '/'
    _metadata = Metadata()
    _metadata.load_from_json(_path)
    return _metadata


def replace_worst_captcha_by_new_captcha(_captchas: list[Captcha], _new_captcha: Captcha):
    i = 0
    _worst_index = 0
    _worst_value = _captchas[0].ocr_value
    for _c in _captchas:
        if _c.ocr_value < _worst_value and _c.ocr_value != -1:
            _worst_value = _c.ocr_value
            _worst_index = i
        i += 1
    _captchas[_worst_index] = _new_captcha


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
    _metadata = Metadata(ocr=_ocr.value, size=_size, threshold=_threshold, path=_path, colors=_colors, fonts=_fonts, date=datetime.now())
    _starting_time = time.time()
    _population = initialise(_size, _colors, _fonts)
    _iterations = 0
    _starting_time_iteration = time.time()
    while not is_population_converged(_population, _size, _threshold):
        # Evaluate the crossed population
        evaluate(_population, _ocr, _reader)
        print("Iteration = {iter}".format(iter=_iterations))
        # Select individuals accordingly to a Threshold
        _parents = selection(_population)
        # If population has totally converged, we get out of the loop
        _son = cross_2_captcha(_parents, _colors, _cross_color_version)
        evaluate_single_captcha(_son, _ocr, _reader)
        if _son.ocr_value >= max(_c.ocr_value for _c in _parents):
            replace_worst_captcha_by_new_captcha(_population, _son)
            mean_ocr_value = sum(_c.ocr_value for _c in _population) / len(_population)
            print("Replaced and average values in the population is {0}".format(mean_ocr_value))
            _iterations += 1
            _metadata.add_iteration(mean_ocr_value, time.time() - _starting_time_iteration)
            _starting_time_iteration = time.time()
    _metadata.set_total_time(time.time() - _starting_time)
    _metadata.stats = get_simple_stats(_population)
    _metadata.save_as_json()
    print("""\
    Convergence of the population :
    Iteration required = {nbiter}
    Time required = {time} seconds
    """.format(nbiter=len(_metadata.iterations), time=_metadata.total_time))
    save_converged_population(_population, _path)
    return _population


if __name__ == "__main__":
    # Pour supprimer rapidement les images/json de certains dossiers
    # for i in range(25,30):
    #     delete_files_with_extension_from_path("./Results/" + str(i) + '/', 'png')
    #     delete_files_with_extension_from_path("./Results/" + str(i) + '/', 'json')
    # fonts = get_available_fonts()
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
    # for i in range(7, 11):
    # retrieve_captcha_from_path("./Results/Probabilist/5")
    metadata = retrieve_metadata_from_path("./Results/Probabilist/6")
    metadata.stats.print_stats()
    # captchas = generate_converged_population(OCR.EASY_OCR, 15, 5, "./Results/Probabilist/6", colors_extended, fonts,
    #                                          CROSSCOLORVERSION.V2)
    # get_simple_stats(captchas)
    # for captcha in new_list:
    #     print(captcha.ocr_value)
