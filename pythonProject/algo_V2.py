# Commande à utiliser:
# python3 algo.py NomImage.png
# /!\ L'image doit être au format ".png" /!\

import json
import easyocr
import sys
import csv
import random
from os import walk
import cairosvg
import os
from glob import glob
import requests
import time
import urllib
from toolbox import *


class BColors:
    GREEN = '\033[92m'  # GREEN
    YELLOW = '\033[93m'  # YELLOW
    RED = '\033[91m'  # RED
    BLUE = '\033[96m'  # BLUE
    RESET = '\033[0m'  # RESET COLOR


def init_image(colors, fonts):
    for i in range(10):
        color = random.choice(colors)
        font = random.choice(fonts)
        text = new_string()
        path = "./Image/test/" + text + "_" + color + "_" + font[:-4]
        print(path)
        get_new_captcha(path, text=text, color=color, font=font)


def average_color(color, json_data):
    cpt_color = 0
    cpt = 0
    for letter, value in json_data.items():
        for elem, police in value.items():
            for color, score in police.items():
                if color == color:
                    cpt_color += score
                    cpt += 1
    return cpt_color / cpt


def relation_color_font(color, font, json_data):
    cpt_color = 0
    cpt = 0
    for letter, value in json_data.items():
        for police, elem in value.items():
            for color, score in elem.items():
                if color == color and police == font:
                    cpt_color += score
                    cpt += 1
    return cpt_color / cpt


def find_best_relation(colors, fonts, json_data):
    best_relation = 1
    for color in colors:
        for font in fonts:
            relation = relation_color_font(color, font, json_data)
            print(relation)
            if relation < best_relation:
                best_relation = relation
    return best_relation


def selection(results):
    list = {}
    for elem, value in results.items():
        if value <= 25:
            list[elem] = value
    return list


def evaluation(text_captcha, text_ocr):
    for file in files:
        file_path = path + file
        list = easy_ocr(file_path)
        if list != []:
            print("Image = " + str(file[:-4]))
            print("Algo = " + str(list[1]))
            results = compare(file[:-4], list[1], data_array, results)
        else:
            print("Fichier non reconnu par EasyOCR !")

    return results


def create_random_list(initial_list):
    final_list = []
    list = []
    for elem, probability in initial_list.items():
        for i in range(probability):
            list.append(elem)
    print(list)
    for i in range(10):
        final_list.append(random.choice(list))
    print(final_list)


def choice_folder(paths):
    path = random.choice(paths)
    paths.pop(paths.index(path))
    return paths, path


def add_file(files, path):
    for (directory, subdirectories, file) in walk(path):
        files.extend(file)
    return files


def new_string():
    string = ""
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    for i in range(10):
        string += random.choice(letters)
    return string


def get_data_name(filename):
    data = filename.split("_")
    data[-1] = data[-1][:-4]
    return data


def mutation(colors, fonts):
    list = ["color", "lettre", "police"]
    choice = random.choice(list)
    if choice == "color":
        filename = []
        print("color")
        for root, dirs, files in os.walk("./Image/test"):
            for i in files:
                filename.append(i[:-4].split("_"))
        os.system('rm ./Image/test/*')
        for i in range(10):
            color = random.choice(colors)
            path = "./Image/test/" + filename[i][0] + "_" + color + "_" + filename[i][2]
            get_new_captcha(path, text=filename[i][0], color=color, font=filename[i][2])
    elif choice == "lettre":
        filename = []
        print("lettre")
        for root, dirs, files in os.walk("./Image/test"):
            for i in files:
                filename.append(i[:-4].split("_"))
        os.system('rm ./Image/test/*')
        for i in range(10):
            text = new_string()
            path = "./Image/test/" + text + "_" + filename[i][1] + "_" + filename[i][2]
            get_new_captcha(path, text=text, color=filename[i][1], font=filename[i][2])

    elif choice == "police":
        filename = []
        print("lettre")
        for root, dirs, files in os.walk("./Image/test"):
            for i in files:
                filename.append(i[:-4].split("_"))
        os.system('rm ./Image/test/*')
        for i in range(10):
            police = random.choice(fonts)
            path = "./Image/test/" + filename[i][0] + "_" + filename[i][1] + "_" + police
            get_new_captcha(path, text=filename[i][0], color=filename[i][1], font=police)


