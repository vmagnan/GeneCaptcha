# Commande à utiliser:
# python3 algo.py NomImage.png
# /!\ L'image doit être au format ".png" /!\

import easyocr
import sys
from toolbox import get_paths_files_with_extension_from_folder


def compareLettre(lettre, tab):
    for k in range(len(tab)):
        if lettre == tab[k]:
            # print(lettre + " ressemble")
            return True


def checkLettre(lettreAlgo, lettreImage):
    switcher = {
        "m": compareLettre(lettreImage, ['M', 'n', 'N']),
        "u": compareLettre(lettreImage, ['U']),
        "U": compareLettre(lettreImage, ['u']),
        "i": compareLettre(lettreImage, ['I', 'l']),
        "w": compareLettre(lettreImage, ['W']),
        "B": compareLettre(lettreImage, ['S', 's']),
        "W": compareLettre(lettreImage, ['w'])
    }
    return switcher.get(lettreAlgo, False)


def compare(texteOriginal, texteAlgo):  # prend en argument le texte original de la photo et celui que l'algo a retourné
    coeffLong = 0  # coefficient de variation de la longueur
    nbLettreSimilaire = 0  # nombre de lettre similaire entre le texte original et celui trouvé par l'algo
    lettreRessemblante = 0  # nombre de lettre qui se ressemblent
    original = list(texteOriginal)
    algo = list(texteAlgo)

    longueurOriginalInitiale = len(original)
    longueurAlgoInitiale = len(algo)

    cpt = 0

    longueurAlgo = len(algo)
    longueurOriginal = len(original)

    while cpt < longueurAlgo:  # parcourt le texte retourné par l'algorithme
        cpt2 = 0
        while cpt2 < longueurOriginal:  # parcourt le texte original qui apparait sur l'image
            # verifie si la lettre de l'algo et celle de l'image sont les mêmes
            if algo[cpt] == original[cpt2]:
                print("les lettres sont similaires : " + algo[cpt])
                nbLettreSimilaire += 1
                # Retire les lettres des listes de caractère dans le cas où elles sont similaire
                algo.pop(cpt)
                original.pop(cpt2)
                longueurAlgo -= 1
                longueurOriginal -= 1
                cpt2 = longueurOriginal
            # verifie si la lettre de l'algo et celle de l'image se ressemblent
            elif checkLettre(algo[cpt], original[cpt2]):
                print(algo[cpt] + " ressemble à " + original[cpt2])
                lettreRessemblante += 1
                algo.pop(cpt)
                original.pop(cpt2)
                longueurAlgo -= 1
                longueurOriginal -= 1
                cpt2 = longueurOriginal
            else:
                cpt2 += 1
                if cpt2 >= longueurOriginal:
                    cpt += 1

    print("Nombre de lettres similaires = {nb}".format(nb=nbLettreSimilaire))
    print("Nombre de lettres qui se ressemblent = {nb}".format(nb=lettreRessemblante))
    print("{pourcentage}% de réussite".format(pourcentage=nbLettreSimilaire / longueurOriginalInitiale * 100))


if __name__ == "__main__":
    # Initialisation
    reader = easyocr.Reader(['en'])  # need to run only once to load model into memory
    paths = get_paths_files_with_extension_from_folder('../Images/SVG', 'png')
    for path in paths:
        result = reader.readtext(path)
        liste = [x for elem in result for x in elem]
        # Extract name of file
        path_array=path.split('/')
        filename = path_array[-1:][0].replace('.png', '') # Last value of path_array(output is a 1 value array)
        str = """\
                ------------------------------------------------------------------------------------------------------------------
                Path = {path}
                Texte de l'image = {text}
                """.format(path=path, text=filename)
        if len(result) > 0:
            str += "Resultat d'EasyOCR = {result}".format(result=liste)
            if liste[1] == filename:
                str += "Its a Match !!!"
        else:
            str += "Resultat d'EasyOCR = None"
        print(str)
        if len(result) > 0:
            compare(liste[1], filename)

# def evaluation():

# def selection():

# def mutation():
