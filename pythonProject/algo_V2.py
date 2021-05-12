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


def init_image(liste_color, liste_font):
    os.system('rm ./Image/test/*')
    for i in range(5):
        color = random.choice(liste_color)
        font = random.choice(liste_font)
        text = newString()
        path = "./Image/test/"+text+"_"+color+"_"+font[:-4]
        print(path)
        get_new_captcha(path, text=text, color=color, font=font)


def levenshtein(string_image, string_OCR, data_list):#marche ausssi avec len(image_text) - nbLettreJuste mais comme ca on peut modifier le score plus facilement
    print("levensthein")
    global data
    score = 0
    orginal_length = len(string_image)
    OCR_length = len(string_OCR)
    score += abs(orginal_length-OCR_length)

    image_text = list(string_image[0])
    OCR_text = list(string_OCR)
    same_letter = 0
    while len(OCR_text) != 0:
        cpt = 0
        while cpt < len(image_text):
            if OCR_text[0] == image_text[cpt]:
                coord = find_letter(OCR_text[0], image_text[cpt], data_list)
                inc(coord, data_list)
                image_text.pop(cpt)
                cpt = len(image_text)
                same_letter += 1
                print(string_image)
                print("imag_text, string_image = ", image_text, string_image)
                data[OCR_text[0]][string_image[2]][string_image[1]] += 1
            else:
                cpt += 1
            if cpt == len(image_text):
                OCR_text.pop(0)

    score += (len(list(string_OCR)) - same_letter)
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

# def calculBestRapport(liste_color, liste_font, json_data):
#   bestRapport = 1
#   for color in liste_color:
#       for font in liste_font:
#           rapport = rapportcolorfont(color, font, json_data)
#           print(rapport)
#           if rapport < bestRapport:
#               bestRapport = rapport
#   return bestRapport

def selection(result_list):
    print("selection")
    liste = []
    for i in result_list:
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
            print(liste)
            if liste != []:
                print("Image = " + str(files[i][:-4]))
                print("Algo = " + str(liste[1]))
                print(files_list[i])
                files_list[i].append(levenshtein(files_list[i], liste[1], data_list)) #compare(fichier[:-4], liste[1], data_list, result_list)
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

def mutation(liste_color, liste_font,files_list):
    print("mutation")
    print(files_list)
    liste = ["color", "lettre", "font"]
    choice = 'lettre' #random.choice(liste)
    if choice == "color":
        print("color")
        os.system('rm ./Image/test/*')
        for i in range(len(files_list)):
            print("new captcha")
            color = random.choice(liste_color)
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
            font = random.choice(liste_font)
            path = "./Image/test/"+files_list[i][0]+"_"+files_list[i][1]+"_"+font
            print(path)
            get_new_captcha(path, text=files_list[i][0], color=files_list[i][1], font=font)




def easyOCR(file_path):
    reader = easyocr.Reader(['en']) # need to run only once to load model into memory
    result = reader.readtext(file_path)
    liste = [x for elem in result for x in elem]
    return liste

def print_tab(data_list):
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

# def compare(textOriginal, textAlgo, data_list, result_list): #prend en argument le text original de la photo et celui que l'algo a retourné
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
#               coord = find_letter(algo[cpt], original[cpt2], data_list)
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
#               coord = find_letter(algo[cpt], original[cpt2], data_list)
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
#   result_list[textOriginal] = score
#   print("Nombre de lettre similaires = " + str(nbLettreSimilaire))
#   print("Nombre de lettres qui se ressemblent = " + str(lettreRessemblante))
#   print_color(score)
#   return result_list

# def print_color(score):
#     val = score
#     if val <= 35:
#         print(bcolors.RED + str(val) + "%"+" de reussite" + bcolors.RESET)
#     elif val > 35 and val <= 70:
#         print(bcolors.YELLOW + str(val) + "%"+" de reussite" + bcolors.RESET)
#     else:
#         print(bcolors.GREEN + str(val) + "%"+" de reussite" + bcolors.RESET)




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