def easy_ocr(file_path):
    reader = easyocr.Reader(['en'])  # need to run only once to load model into memory
    result = reader.readtext(file_path)
    array = [x for elem in result for x in elem]
    return array


def print_array(data_array):
    for line in data_array:
        string = ""
        for elem in line:
            if elem == "ï»¿":
                string += " |"
            else:
                if elem != "0":
                    string += BColors.BLUE + str(elem) + BColors.RESET + "|"
                else:
                    string += str(elem) + "|"
        print(string)


def compare(text_captcha, text_ocr, data_array,
            results):  # prend en argument le texte original de la photo et celui que l'algo a retourné
    coeff_long = 0  # coefficient de variation de la longueur
    nb_same_letters = 0  # nombre de lettre similaire entre le texte original et celui trouvé par l'algo
    nb_alike_letters = 0  # nombre de lettre qui se ressemblent
    original = list(text_captcha)
    ocr = list(text_ocr)

    initial_original_length = len(original)
    initial_ocr_length = len(ocr)

    cpt = 0

    ocr_length = len(ocr)
    original_length = len(original)

    while cpt < ocr_length:  # parcourt le texte retourné par l'algorithme
        cpt2 = 0
        while cpt2 < original_length:  # parcourt le texte original qui apparait sur l'image
            # verifie si la lettre de l'algo et celle de l'image sont les mêmes
            if ocr[cpt] == original[cpt2]:
                coord = find_letter(ocr[cpt], original[cpt2], data_array)
                inc(coord, data_array)
                print("les lettre sont similaires : " + ocr[cpt])
                nb_same_letters += 1
                # Retire les lettres des listes de caractère dans le cas où elles sont similaire
                ocr.pop(cpt)
                original.pop(cpt2)
                ocr_length -= 1
                original_length -= 1
                cpt2 = original_length
            # verifie si la lettre de l'algo et celle de l'image se ressemblent
            elif check_letter(ocr[cpt], original[cpt2]):
                coord = find_letter(ocr[cpt], original[cpt2], data_array)
                inc(coord, data_array)
                print(ocr[cpt] + " ressemble à " + original[cpt2])
                nb_alike_letters += 1
                ocr.pop(cpt)
                original.pop(cpt2)
                ocr_length -= 1
                original_length -= 1
                cpt2 = original_length
            else:
                cpt2 += 1
                if cpt2 >= original_length:
                    cpt += 1

    score = (nb_same_letters + (nb_alike_letters / 2)) / initial_original_length * 100
    results[text_captcha] = score
    print("Nombre de lettre similaires = " + str(nb_same_letters))
    print("Nombre de lettres qui se ressemblent = " + str(nb_alike_letters))
    print_color(score)
    return results


def print_color(score):
    val = score
    if val <= 35:
        print(BColors.RED + str(val) + "%" + " de reussite" + BColors.RESET)
    elif 35 < val <= 70:
        print(BColors.YELLOW + str(val) + "%" + " de reussite" + BColors.RESET)
    else:
        print(BColors.GREEN + str(val) + "%" + " de reussite" + BColors.RESET)


