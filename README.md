# GeneCaptcha

**Purpose :** Find optimal image's parameters to prevent OCR to solve the text of a captcha.

## Installation

Clone the repo : `git clone https://github.com/valm13/GeneCaptcha.git`

### Captcha's generator server

* Install nodeJS and npm : <https://nodejs.org/en/download/>
* Go to : captcha-generators/svg_captcha and execute : `npm install package.json`
* Then, move the file from captcha-generators/svg_captcha/index.js to captcha-generators/svg_captcha/node_modules/svg-captcha/index.js
* That's it !!!

### Python program

* Require python 3.6+ : <https://www.python.org/downloads/>
* Install the following dependancies with pip : `pip install pytesseract, CairoSVG, Pillow, easyocr`
* Install Tesseract : <https://tesseract-ocr.github.io/tessdoc/Installation.html>
* Install CairoSVG : <https://cairosvg.org/documentation/#installation>
* Verify that your PATH include pytesseract.
