import json
import time
import textwrap
import matplotlib.pyplot as plt
import webcolors
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


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        elif isinstance(obj, datetime):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class Stats:
    def __init__(self, characters_apparition, fonts_apparition, txt_color_apparition, bg_color_apparition):
        self.characters_apparition = characters_apparition
        self.fonts_apparition = fonts_apparition
        self.txt_color_apparition = txt_color_apparition
        self.bg_color_apparition = bg_color_apparition

    def repr_json(self):
        return dict(characters_apparition=self.characters_apparition, fonts_apparition=self.fonts_apparition,
                    txt_color_apparition=self.txt_color_apparition, bg_color_apparition=self.bg_color_apparition)

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

    def repr_json(self):
        return dict(stats=self.stats, ocr=self.ocr, size=self.size, threshold=self.threshold, path=self.path,
                    colors=self.colors,
                    fonts=self.fonts, iterations=self.iterations, total_time=self.total_time, date=self.date)

    def save_as_json(self, _path=None):
        """
        Save all attributes as JSON
        :param _path: Path to the directory where to save the JSON
        :return: Nothing
        """
        if _path is None:
            _path = self.path
        with open(_path + 'metadata.json', 'w', encoding='utf-8') as file:
            data = json.dumps(self.repr_json(), ensure_ascii=False, indent=4, cls=ComplexEncoder)
            print(data)
            file.write(data)

    def load_from_json(self, path):
        """
        Save all attributes as JSON
        :param path: Path to the directory where to save the JSON
        :return: Nothing
        """
        path = add_trailing_slash_to_path(path)
        with open(path + 'metadata.json', 'r', encoding='utf-8') as file:
            _json_object = json.load(file)
            for _k in _json_object.keys():
                if _k == 'ocr':
                    if _json_object[_k] == 'EASY_OCR':
                        self.__dict__[_k] = OCR.EASY_OCR
                    else:
                        self.__dict__[_k] = OCR.TESSERACT
                elif _k == 'stats':
                    _stats = None
                    if len(_json_object[_k]) == 4:
                        _stats = Stats(_json_object[_k]['characters_apparition'], _json_object[_k]['fonts_apparition'],
                                       _json_object[_k]['txt_color_apparition'], _json_object[_k]['bg_color_apparition'])
                    self.__dict__[_k] = _stats
                else:
                    self.__dict__[_k] = _json_object[_k]


