import telebot
import parser
from telebot import apihelper, types

#from imageai.Detection import ObjectDetection
import os, sys
#import markovify
sys.path.insert(1, './gpt2/src')
from interactive_conditional_samples import run_model
#python src/interactive_conditional_samples.py 
from threading import Thread

# telegram params
TOKEN = ""
bot = telebot.TeleBot(TOKEN)

apihelper.proxy = {'https':'socks5://dante:hrenota@31.14.131.25:7777'}


source_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
source_markup_btn1 = types.KeyboardButton('Park Kultury')
source_markup_btn2 = types.KeyboardButton('Biblioteka imeni Lenina')
source_markup.add(source_markup_btn1, source_markup_btn2)

source_markup2 = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
source_markup2_btn1 = types.KeyboardButton('Stay at Kropotkinskaya')
source_markup2_btn2 = types.KeyboardButton('Park Kultury')
source_markup2_btn3 = types.KeyboardButton('Biblioteka imeni Lenina')
source_markup2_btn4 = types.KeyboardButton('Examine the artifact')
source_markup2.add(source_markup2_btn1, source_markup2_btn2, source_markup2_btn3, source_markup2_btn4)

source_markup3 = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
source_markup3_btn1 = types.KeyboardButton('Read the newspapers')
source_markup3_btn2 = types.KeyboardButton('Read the Soviet archives')
source_markup3_btn3 = types.KeyboardButton('Discuss the stories with an odd visitor')
source_markup3.add(source_markup3_btn1, source_markup3_btn2,source_markup3_btn3)

class Task():
    isRunning = False
    mySource = ''
    myFilter = ''
    def __init__(self):
        return
task = Task()


# motifs dataset
#with open("models/motifs_list.txt") as f:
#    text = f.read()

# Build the markov model.
#text_model = markovify.Text(text,state_size=2)

#load gpt2 model
tfsession, interact_model = run_model()
print('gpt2 model is loaded')

execution_path = os.getcwd()


def answer_story(bot, chat_id, text):
    answer = interact_model(tfsession, text)
    bot.send_message(chat_id, answer)
    return

def continue_sentence(beginning):
    print(beginning)
    return text_model.make_sentence_with_start(beginning)

@bot.message_handler(commands=['start'])
def send_welcome(message):
#   bot.reply_to(message, "You've been added to the Game. Send me your found objects to DEFINE or start a story.")
   bot.reply_to(message, "You've been added to the Game. You're exploring Moscow Metro system and its secrets. Type \"/metro\" to enter the underground.")

@bot.message_handler(commands=['metro'])
def start_handler(message):
    if not task.isRunning:
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, 'You\'re entering the Kropotkinskaya metro station. Where to go?', reply_markup=source_markup)
        bot.register_next_step_handler(msg, askStation)
        task.isRunning = True

def askStation(message):
    chat_id = message.chat.id
    text = message.text
    if 'Kropotkinskaya' in text:
        msg = bot.send_message(chat_id, 'You\'re at Kropotkinskaya metro station. You see an information stand and some artifact. Stay to examine or go to the neighbour stations.', reply_markup=source_markup2)
        bot.register_next_step_handler(msg, askKropotkinskaya) 
    elif 'Biblioteka imeni Lenina' in text:
        msg = bot.send_message(chat_id, 'You\'re at Biblioteka imeni Lenina metro station. Stay to examine, go to the neighbour stations or visit the library.')
        bot.register_next_step_handler(msg, askLibrary)         
        return     

def askKropotkinskaya(message):
    chat_id = message.chat.id
    text = message.text
    if 'info' in text:
        msg = bot.send_message(chat_id, 'The station was originally planned to serve the enormous Palace of the Soviets (Dvorets Sovetov), which was to rise nearby on the former site of the Cathedral of Christ the Saviour. Kropotkinskaya was therefore designed to be the largest and grandest station on the first line. However, the  Palace of the Soviets (Dvorets Sovetov) project was cancelled by Nikita Khrushchev in 1953, leaving the Metro station as the only part of the complex that was actually built.', reply_markup=source_markup2)
        bot.register_next_step_handler(msg, askStation) 
    elif 'artifact' in text:
        msg = bot.send_message(chat_id, 'It is a story about the Dark Driver. The legend has it, that in the 1980’s a train went up in flames on the orange Kaluzhsko–Rizhskaya line. Without wasting any time, the driver of the train threw himself in the fire to save as many passengers as he could. Eventually, the man managed to get everyone out of the burning car but died later on in a hospital because of severe thermal injuries. The superiors blamed the incident on him and his supposed lack of professional qualifications. Up to this day, the enraged ghost appeared in the tunnels in search of revenge.', reply_markup=source_markup2)
        msg = bot.send_message(chat_id, 'Where to go next?',reply_markup=source_markup)
        bot.register_next_step_handler(msg, askStation)         
        return


Biblioteka_artifact = 'It is a note from a Soviet diary dated year 1988. It says: "At 18.00 (I was leaving the metro station "Biblioteka im. Lenina") I saw a demonstration of refusers-Jews. A man of forty, everything is quite calculated - posters, types of people, texts in Russian and English, but something in this group of people who courageously stood in a crowd hostile to them (however, they got used to it, no one particularly paid attention) painfully miserable. Are there any secrets or circumstances to torture people! I cried. Yes ... I have not had tears for such a long time. Tears were joyful. It means alive, the soul has not yet become hardened.'

def askLibrary(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if 'library' in text:
        msg = bot.send_message(chat_id, 'You\'re at the Russian state library – former Lenin library. There are some secrets in Moscow Metro. You can do a research here. Or you know some rumours already?', reply_markup=source_markup3)
        bot.register_next_step_handler(msg, askLibraryInside)         
        return

def askLibraryInside(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if 'visitor' in text:
        msg = bot.send_message(chat_id, 'There\'s a very special type of the Leninka visitors – looking like hobos, holding a PhD, ready to chat. His name is Victor and he understood that you know something already. Share that with him and wait patiently – he was made in USSR so it takes time to go back to these times.')
        bot.register_next_step_handler(msg, text_handler)         
        return

#@bot.message_handler(content_types=['text'])
def text_handler(message):
    bot.reply_to(message, 'I know what you\'re talking about.')
    text = message.text.lower()
    chat_id = message.chat.id
    #try:
        #answer = continue_sentence(text.split(' ')[0])
    #   if not answer: raise RuntimeError
    #except:
    #   answer = text_model.make_sentence()
    
    while True:
        answer_story(bot, chat_id, text)
#    t = Thread(target=answer_story, args=(bot, chat_id, text))
#    t.start()
    #bot.register_next_step_handler(msg, text_handler)
    
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
    #   print(imagepath)
    #   print(detector)
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
    #       sent3 = continue_sentence(sent2[-1])
    #       bot.send_message(chat_id, sent3)
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