def check_letter(letter_algo, letter_image):
    switcher = {
        "m": compare_letter(letter_image, ['M', 'n', 'N']),
        "u": compare_letter(letter_image, ['U', 'v', 'V']),
        "U": compare_letter(letter_image, ['u', 'v', 'V']),
        "i": compare_letter(letter_image, ['I', 'l']),
        "w": compare_letter(letter_image, ['W']),
        "B": compare_letter(letter_image, ['S', 's', '8']),
        "z": compare_letter(letter_image, ['Z']),
        "Z": compare_letter(letter_image, ['z']),
        "p": compare_letter(letter_image, ['P', 'F', 'f']),
        "P": compare_letter(letter_image, ['p', 'F', 'f']),
        "f": compare_letter(letter_image, ['F', 'p', 'P']),
        "F": compare_letter(letter_image, ['f', 'p', 'P']),
        "k": compare_letter(letter_image, ['K', 'x', 'X']),
        "K": compare_letter(letter_image, ['k', 'x', 'X']),
        "x": compare_letter(letter_image, ['X', 'K', 'k']),
        "X": compare_letter(letter_image, ['x', 'K', 'k']),
        "c": compare_letter(letter_image, ['C']),
        "C": compare_letter(letter_image, ['c']),
        "j": compare_letter(letter_image, ['J']),
        "J": compare_letter(letter_image, ['j']),
        "o": compare_letter(letter_image, ['O', 'Q', '0']),
        "O": compare_letter(letter_image, ['o', 'Q', '0']),
        "Q": compare_letter(letter_image, ['o', 'O', '0']),
        "0": compare_letter(letter_image, ['o', 'O', 'Q']),
        "v": compare_letter(letter_image, ['V', 'u', 'U']),
        "V": compare_letter(letter_image, ['v', 'u', 'U']),
        "S": compare_letter(letter_image, ['s', '5']),
        "s": compare_letter(letter_image, ['S', '5']),
        "W": compare_letter(letter_image, ['w'])
    }
    return switcher.get(letter_algo, False)


def compare_letter(letter, tab):
    for k in range(len(tab)):
        if letter == tab[k]:
            return True


def find_letter(letter_image, letter_algo, data_csv):
    coord = [0, 0]
    for i in data_csv[0]:
        if i == letter_image:
            coord[0] = data_csv[0].index(letter_image)
    for i in range(len(data_csv)):
        if data_csv[i][0] == letter_algo:
            coord[1] = i
    return coord


def inc(coord, matrix):
    nb = int(matrix[coord[0]][coord[1]])
    nb += 1
    matrix[coord[0]][coord[1]] = nb


if __name__ == "__main__":
    # Overture du CSV
    csv_file = open('matrice.csv', encoding='ISO-8859-1')
    data_csv = csv.reader(csv_file, delimiter=';')
    data_array = list(data_csv)

    # Ouverture du fichier lettre.json
    json_file = open('lettre.json')
    json_data = json.load(json_file)

    fonts = get_available_fonts()
    # print(json_data)

    # Coefficient d'efficacité moyen de chaque Police

    # Coefficient d'efficacité moyen de chaque couleur
    colors = ["red", "blue", "green", "yellow"]  # {'Bleu': 1, 'Rouge': 1, 'Jaune': 1, 'Vert': 1}

    # Coefficient d'efficacité moyen de chaque lettre
    letters = {'A': 1, 'B': 2, 'C': 1, 'D': 5, 'E': 1, 'F': 3, 'G': 8, 'H': 2}  # A completer
    results = {}
    paths = ["Image/2/Noise-1/", "Image/2/Noise-3/", "Image/2/Noise-5/", "Image/5/Noise-1/", "Image/5/Noise-3/",
             "Image/5/Noise-5/", "Image/10/Noise-1/", "Image/10/Noise-3/", "Image/10/Noise-5/"]

    # mutation(listeCouleur, listePolice)
    init_image(colors, fonts)
    # print(calculBestRapport(listeCouleur, listePolice, json_data))

    while paths != []:  # Condition d'arret de l'algo
        files = []
        mutation(colors, fonts)
        results = evaluation(files, results, path, data_array)
        print("liste resultat = " + str(results))
        results = selection(results)
        sorted(results.items(), key=lambda t: t[1])
        print("liste resultat apres selection = " + str(results))

    print_array(data_array)
    print(results)
    results = selection(results)