def initialise(_number: int, _colors: list[string], _fonts: list[string], _no_color_mode: bool) -> list[Captcha]:
    """
    Initialise N captcha, save them to ./Image and return the corresponding captcha list
    :param _number: Number of captcha
    :param _colors: Available colors
    :param _fonts: Available fonts
    :param _no_color_mode: Captcha in black and white when activated
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
        get_new_captcha(_path, _no_color=_no_color_mode, text=_text, color=_txt_color, background=_bg_color, font=_font, width=WIDTH,
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


def mutate_color_v2(_color: string, _colors: list[string], _forbidden_color: string = "") -> string:
    """
    Mutate the color V2
    1/10 chance to mutate the color
    Change the color by the one before or after the actual color index in the list
    :param _forbidden_color: Forbidden color, in order to get different color for the text and background
    :param _color: Color to mutate
    :param _colors: List of colors
    :return:
    """
    if random.randint(1, 10) == 1:
        _pos_color = _colors.index(_color)
        # We have the index, we don't need to remember the color to mutate
        # It's supposed to fix the problem with same color for the text and the background
        _color = _forbidden_color
        while _color == _forbidden_color:
            random_number = random.choice([-1, 1])
            _new_index_color = _pos_color + random_number
            if _new_index_color > len(_colors) - 1:
                _color = _colors[0]
            else:
                _color = _colors[_new_index_color]
    return _color


def cross_2_captcha(_parents: tuple[Captcha, Captcha], _colors: list[string], _no_color_mode: bool,
                    _cross_color_version: CROSSCOLORVERSION = CROSSCOLORVERSION.V1, ) -> Captcha:
    """
    Cross 2 captcha attributes to create a new one
    :param _parents: Tuple of parents
    :param _colors: List of colors, needed in the cross_color_v2
    :param _no_color_mode: Captcha in black and white when activated
    :param _cross_color_version: Version of crosscolor
    :return: Son captcha
    """
    _text = cross_text(_parents[0].text, _parents[1].text)
    if _cross_color_version == CROSSCOLORVERSION.V2:
        _txt_color = cross_color_v2(_parents[0].txt_color, _parents[1].txt_color, _colors)
        _bg_color = _txt_color
        while _bg_color == _txt_color:
            _bg_color = cross_color_v2(_parents[0].bg_color, _parents[1].bg_color, _colors, _txt_color)

    else:
        _txt_color = cross_color_v1(_parents[0].txt_color, _parents[1].txt_color)
        _bg_color = _txt_color
        while _bg_color == _txt_color:
            _bg_color = cross_color_v1(_parents[0].bg_color, _parents[1].bg_color)
    _font = random.choice([_parents[0].font, _parents[1].font])
    _path = "./Image/Crossed/" + "_".join([_text, _txt_color, _bg_color, _font])
    get_new_captcha(_path, _no_color=_no_color_mode, text=_text, color=_txt_color, background=_bg_color, font=_font, width=WIDTH,
                    height=HEIGHT,
                    font_size=FONT_SIZE)
    _captcha = Captcha(_text, _txt_color, _bg_color, _font, _path,
                       max([_parents[0].generation, _parents[1].generation]) + 1)
    return _captcha


def crossover(_captchas: list[Captcha], _population_size: int, _colors: list[string], _no_color_mode: bool = False,
              _cross_color_version: CROSSCOLORVERSION = CROSSCOLORVERSION.V1) -> list[Captcha]:
    """
    Shuffle the list, cross the two last captchas, add the parents and the son to the new list
    For each available couple : select 2 random captchas from the list, cross them and add the three captchas to the return list
    And then remove the 2 parents from the initial list
    :param _no_color_mode: Captcha in black and white when activated
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
        _son = cross_2_captcha((_parent_1, _parent_2), _colors, _no_color_mode, _cross_color_version)
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
    Save all captchas as png to a path by moving them from old path to the new one
    Be careful, this function also delete the png already located to the path !
    :param _captchas: List of captchas
    :param _path: Path
    :return:
    """
    for _captcha in _captchas:
        _new_path = _path + "_".join([_captcha.text, _captcha.txt_color, _captcha.bg_color, _captcha.font])
        os.rename(_captcha.path + ".png", _new_path + ".png")
        _captcha.path = _new_path


def sort_dic_by_value_descending(_dic: dict) -> dict:
    """
    Sort dictionary by value and descending
    :param _dic: Dictionary to sort
    :return: Sorted dictionary
    """
    return dict(sorted(_dic.items(), key=lambda item: item[1], reverse=True))


def get_stats(_captchas: list[Captcha]) -> Stats:
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
    _path = add_trailing_slash_to_path(_path)
    _captchas = []
    _files = get_paths_files_with_extension_from_folder(_path, "png")
    try:
        _files.remove(_path + 'occurence_donuts.png')
    except:
        pass
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
    _path = add_trailing_slash_to_path(_path)
    _metadata = Metadata()
    _metadata.load_from_json(_path)
    return _metadata


def replace_worst_captcha_by_new_captcha(_captchas: list[Captcha], _new_captcha: Captcha):
    _i = 0
    _worst_index = 0
    _worst_value = _captchas[0].ocr_value
    for _c in _captchas:
        if _c.ocr_value < _worst_value and _c.ocr_value != -1:
            _worst_value = _c.ocr_value
            _worst_index = _i
        _i += 1
    _captchas[_worst_index] = _new_captcha


def save_captcha_list_as_json(_captchas: list[Captcha], _path: string):
    _path = add_trailing_slash_to_path(_path)
    json_string = json.dumps([_c.__dict__ for _c in _captchas])
    with open(_path + 'captchas.json', 'w', encoding='utf-8') as file:
        file.write(json_string)


def generate_converged_population(_ocr: OCR, _size: int, _threshold: int, _path: string, _colors: list[string],
                                  _fonts: list[string], _no_color_mode: bool = False,
                                  _cross_color_version: CROSSCOLORVERSION = CROSSCOLORVERSION.V1) -> \
        (list[Captcha], Metadata):
    """
    Generate a converged population with a genetic algorithm
    :param _no_color_mode: Captcha in black and white when activated
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
    _path = add_trailing_slash_to_path(_path)
    # Initialize metadata
    _metadata = Metadata(ocr=_ocr.value, size=_size, threshold=_threshold, path=_path, colors=_colors, fonts=_fonts, date=datetime.now())
    _starting_time = time.time()
    _population = initialise(_size, _colors, _fonts, _no_color_mode)
    _iterations = 0
    _starting_time_iteration = time.time()
    while not is_population_converged(_population, _size, _threshold):
        # Evaluate the crossed population
        evaluate(_population, _ocr, _reader)
        print("Iteration = {iter}".format(iter=_iterations))
        # Select individuals accordingly to a Threshold
        _parents = selection(_population)
        # If population has totally converged, we get out of the loop
        _son = cross_2_captcha(_parents, _colors, _no_color_mode, _cross_color_version)
        evaluate_single_captcha(_son, _ocr, _reader)
        if _son.ocr_value >= max(_c.ocr_value for _c in _parents):
            replace_worst_captcha_by_new_captcha(_population, _son)
            mean_ocr_value = sum(_c.ocr_value for _c in _population) / len(_population)
            print("Replaced and average values in the population is {0}".format(mean_ocr_value))
            _iterations += 1
            _metadata.add_iteration(mean_ocr_value, time.time() - _starting_time_iteration)
            _starting_time_iteration = time.time()
    # Remove all files in that path
    delete_files_with_extension_from_path(_path, 'png')
    delete_files_with_extension_from_path(_path, 'json')
    _metadata.set_total_time(time.time() - _starting_time)
    # Save our new population and metadata
    _metadata.stats = get_stats(_population)
    _metadata.save_as_json(_path)
    print("""\
    Convergence of the population :
    Iteration required = {nbiter}
    Time required = {time} seconds
    """.format(nbiter=len(_metadata.iterations), time=_metadata.total_time))
    save_converged_population(_population, _path)
    save_captcha_list_as_json(_population, _path)
    return _population, _metadata


