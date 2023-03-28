import openai
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
import random
import time
from text_rewrite import TextRewrite
import language_tool_python
import pickle

class Generator:
	def fixGrammar(self, sentence):
		return self.languageTool.correct(sentence)

	def checkDict(self, my_dict, search_string, version):
		for question in my_dict:
			if question[version] == search_string:
				return True
		return False

	# Take in a paragraph and rewrite sentences at 0-1 chance
	def randomSentences(self, paragraph, chance=1):
		sentences = sent_tokenize(paragraph)
		for i, sentence in enumerate(sentences):
			if random.random() < chance:
				sentences[i] = self.fixGrammar(TextRewrite(sentence).work())
		return " ".join(sentences)

	def synonymsInit(self):
		self.formatedResponse["synonymAnswers"] = []
		for question in tqdm(self.formatedResponse["questions"], desc='Synonyms', total=len(self.formatedResponse["questions"])):
			response, related = question["response"], question["related"]
			self.formatedResponse["synonymAnswers"].append({"response": self.randomSentences(response), "related": self.randomSentences(related)})

		return self.formatedResponse

	def __init__(self, chapterNumber, sgInfo, relateTo, apiKey, formatedResponse=None, synonyms=True):
		self.sgInfo = sgInfo
		self.relateTo = relateTo
		self.apiKey = apiKey
		self.formatedResponse = formatedResponse
		self.languageTool = language_tool_python.LanguageTool('en-US')
		self.chapterNumber = chapterNumber
		self.synonyms = synonyms

	# Generate AI Response for questions
	def generateResponse(self, question):
		# Ask for answer and relate it ai
		prompt = "It is important that the response is 4 sentences. Write a simple 4 sentence academic response paragraph in the style of a 9th grader answering the following question: \""
		completion = openai.Completion.create(
			engine="text-davinci-003",
			prompt=(prompt + question),
			max_tokens=1024,
			n=1,
			stop=None,
			temperature=0.7,
		)
		response = completion.choices[0].text

		prompt2 = "It is IMPORTANT that the response is EXACTLY 2 sentences and is relating to " + self.relateTo + ". Write a simple 2 sentence academic response paragraph in the style of a 9th grader relating the following question to " + self.relateTo + ": \""
		completion2 = openai.Completion.create(
			engine="text-davinci-003",
			prompt=(prompt2 + question + "\". This response should not focus on answering the question, but should focus on relating the topic to " + self.relateTo + "."),
			max_tokens=1024,
			n=1,
			stop=None,
			temperature=0.75,
		)
		response2 = completion2.choices[0].text
		return response, response2

	# Generate AI Response for terms
	def generateTermResponse(self, term):
		# Ask for answer and relate it ai
		prompt = "It is important that the response is 1 sentences. Without adding a bullet point or dash in front, write a simple bullet point definition without using the defined work for the word: "
		completion = openai.Completion.create(
			engine="text-davinci-003",
			prompt=(prompt + term),
			max_tokens=1024,
			n=1,
			stop=None,
			temperature=0.7,
		)
		return completion.choices[0].text

	# Format the Responses to a dicitonary
	def formatResponse(self):
		# Set up the OpenAI API client
		openai.api_key = self.apiKey

		try:
			tempPickle = open('Chapter' + self.chapterNumber + '.pkl', 'rb+')
			self.formatedResponse = pickle.load(tempPickle)
		except (FileNotFoundError, EOFError):
			self.formatedResponse = {"questions": [], "terms": [], "synonymAnswers": []}

		tempPickle = open('Chapter' + self.chapterNumber + '.pkl', 'wb+')
		for question in tqdm(self.sgInfo["questions"], desc='Questions', total=len(self.sgInfo["questions"])):
			if self.checkDict(self.formatedResponse["questions"], question, "question"):
				continue
			while(True):
				try:
					response, related = self.generateResponse(question)
					break
				except (openai.error.ServiceUnavailableError, openai.error.RateLimitError):
					time.sleep(10)
			self.formatedResponse["questions"].append({"question": question, "response": response, "related": related})
			pickle.dump(self.formatedResponse, tempPickle)
		for term in tqdm(self.sgInfo["keyTerms"], desc='Terms', total=len(self.sgInfo["keyTerms"])):
			if self.checkDict(self.formatedResponse["terms"], question, "term"):
				continue
			while(True):
				try:
					response = self.generateTermResponse(term)
					break
				except (openai.error.ServiceUnavailableError, openai.error.RateLimitError):
					time.sleep(10)
			self.formatedResponse["terms"].append({"term": term, "response": response})
			pickle.dump(self.formatedResponse, tempPickle)
		
		if self.synonyms:
			self.synonymsInit()
		return self.formatedResponse