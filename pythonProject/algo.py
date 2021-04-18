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

    print("Nombre de lettres similaires = " + str(nbLettreSimilaire))
    print("Nombre de lettres qui se ressemblent = " + str(lettreRessemblante))
    print(str(nbLettreSimilaire / longueurOriginalInitiale * 100) + "%" + " de reussite")


if __name__ == "__main__":
    reader = easyocr.Reader(['en'])  # need to run only once to load model into memory
    result = reader.readtext(sys.argv[1])
    liste = [x for elem in result for x in elem]

    print("Image = " + str(sys.argv[1][:-4]))
    print("Algo = " + str(liste[1]))

    texte = list(liste[1])
    compare(sys.argv[1][:-4], texte)

# def evaluation():

# def selection():

# def mutation():
