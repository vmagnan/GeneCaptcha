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

class bcolors:
	GREEN = '\033[92m' #GREEN
	YELLOW = '\033[93m' #YELLOW
	RED = '\033[91m' #RED
	BLUE = '\033[96m' #BLUE
	RESET = '\033[0m' #RESET COLOR

def main():
	# Overture du CSV
	csvFile = open('matrice.csv', encoding='ISO-8859-1')
	dataCSV = csv.reader(csvFile, delimiter=';')
	data_list = list(dataCSV)

	#Ouverture du fichier lettre.json
	json_file = open('lettre.json')
	json_data = json.load(json_file)

	listePolice = get_available_fonts()
	#print(json_data)


	#Coefficient d'efficacité moyen de chaque Police 

	#Coefficient d'efficacité moyen de chaque couleur
	listeCouleur = ["red", "blue", "green", "yellow"]#{'Bleu': 1, 'Rouge': 1, 'Jaune': 1, 'Vert': 1} 

	#Coefficient d'efficacité moyen de chaque lettre
	listeLettre = {'A': 1, 'B': 2, 'C': 1, 'D': 5, 'E': 1, 'F': 3, 'G': 8,'H': 2} #A completer
	listeResultat = {}
	listePath = ["Image/2/Noise-1/", "Image/2/Noise-3/", "Image/2/Noise-5/", "Image/5/Noise-1/", "Image/5/Noise-3/", "Image/5/Noise-5/", "Image/10/Noise-1/", "Image/10/Noise-3/", "Image/10/Noise-5/"]

	#mutation(listeCouleur, listePolice)
	initImage(listeCouleur, listePolice)
	#print(calculBestRapport(listeCouleur, listePolice, json_data))

	while listePath != []: #Condition d'arret de l'algo
		listeFichiers = []
		mutation(listeCouleur, listePolice)
		listeResultat = evaluation(listeFichiers, listeResultat, path, data_list)
		print("liste resultat = " + str(listeResultat))
		listeResultat = selection(listeResultat)
		sorted(listeResultat.items(), key=lambda t: t[1])
		print("liste resultat apres selection = " + str(listeResultat))

	
	printTab(data_list)
	print(listeResultat)
	listeResultat = selection(listeResultat)

def initImage(listeCouleur, listePolice):
	for i in range(10):
		couleur = random.choice(listeCouleur)
		police = random.choice(listePolice)
		texte = newString()
		path = "./Image/test/"+texte+"_"+couleur+"_"+police[:-4]
		print(path)
		get_new_captcha(path, text=texte, color=couleur, font=police)



def moyenneCouleur(Couleur, json_data):
	cptCouleur = 0
	cpt = 0
	for lettre, valeur in json_data.items():
		for elem, police in valeur.items():
			for couleur, score in police.items():
				if couleur == Couleur:
					cptCouleur += score
					cpt += 1
	return cptCouleur/cpt

def rapportCouleurPolice(Couleur, Police, json_data):
	cptCouleur = 0
	cpt = 0
	for lettre, valeur in json_data.items():
		for police, elem in valeur.items():
			for couleur, score in elem.items():
				if couleur == Couleur and police == Police:
					cptCouleur += score
					cpt += 1
	return cptCouleur/cpt

def calculBestRapport(listeCouleur, listePolice, json_data):
	bestRapport = 1
	for couleur in listeCouleur:
		for police in listePolice:
			rapport = rapportCouleurPolice(couleur, police, json_data)
			print(rapport)
			if rapport < bestRapport:
				bestRapport = rapport
	return bestRapport

def selection(listeResultat):
	liste = {}
	for elem, valeur in listeResultat.items():
		if valeur <= 25:
			liste[elem]=valeur
	return liste


def evaluation(texteOriginal, texteAlgo):
	for fichier in listeFichiers:
		filePath = path + fichier
		liste = easyOCR(filePath)
		if liste != []:
			print("Image = " + str(fichier[:-4]))
			print("Algo = " + str(liste[1]))
			listeResultat = compare(fichier[:-4], liste[1], data_list, listeResultat)
		else:
			print("Fichier non reconnu par EasyOCR !")

	return listeResultat

def createRandomListe(listeInitiale):
	listeFinale = []
	liste = []
	for elem, proba in listeInitiale.items():
		for i in range(proba):
			liste.append(elem)
	print(liste)
	for i in range(10):
		listeFinale.append(random.choice(liste))
	print(listeFinale)

