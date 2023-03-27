import requests
from bs4 import BeautifulSoup

class GetDocumentLink:
	def __init__(self, chapterNumber):
		self.chapterNumber = chapterNumber

	def getFileLink(self):
		page = requests.get("https://drive.google.com/embeddedfolderview?authuser=0&id=1zuLOm7bYBsIPaaqGZiC6RgHpwTrupi-H#list")
		newUrl = BeautifulSoup( page.content , 'html.parser').find("meta")['content'].split("url=")[1]
		newPage = requests.get(newUrl)
		soup = BeautifulSoup( newPage.content , 'html.parser')

		for link in soup.find_all("a"):
			if self.chapterNumber in link.text:
				return "https://docs.google.com/uc?export=download&id=" + link["href"].split("/d/")[1].split("/view")[0]

		return None