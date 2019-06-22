import json
import random
import os
import Levenshtein as lev

def checkWordsInText(word_list, text):
    for w in word_list:
        if w in text: return w
    else:
        return False

class Game:
    def __init__(self):
        self.player = Player()
        self.current_room = None
        self.start_room = None
        self.lines = {}
        self.stations = []
        self.tmp_objects = []
        self.tmp_names = []
        self.second_level = False
        self.dialogue = False
    
    def load_json(self, filename):
        lines = self.lines
        with open(filename, "r", encoding='utf-8') as jsondata:
            data = json.load(jsondata)
        for d in data:
            ln = d["line"]
            if ln not in lines.keys():
                l = Line(ln)
                lines[ln] = l
            else:
                l = lines[ln]
            s = Station(d["name"], l)
            s.info["opened"] = d["opened"]
            s.info["type"] = d["type"]
            s.info["elevation"] = d["elevation"]
        for d in data:
            ln = d["line"]
            sn = d["name"]
            s = lines[ln][sn]
            tsfr = d["transfer"]
            for t in tsfr:
                ts = lines[t["line"]][t["name"]]
                s.addTransfer(ts)
        self.stations = [r for l in self.lines.values() for r in l.rooms]
        self.start_room = self.lines["1"]["Kropotkinskaya"]

    def load_text_objects(self, filename):
        with open(filename, "r", encoding='utf-8') as f:
            while True:
                l = f.readline()
                if not l: 
                     break
                self.tmp_objects.append({'text': l})
    
    def load_img_objects(self, filepath):
        images = os.listdir(filepath)
        for img in images:
            self.tmp_objects.append({'image': os.path.join(filepath,img)})
    
    def load_names(self, filename):
        with open(filename, "r", encoding='utf-8') as f:
            while True:
                l = f.readline()
                if not l: 
                     break
                name = l.split(",")[0]
                info = l[len(name + ', '):]
                self.tmp_names.append((name, info))
            
    def generate_npcs(self, amount=50):
        for i in range(amount):
            npc_name = random.choice(self.tmp_names)
            npc_class = random.choice(list(NPC.classes.keys()))
            npc_object = random.choice(self.tmp_objects)
            npc_location = random.choice(self.stations)
            n = NPC(*npc_name, npc_class)
            n.addObject(npc_object)
            npc_location.addNPC(n)
            
    
    def load_NPCs(self, filename):
        ...
     #add NPCs to the corresponding stations with corresponding objects from json   
        
    def start(self):
        return self.enterRoom(self.start_room)
    
    def enterRoom(self, room):
        self.current_room = room
        return self.current_room.get_description()
    
    def welcomeMessage(self):
        return "You're exploring Moscow Metro system and its secrets. You can travel to any station on the current line or transfer to other lines on the hub stations. The artifacts that you\'re collecting can drive you even further."
    
    def wrongMessage(self):
        return 'You can travel to any station on the current line or transfer to other lines on the hub stations.'
    
    def tryNextRoom(self, text):
        w = checkWordsInText(self.current_room.keys(), text)
        if w:
            next_room = self.current_room[w]
            return self.enterRoom(next_room)
        else:
            return None
            
    def secondLevel(self):
        com = self.player.isEnoughCommunication()
        if com and not self.second_level:
            library = Room("Russian State Library", Line("Library"))
            self.lines["1"]["Biblioteka Imeni Lenina"].addTransfer(library)
            #char = NPC("Solomon Nikritin", "avant-garde artist", "Projectionist, creator of Tectonics – organisational science.")
            char = NPC("The Archivist", "AI", "Embodied mind.")
            char.addObject({"text": "What do you think about the Russian Kosmotechniks?"})
            #char.addObject({"text": "It is abundantly clear that everything that surrounds us consists of bodies and phenomena, and all bodies and phenomena are learned by us in so far as we are able to distinguish them from everything other things, since they are a closed whole and at the same time consist of parts. It is in the binding, in the assembly of these parts into a closed whole (that is, in the assembly) and in the separation, in the disassembly of the closed assembly (that is, in dismantling) all conceivable work is manifested. It is necessary to find some closed figure, which, when dissected into many parts, would not lose its basic qualities, could become a necessary unit of measure and help solve the problems of Tectonics."})
            library.addNPC(char)
            self.second_level = True
        return com
    
    acts = {'talk': 'Talk to ',
            'info': 'Read the information',
            'line': 'Get list of stations to go',
            'trns': 'Get list of transfers'}
    
    def getActions(self):
        actions = ['Read the information', 'Get list of stations to go']
        if self.current_room.listTransfers():
            actions.append('Get list of transfers')
        if self.current_room.listObjects():
            actions.append('Examine the objects')
        if self.current_room.listNPC():
            for name in self.current_room.listNPC().keys():
                actions.append('Talk to ' + name)
        if self.player.inventory:
             actions.append('List objects collected')
        if self.player.diary:
             actions.append('List people met')
        if self.secondLevel():
            actions.append('Go to the Biblioteka Imeni Lenina')
        return actions
    
    def makeAction(self, action):
        ans = self.tryNextRoom(action)
        objects = []
        speechs = []
        if action == 'Read the information':
            ans = str(self.current_room.info)
        elif action == 'Get list of stations to go':
            ans = "\n".join(self.current_room.line.listRooms().keys())
        elif action == 'Get list of transfers':
            ans = "\n".join(self.current_room.listTransfers().keys())
        #elif action == 'Examine the objects':
        #    ans = "You see " + ("these objects" if len(self.objects)>1 else "this object") + ":"
        #    for obj in self.objects:
        #        if "image" in obj.keys():
        #            imgs.append(obj["image"])
        #        elif "text" in obj.keys():
        #            speechs.append(obj["text"])
        elif action.startswith(Game.acts["talk"]):
            name = action[len(Game.acts["talk"]):]
            npc = self.current_room.listNPC()[name]
            ans = npc.getInfo()
            speech, obj = npc.objectInfo()
            if action == "Talk to The Archivist": self.dialogue = True
            speechs.append((name, speech))
            objects.append(obj)
            self.player.diary.append(npc)
            self.player.inventory.append(obj)

            
        elif action == 'List objects collected':
            ans = "You found these objects while exploring the Metro:"
            imgs = [z["image"] for z in self.player.inventory]
        elif action == 'List people met':
            ans = "You met these people on your way: \n" + '\n'.join([z.name + ' ' + z.npc_class for z in self.player.diary])
        if not ans: ans = self.wrongMessage()
        return (ans, objects, speechs)

 