def choixDossier(listePath):
	path = random.choice(listePath)
	listePath.pop(listePath.index(path))
	return listePath, path

def ajoutFichier(listeFichiers, path):
	for (repertoire, sousRepertoires, fichiers) in walk(path):
		listeFichiers.extend(fichiers)
	return listeFichiers

def newString():
	string = ""
	listeLettres = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
	for i in range(10):
		string += random.choice(listeLettres)
	return string

def getDataName(fileName):
	data = fileName.split("_")
	data[-1] = data[-1][:-4]
	return data

def mutation(listeCouleur, listePolice):
	liste = ["color", "lettre", "police"]
	choice = random.choice(liste)
	if choice == "color":
		fileName = []
		print("color")
		for root, dirs, files in os.walk("./Image/test"):
			for i in files:
				fileName.append(i[:-4].split("_"))
		os.system('rm ./Image/test/*')
		for i in range(10):
			couleur = random.choice(listeCouleur)
			path = "./Image/test/"+fileName[i][0]+"_"+couleur+"_"+fileName[i][2]
			get_new_captcha(path, text=fileName[i][0], color=couleur, font=fileName[i][2])
	elif choice == "lettre":
		fileName = []
		print("lettre")
		for root, dirs, files in os.walk("./Image/test"):
			for i in files:
				fileName.append(i[:-4].split("_"))
		os.system('rm ./Image/test/*')
		for i in range(10):
			texte = newString()
			path = "./Image/test/"+texte+"_"+fileName[i][1]+"_"+fileName[i][2]
			get_new_captcha(path, text=texte, color=fileName[i][1], font=fileName[i][2])

	elif choice == "police":
		fileName = []
		print("lettre")
		for root, dirs, files in os.walk("./Image/test"):
			for i in files:
				fileName.append(i[:-4].split("_"))
		os.system('rm ./Image/test/*')
		for i in range(10):
			police = random.choice(listePolice)
			path = "./Image/test/"+fileName[i][0]+"_"+fileName[i][1]+"_"+police
			get_new_captcha(path, text=fileName[i][0], color=fileName[i][1], font=police)




def easyOCR(filePath):
	reader = easyocr.Reader(['en']) # need to run only once to load model into memory
	result = reader.readtext(filePath)
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

def compare(texteOriginal, texteAlgo, data_list, listeResultat): #prend en argument le texte original de la photo et celui que l'algo a retourné
	coeffLong = 0 #coefficient de variation de la longueur
	nbLettreSimilaire = 0 #nombre de lettre similaire entre le texte original et celui trouvé par l'algo
	lettreRessemblante = 0 #nombre de lettre qui se ressemblent
	original = list(texteOriginal)
	algo = list(texteAlgo)

	longueurOriginalInitiale = len(original)
	longueurAlgoInitiale = len(algo)

	cpt = 0

	longueurAlgo = len(algo)
	longueurOriginal = len(original)

	while cpt < longueurAlgo: #parcourt le texte retourné par l'algorithme
		cpt2 = 0
		while cpt2 < longueurOriginal: #parcourt le texte original qui apparait sur l'image
			# verifie si la lettre de l'algo et celle de l'image sont les mêmes
			if algo[cpt] == original[cpt2]:
				coord = findLettre(algo[cpt], original[cpt2], data_list)
				inc(coord, data_list)
				print("les lettre sont similaires : " + algo[cpt])
				nbLettreSimilaire +=1
				#Retire les lettres des listes de caractère dans le cas où elles sont similaire
				algo.pop(cpt)
				original.pop(cpt2)
				longueurAlgo -= 1
				longueurOriginal -= 1
				cpt2 = longueurOriginal
			# verifie si la lettre de l'algo et celle de l'image se ressemblent
			elif checkLettre(algo[cpt], original[cpt2]):
				coord = findLettre(algo[cpt], original[cpt2], data_list)
				inc(coord, data_list)
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

	score = (nbLettreSimilaire + (lettreRessemblante/2))/longueurOriginalInitiale*100
	listeResultat[texteOriginal] = score
	print("Nombre de lettre similaires = " + str(nbLettreSimilaire))
	print("Nombre de lettres qui se ressemblent = " + str(lettreRessemblante))
	printColor(score)
	return listeResultat

def printColor(score):
	val = score
	if val <= 35:
		print(bcolors.RED + str(val) + "%"+" de reussite" + bcolors.RESET)
	elif val > 35 and val <= 70:
		print(bcolors.YELLOW + str(val) + "%"+" de reussite" + bcolors.RESET)
	else:
		print(bcolors.GREEN + str(val) + "%"+" de reussite" + bcolors.RESET)




