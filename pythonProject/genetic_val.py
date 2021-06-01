import time

from colorutils import *
from jellyfish import levenshtein_distance

from toolbox import *

TEXT_LENGTH = 8
WIDTH = 600
HEIGHT = 200
FONT_SIZE = 64
# READER = easyocr.Reader(['en'])
THRESHOLD = 6
POPULATION_SIZE = 10


class Captcha:
    def __init__(self, text, txt_color, bg_color, font, path):
        self.text = text
        self.txt_color = txt_color
        self.bg_color = bg_color
        self.font = font
        self.path = path
        self.value_easyocr = -1
        self.value_tesseract = -1


class Small_Stat:
    def __init__(self, text, txt_color, bg_color, font, path):
        self.text = text
        self.txt_color = txt_color
        self.bg_color = bg_color
        self.font = font
        self.path = path
        self.value_easyocr = -1
        self.value_tesseract = -1


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


def evaluate(_captchas: list[Captcha]):
    """
    Evaluate all captchas
    :param _captchas: Captcha list
    :return: Nothing
    """
    for _captcha in _captchas:
        if _captcha.value_easyocr == -1 or _captcha.value_tesseract == -1:
            _path = _captcha.path + '.png'
            _text = _captcha.text
            _tesseract_string = get_string_ocr_pytesseract(_path)
            _easyocr_string = get_string_ocr_easyocr(_path, READER)
            _captcha.value_tesseract = levenshtein_distance(_tesseract_string, _text)
            _captcha.value_easyocr = levenshtein_distance(_easyocr_string, _text)


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


