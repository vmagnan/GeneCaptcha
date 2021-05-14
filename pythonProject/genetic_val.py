from toolbox import *
from jellyfish import levenshtein_distance


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
    width = 600
    height = 200
    font_size = 64
    captchas = []
    for i in range(number):
        bg_color = random.choice(_colors)
        txt_color = random.choice(_colors)
        while bg_color == txt_color:
            txt_color = random.choice(_colors)
        font = random.choice(_fonts)
        text = get_random_string(8)
        path = "./Image/" + "_".join([text, txt_color, bg_color, font])
        get_new_captcha(path, text=text, color=txt_color, background=bg_color, font=font, width=width, height=height,
                        font_size=font_size)
        captchas.append(Captcha(text, txt_color, bg_color, font, path))
    return captchas


def evaluate(captchas):
    for captcha in captchas:
        tesseract_string = get_string_ocr_pytesseract(captcha.path)
        easyocr_string = get_string_ocr_easyocr(captcha.path)
        captcha.value_tesseract = levenshtein_distance(tesseract_string, captcha.text)
        captcha.value_easyocr = levenshtein_distance(easyocr_string, captcha.text)


# def mutate:
def func():
    svg_code = """
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12" y2="16"/>
            </svg>
        """
    cairosvg.svg2png(bytestring=svg_code, write_to='Image/output.png')


if __name__ == "__main__":
    number_captchas = 10
    colors = ["black", "grey", "white", "brown", "red", "orange", "yellow", "green", "cyan", "blue", "purple", "pink"]
    fonts = get_available_fonts()
    # initialise(number_captchas, colors, fonts)
    # evaluate(captchas)
    func()
    print("coucou")