def draw_single_donut_from_dic(_dic: dict, _path: str = None, _title: str = None, _color: bool = False):
    _fig, _ax = plt.subplots()
    if _title is not None:
        _fig.suptitle(_title)
    else:
        _fig.suptitle("A Beautiful donut")
    _total_values = sum(_dic.values())
    _sizes = []
    _labels = _dic.keys()
    for _l in _labels:
        _sizes.append(_dic[_l] / _total_values)
    _colors = None
    if _color:
        _colors = []
        for _l in _labels:
            _colors.append(webcolors.name_to_hex(_l))
        _ax.pie(_sizes, autopct=None, startangle=90, wedgeprops=dict(width=.3), colors=_colors)
    else:
        _ax.pie(_sizes, labels=_labels, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=.3))
    _ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    # mng = plt.get_current_fig_manager()
    # mng.full_screen_toggle()
    if _path is None:
        plt.show()
    else:
        if _title is not None:
            plt.savefig(_path + _title + '-donut.png', dpi=200, bbox_inches='tight')
        else:
            plt.savefig(_path + 'donut.png', dpi=200, bbox_inches='tight')


def draw_occurences_donut_from_stats(_stats: Stats, _path: str = None):
    _fig, ((_ax1, _ax2), (_ax3, _ax4)) = plt.subplots(2, 2)
    _fig.suptitle("Occurences")
    for _i in range(0, 4):
        if _i == 1:
            _dic = _stats.characters_apparition
            _title = "Characters"
            _ax = _ax1
        elif _i == 2:
            _dic = _stats.fonts_apparition
            _title = "Fonts"
            _ax = _ax2
        elif _i == 3:
            _dic = _stats.txt_color_apparition
            _title = "Text Colors"
            _ax = _ax3
        else:
            _dic = _stats.bg_color_apparition
            _title = "Background Colors"
            _ax = _ax4
        _total_values = sum(_dic.values())
        _sizes = []
        _labels = _dic.keys()
        for _l in _labels:
            _sizes.append(_dic[_l] / _total_values)
        _ax.pie(_sizes, labels=_labels, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=.3))
        _ax.set_title(_title)
        _ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    if _path is None:
        plt.show()
    else:
        plt.savefig(_path + 'occurence_donuts.png', dpi=200, bbox_inches='tight')


