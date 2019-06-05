import telebot
import parser
from telebot import apihelper
from imageai.Detection import ObjectDetection
import os
import markovify

#main variables
TOKEN = "838747096:AAH1CHU_bdf-Lb8V_J18tt6ad9dXV4GhSb0"
bot = telebot.TeleBot(TOKEN)

#apihelper.proxy = {'https':'socks5://dante:hrenota@31.14.131.25:7777'}


with open("models/motifs_list.txt") as f:
    text = f.read()

# Build the model.
text_model = markovify.Text(text,state_size=2)



execution_path = os.getcwd()

def continue_sentence(beginning):
	print(beginning)
	return text_model.make_sentence_with_start(beginning)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
   bot.reply_to(message, "You've been added to the Game. Send me your found objects to DEFINE or start a story.")

@bot.message_handler(commands=['story'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.reply_to(message, "Let me tell you a story.")
    story = ''
    for i in range(5):
        story += text_model.make_sentence() + " " 
    bot.send_message(chat_id, story)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id
    try:
    	answer = continue_sentence(text.split(' ')[0])
    	if not answer: raise RuntimeError
    except:
    	answer = text_model.make_sentence()
    bot.send_message(chat_id, answer)
    
#    if "game" in text:
#        bot.send_message(chat_id, 'You can understand the Game only by playing.')
#    else:
#        bot.send_message(chat_id, 'Send me a photo or start a story by typing a command \"/play\".')

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message): 
	try:
		chat_id = message.chat.id    
		file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
		imagepath = os.path.join(execution_path , file_info.file_path)
		downloaded_file = bot.download_file(file_info.file_path)
		with open(imagepath, 'wb') as new_file:
			new_file.write(downloaded_file)
		#bot.reply_to(message,"Getting you some definitions!")
		bot.reply_to(message,"Let me think.")
	
		detector = ObjectDetection()
		detector.setModelTypeAsRetinaNet()
		detector.setModelPath("models/resnet50_coco_best_v2.0.1.h5")
		detector.loadModel()
	#	print(imagepath)
	#	print(detector)
		detections = detector.detectObjectsFromImage(input_image=imagepath, output_image_path=imagepath+".new.jpg")
		firstIteration = True
		toldStoryOnAnyObject = False
		sent1 = text_model.make_sentence()
		sent2 = text_model.make_sentence()
		print(sent1)
		for eachObject in detections:
			if firstIteration:
				answer = "Once upon a time, there lived a beautiful "+ eachObject["name"] +'.'
				firstIteration = False
			else:
				answer = "Then they saw an old "+ eachObject["name"] +'.'
			try:
				sent1 = continue_sentence(eachObject["name"])
				sent2 = continue_sentence(sent1.split(' ')[-1].strip('.'))
				toldStoryOnAnyObject = True

			#bot.reply_to(message, "I think it's a "+ eachObject["name"])
				bot.send_message(chat_id, answer)
				bot.send_message(chat_id, sent1)
				bot.send_message(chat_id, sent2)
			except:
				pass	
	#		sent3 = continue_sentence(sent2[-1])
	#		bot.send_message(chat_id, sent3)
		if not detections or not toldStoryOnAnyObject:
			if not detections:
				#bot.reply_to(message,"THIS IS NOT AN OBJECT." )
				bot.reply_to(message,"I don't see there anything to speculate about but I can tell you another story.")
			elif not toldStoryOnAnyObject:
				bot.reply_to(message, "In old time the ancients didn't know stories about " + eachObject["name"] \
				 + " so let me tell my story.")  
			story = ''
			for i in range(3):
				story += text_model.make_sentence() + " " 
			bot.send_message(chat_id, story)
		bot.send_message(chat_id, "What happened then? Now you continue.")
	except:
		bot.reply_to(message,"Give me a picture where I can get characters for my story.")
		
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)
bot.polling()
