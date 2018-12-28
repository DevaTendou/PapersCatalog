import PyPDF2
import re
import subprocess
from functools import reduce
from os import listdir, rename
	
def parsePhrase(phrase):
	newPhrase = reduce(lambda x, y: x if y in "\\/*?\":\t|<>\n\r" else x+y, phrase)
	return newPhrase

def getTitle(pdf):
	pdfRead = PyPDF2.PdfFileReader(pdf)
	home = pdfRead.getPage(0)
	lista = home.extractText().splitlines()

	titulo = []
	phrase = ''
	for i, line in enumerate(lista):
		phrase += line
		if line.istitle():
			phrase = re.sub(r"(\w)([A-Z])", r"\1 \2", phrase)
			titulo.append(phrase)
			phrase = ''
			return titulo


path = ".\\_Por_Organizar"
files = listdir(path)
name, newName = [], []
for f in files:
	args = ['pdftotext.exe', '-f', '1', '-l', '1', '-q', ".\\_Por_Organizar\\" + f, f[:-4]+'.txt']
	try: 
		subprocess.call(args)
		name.append(f)
		txt = open('.\\'+f[:-4]+'.txt')
		phrase = txt.readline()
		cleanPhrase = parsePhrase(phrase)
		newName.append(cleanPhrase)
		txt.close()
	except: continue

tuple = zip(name, newName)
for name, newName in tuple:
	#print(name, '-->', newName)
	rename(path+'\\'+name, path+'\\'+newName[:-1]+'.pdf')
	

	


			