def checkLettre(lettreAlgo, lettreImage):
	switcher = {
		"m": compareLettre(lettreImage, ['M','n','N']),
		"u": compareLettre(lettreImage, ['U','v','V']),
		"U": compareLettre(lettreImage, ['u','v','V']),
		"i": compareLettre(lettreImage, ['I','l']),
		"w": compareLettre(lettreImage, ['W']),
		"B": compareLettre(lettreImage, ['S','s','8']),
		"z": compareLettre(lettreImage, ['Z']),
		"Z": compareLettre(lettreImage, ['z']),
		"p": compareLettre(lettreImage, ['P','F','f']),
		"P": compareLettre(lettreImage, ['p','F','f']),
		"f": compareLettre(lettreImage, ['F','p','P']),
		"F": compareLettre(lettreImage, ['f','p','P']),
		"k": compareLettre(lettreImage, ['K','x','X']),
		"K": compareLettre(lettreImage, ['k','x','X']),
		"x": compareLettre(lettreImage, ['X','K','k']),
		"X": compareLettre(lettreImage, ['x','K','k']),
		"c": compareLettre(lettreImage, ['C']),
		"C": compareLettre(lettreImage, ['c']),
		"j": compareLettre(lettreImage, ['J']),
		"J": compareLettre(lettreImage, ['j']),
		"o": compareLettre(lettreImage, ['O','Q','0']),
		"O": compareLettre(lettreImage, ['o','Q','0']),
		"Q": compareLettre(lettreImage, ['o','O','0']),
		"0": compareLettre(lettreImage, ['o','O','Q']),
		"v": compareLettre(lettreImage, ['V','u','U']),
		"V": compareLettre(lettreImage, ['v','u','U']),
		"S": compareLettre(lettreImage, ['s','5']),
		"s": compareLettre(lettreImage, ['S','5']),
		"W": compareLettre(lettreImage, ['w'])
	}
	return switcher.get(lettreAlgo,False)

def compareLettre(lettre, tab):
	for k in range(len(tab)):
		if lettre == tab[k]:
			return True

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

def tesseract(fichier):
	cmd = "convert -density 100 " + str(fichier) + "-depth 8 -strip -background white alpha off out.tiff"
	os.system(cmd)
	os.system('tesseract out.tiff test')
	os.system('cat test.txt')




def svg_to_png(svg_path):
    """
    :param svg_path: Path to a svg file
    :return: Nothing
    """
    cairosvg.svg2png(url=svg_path, write_to=svg_path.replace(".svg", ".png"))


def get_paths_files_with_extension_from_folder(folder, extension='svg'):
    """
    :param extension: Extension of the files you are searching, default is svg
    :param folder: Folder in which searching files
    :return list of path to svg files without extension:
    """
    list_paths_to_files = [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.' + extension))]
    for i in range(len(list_paths_to_files)):
        list_paths_to_files[i] = list_paths_to_files[i].replace("\\", "/")
    return list_paths_to_files


def beautify_string(string):
    string_no_slash = string.replace("\\", "")
    string_remove_last_char = string_no_slash[:-1]
    string_remove_first_char = string_remove_last_char[1:]
    return string_remove_first_char


def get_new_captcha(path, /, **keywords):
    """
    Requête le serveur nodejs pour générer un captcha
    Exemple d'appel : get_new_captcha("./coucou"+font, text="A38hCNp8", color="green", font=font)
    :param path: Le chemin de l'image à sauvegarder (Ne pas spécifier l'extension)
    :param keywords: Tableau de paramètres correspondant actuellement aux paramètres nommés : text, color et font.
    :return: 0 = OK | 1 = Erreur
    """
    if len(keywords) > 0 and 'text' in keywords:
        url = "http://localhost:8080/captcha?" + urllib.parse.urlencode(keywords)
        print(url)
        r = requests.get(url)
        if r.status_code == 200:
            byte_string = beautify_string(r.content.decode("utf8"))
            cairosvg.svg2png(bytestring=byte_string, write_to=path + ".png")
            return 0
    return 1


def get_available_fonts():
    """
    Renvoie les polices disponibles sur le serveur nodejs
    :return: Tableau de font
    """
    url = "http://localhost:8080/fonts"
    r = requests.get(url)
    if r.status_code == 200:
        array = r.content.decode("utf8")
        array = array[:-1]
        array = array[1:]
        return array.split("/")
    return None

main()