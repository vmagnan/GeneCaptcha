# Commande à utiliser:
# python3 algo.py NomImage.png
# /!\ L'image doit être au format ".png" /!\



import json
import easyocr
import sys
import csv
import random
from random import randint
from os import walk
import cairosvg
import os
from glob import glob
import requests
import time
import urllib
from toolbox import *

class bcolors:
    GREEN = '\033[92m' #GREEN
    YELLOW = '\033[93m' #YELLOW
    RED = '\033[91m' #RED
    BLUE = '\033[96m' #BLUE
    RESET = '\033[0m' #RESET COLOR

data = {}


def init_image(listecolor, listefont):
    os.system('rm ./Image/test/*')
    for i in range(5):
        color = random.choice(listecolor)
        font = random.choice(listefont)
        text = newString()
        path = "./Image/test/"+text+"_"+color+"_"+font[:-4]
        print(path)
        get_new_captcha(path, text=text, color=color, font=font)


def levenshtein(stringImage, stringOCR, data_list):#marche ausssi avec len(image_text) - nbLettreJuste mais comme ca on peut modifier le score plus facilement
    print("levensthein")
    global data
    score = 0
    orginal_length = len(stringImage)
    OCR_length = len(stringOCR)
    score += abs(orginal_length-OCR_length)

    image_text = list(stringImage[0])
    OCR_text = list(stringOCR)
    same_letter = 0
    while len(OCR_text) != 0:
        cpt = 0
        while cpt < len(image_text):
            if OCR_text[0] == image_text[cpt]:
                coord = findLettre(OCR_text[0], image_text[cpt], data_list)
                inc(coord, data_list)
                image_text.pop(cpt)
                cpt = len(image_text)
                same_letter += 1
                print(stringImage)
                data[image_text[0]][stringImage[2]][stringImage[1]] += 17000000
            else:
                cpt += 1
            if cpt == len(image_text):
                OCR_text.pop(0)

    score += (len(list(stringOCR)) - same_letter)
    print("score", score)
    return score

# def moyennecolor(color, json_data):
#   cptcolor = 0
#   cpt = 0
#   for lettre, valeur in json_data.items():
#       for elem, font in valeur.items():
#           for color, score in font.items():
#               if color == color:
#                   cptcolor += score
#                   cpt += 1
#   return cptcolor/cpt

# def rapportcolorfont(color, font, json_data):
#   cptcolor = 0
#   cpt = 0
#   for lettre, valeur in json_data.items():
#       for font, elem in valeur.items():
#           for color, score in elem.items():
#               if color == color and font == font:
#                   cptcolor += score
#                   cpt += 1
#   return cptcolor/cpt

# def calculBestRapport(listecolor, listefont, json_data):
#   bestRapport = 1
#   for color in listecolor:
#       for font in listefont:
#           rapport = rapportcolorfont(color, font, json_data)
#           print(rapport)
#           if rapport < bestRapport:
#               bestRapport = rapport
#   return bestRapport

def selection(listeResultat):
    print("selection")
    liste = []
    for i in listeResultat:
        if i[3] >= 5 and len(i) == 4:
            liste.append(i)
    return liste

def evaluation(data_list, data):
    print("evaluation")
    files_list = []
    for root, dirs, files in os.walk("./Image/test/"):
        print(files)
        for i in range(len(files)):
            files_list.append(files[i][:-4].split("_"))
            print(files_list)
            file_path =  "./Image/test/" + files[i]
            liste = easyOCR(file_path)
            if liste != []:
                print("Image = " + str(files[i][:-4]))
                print("Algo = " + str(liste[1]))
                print(files_list[i])
                files_list[i].append(levenshtein(files_list[i], liste[1], data_list)) #compare(fichier[:-4], liste[1], data_list, listeResultat)
            else:
                print("Fichier non reconnu par EasyOCR !")
    print(files_list)
    return files_list

# def createRandomListe(listeInitiale):
#   listeFinale = []
#   liste = []
#   for elem, proba in listeInitiale.items():
#       for i in range(proba):
#           liste.append(elem)
#   print(liste)
#   for i in range(10):
#       listeFinale.append(random.choice(liste))
#   print(listeFinale)