def crossover(_captchas: list[Captcha]) -> list[Captcha]:
    """
    Shuffle the list, cross the two last captchas, add the parents and the son to the new list
    For each available couple : select 2 random captchas from the list, cross them and add the three captchas to the return list
    And then remove the 2 parents from the initial list
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
    while len(_captchas) >= 2 and len(_new_population) < POPULATION_SIZE:
        random.shuffle(_captchas)
        _parent_1 = _captchas.pop()
        _parent_2 = _captchas.pop()
        _son = cross_2_captcha(_parent_1, _parent_2)
        if len(_new_population) < POPULATION_SIZE:
            _new_population.append(_son)
    return _new_population


def selection(_captchas: list[Captcha]) -> list[Captcha]:
    """
    Select all captcha with a levenshtein distance > THRESHOLD & with a different text color from its background
    :param _captchas: Captcha list
    :return: List of Selected captchas
    """
    _selected_captchas = []
    for _captcha in _captchas:
        if _captcha.value_easyocr >= THRESHOLD:
            if _captcha.txt_color != _captcha.bg_color:
                _selected_captchas.append(_captcha)
    return _selected_captchas


def is_population_optimized(_captchas: list[Captcha]) -> bool:
    """
    Return true when the population is full and their EasyOCR values are >= THRESHOLD
    :param _captchas: Captcha list
    :return:
    """
    if len(_captchas) < POPULATION_SIZE:
        return False
    for _captcha in _captchas:
        if _captcha.value_easyocr < THRESHOLD:
            return False
    return True


def save_optimized_population(_captchas: list[Captcha], _path: string):
    """
    Save all captchas as png to a path
    :param _captchas: List of captchas
    :param _path: Path
    :return:
    """
    for _captcha in _captchas:
        _captcha.path = _path + "_".join([_captcha.text, _captcha.txt_color, _captcha.bg_color, _captcha.font])
        get_new_captcha(_captcha.path, text=_captcha.text, color=_captcha.txt_color, background=_captcha.bg_color,
                        font=_captcha.font, width=WIDTH,
                        height=HEIGHT,
                        font_size=FONT_SIZE)


def sort_frequency_dic_by_value_descending(_dic: dict) -> dict:
    return dict(sorted(_dic.items(), key=lambda item: item[1], reverse=True))


def get_simple_stats(_captchas: list[Captcha]):
    _characters_frequency = {}
    _fonts_frequency = {}
    _txt_color_frequency = {}
    _bg_color_frequency = {}
    for _captcha in _captchas:
        # Calculate the sum of all char used in all captchas
        for _char in _captcha.text:
            if _char in _characters_frequency:
                _characters_frequency[_char] += 1
            else:
                _characters_frequency[_char] = 1
        # Calculate the sum of all fonts used in all captchas
        if _captcha.font in _fonts_frequency:
            _fonts_frequency[_captcha.font] += 1
        else:
            _fonts_frequency[_captcha.font] = 1
        # Calculate the sum of all txt colors used in all captchas
        if _captcha.txt_color in _txt_color_frequency:
            _txt_color_frequency[_captcha.txt_color] += 1
        else:
            _txt_color_frequency[_captcha.txt_color] = 1
        # Calculate the sum of all bg colors used in all captchas
        if _captcha.bg_color in _bg_color_frequency:
            _bg_color_frequency[_captcha.bg_color] += 1
        else:
            _bg_color_frequency[_captcha.bg_color] = 1
    # Sort frequencies by value and descending
    _characters_frequency = sort_frequency_dic_by_value_descending(_characters_frequency)
    _fonts_frequency = sort_frequency_dic_by_value_descending(_fonts_frequency)
    _txt_color_frequency = sort_frequency_dic_by_value_descending(_txt_color_frequency)
    _bg_color_frequency = sort_frequency_dic_by_value_descending(_bg_color_frequency)
    print("""\
    Characters frequency : {chs}
    Fonts frequency : {fts}
    Text-Color frequency : {txtcos}
    Background-Color frequency : {bgcos}""".format(chs=_characters_frequency, fts=_fonts_frequency,
                                                   txtcos=_txt_color_frequency, bgcos=_bg_color_frequency))


def retrieve_captcha_from_path(path: string) -> list[Captcha]:
    _captchas = []
    _files = get_paths_files_with_extension_from_folder(path, "png")
    for _file in _files:
        _file_beautified = _file.replace(".png", "").replace(path, "").replace("/", "")
        (_text, _txt_color, _bg_color, _font) = tuple(map(str, _file_beautified.split('_')))
        if _text != "" and _txt_color != "" and _bg_color != "" and _font != "":
            _captchas.append(Captcha(_text, _txt_color, _bg_color, _font, _file))
    return _captchas


if __name__ == "__main__":
    get_simple_stats(retrieve_captcha_from_path("./Results/4"))
    # starting_time = time.time()
    # colors = ["#000000", "#808080", "#FFFFFF", "#8B4513", "#FF0000", "#FFA500", "#FFFF00", "#008000", "#00FFFF",
    #           "#0000FF", "#800080", "#FF1493"]
    # crossed_population = []
    # fonts = get_available_fonts()
    # delete_files_with_extension_from_path("./Image/", 'png')
    # population = initialise(POPULATION_SIZE, colors, fonts)
    # evaluate(population)
    # iterations = 0
    # while not is_population_optimized(population):
    #     print("Iteration = {iter}".format(iter=iterations))
    #     # Select individuals accordingly to a Threshold
    #     selected_population = selection(population)
    #     print("{nb} Selected captcha".format(nb=len(selected_population)))
    #     # If population is optimized, we get out of the loop
    #     if len(selected_population) >= POPULATION_SIZE:
    #         population = selected_population
    #         break
    #     # If there are at least 2 selected individuals, we reproduce them
    #     if len(selected_population) > 1:
    #         crossed_population = crossover(selected_population)
    #     # Otherwise, we generate new individuals, and append the one selected if it exists
    #     else:
    #         new_population = initialise(POPULATION_SIZE - len(selected_population), colors, fonts)
    #         if len(selected_population) > 1:
    #             new_population.append(selected_population.pop())
    #         crossed_population = new_population
    #     # Evaluate the crossed population
    #     evaluate(crossed_population)
    #     # And so on !
    #     population = crossed_population
    #     iterations += 1
    # print("""\
    # Optimization of the population :
    # Iteration required = {iter}
    # Time required = {time} seconds
    # """.format(iter=iterations, time=time.time() - starting_time))
    # save_optimized_population(population, "Image/Optimized/1/")
