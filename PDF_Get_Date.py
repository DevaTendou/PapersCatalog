from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import shutil
import glob

path = "./dl_acm_org/"
pdfInDir = glob.glob(path + "*.pdf")

year = 0
for pdf in pdfInDir:
	file = open(pdf, 'rb')
	parser = PDFParser(file)
	doc = PDFDocument(parser)
	try:	
		datestring = doc.info[0]['CreationDate'][2:6]
		year = str(int(datestring))
		file.close()
		shutil.move(path + pdf, path + year + "/" + pdf)
	except:	continue
	
	
	

