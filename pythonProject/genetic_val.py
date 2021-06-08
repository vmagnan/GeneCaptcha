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


class Captcha:
    def __init__(self, text, txt_color, bg_color, font, path):
        self.text = text
        self.txt_color = txt_color
        self.bg_color = bg_color
        self.font = font
        self.path = path
        self.ocr_value = -1


class Metadata:
    def __init__(self, ocr: string, size: int, threshold: int, path: string, colors: list[string],
                 _fonts: list[string], date: string):
        self.ocr = ocr
        self.size = size
        self.threshold = threshold
        self.path = path
        self.colors = colors
        self.fonts = fonts
        self.iterations = []
        self.total_time = 0
        self.date = date

    def add_iteration(self, selected: int, iteration_time: float):
        self.iterations.append((selected, iteration_time))

    def set_total_time(self, total_time: float):
        self.total_time = total_time

    def save_as_json(self, path=None):
        if path is None:
            path = self.path
        with open(path + 'metadata.json', 'w', encoding='utf-8') as file:
            json.dump(self.__dict__, file, ensure_ascii=False, indent=4, default=str)
        # json_str = json.dumps(self.__dict__)
        # print(json_str)


def initialise(_number: int, _colors: list[string], _fonts: list[string]) -> list[Captcha]:
    """
    Initialise N captcha, save them to ./Image and return the corresponding captcha list
    :param _number: Number of captcha
    :param _colors: Available colors
    :param _fonts: Available fonts
    :return: Captcha list
    """
    _captchas = []
    for i in range(_number):
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
    :param _captchas: Captcha list
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


def cross_color(color_1_hex: string, color_2_hex: string) -> string:
    """ Cross colors by making the average of rgb values
    :param color_2_hex: First color in hexadecimal string
    :param color_1_hex: Second color in hexadecimal string
    :return: Average color in hexadecimal string
    """
    _r1, _g1, _b1 = hex_to_rgb(color_1_hex)
    _r2, _g2, _b2 = hex_to_rgb(color_2_hex)
    _rf = (_r1 + _r2) / 2
    _gf = (_g1 + _g2) / 2
    _bf = (_b1 + _b2) / 2
    _result_hex = rgb_to_hex((_rf, _gf, _bf))
    return mutate_color(_result_hex)


def mutate_color(_color_hex: string) -> string:
    """
    Mutate the color
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


def cross_2_captcha(_captcha_1: Captcha, _captcha_2: Captcha) -> Captcha:
    """
    Cross 2 captcha attributes to create a new one
    :param _captcha_1: First parent captcha
    :param _captcha_2: Second parent captcha
    :return: Son captcha
    """
    _text = cross_text(_captcha_1.text, _captcha_2.text)
    _txt_color = cross_color(_captcha_1.txt_color, _captcha_2.txt_color)
    _bg_color = cross_color(_captcha_1.bg_color, _captcha_2.bg_color)
    _font = random.choice([_captcha_1.font, _captcha_2.font])
    _path = "./Image/Crossed/" + "_".join([_text, _txt_color, _bg_color, _font])
    get_new_captcha(_path, text=_text, color=_txt_color, background=_bg_color, font=_font, width=WIDTH, height=HEIGHT,
                    font_size=FONT_SIZE)
    _captcha = Captcha(_text, _txt_color, _bg_color, _font, _path)
    return _captcha


def crossover(_captchas: list[Captcha], _population_size: int) -> list[Captcha]:
    """
    Shuffle the list, cross the two last captchas, add the parents and the son to the new list
    For each available couple : select 2 random captchas from the list, cross them and add the three captchas to the return list
    And then remove the 2 parents from the initial list
    :param _population_size:
    :param _captchas:
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
        _son = cross_2_captcha(_parent_1, _parent_2)
        if len(_new_population) < _population_size:
            _new_population.append(_son)
    return _new_population


def selection(_captchas: list[Captcha], _threshold: int) -> list[Captcha]:
    """
    Select all captcha with a levenshtein distance > THRESHOLD & with a different text color from its background
    :param _threshold:
    :param _captchas: Captcha list
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
    :param _threshold:
    :param _population_size:
    :param _captchas: Captcha list
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
    return dict(sorted(_dic.items(), key=lambda item: item[1], reverse=True))


def get_simple_stats(_captchas: list[Captcha]):
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
    Number of captchas : {nb}
    Characters apparition : {chs}
    Fonts apparition : {fts}
    Text-Color apparition : {txtcos}
    Background-Color apparition : {bgcos}""".format(nb=len(_captchas), chs=_characters_apparition,
                                                    fts=_fonts_apparition,
                                                    txtcos=_txt_color_apparition, bgcos=_bg_color_apparition))


def retrieve_captcha_from_path(path: string) -> list[Captcha]:
    _captchas = []
    _files = get_paths_files_with_extension_from_folder(path, "png")
    for _file in _files:
        _file_beautified = _file.replace(".png", "").replace(path, "").replace("/", "")
        (_text, _txt_color, _bg_color, _font) = tuple(map(str, _file_beautified.split('_')))
        if _text != "" and _txt_color != "" and _bg_color != "" and _font != "":
            _captchas.append(Captcha(_text, _txt_color, _bg_color, _font, _file))
    return _captchas


def get_converged_population(_ocr: OCR, _size: int, _threshold: int, _path: string, _colors: list[string],
                             _fonts: list[string]) -> \
        list[Captcha]:
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
            _crossed_population = crossover(_selected_population, _size)
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
    colors = ["#000000", "#808080", "#FFFFFF", "#8B4513", "#FF0000", "#FFA500", "#FFFF00", "#008000", "#00FFFF",
              "#0000FF", "#800080", "#FF1493"]
    fonts = get_available_fonts()
    get_simple_stats(
        get_converged_population(_ocr=OCR.EASY_OCR, _size=20, _threshold=6, _path="./Results/14", _colors=colors,
                                 _fonts=fonts))
    # get_simple_stats(retrieve_captcha_from_path("./Results/6"))
