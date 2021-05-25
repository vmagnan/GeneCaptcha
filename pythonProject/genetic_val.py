from toolbox import *
from jellyfish import levenshtein_distance
from colorutils import *

TEXT_LENGTH = 8
WIDTH = 600
HEIGHT = 200
FONT_SIZE = 64
READER = easyocr.Reader(['en'])


class Captcha:
    def __init__(self, text, txt_color, bg_color, font, path):
        self.text = text
        self.txt_color = txt_color
        self.bg_color = bg_color
        self.font = font
        self.path = path
        self.value_easyocr = -1
        self.value_tesseract = -1


def initialise(number, _colors, _fonts):
    captchas = []
    for i in range(number):
        bg_color = random.choice(_colors)
        txt_color = random.choice(_colors)
        while bg_color == txt_color:
            txt_color = random.choice(_colors)
        font = random.choice(_fonts)
        text = get_random_string(TEXT_LENGTH)
        path = "./Image/" + "_".join([text, txt_color, bg_color, font])
        get_new_captcha(path, text=text, color=txt_color, background=bg_color, font=font, width=WIDTH, height=HEIGHT,
                        font_size=FONT_SIZE)
        captchas.append(Captcha(text, txt_color, bg_color, font, path))
    return captchas


def evaluate(captchas):
    for captcha in captchas:
        if captcha.value_easyocr == -1 or captcha.value_tesseract == -1:
            tesseract_string = get_string_ocr_pytesseract(captcha.path)
            easyocr_string = get_string_ocr_easyocr(captcha.path, READER)
            captcha.value_tesseract = levenshtein_distance(tesseract_string, captcha.text)
            captcha.value_easyocr = levenshtein_distance(easyocr_string, captcha.text)


def cross_text(text_1: string, text_2: string) -> string:
    """
    Cross 2 text from their used characters
    :param text_1: Text of the 1st captcha
    :param text_2: Text of the 2nd captcha
    :return: Random text with allowed characters from text_1 & text_2
    """
    union_chars = list(set(text_1).union(set(text_2)))
    return mutate_text(get_random_string(TEXT_LENGTH, union_chars))


def mutate_text(text: string) -> string:
    """
    Mutate a random single character of text by replacing it by one that doesn't exists in this string
    Idea of improvement : Add the union character set of the two parents as argument, and generates a random character that doesn't appear in this union
    :param text: Texte to mutate
    :return: Maybe a mutated text (1/10 chance)
    """
    if random.randint(1, 10) == 1:
        position = random.randint(0, len(text) - 1)
        all_characters = string.ascii_letters + string.digits
        allowed_characters = list(set(all_characters).difference(set(text)))
        # Turn string to list of char because strings are immutable
        text_characters = list(text)
        text_characters[position] = random.choice(allowed_characters)
        text = "".join(text_characters)
    return text


def cross_color(color_1_hex: string, color_2_hex: string) -> string:
    """ Cross colors by making the average of rgb values
    :param color_2_hex: First color in hexadecimal string
    :param color_1_hex: Second color in hexadecimal string
    :return: Average color in hexadecimal string
    """
    r1, g1, b1 = hex_to_rgb(color_1_hex)
    r2, g2, b2 = hex_to_rgb(color_2_hex)
    rf = (r1 + r2) / 2
    gf = (g1 + g2) / 2
    bf = (b1 + b2) / 2
    result_hex = rgb_to_hex((rf, gf, bf))
    return mutate_color(result_hex)


def mutate_color(color_hex: string) -> string:
    """
    Mutate the color
    1/10 chance to mutate the color
    Offset of 20 for each element
    :param color_hex: color to mutate in hexadecimal string
    :return: mutated color in hexadecimal string
    """
    if random.randint(1, 10) == 1:
        tuple_rgb = hex_to_rgb(color_hex)
        for v in tuple_rgb:
            v = v + random.randint(-10, 10)
            if v < 0:
                v = 0
            if v > 255:
                v = 255
        color_hex = rgb_to_hex(tuple_rgb)
    return color_hex


def crossover(captcha_1: Captcha, captcha_2: Captcha) -> Captcha:
    """
    Cross 2 captcha attributes to create a new one
    :param captcha_1: First parent captcha
    :param captcha_2: Second parent captcha
    :return: Son captcha OR nothing if bg_color = txt_color
    """
    text = cross_text(captcha_1.text, captcha_2.text)
    txt_color = cross_color(captcha_1.txt_color, captcha_2.txt_color)
    bg_color = cross_color(captcha_1.bg_color, captcha_2.bg_color)
    font = random.choice([captcha_1.font, captcha_2.font])
    path = "./Image/Crossed/" + "_".join([text, txt_color, bg_color, font])
    get_new_captcha(path, text=text, color=txt_color, background=bg_color, font=font, width=WIDTH, height=HEIGHT,
                    font_size=FONT_SIZE)
    print('''\
          Crossed from : 
          Text1 :  {text1}
          Text2 : {text2}\
          '''.format(text1=captcha_1.text, text2=captcha_2.text))


if __name__ == "__main__":
    number_captchas = 100
    colors = ["#000000", "#808080", "#FFFFFF", "#8B4513", "#FF0000", "#ffa500", "#ffff00", "#008000", "#00ffff",
              "#0000ff", "#800080", "#ff1493"]
    fonts = get_available_fonts()
    population = initialise(number_captchas, colors, fonts)
    # evaluate(captchas)
    for i in range(0, number_captchas, 2):
        crossover(population[i], population[i + 1])