def draw_donuts_multiple_population_from_x_to_y(x: int, y: int, _directory_captcha: str, _directory_donuts: str, _sanatize_dir_donuts:bool=True):
    _all_captchas = []
    _directory_captcha = add_trailing_slash_to_path(_directory_captcha)
    if _sanatize_dir_donuts:
        _directory_donuts = add_trailing_slash_to_path(_directory_donuts)
    for i in range(x, y + 1):
        _captchas = retrieve_captcha_from_path(_directory_captcha + str(i))
        _all_captchas += _captchas

    stats = get_stats(_all_captchas)
    # draw_occurences_donut_from_stats(stats, "./6-13")
    prefix_filename_donut = _directory_donuts + "{0}-{1}".format(x, y)
    draw_single_donut_from_dic(stats.characters_apparition, prefix_filename_donut, "Characters")
    draw_single_donut_from_dic(stats.bg_color_apparition, prefix_filename_donut, "Background Colors", True)
    draw_single_donut_from_dic(stats.txt_color_apparition, prefix_filename_donut, "Text Colors", True)
    draw_single_donut_from_dic(stats.fonts_apparition, prefix_filename_donut, "Fonts")


def generate_populations_from_x_to_y(_x: int, _y: int, _ocr: OCR, _size: int, _threshold: int, _path: string, _colors: list[string],
                                     _fonts: list[string], _no_color_mode: bool = False,
                                     _cross_color_version: CROSSCOLORVERSION = CROSSCOLORVERSION.V1):
    for i in range(_x, _y + 1):
        _captchas, _metadata = generate_converged_population(_ocr, _size, _threshold, _path + str(i), _colors, _fonts,
                                                             _no_color_mode,
                                                             _cross_color_version.V2)
        draw_occurences_donut_from_stats(_metadata.stats, _path + str(i) + "/")


