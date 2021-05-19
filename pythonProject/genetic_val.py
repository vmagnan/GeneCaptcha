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
        self.value_easyocr = 0
        self.value_tesseract = 0


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
    return get_random_string(TEXT_LENGTH, union_chars)


def cross_color(color_1_hex: string, color_2_hex: string) -> string:
    """ Cross colors by making the average of rgb values
    :param color_2_hex: First color in hexadecimal
    :param color_1_hex: Second color in hexadecimal
    :return: Average color in hexadecimal
    """
    r1, g1, b1 = hex_to_rgb(color_1_hex)
    r2, g2, b2 = hex_to_rgb(color_2_hex)

    rf = (r1 + r2) / 2
    gf = (g1 + g2) / 2
    bf = (b1 + b2) / 2
    result_hex = rgb_to_hex((rf, gf, bf))
    return result_hex


def crossover(captcha_1: Captcha, captcha_2: Captcha) -> Captcha:
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


# def mutate:


if __name__ == "__main__":
    number_captchas = 10
    colors = ["#000000", "#808080", "#FFFFFF", "#8B4513", "#FF0000", "#ffa500", "#ffff00", "#008000", "#00ffff",
              "#0000ff", "#800080", "#ff1493"]
    fonts = get_available_fonts()
    population = initialise(number_captchas, colors, fonts)
    # evaluate(captchas)
    for i in range(0, number_captchas, 2):
        crossover(population[i], population[i + 1])
    colorutils
