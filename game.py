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
        return {p.name for p in self.npcs}
    
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
        self.d.update(self.listTransfers())
        self.d.update(self.line.listRooms())
        return self.d.keys()
        
        
    def getActions(self):
        self.actions = ['Read the information', 'Get list of stations to go']
        if self.listTransfers():
            self.actions.append('Get list of transfers')
        if self.listObjects():
            self.actions.append('Examine the objects')
        if self.listNPC():
            self.actions.append('Talk to a person')
        return self.actions
    
    def makeAction(self, action):
        imgs = []
        texts = []
        if action == 'Read the information':
            ans = str(self.info)
        elif action == 'Get list of stations to go':
            ans = "\n".join(self.line.listRooms().keys())
        elif action == 'Get list of transfers':
            ans = "\n".join(self.listTransfers().keys())
        elif action == 'Examine the objects':
            ans = "You see " + ("these objects" if len(self.objects)>1 else "this object") + ":"
            for obj in self.objects:
                if "image" in obj.keys():
                    imgs.append(obj["image"])
                elif "text" in obj.keys():
                    texts.append(obj["text"])
        elif action == 'Talk to a person':
            ...
        return (ans, imgs, texts)
    
    
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
    

def load_json(filename):
    import json
    with open(filename, "r") as jsondata:
        data = json.load(jsondata)
    lines = {}
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
    return lines

def load_text_objects(filename, stations):
    import random
    with open(filename, "r") as f:
        while True:
            l = f.readline()
            if not l: 
                 break
            s = random.choice(stations)
            s.addObject({'text': l})
    
def load_img_objects(filepath, stations):
    import random
    import os
    images = os.listdir(filepath)
    for img in images:
        s = random.choice(stations)
        s.addObject({'image': os.path.join(filepath,img)})
    