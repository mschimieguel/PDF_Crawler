import re
import requests
import os
import img2pdf
import math
from bs4 import BeautifulSoup
import sys
import PyPDF2
 
site =  input("Digite o site :")
response = requests.get(site)
#print (response.status_code) # == 200 ok
#print (response.status_code) == 404 ERROR
soup = BeautifulSoup(response.text, 'html.parser')
img_tags = soup.find_all('img',class_='absimg')
script_tags = soup.find_all('script')

page_tags = soup.find_all('div',class_='outer_page only_ie6_border')
num_pages = int(page_tags[-1]['id'][11:])

#print(num_pages)

print ("copiando URLs ...\n")
#pegando as url das imagens diretamente 
urls_img = [img_tags[i]['orig'] for i in range(0,len(img_tags) )]
paginas = len(urls_img)
for i in range(paginas):
	print("Pegando url pagina ",i+1)
#pegando as urls das imagens via jsonp
j = 1;
for i in range (len(script_tags)):
	try:
		url_jasonp = re.search("(?P<url>https?://[^\s]+(jsonp))",script_tags[i].text).group("url")
		print ("Pegando url pagina ",j + paginas)
		response2 = requests.get(url_jasonp)
		urls_img.append( re.search("(?P<url>https?://[^\s]+(jpg))",response2.text).group("url") ) 
		j = j + 1
	except:
		continue

if (len(urls_img) != num_pages):
	print("ERRO 1.1 tente novamente")
	sys.exit()

try:
	os.mkdir("img")
except:
	print("")

print ("Baixando imagens...\n")
n_digits = math.floor(math.log10(len(urls_img)) + 1)
page = 1	
for url in urls_img:
	name_file = "img/page_" + str(page).zfill(n_digits) +".jpg"
	print("baixando pagina ",page)
	with open(name_file, 'wb') as f:
		response_arq = requests.get(url)
		f.write(response_arq.content)
	page = page + 1	


print ("Compilando em pdf...\n")
namePDF = re.search("(?P<url>https?://[^\s]+(}))",script_tags[len(script_tags)-1].text).group("url")
for i in range(len(namePDF)-1,0,-1):
	if(namePDF[i] == '/'):
		break
namePDF = namePDF[i+1:-2]

#listando os nomes das imagens baixadas em arq
os.chdir('img/')
arq = os.listdir(os.getcwd())
arq.sort()

if ( len(arq) != num_pages):
	print("ERRO 1.2 tente novamente")
	os.system('rm *.jpg')
	sys.exit()

with open("../"+namePDF+".pdf", "wb") as f:	
	f.write(img2pdf.convert([i for i in arq if i.endswith(".jpg")]))


reader = PyPDF2.PdfFileReader(open("../"+namePDF+".pdf",'rb'))
pdfpages = reader.getNumPages() 

os.chdir('../')
if (num_pages != pdfpages):
	os.system("rm "+namePDF+".pdf")
	print("ERRO 1.3 tente novamente")

#removendo as imagens baixadas
os.system('rm img/*.jpg')