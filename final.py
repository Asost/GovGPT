from docx import Document
import json
from parseDoc import Parser
from generateAndFormat import Generator
from generateDocx import GenerateDocx
from fileDownload import GetDocumentLink
# Start Time checker
import time
start_time = time.time()

# Set up the OpenAI API client
apiKey = "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"

# Info needed
name = "Joohn Doe"
period = "6"
relateTo = "Minecraft"
chapterNumber = "12"

#sgDoc = urlToDoc("https://sites.google.com/a/clovisusd.k12.ca.us/nitschke-s-cnec-website/calendar/CH%20" + chapterNumber + "%20SG%20AP%20GOV20.docx")
sgURL = GetDocumentLink(chapterNumber).getFileLink()
#sgInfo = Parser("CH 11 SG AP GOV20.docx").parse()
sgInfo = Parser(sgURL).parse()

try:
	formatedResponse = json.load(open("formatedResponse" + chapterNumber + ".json"))
	print(formatedResponse["synonymAnswers"])
except KeyError:
	formatedResponse = json.load(open("formatedResponse" + chapterNumber + ".json"))
	formatedResponse = Generator(sgInfo, relateTo, apiKey, formatedResponse).synonymsInit()
	with open("formatedResponse" + chapterNumber + ".json", "w") as file:
		json.dump(formatedResponse, file)
except FileNotFoundError:
	formatedResponse = Generator(sgInfo, relateTo, apiKey).formatResponse()
	with open("formatedResponse" + chapterNumber + ".json", "w") as file:
		json.dump(formatedResponse, file)

finalDoc, questionlessDocument = GenerateDocx(sgInfo, chapterNumber, formatedResponse, questionless=True, name=name, period=period).generateAIdocx()

finalDoc.save("AP GOV Study Guide Chapter " + chapterNumber + ".docx")
if questionlessDocument:
	questionlessDocument.save("AP GOV Study Guide Chapter " + chapterNumber + "QuestionLess.docx")

# End Time and check
elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
print(f"Elapsed time: {elapsed}")