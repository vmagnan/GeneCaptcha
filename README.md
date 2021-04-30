# GeneCaptcha

**Objectif :** Trouver les paramètres optimaux empêchant les OCR de résoudre le texte inclut dans des captchas.

## Installation

Cloner le repo : `git clone https://github.com/valm13/GeneCaptcha.git`

### Serveur de captchas

* Installer nodeJS et npm : <https://nodejs.org/en/download/>
* Aller dans le répertoire : captcha-generators\svg_captcha et exécuter : `npm install package.json`

### Pour faire fonctionner le programme python

* Nécessite python 3.6+ : <https://www.python.org/downloads/>
* Installer les dépendances avec pip : `pip install pytesseract, CairoSVG, Pillow, easyocr`
* Installer Tesseract : <https://tesseract-ocr.github.io/tessdoc/Installation.html>
* Installer CairoSVG : <https://cairosvg.org/documentation/#installation>
* Verifier que pytesseract soit bien dans le PATH.