def newString():
    string = ""
    letter_list = ['a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'm', 'l', 'k', 'j', 'h', 'g', 'f', 'd', 's', 'q', 'w', 'x', 'c', 'v', 'b', 'n', 'A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'M', 'L', 'K', 'J', 'H', 'G', 'F', 'D', 'S', 'Q', 'W', 'X', 'C', 'V', 'B', 'N', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    for i in range(10):
        string += random.choice(letter_list)
    return string

def modify_string(string):
    print("modify_string")
    string_list = list(string)
    new_string = ""
    letter_list = ['a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'm', 'l', 'k', 'j', 'h', 'g', 'f', 'd', 's', 'q', 'w', 'x', 'c', 'v', 'b', 'n', 'A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'M', 'L', 'K', 'J', 'H', 'G', 'F', 'D', 'S', 'Q', 'W', 'X', 'C', 'V', 'B', 'N', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    for i in range(randint(1,3)):
        lettre = random.choice(letter_list)
        nb = randint(0,9)
        print(string_list[nb])
        string_list[nb] = lettre
    for i in range(len(string_list)):
        new_string += string_list[i]
    return new_string

# def getDataName(fileName):
#   data = fileName.split("_")
#   data[-1] = data[-1][:-4]    
#   return data

def mutation(listecolor, listefont,files_list):
    print("mutation")
    print(files_list)
    liste = ["color", "lettre", "font"]
    choice = 'lettre' #random.choice(liste)
    if choice == "color":
        print("color")
        os.system('rm ./Image/test/*')
        for i in range(len(files_list)):
            print("new captcha")
            color = random.choice(listecolor)
            path = "./Image/test/"+files_list[i][0]+"_"+color+"_"+files_list[i][2]
            print(path)
            get_new_captcha(path, text=files_list[i][0], color=color, font=files_list[i][2]+".ttf")
    elif choice == "lettre":
        print("lettre")
        os.system('rm ./Image/test/*')
        print(files_list)
        for i in range(len(files_list)):
            print("new captcha")
            text = modify_string(files_list[i][0])
            print(files_list[i][2])
            path = "./Image/test/"+text+"_"+files_list[i][1]+"_"+files_list[i][2]
            print(path)
            get_new_captcha(path, text=text, color=files_list[i][1], font=files_list[i][2]+".ttf")
    elif choice == "font":
        print("lettre")
        os.system('rm ./Image/test/*')
        print(files_list)
        for i in range(len(files_list)):
            print("new captcha")
            font = random.choice(listefont)
            path = "./Image/test/"+files_list[i][0]+"_"+files_list[i][1]+"_"+font
            print(path)
            get_new_captcha(path, text=files_list[i][0], color=files_list[i][1], font=font)




def easyOCR(file_path):
    reader = easyocr.Reader(['en']) # need to run only once to load model into memory
    result = reader.readtext(file_path)
    liste = [x for elem in result for x in elem]
    return liste

def printTab(data_list):
    for line in data_list:
        string = ""
        for elem in line:
            if elem == "ï»¿":
                string += " |"
            else:
                if elem != "0":
                    string += bcolors.BLUE + str(elem) + bcolors.RESET + "|"
                else:
                    string += str(elem) + "|"
        print(string)

# def compare(textOriginal, textAlgo, data_list, listeResultat): #prend en argument le text original de la photo et celui que l'algo a retourné
#   coeffLong = 0 #coefficient de variation de la longueur
#   nbLettreSimilaire = 0 #nombre de lettre similaire entre le text original et celui trouvé par l'algo
#   lettreRessemblante = 0 #nombre de lettre qui se ressemblent
#   original = list(textOriginal)
#   algo = list(textAlgo)

#   orginal_lengthInitiale = len(original)
#   longueurAlgoInitiale = len(algo)

#   cpt = 0

#   longueurAlgo = len(algo)
#   orginal_length = len(original)

#   while cpt < longueurAlgo: #parcourt le text retourné par l'algorithme
#       cpt2 = 0
#       while cpt2 < orginal_length: #parcourt le text original qui apparait sur l'image
#           # verifie si la lettre de l'algo et celle de l'image sont les mêmes
#           if algo[cpt] == original[cpt2]:
#               coord = findLettre(algo[cpt], original[cpt2], data_list)
#               inc(coord, data_list)
#               print("les lettre sont similaires : " + algo[cpt])
#               nbLettreSimilaire +=1
#               #Retire les lettres des listes de caractère dans le cas où elles sont similaire
#               algo.pop(cpt)
#               original.pop(cpt2)
#               longueurAlgo -= 1
#               orginal_length -= 1
#               cpt2 = orginal_length
#           # verifie si la lettre de l'algo et celle de l'image se ressemblent
#           elif checkLettre(algo[cpt], original[cpt2]):
#               coord = findLettre(algo[cpt], original[cpt2], data_list)
#               inc(coord, data_list)
#               print(algo[cpt] + " ressemble à " + original[cpt2])
#               lettreRessemblante += 1
#               algo.pop(cpt)
#               original.pop(cpt2)
#               longueurAlgo -= 1
#               orginal_length -= 1
#               cpt2 = orginal_length
#           else:
#               cpt2 += 1
#               if cpt2 >= orginal_length:
#                   cpt += 1

#   score = (nbLettreSimilaire + (lettreRessemblante/2))/orginal_lengthInitiale*100
#   listeResultat[textOriginal] = score
#   print("Nombre de lettre similaires = " + str(nbLettreSimilaire))
#   print("Nombre de lettres qui se ressemblent = " + str(lettreRessemblante))
#   printColor(score)
#   return listeResultat

def printColor(score):
    val = score
    if val <= 35:
        print(bcolors.RED + str(val) + "%"+" de reussite" + bcolors.RESET)
    elif val > 35 and val <= 70:
        print(bcolors.YELLOW + str(val) + "%"+" de reussite" + bcolors.RESET)
    else:
        print(bcolors.GREEN + str(val) + "%"+" de reussite" + bcolors.RESET)




# def checkLettre(lettreAlgo, lettreImage):
#   switcher = {
#       "m": compareLettre(lettreImage, ['M','n','N']),
#       "u": compareLettre(lettreImage, ['U','v','V']),
#       "U": compareLettre(lettreImage, ['u','v','V']),
#       "i": compareLettre(lettreImage, ['I','l']),
#       "w": compareLettre(lettreImage, ['W']),
#       "B": compareLettre(lettreImage, ['S','s','8']),
#       "z": compareLettre(lettreImage, ['Z']),
#       "Z": compareLettre(lettreImage, ['z']),
#       "p": compareLettre(lettreImage, ['P','F','f']),
#       "P": compareLettre(lettreImage, ['p','F','f']),
#       "f": compareLettre(lettreImage, ['F','p','P']),
#       "F": compareLettre(lettreImage, ['f','p','P']),
#       "k": compareLettre(lettreImage, ['K','x','X']),
#       "K": compareLettre(lettreImage, ['k','x','X']),
#       "x": compareLettre(lettreImage, ['X','K','k']),
#       "X": compareLettre(lettreImage, ['x','K','k']),
#       "c": compareLettre(lettreImage, ['C']),
#       "C": compareLettre(lettreImage, ['c']),
#       "j": compareLettre(lettreImage, ['J']),
#       "J": compareLettre(lettreImage, ['j']),
#       "o": compareLettre(lettreImage, ['O','Q','0']),
#       "O": compareLettre(lettreImage, ['o','Q','0']),
#       "Q": compareLettre(lettreImage, ['o','O','0']),
#       "0": compareLettre(lettreImage, ['o','O','Q']),
#       "v": compareLettre(lettreImage, ['V','u','U']),
#       "V": compareLettre(lettreImage, ['v','u','U']),
#       "S": compareLettre(lettreImage, ['s','5']),
#       "s": compareLettre(lettreImage, ['S','5']),
#       "W": compareLettre(lettreImage, ['w'])
#   }
#   return switcher.get(lettreAlgo,False)

# def compareLettre(lettre, tab):
#   for k in range(len(tab)):
#       if lettre == tab[k]:
#           return True

def findLettre(lettreImage, lettreAlgo, dataCSV):
    coord = [0,0]
    for i in dataCSV[0]:
        if i == lettreImage:
            coord[0] = dataCSV[0].index(lettreImage)
    for i in range(len(dataCSV)):
        if dataCSV[i][0] == lettreAlgo:
            coord[1] = i
    return coord

def inc(coord, matrice):
    nb = int(matrice[coord[0]][coord[1]])
    nb += 1
    matrice[coord[0]][coord[1]] = nb
