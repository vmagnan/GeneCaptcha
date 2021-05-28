from colorutils import *
from jellyfish import levenshtein_distance
import time
from toolbox import *

TEXT_LENGTH = 8
WIDTH = 600
HEIGHT = 200
FONT_SIZE = 64
READER = easyocr.Reader(['en'])
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
            path = captcha.path + '.png'
            text = captcha.text
            tesseract_string = get_string_ocr_pytesseract(path)
            easyocr_string = get_string_ocr_easyocr(path, READER)
            captcha.value_tesseract = levenshtein_distance(tesseract_string, text)
            captcha.value_easyocr = levenshtein_distance(easyocr_string, text)


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


def cross_2_captcha(captcha_1: Captcha, captcha_2: Captcha) -> Captcha:
    """
    Cross 2 captcha attributes to create a new one
    :param captcha_1: First parent captcha
    :param captcha_2: Second parent captcha
    :return: Son captcha
    """
    text = cross_text(captcha_1.text, captcha_2.text)
    txt_color = cross_color(captcha_1.txt_color, captcha_2.txt_color)
    bg_color = cross_color(captcha_1.bg_color, captcha_2.bg_color)
    font = random.choice([captcha_1.font, captcha_2.font])
    path = "./Image/Crossed/" + "_".join([text, txt_color, bg_color, font])
    get_new_captcha(path, text=text, color=txt_color, background=bg_color, font=font, width=WIDTH, height=HEIGHT,
                    font_size=FONT_SIZE)
    captcha = Captcha(text, txt_color, bg_color, font, path)
    return captcha


def crossover(captchas: list[Captcha]) -> list[Captcha]:
    """
    Suffle the list, cross the two last captchas, add the parents and the son to the new list
    For each available couple : select 2 random captchas from the list, cross them and add the three captchas to the return list
    And then remove the 2 parents from the initial list
    :param captchas:
    :return:
    """
    if not captchas:
        print("crossover : Population passed is empty")
        return []
    new_population = []
    while len(captchas) >= 2 and len(new_population) < POPULATION_SIZE:
        # print(len(captchas))
        random.shuffle(captchas)
        parent_1 = captchas.pop()
        parent_2 = captchas.pop()
        son = cross_2_captcha(parent_1, parent_2)
        new_population.append(parent_1)
        new_population.append(parent_2)
        new_population.append(son)
    if len(captchas) == 1 and len(new_population) < POPULATION_SIZE:
        new_population.append(captchas.pop())
    return new_population


def selection(captchas):
    """
    Select all captcha with a levenshtein distance > THRESHOLD & with a different text color from its background
    :param captchas: List of captchas to select
    :return: List of selected captchas
    """
    selected_captchas = []
    for captcha in captchas:
        if captcha.value_easyocr > THRESHOLD:
            if captcha.txt_color != captcha.bg_color:
                selected_captchas.append(captcha)
    return selected_captchas


def is_population_optimized(captchas):
    if len(captchas) < POPULATION_SIZE:
        return False
    for captcha in captchas:
        if captcha.value_easyocr < THRESHOLD:
            return False
    return True


def save_optimized_population(captchas, path):
    for c in captchas:
        c.path = path + "_".join([c.text, c.txt_color, c.bg_color, c.font])
        get_new_captcha(c.path, text=c.text, color=c.txt_color, background=c.bg_color, font=c.font, width=WIDTH,
                        height=HEIGHT,
                        font_size=FONT_SIZE)


if __name__ == "__main__":
    starting_time = time.time()
    colors = ["#000000", "#808080", "#FFFFFF", "#8B4513", "#FF0000", "#ffa500", "#ffff00", "#008000", "#00ffff",
              "#0000ff", "#800080", "#ff1493"]
    fonts = get_available_fonts()
    population = initialise(POPULATION_SIZE, colors, fonts)
    evaluate(population)
    iterations = 0
    while not is_population_optimized(population):
        print("Iteration = {iter}".format(iter=iterations))
        selected_population = selection(population)
        print("{nb} Selected captcha".format(nb=len(selected_population)))
        if len(selected_population) > 1:
            crossed_population = crossover(selected_population)
        else:
            crossed_population = initialise(POPULATION_SIZE, colors, fonts)
        evaluate(crossed_population)
        population = crossed_population
        iterations += 1


    print("""\
    Optimization of the population :
    Iteration required = {iter}
    Time required = {time} seconds
    """.format(iter=iterations, time=time.time() - starting_time))
    save_optimized_population(crossed_population, "Image/Optimized/1/")