def find_letter(lettreImage, lettreAlgo, CSV_data):
    coord = [0,0]
    for i in CSV_data[0]:
        if i == lettreImage:
            coord[0] = CSV_data[0].index(lettreImage)
    for i in range(len(CSV_data)):
        if CSV_data[i][0] == lettreAlgo:
            coord[1] = i
    return coord

def inc(coord, matrice):
    nb = int(matrice[coord[0]][coord[1]])
    nb += 1
    matrice[coord[0]][coord[1]] = nb

def find_best_score(listeLettres, liste_font,liste_color, data):
    list_score = []
    for letter in data:
        #print(letter, type(letter))
        for font in data[letter]:
            #print(font, type(font))
            for color , value in data[letter][font].items():
                #print(color, value, type(color), type(value))
                if len(list_score) < 10:
                    score = value
                    new_item = [letter, font, color, score]
                    list_score.append(new_item)
                    #print(list_score)
                else:
                    for i in range(len(list_score)):
                        #print(list_score, i)
                        if value > list_score[i][3] and len(list_score[i]) == 4:
                            print("changement de score")
                            print(list_score, letter, font, color, i)
                            list_score[i] = [letter, font, color, value]
                            break
    return list_score

if __name__ == "__main__":
    # Overture du CSV
    csv_file = open('matrice.csv', encoding='ISO-8859-1')
    CSV_data = csv.reader(csv_file, delimiter=';')
    data_list = list(CSV_data)

    #Ouverture du fichier lettre.json
    json_file = open('lettre.json')
    json_data = json.load(json_file)

    liste_font = get_available_fonts()
    #print(json_data)

    result_list = {}
    data = {}

    #Coefficient d'efficacité moyen de chaque font 

    #Coefficient d'efficacité moyen de chaque color
    liste_color = ["red", "blue", "green", "yellow"]#{'Bleu': 1, 'Rouge': 1, 'Jaune': 1, 'Vert': 1} 

    #Coefficient d'efficacité moyen de chaque lettre
    listeLettres = ['a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'm', 'l', 'k', 'j', 'h', 'g', 'f', 'd', 's', 'q', 'w', 'x', 'c', 'v', 'b', 'n', 'A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'M', 'L', 'K', 'J', 'H', 'G', 'F', 'D', 'S', 'Q', 'W', 'X', 'C', 'V', 'B', 'N', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


    for letter in listeLettres:
        font_data = {}
        for font in liste_font:
            font = font[:-4]
            color_data = {}
            for color in liste_color:
                color_data[color] = 0
            font_data[font] = color_data
        data[letter] = font_data
    print(len(data))

    
    #print(json.dumps(data, indent=4))


    compteur = 0
    init_image(liste_color, liste_font)
    #print(calculBestRapport(liste_color, liste_font, json_data))
    while compteur < 4: #Condition d'arret de l'algo
        print("\n\n\n\n\n tour numero "+str(compteur)+"\n\n\n\n\n")
        listeFichiers = evaluation(data_list, data)
        print("liste resultat = " + str(listeFichiers))
        listeFichiers = selection(listeFichiers)
        sorted(result_list.items(), key=lambda t: t[1])
        print("liste resultat apres selection = " + str(listeFichiers))
        #print(find_best_score(listeLettres, liste_font, liste_color, data))
        mutation(liste_color, liste_font, listeFichiers)
        for root, dirs, files in os.walk("./Image/test/"):
            print("liste des fichier apres mutation ", files)
        compteur += 1
        #find_best_score(listeLettres, liste_font, liste_color)
        # print(json.dumps(data, indent=4))
        # print_tab(data_list)
    print(json.dumps(data, indent=4))
    print_tab(data_list)
    print(result_list)
    print(find_best_score(listeLettres, liste_font, liste_color, data))