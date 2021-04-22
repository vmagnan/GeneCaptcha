// Doc : https://github.com/produck/svg-captcha

const { request, json } = require('express')
const express = require('express')
const app = express()
var svgCaptcha = require('svg-captcha');

function generateCaptcha(text, bg_color) {
    var options = {
    width: 600,
    height: 200,
    noise: 0,
    color: false,
    inverse: false,
    ignoreChars: '',
    fontSize: 128,
    charPreset: '',
    };
    if(arguments.length == 2)
        options.background = bg_color;
    var captcha = svgCaptcha(text, options);
    console.log(captcha);
    return captcha;
}
app.get('/captcha/:text', (req,res) => {
    const text = req.params.text;
    const captcha = generateCaptcha(text);
    return res.status(200).json(captcha)
})
app.get('/captcha/:text/:color', (req,res) => {
    const text = req.params.text;
    const color = req.params.color;
    const captcha = generateCaptcha(text,color);
    return res.status(200).json(captcha)
})
app.listen(8080, () => {
    console.log('Serveur de génération de captcha à l\'écoute');
    console.log('Exemple de requête : http://localhost:8080/captcha/texte/couleur');
  })