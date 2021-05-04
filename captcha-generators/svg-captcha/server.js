// Doc : https://github.com/produck/svg-captcha
const { request, json } = require('express')
const express = require('express')
const app = express()
const path = require("path")
const fs = require("fs")
var svgCaptcha = require('svg-captcha');
function generateCaptcha(params) {
    var options = {
        width: 600,
        height: 200,
        noise: 0,
        color: 'black',
        background: 'white',
        inverse: false,
        ignoreChars: '',
        fontSize: 128,
        charPreset: '',
    };
    if (params === undefined)
        return undefined;
    if (params.text === undefined)
        return undefined;
    if (params.color != undefined)
        options.color = params.color;
    if (params.background != undefined)
        options.background = params.background;
    if (params.width != undefined)
        options.width = params.width;
    if (params.height != undefined)
        options.height = params.height;
    if (params.font != undefined)
        svgCaptcha.loadFont("./fonts/" + params.font);
    if (params.font_size != undefined)
        options.fontSize = params.font_size;
    if (params.noise != undefined)
        options.noise = params.noise;
    return svgCaptcha(params.text, options);
}
app.get('/captcha', (req, res) => {
    const text = req.query.text;
    const color = req.query.color;
    const background = req.query.background;
    const font = req.query.font;
    const width = req.query.width;
    const height = req.query.height;
    const font_size = req.query.font_size;
    const noise = req.query.noise;
    // console.log("text ="+text+"|color = "+color+"|font= "+font+"|width= "+width+"|height= "+height);
    var captcha = generateCaptcha({ text: text, color: color, background:background, font: font, width: width, height: height, font_size: font_size, noise: noise });
    if (captcha === undefined)
        return res.status(500).json({
            error: 'Requête mal formatée, le champ text n\'est pas présent.',
            example_url: 'Veuillez utiliser des paramètres de la forme text=blabla&color=blue&background=green&font=comic-sans-ms.ttf&width=800&height=400&font_size=100&noise=1'
        });
    return res.status(200).json(captcha)
})
app.get('/fonts', (req, res) => {
    const directoryPath = path.join('./fonts')
    let fonts = ""
    fs.readdir(directoryPath, function (err, files) {
        if (err) {
            console.log("Error getting directory information.")
            return res.status(404).json({})
        } else {
            files.forEach(function (file) {
                fonts += file + "/"
            })
            fonts = fonts.slice(0, -1)
            return res.status(200).json(fonts)
        }
    })
})
app.listen(8080, () => {
    console.log('Serveur de génération de captcha à l\'écoute');
    console.log('Exemple de requête : http://localhost:8080/captcha?text=blabla&color=blue&font=comicsansms.ttf&width=800&height=400&font_size=100&noise=1');
    console.log('Seul le paramètre text est obligatoire, les autres sont optionnels. Pour la couleur, c\'est soit en hexa, soit les noms anglais');
})