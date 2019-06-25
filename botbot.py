# telegram
import telebot
import parser
from telebot import apihelper, types

TOKEN = '838747096:AAH1CHU_bdf-Lb8V_J18tt6ad9dXV4GhSb0'
#TOKEN = input("Enter token: ").strip("\n")
bot = telebot.TeleBot(TOKEN)
apihelper.proxy = {'https':'socks5://dante:hrenota@31.14.131.25:7777'}

# ai
#from imageai.Detection import ObjectDetection
import os, sys
#import markovify
sys.path.insert(1, './gpt2/src')
#sys.path.insert(1, './src/samples')
from interactive_conditional_samples import run_model
#python interactive_conditional_samples.py 
from threading import Thread

# game logic
import game
g = game.g
g.load_text_objects("artifacts.txt")
g.load_img_objects("image_artifacts")
g.load_json("stations.js")
#lines = game.load_json("https://github.com/agershun/mosmetro/blob/master/step1/stations.js")
g.load_names("names.txt")
#g.generate_npcs()
g.state_npcs()

def addButtons(*button_names):
    source_markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btns = []
    for bn in button_names: btns.append(types.KeyboardButton(bn))
    source_markup.add(*btns)
    return source_markup

"""
'Read the newspapers')
'Read the Soviet archives')
'Discuss the stories with an odd visitor')

class Task():
    isRunning = False
    mySource = ''
    myFilter = ''
    def __init__(self):
        return
task = Task()
"""

# motifs dataset
#with open("models/motifs_list.txt") as f:
#    text = f.read()

# Build the markov model.
#text_model = markovify.Text(text,state_size=2)

#load gpt2 model
#tfsession, interact_model = run_model()
#print('gpt2 model is loaded')

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
   bot.reply_to(message, "You've been added to the Game, " + message.from_user.username + ". Type \"/metro\" to enter the underground.")

@bot.message_handler(commands=['metro'])
def start_handler(message):
    p = game.Player(message.chat.id, message.from_user.username)
    ans = p.welcome()
    bot.reply_to(message, ans)
    ans = p.start()
    msg = bot.send_message(message.chat.id, ans, reply_markup=addButtons(*p.getActions()))
    bot.register_next_step_handler(msg, gameHandler)

def gameHandler(message):
    chat_id = message.chat.id
    text = message.text 
    p = g.players[chat_id]
    # getting game answer
    ans, objects, speechs = p.makeAction(text)
                
    # sending game answer
    msg = bot.send_message(chat_id, ans, reply_markup=addButtons(*p.getActions()))
    for speech in speechs:
        #txt = "**"+speech[0]+"**"+": __"+speech[1]+"__"
        txt = "__{1}__".format(*speech)
        bot.send_message(chat_id, txt, parse_mode="markdown")
    for obj in objects:
        if 'image' in obj.keys():
            img = obj['image']
            with open(img, "rb") as img_bin:
                bot.send_photo(chat_id, img_bin)
        if 'text' in obj.keys():
            txt = obj['text']
            bot.send_message(chat_id, txt)

    # new step
    #if p.dialogue:
    #    bot.register_next_step_handler(msg, dialogue_handler)
    if p.receivingPhoto:
        bot.register_next_step_handler(msg, handle_game_pics)
    else:
        bot.register_next_step_handler(msg, gameHandler)


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
def dialogue_handler(message):
    bot.reply_to(message, 'I\'m going to the archive. Wait for me.')
    text = message.text #.lower()
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
    


@bot.message_handler(content_types=['photo'])
def handle_game_pics(message): 
    chat_id = message.chat.id    
    print ('message.photo =', message.photo)
    file_info = bot.get_file(message.photo[-1].file_id)

    imagepath = os.path.join(execution_path , file_info.file_path)
    print ('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(imagepath, 'wb') as new_file:
        new_file.write(downloaded_file)
    p = g.players[chat_id]
    p.current_room.npcs[0].addObject({'image': imagepath})
    msg = bot.send_message(chat_id, "Thank you! I\'ll give to the next one.")
    p.receivingPhoto = False
    bot.register_next_step_handler(msg, gameHandler)

#@bot.message_handler(content_types=['photo'])
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

