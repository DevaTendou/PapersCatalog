import os, glob, shutil, subprocess, re, csv
from subprocess import Popen, PIPE
from Levenshtein import distance, ratio
from copy import deepcopy
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

global DocsWithError

path = ".\\dl_acm_org\\"
dirs = next(os.walk(path))[1]
keywords, DocsWithError, excelMap = [], [], []

def keywordsChangeToDict(excelMap):
	listToWork = []
	for e in excelMap:  listToWork += e[1]							#Junta todas as keywords numa lista
	generalizeDict = {k:v for k,v in getProperKeys(listToWork)}		#Generaliza as keywords para palavras semelhantes dentro da lista e transforma-as num dicionario
	return generalizeDict

def getProperKeys(listOfKeys):
	tempList = deepcopy(listOfKeys)
	keysOfChoice = []
	for i, key in enumerate(listOfKeys):
		values = []
		for j, temp in enumerate(tempList):
			if i != j:	values.append(ratio(key, temp))
			else: values.append(0.0)
			
		maxValue = max(values)
		if maxValue >= 0.9:
			indexOfKey = values.index(maxValue)
			keyReplace = tempList[indexOfKey]
			keysOfChoice.append([key] + [keyReplace])
			tempList = [keyReplace if key is t else t for t in tempList]
		else: keysOfChoice.append([key] + [key])
	return keysOfChoice

def splitText(delims, text):
	lista = [text]
	delims = delims.split("|")
	for d in delims:
		temp = []
		for l in lista:	temp += l.split(d)
		lista = temp
	return lista

def cleanBadChars(lista):
	lista = [x.lower() for x in lista]
	lista = [x for x in lista if len(x)]
	lista = [x[1:] if x[0] is " " else x for x in lista]
	lista = [x[:-1] if x[-1] is " " else x for x in lista]
	lista = [re.sub(r'([^\s\w]|_)+', '', x) for x in lista]
	return lista
	
def getFilesInDir(path, dir, keyword):
	newPath = path + dir + '\\'
	filesInDir = glob.glob(newPath + keyword)
	return filesInDir

def createDir(path, name):
	if not os.path.exists(path+'\\'+name):	os.makedirs(path+'\\'+name)
	else:	
		shutil.rmtree(path+'\\'+name)
		createDir(path, name)
		
def outputTxt(pdf, tempDir):
	PDF_Name = os.path.split(pdf)[-1]
	args = ['pdftotext.exe', '-f', '1', '-l', '1', pdf, tempDir+"\\"+PDF_Name[:-4]+'.txt']
	p = Popen(args, stdout=PIPE, stderr=PIPE)
	output, error = p.communicate()
	error = str(error)
	if "Syntax Error:" in error:	DocsWithError.append(pdf)
	
def getKeywords(txtPath):
	file = open(txtPath, 'r')
	
	splitTxt = file.read().split('\n')	#Divide o TXT por linhas e guarda numa lista
	begin, end = 0, 0
	for i, line in enumerate(splitTxt):	#Por cada linha indexada da lista:
		if ("KEYWORD" in line.upper()) or ("GENERAL TERM" in line.upper()) :	#Se for encontrada a palavra "Keyword":
			begin = i
			break
	file.close()
	
	if not begin:
		#print("Error in:", txtPath, "\n\t\t Keyword Tag not found!")
		return []			#Se não for encontrada a palavra "Keyword" retorna uma lista vazia
	else:
		keywords = []
		for element in splitTxt[begin:begin+2]:								#Para cada par elementos na lista:
			if len(element) < 200:	#Se o tamanho do elemento for superior a 200 entao nao e realizada a operacao
				keywords += splitText(", |,|; |;|: |:|.|. | \0", element)
			#else: print("Error in:", txtPath, "\n\t\t String is too long")
		return keywords

for dir in dirs:
	tempDir = "Temp"												#Nome temporario da nova directoria
	createDir(path, tempDir) 										#Cria uma diretoria temporaria
	
	PDFs_In_Dir = getFilesInDir(path, dir, "*.pdf") 				#Devolve todos os PDFs na presente directoria
	for pdf in PDFs_In_Dir:	outputTxt(pdf,  path+"\\"+tempDir+"\\")
	
	TXTs_In_Dir = getFilesInDir(path, tempDir, "*.txt")				#Devolve todos os TXTs na presente directoria
	dismissList = ["KEYWORD", "KEY WORD", "GENERAL TERM"] 			#Tags a serem descartadas
	for txt in TXTs_In_Dir:											#Por cada TXT na directoria:
		for k in getKeywords(txt):									#Por cada key na lista de keys:							
			if all(dismiss not in k.upper() for dismiss in dismissList): #Caso a key nao seja descartada:
				keywords += [k]										#Adiciona-se a lista de keywords								
	shutil.rmtree(path+"\\"+ tempDir)								#Remove a diretoria temporaria
	excelMap += [[dir] + [cleanBadChars(keywords)]]					#(cleanBadChars())	<-	Remove incongruencias nas palavras
	keywords = []
	
generalizeDict = keywordsChangeToDict(excelMap)						#Generaliza todas as keywords a partir do Levenshtein distance e representa as mudanças em um dicionario

finalExcel = deepcopy(excelMap)
for i, cell in enumerate(excelMap):
	for j, key in enumerate(cell[1]):	finalExcel[i][1][j] = generalizeDict[key]

def countItems(lista):
	conj = list(set(lista))
	countDict = {element:lista.count(element) for element in conj}
	return countDict




def plotHistogram(year, keywords):
	counts = Counter(keywords)

	labels, values = zip(*counts.items())

	# sort your values in descending order
	indSort = np.argsort(values)[::-1]

	# rearrange your data
	labels = np.array(labels)[indSort]
	values = np.array(values)[indSort]
	
	indexes = np.arange(len(labels))
	bar_width = 0.35
	plt.figure(figsize=(16.0, 10.0))
	plt.bar(indexes, values)
	plt.title(year)
	# add labels
	plt.subplots_adjust(bottom=0.35)
	plt.xticks(indexes, labels, fontsize=8, rotation=90)
	plt.savefig(year+"_histogram.png")
	
for year, keys in finalExcel:	plotHistogram(year, keys)
	
	
	
		



		
		
		