class Line:
    def __init__(self, name):
        self.name = name
        self.rooms = []
        
    def addRoom(self, room):
        self.rooms.append(room)
        
    def listRooms(self):
        return {r.name:r for r in self.rooms}
        
    def __str__(self):
        return "Line: " + self.name
        
    def __getitem__(self, r):
        return self.listRooms()[r]

class Room:
    def __init__(self, name, line):
        self.name = name
        self.info = {}
        self.objects = []
        self.trnsfs = []
        self.npcs = []
        self.line = line
        self.line.addRoom(self)
    
    def addTransfer(self, trnsf_station):
        self.trnsfs.append(trnsf_station)
    
    def addNPC(self, npc):
        self.npcs.append(npc)
        
    def addObject(self, obj):
        self.objects.append(obj)
        
    def listTransfers(self):
        return {r.name:r for r in self.trnsfs}
            
    def listObjects(self):
        return self.objects
        
    def listNPC(self):
        return {p.name:p for p in self.npcs}
    
    def __str__(self):
        r = [self.name, str(self.info), 
             "Objects:\n\n"+"\n".join(self.objects),
             "NPCs:\n\n"+"\n".join(self.npcs),
             "Transfer: "+", ".join(self.listTransfers().keys()),
             str(self.line)]
        return "\n\n====\n\n".join(r)
        
    def __getitem__(self, r):
        self.keys()
        return self.d[r]
    
    def keys(self):
        self.d = {}
        self.d.update(self.line.listRooms())
        self.d.update(self.listTransfers())
        return self.d.keys()
            
    def get_description(self):
        ...


class Station(Room):
    def get_description(self):
        d = "You\'re at " + self.name + " metro station. You see an information stand" +\
        (" and some artifact" if self.objects else "") +\
        (" and person" if self.npcs else "") +\
        ". Stay to examine or go to the neighbour stations."
        return d
    
class Station2(Station):
    ...
    

class NPC:
    classes = {
    "guard": "",
    "conductor": "",
    "writer": "",
    "scientist": "",
    "programmer": "",
    "translator": ""
    }
    def __init__(self, name, info, npc_class):
        self.name = name
        self.npc_class = npc_class
        self.objects = []
        self.info = info
    
    def getInfo(self):
        welcome = "You met " + self.npc_class + " " + self.name + ". Known as " + self.info 
        #info = NPC.classes[self.npc_class]
        return welcome #+ " " + info
    
    def objectInfo(self):
        text = "\"I have something for you.\"" if self.objects else "I don't have anything for you."
        return (text, self.objects[-1] if self.objects else None)
    
    def addObject(self, obj):
        self.objects.append(obj)
    
    def takeLastObject(self):
        return self.objects.pop(-1)
    
class Player:
    def __init__(self):
        self.inventory = []
        self.diary = []
    
    def addObjectFromNPC(self, obj, npc):
        self.inventory.append(obj)
        self.diary.append(npc)
    
    def isEnoughCommunication(self):
        #return True
        return len(self.diary) >= 2
    