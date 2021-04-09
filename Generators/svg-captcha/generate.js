// Doc : https://github.com/produck/svg-captcha
const fs = require('fs')
var svgCaptcha = require('svg-captcha');
var nb = 10

function generateNOfType(number, config) {
    for (let i = 0; i < number; i++) {
        var captcha = svgCaptcha.create(config);
        console.log(captcha.text);
        fs.writeFile('./' + config.size + '/Noise-' + config.noise + '/' + captcha.text + '.svg', captcha.data, (err) => {
            if (err) throw err;
            console.log('./' + config.size + '/Noise-' + config.noise + '/' + captcha.text + '.svg saved');
        });
    }
}

function createDirRecursive(path) {
    fs.mkdir(path, { recursive: true }, (err) => {
        if (err) {
            throw err;
        }
        console.log("Directory " + path + " is created.");
    });
}
var sizes = [20];
var Myoptions = {
    size: 1,
    width: 150,
    height: 50,
    noise: 1,
    color: true,
    background: 'white',
    inverse: false,
    ignoreChars: '',
    fontSize: 56,
    charPreset: '',
};

for (i = 0; i < sizes.length; i++) {
    Myoptions.size = sizes[i];
    for (Myoptions.noise = 1; Myoptions.noise < 6; Myoptions.noise+=2)
        generateNOfType(nb, Myoptions);
  } 
