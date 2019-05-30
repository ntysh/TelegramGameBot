import telebot
import parser
from telebot import apihelper
from imageai.Detection import ObjectDetection
import os

#main variables
TOKEN = "838747096:AAH1CHU_bdf-Lb8V_J18tt6ad9dXV4GhSb0"
bot = telebot.TeleBot(TOKEN)

apihelper.proxy = {'https':'socks5h://dante:hrenota@31.14.131.25:7777'}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
   bot.reply_to(message, "You are added to the game. Send me your found objects to DEFINE.")

@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id
    if "game" in text or "Game" in text:
        bot.send_message(chat_id, 'Too early to know.')
    elif text == "play":
        bot.send_message(chat_id, 'Count to five. Ha-ha-ha.')
    else:
        bot.send_message(chat_id, 'Give me an object.')

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):    
	try: 
		file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
		downloaded_file = bot.download_file(file_info.file_path)
		src='/Users/tysh/Documents/newnormal/ImageAI/'+file_info.file_path;
		with open(src, 'wb') as new_file:
			new_file.write(downloaded_file)
		bot.reply_to(message,"Getting you some definitions!") 
		execution_path = os.getcwd()
		detector = ObjectDetection()
		detector.setModelTypeAsRetinaNet()
		detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
		detector.loadModel()
		detections = detector.detectObjectsFromImage(input_image=os.path.join(execution_path , file_info.file_path), output_image_path=os.path.join(execution_path , file_info.file_path + "imagenew.jpg"))

		for eachObject in detections:
			bot.reply_to(message, "I think it's a "+ eachObject["name"])
	except Exception as e:
		bot.reply_to(message,"THIS IS NOT AN OBJECT." ) 

@bot.message_handler(func=lambda m: True)
def echo_all(message):
   bot.reply_to(message, message.text)
bot.polling()