if __name__ == "__main__":
    colors = ["red", "pink", "purple", "blue", "cyan", "green", "yellow", "orange"]
    colors_extended = ["mediumvioletred", "deeppink", "palevioletred", "hotpink", "lightpink", "pink", "darkred", "red",
                       "firebrick", "crimson", "indianred", "lightcoral", "salmon", "darksalmon", "lightsalmon",
                       "orangered", "tomato", "darkorange", "coral", "orange", "darkkhaki", "gold", "khaki",
                       "peachpuff", "yellow", "palegoldenrod", "moccasin", "papayawhip", "lightgoldenrodyellow",
                       "lemonchiffon", "lightyellow", "maroon", "brown", "saddlebrown", "sienna", "chocolate",
                       "darkgoldenrod", "peru", "rosybrown", "goldenrod", "sandybrown", "tan", "burlywood", "wheat",
                       "navajowhite", "bisque", "blanchedalmond", "cornsilk", "darkgreen", "green", "darkolivegreen",
                       "forestgreen", "seagreen", "olive", "olivedrab", "mediumseagreen", "limegreen", "lime",
                       "springgreen", "mediumspringgreen", "darkseagreen", "mediumaquamarine", "yellowgreen",
                       "lawngreen", "chartreuse", "lightgreen", "greenyellow", "palegreen", "teal", "darkcyan",
                       "lightseagreen", "cadetblue", "darkturquoise", "mediumturquoise", "turquoise", "aqua", "cyan",
                       "aquamarine", "paleturquoise", "lightcyan", "navy", "darkblue", "mediumblue", "blue",
                       "midnightblue", "royalblue", "steelblue", "dodgerblue", "deepskyblue", "cornflowerblue",
                       "skyblue", "lightskyblue", "lightsteelblue", "lightblue", "powderblue", "indigo", "purple",
                       "darkmagenta", "darkviolet", "darkslateblue", "blueviolet", "darkorchid", "fuchsia", "magenta",
                       "slateblue", "mediumslateblue", "mediumorchid", "mediumpurple", "orchid", "violet", "plum",
                       "thistle", "lavender", "mistyrose", "antiquewhite", "linen", "beige", "whitesmoke",
                       "lavenderblush", "oldlace", "aliceblue", "seashell", "ghostwhite", "honeydew", "floralwhite",
                       "azure", "mintcream", "snow", "ivory", "white", "black", "darkslategray", "dimgray", "slategray",
                       "gray", "lightslategray", "darkgray", "silver", "lightgray", "gainsboro"]
    # for col in colors_extended:
    #     hex = webcolors.name_to_hex(col)
    #     print("({0},{1})".format(col,hex))
    # for i in range(8,9):
    #     path = "./Results/Determinist/" + str(i) + "/"
    #     captchas = retrieve_captcha_from_path(path)
    #     metadata = retrieve_metadata_from_path(path)
    #     draw_single_donut_from_dic(metadata.stats.bg_color_apparition,path,"bg-color",True)
    directory = "Probabilist"
    start = 31
    end = 38
    draw_donuts_multiple_population_from_x_to_y(start, end, "./Results/" + directory + "/", "./x11-", False)
    start = 14
    end = 20
    draw_donuts_multiple_population_from_x_to_y(start, end, "./Results/" + directory + "/", "./x11-", False)
    start = 6
    end = 13
    draw_donuts_multiple_population_from_x_to_y(start, end, "./Results/" + directory + "/", "./rainbow-", False)
    start = 21
    end = 30
    draw_donuts_multiple_population_from_x_to_y(start, end, "./Results/" + directory + "/", "./rainbow-", False)
    start = 39
    end = 50
    draw_donuts_multiple_population_from_x_to_y(start, end, "./Results/" + directory + "/", "./b&w-", False)
    # fonts = get_available_fonts()
    # # Colors extended from 31 to 38
    # start = 31
    # end = 38
    directory = "Probabilist"
    # generate_populations_from_x_to_y(start, end, OCR.EASY_OCR, 35, 8, "./Results/" + directory + "/", colors_extended, fonts, False,
    #                                  CROSSCOLORVERSION.V2)
    # draw_donuts_multiple_population_from_x_to_y(start, end, "./Results/" + directory + "/", "./")
    # Black & White from 39 to 50
    start = 51
    end = 51
    generate_populations_from_x_to_y(start, end, OCR.EASY_OCR, 10, 4, "./Results/" + directory + "/", colors_extended, fonts, _no_color_mode=True)
    draw_donuts_multiple_population_from_x_to_y(start, end, "./Results/" + directory + "/", "./")
    # for i in range(8,12):
    #     path = "./Results/Determinist/"+str(i)+"/"
    #     captchas = retrieve_captcha_from_path(path)
    #     metadata = retrieve_metadata_from_path(path)
    #     metadata.stats = get_stats(captchas)
    #     metadata.save_as_json(path)
    #     save_captcha_list_as_json(captchas, path)
    #     draw_occurences_donut_from_stats(metadata.stats, path)