### warning
# this code is a ridiculous mess. dont even think about reading it.

# just think about this okay.
#   1) it's a relatively simple app, but it has almost 1000 lines of code
#   2) there is a warning not to read it, saying it's a mess
#   3) i wrote it, and i dont even understand it myself

# module imports
import json, requests, threading, ast, os, time
import tkinter as tk
from tkinter import ttk

# install argon2 if it's not installed yet, for logging in
import os, sys
try:
    from argon2 import low_level
except ImportError:
    os.system(f'{sys.executable} -m pip install argon2-cffi')
    from argon2 import low_level

# modules for the login feature
from hashlib import blake2b
from base64 import urlsafe_b64encode, b64encode, b64decode


# copypasted from https://github.com/Aedial/novelai-api, for logging in
def argon_hash(email: str, password: str, size: int, domain: str) -> str:
    pre_salt = password[:6] + email + domain

    # salt
    blake = blake2b(digest_size = 16)
    blake.update(pre_salt.encode())
    salt = blake.digest()

    raw = low_level.hash_secret_raw(password.encode(), salt, 2, int(2000000/1024), 1, size, low_level.Type.ID)
    hashed = urlsafe_b64encode(raw).decode()

    return hashed

# copypasted from https://github.com/Aedial/novelai-api, for logging in
def get_access_key(email: str, password: str) -> str:
    return argon_hash(email, password, 64, "novelai_data_access_key")[:64]

# uses argon_hash and get_access_key to get an authorization key from email and password, which is basically logging in.
def getAuth(email, password):
    accessKey = get_access_key(email, password)
    url = r"https://api.novelai.net/user/login"
    response = requests.request("POST", url, headers={'Content-Type': 'application/json'}, data = json.dumps({'key':accessKey}))

    if response.status_code != 201:
        print(email, password)
        exit('wrong username and/or password')
    
    content = response.content
    decodedContent = content.decode()
    decodedContent = decodedContent.replace("null", "0.0000")
    stringified = ast.literal_eval(decodedContent)
    
    auth = stringified['accessToken']
    return auth

def readTxt(fileName):
    with open(fileName, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents

def createTxt(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# styling
textSettings = {'bg':'black', 'insertbackground':'red', 'fg':'light blue', 'height':'9', 'font':('comic sans', '15')}
labelSettings = {'font':('comic sans', '10'), 'bg':'black', 'fg':'light blue'}

# login section
if 'login info.txt' in os.listdir(os.getcwd()):
    info = readTxt('login info.txt')
    email, password = map(lambda s:s.partition(':')[2], info.split('\n'))
else:
    email, password = 'goose@honk.ca', 'honk!let_me_in!'
if True:
    # lol
    
    loginWindow = tk.Tk()
    loginWindow.config(bg='black')
    
    label = tk.Label(loginWindow, text='please enter your email and password', **labelSettings)
    entries = []
    for string in email, password:
        entries.append(tk.Entry(loginWindow, width=30))
        entries[-1].insert(0, string)
        
    goose = tk.Text(loginWindow, fg='green', bg='black')
    goose.insert(1.0, '''
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@B5Y5#@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@J  . 7JYG@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@B  ^J5BBP#@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@&: ?@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@5 .B@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@~ ^#@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@&&#B~  ^#@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@GPB###BPJ7~:..     ^#@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@P7^...              ?@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@G7.                !@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@&5!:             ~#@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@G?~:         ^5@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@&Y7!:   .:!Y&@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@577!!YG&#B@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@GYP&@@@&GGPPP&@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@G@@@@@@@#BG#&@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@B5B#&&@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@YY5B&@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@&@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    '''[1:-1])
    
    i = tk.IntVar()
    i.set(1)
    c = tk.Checkbutton(loginWindow, text = "store login info in txt file for later", variable=i, **labelSettings, selectcolor='blue')
    
    def submit():
        global email, password, authorizationToken
        email, password = entries[0].get(), entries[1].get()
        authorizationToken = getAuth(email, password)
        
        if i.get() == 1:
            createTxt('login info.txt', f'email:{email}\npassword:{password}')

        loginWindow.destroy()
    
    btn = tk.Button(loginWindow, command=submit, text='click here or hit enter to submit', **labelSettings)
    loginWindow.bind('<Return>', lambda *args:submit())

    for w in [label, *entries, btn, c, goose]:
        w.pack()
    loginWindow.mainloop()






# an object for keeping track of choices as you make them, and a convenient .show() to print out various informations
# the choices in this app's case will be the multiple outputs you choose from
class Tree:
    def __init__(self):
        self.optionLists = []
        self.route = []
        self.history = {}

    def choose(self, optionList, choiceIndex):
        self.optionLists.append(optionList)
        self.route.append(choiceIndex)
    
    def select(self, moment, choiceIndex):
        return self.optionLists[moment][choiceIndex]
    
    def setHistory(self):
        history = {}
        for t, (options, choiceIndex) in enumerate(zip(self.optionLists, self.route)):
            history[t] = {
                'options':options,
                'choice':options[choiceIndex]
            }
        self.history = history
    
    def show(self, remakeHistory=1):
        seperator = ('---+++---')
        if remakeHistory:
            self.setHistory()
        print(seperator)
        print(f'optionLists: {self.optionLists}')
        print(f'route: {self.route}')
        
        print('history:\ntime\toptions\tchoice')
        for t in self.history.keys():
            print('\t'.join(map(str,[t]+list(self.history[t].values()))))
        print(seperator)


headers = {'Content-Type': 'application/json',
           'authorization': f'Bearer {authorizationToken}',
           }

prefixes = '''
vanilla
general_crossgenre
inspiration_crabsnailandmonkey
inspiration_mercantilewolfgirlromance
inspiration_nervegear
inspiration_thronewars
inspiration_witchatlevelcap
style_algernonblackwood
style_arthurconandoyle
style_edgarallanpoe
style_hplovecraft
style_julesverne
style_shridanlefanu
theme_19thcenturyromance
theme_actionarcheology
theme_ai
theme_airships
theme_childrens
theme_christmas
theme_darkfantasy
theme_dragons
theme_egypt
theme_generalfantasy
theme_history
theme_horror
theme_huntergatherer
theme_litrpg
theme_magicacademy
theme_magiclibrary
theme_mars
theme_medieval
theme_militaryscifi
theme_naval
theme_philosophy
theme_pirates
theme_poeticfantasy
theme_postapocalyptic
theme_rats
theme_romanceofthreekingdoms
theme_romanempire
theme_spaceopera
theme_superheroes
theme_textadventure
theme_valentines
theme_vikings
theme_westernromance
utility_lorebookgenerator
'''[1:-1].split('\n')

if 'storage' not in os.listdir(os.getcwd()):
    os.mkdir('storage')

def listToFile(list_arg, filename, overwrite = 0):
    if overwrite:
        mode = "w"
    else:
        mode = "x"
    with open(filename, mode) as f:
        json.dump(list_arg, f, indent=1)

def uniqueTime():
    return str(time.time()).replace('.', 'd')

# making calls with the NovelAI API, it generates text using an AI
def apiCall(payload):

    # for simulating the wait of an api call, to practice queueing and multi threading without actually using NAI's compute
    if 0:
        time.sleep(2)
        return payload

    # for making sure everything is working as expected.
    debug = True
    if debug:
        print({'payload':payload} ,'\n')

    url = "https://api.novelai.net/ai/generate"
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))

    if debug:
        print({'headers':headers} ,'\n')
    
    content = response.content
    
    if debug:
        print({'content':content} ,'\n')
    
    decodedContent = content.decode()
    decodedContent = decodedContent.replace("null", "0.0000")
    stringified = ast.literal_eval(decodedContent)
    
    output = stringified["output"]

    if 'storage' in os.listdir(os.getcwd()):
        listToFile({'payload':payload,'output':output}, os.getcwd()+'\\storage\\'+uniqueTime()+'.json')
    if debug:
        print('--------------------\n')
    return output

def textGrab(textWidget):
    text = textWidget.get(1.0, 'end')[:-1]
    return text

def textClear(widget):
    widget.delete(1.0, 'end')

def textInsert(widget, insertion):
    widget.insert(1.0, insertion)

def textAppend(widget, appendage):
    widget.insert('end', appendage)

# basic multithreading
def multiThread(function):
    threading.Thread(target=function).start()

def setTabTitle(nbIndex, tabIndex, title):
    notebooks[nbIndex].tab(tabIndex, text=title)

# styling
textSettings = {'bg':'black', 'insertbackground':'red', 'fg':'light blue', 'height':'9', 'font':('comic sans', '15'), 'insertbackground':'white'}
labelSettings = {'font':('comic sans', '10'), 'bg':'black', 'fg':'light blue'}
frameSettings = {'background':'black'}

root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(background = 'black')

tree = Tree()

def assemblePayload(settings, context):
    if '\n\n' in settings:
        settings = settings.partition('\n\n')[2]
    # uses a settings string (from the 'settings' tab and context to put together the payload for the API request

    # for turning the more convenient in-app names of parameters into the names that the API uses.
    settingsMapping = {
        'model':'model',
        'prefix':'module',
        'temperature':'temperature',
        'min_length':'minimum length',
        'max_length':'maximum length'
        }

    # creating a dictionary with the settings
    actualSettings = {}
    for line in settings.split('\n'):
        settingName, givenValue = line.split(':')
        
        for actualName, inAppName in settingsMapping.items():
            if inAppName == settingName:
                actualSettings[actualName] = givenValue

    # correct model names
    modelMapping = {
        'krake':'krake-v2',
        'euterpe':'euterpe-v2',
        'sigurd':'6B-v4',
        'calliope':'2.7B'
        }
    actualSettings['model'] = modelMapping[actualSettings['model']]

    # turning numbers into actual integers
    for string in ['temperature', 'min_length', 'max_length']:
        actualSettings[string] = int(actualSettings[string])

    # little convenience function
    get = lambda s:actualSettings[s]
    
    # the payload that the API will use to generate text
    payload = {
        'input':context,
        'model':get('model'),
        'parameters':{
            'use_string':True,
            'prefix':get('prefix'),
            'temperature':get('temperature'),
            'min_length':get('min_length'),
            'max_length':get('max_length')
            }
        }
    
    return payload

if 'personal settings.txt' in os.listdir(os.getcwd()):
    defaultSettings = readTxt('personal settings.txt')
else:
    defaultSettings = '''
for the model, type krake, euterpe, sigurd or calliope

model:calliope
module:theme_pirates
temperature:1
minimum length:1
maximum length:20
'''[1:-1]

if 'personal prompt.txt' in os.listdir(os.getcwd()):
    defaultPrompt = readTxt('personal prompt.txt')
else:
    defaultPrompt = '''
This is a story about a lone adventurer,
'''[1:-1]

partialD = {'showing':True, 'string':defaultPrompt}
fullD = {'showing':False, 'string':defaultPrompt}
contextBlueprint = {'beginning':[], 'middle':[partialD['string']], 'end':[]}
lorebookStrings = {}

# root --> frame --> notebook (containing tabs) --> text, parameters
mainFrame = tk.Frame(root, **frameSettings)
mainNb = ttk.Notebook(mainFrame)

# ttl.Notebook styling section. if it is badly written, it's because I randomly copied and tried some stuff until it worked. (which can honestly be said about all of my code lol)
style = ttk.Style()
# setting colors
tkinterDefaultColor = '#F0F0F0'
normalColor = 'black'
textColor = 'light blue'
# a helpful dictionary to use with style.theme_create()
styleHelper = {
    'parent notebook':{
        'background':normalColor
        },
    'tab':{
        'default':{
            'background':tkinterDefaultColor,
            'text':normalColor,
            },
        'selected':{
            'background':normalColor,
            'text':textColor
            }
        }
    }
# actually setting the style of the notebook and its tabs
style.theme_create("style name",
                   settings={
                       "TNotebook":{
                           "configure":{
                               "background":styleHelper['parent notebook']['background']
                               }
                           },
                       "TNotebook.Tab": {
                           "configure":{
                               "background":styleHelper['tab']['default']['background'],
                               "foreground":styleHelper['tab']['default']['text'],
                               },
                           "map":{
                               "background":[("selected", styleHelper['tab']['selected']['background'])],
                               "foreground":[('selected', styleHelper['tab']['selected']['text'])]
                               }
                           }
                       }
                   )

style.theme_use("style name")

helpfulTab = tk.Text(mainNb, **textSettings)
experimental = tk.Text(mainNb, **textSettings)
experimentalOutbox = tk.Text(mainNb, **textSettings)
text = tk.Text(mainNb, **textSettings)
settingsText = tk.Text(mainNb, **textSettings)
mainBtn = tk.Button(mainFrame, text='multi generate (f3 works too)') # I will set the command down below, after defining multiGenerate
mainNb.add(text, text='  partial context  ')
mainNb.add(settingsText, text='  settings  ')
#mainNb.add(experimental, text='  experimental  ')
#mainNb.add(experimentalOutbox, text='  outbox  ')
mainNb.add(helpfulTab, text='  helpful stuff  ')
textInsert(helpfulTab, '''
~~~~ hotkeys, code help, module names ~~~~

hotkeys:
Esc: register prompt changes, insert lorebook stuff
F3: multi generate
f12: store lorebook in the 'storage' folder (though this happens automatically when you generate or close the app)
left alt: toggle between seeing the full prompt and only the partial prompt. (without lorebook entries)
    never edit the full prompt. i dont know what will happen.
F1, F2, F10: nothing monkaS

lorebook code help:
keys:key1,key2,key3 <-- is just like in NAI. entry will be inserted in front of context

active:jack,mary <-- will activate if any one of those entries is active
active:jack+mary <-- will activate if BOTH of those entries are active
active:!jack+mary+doggo <-- if jack is not active and mary is active and doggo is active
active:jack,!mary,!doggo <-- if any of the conditions are true, so jack is active, or mary is inactive, or doggo is inactive

order:1 <-- order of checking. 0 if unspecific. put this at least at 1 if you use 'active'. order is normally 0,
    but if you want this code's logic to be applied after other lorebooks' checks are done, make it higher than those lorebooks.

suppress:jack,mary <-- if the entry that this code belongs to is active, it will suppress entries named jack and mary.

-- active and keys are not meant to be used in the same code, idk what will happen if you do --
-- ! and + only work on 'active'. also you cant use both + and , in the same entry --

!! remember !!
press Escape after making a change to make it register. either in a lorebook or in the prompt textbox

'''[1:-1] + '\n\nmodule names:\n' + '\n'.join(prefixes))

miniCodeParameters = ['inbox', 'edit', 'function', 'args', 'outbox']
textInsert(experimental, '\n'.join(map(lambda s:s+':', miniCodeParameters)))

textInsert(settingsText, defaultSettings)
textInsert(text, defaultPrompt)

hotkeys = {}

mainFrame.pack(pady=5)
mainNb.grid(row=0, column=1)
mainBtn.grid(row=1, column=1)

#parameters.pack()
#text.pack()


multiAmount = 3

def expShorten(args):
    previous = textGrab(text)
    nxt = previous[1:]
    textClear(text)
    textInsert(text, nxt)
    textInsert(text, ''.join(args))

def expReplace(args):
    previous = textGrab(text)
    nxt = previous.replace(args[0], args[1])
    textClear(text)
    textInsert(text, nxt)

def exp1():
    l = textGrab(lorebook)
    print(l)

def expF():
    interpretation = {k:v for k,v in map( lambda s:s.split(':'),textGrab(experimental).split('\n') )}
    print(interpretation)
    
    inboxes = [text, *[w for w in tempWidgets if w == tk.Text()]]
    outboxes = [experimentalOutbox]
    editables = [*inboxes, *outboxes]
    
    stringToFunction = {'shorten':expShorten,
                        'replace':expReplace}
    
    # functions you need to call to get the right thing. so do conversions[key]() to get the right value.
    # for example conversions['functions']() will return the function that i mapped to a specific string

    def convInbox():
        inbox = interpretation['inbox']
        if inbox == '':
            return None
        else:
            return inboxes[int(inbox)]
    '''
    conversions = {'inbox':lambda:inboxes[ int(interpretation['inbox']) ],
                   'edit':lambda:outboxes[ int(editables['edit']) ],
                   'function':lambda:stringToFunction[interpretation['function']],
                   'args':lambda:interpretation['args'].split('$$'),
                   'outbox':lambda:outboxes[ int(interpretation['outbox']) ]
                   }
    '''
    
    values = {k:conversions[k]() for k in conversions.keys()}
    # for easy selection from values
    shortened = {'in':'inbox', 'fun':'function', 'args':'args', 'out':'outbox', 'ed':'edit'}
    sel = lambda short:values[shortened[short]]

    # pass arguments to the designated function
    sel('fun')(sel('args'))

hotkeys['F10'] = expF

tempTextWidgets = []
tempWidgets = []
def clearTempWidgets():
    global tempTextWidgets, tempWidgets
    for w in tempWidgets:
        w.destroy()
    tempWidgets = []
    tempTextWidgets = []

def storeLorebooks():
    if 'storage' in os.listdir(os.getcwd()):
        lorebook = list(map(lambda l:{
            'title':l[2],
            'entry':textGrab(l[0]),
            'code':textGrab(l[1])
            },entries.values()))
        listToFile(lorebook, os.getcwd()+'//storage//LB___'+uniqueTime())

hotkeys['F12'] = storeLorebooks
contextHistory = []
def multiGenerate(context):
    storeLorebooks()
    contextHistory.append(textGrab(text))
    clearTempWidgets()
    tree.choose([context],0)
    queue = []
    for i in range(multiAmount):
        settings = textGrab(settingsText)
        payload = assemblePayload(settings, context)
        queue.append(removeArguments(printResponse, [payload]))
    executeQueue(queue)

def onF3():
    global contextBlueprint
    contextBlueprint['middle'] = [textGrab(text)]
    applyBlueprint()
    multiGenerate(fullPrompt)
    
hotkeys['F3'] = onF3
mainBtn.config(command = onF3)

def onKeyPress(event):
    pressed = event.keysym
    if pressed in hotkeys:
        hotkeys[pressed]()

root.bind('<KeyRelease>', onKeyPress)

def onMouseEnter(event):
    return 0
    widget = event.widget
    if widget in tempTextWidgets:
        widget.config(bg='green')
root.bind('<ButtonPress-1>', onMouseEnter)



def applyBlueprint():
    global partialPrompt, fullPrompt, partialD, fullD
    
    activatedEntries = []
    
    sections = {'beginning':'', 'middle':'', 'end':''}
    for key, section in contextBlueprint.items():
        for string in section:
            if len(string) == 0:
                continue
            if string[0] == '$':
                title = string[1:]
                if title in toSuppress:
                    continue
                if title not in activatedEntries:
                    activatedEntries.append(title)
                    string = lorebookStrings[title]
                else:
                    continue
            sections[key] += string

    partialPrompt = sections['middle']
    fullPrompt = ''.join(list(sections.values()))
    partialD['string'] = partialPrompt
    fullD['string'] = fullPrompt
    #print('p:',partialD,'f:',fullD)

def printResponse(payload):
    # this is the only place in the code where an API call is made.
    
    global contextBlueprint
    output = apiCall(payload)
    
    f = tk.Frame(root, borderwidth=5, bg='black')
    tempWidgets.append(f)
    
    t = tk.Text(f, **textSettings)
    tempWidgets.append(t)
    tempTextWidgets.append(t)
    
    t.config(height=5)
    t.insert(1.0, output)
    
    def bf():
        choiceIndex = tempTextWidgets.index(t)
        
        oldPrompt = partialPrompt
        outputOptions = list(map(lambda w:textGrab(w), tempTextWidgets))
        tree.choose(outputOptions, choiceIndex)

        #print('full:', fullPrompt)
        chosenOutput = textGrab(t)
        #print('chosen:', chosenOutput)

        textAppend(text, chosenOutput)
        
        contextBlueprint['middle'].append(chosenOutput)

        applyBlueprint()

        #print('full:', fullPrompt, '\n')

        multiGenerate(fullPrompt)
        clearTempWidgets()
        
    b = tk.Button(f, text='choose', command=lambda:bf())
    tempWidgets.append(b)
    
    for w in (f, t, b):
        if w == f:
            options = {'pady':5}
        else:
            options = {}
        w.pack(**options)

def removeArguments(function, args=[], kwargs={}):
    # returns a function without arguments, so basically a specific 'version' of that function, with those arguments frozen
    return lambda:function(*args, **kwargs)

done = True
def executeQueue(queue):
    def ex():
        global done
        done = False
        for f in queue:
            f()
        done = True
    if done:
        multiThread(ex)
    else:
        print('wait')

hotkeys['F2'] = lambda:tree.show()

root2 = tk.Toplevel()
root2.title('lorebook')

lbFrame = tk.Frame(root2, **frameSettings)
lbContainer = ttk.Notebook(lbFrame)

lbFrame.pack()
lbContainer.grid(row=0, columnspan = 10)

def addLb():
    # cant have an empty title
    title = titleEntry.get()
    if len(title) == 0:
        return 0

    #cant have the same title twice
    title = titleEntry.get()
    for l in entries.values():
        if l[2] == title:
            return 0
    
    addEntry({'title':title, 'entry':'', 'code':''})

def deleteLb():
    toDestroy = None
    title = titleEntry.get()
    for l in entries.values():
        if l[2] == title:
            toDestroy = l[3]

    if toDestroy != None:
        l[3].destroy()
        del entries[title]

newLbButton = tk.Button(lbFrame, text='add lorebook (click or press enter)', command=addLb)
titleEntry = tk.Entry(lbFrame)
titleEntry.bind('<Return>', lambda *args:addLb())
deleteLbButton = tk.Button(lbFrame, text='delete lorebook (type name and press button)', command=deleteLb)

for n, w in enumerate([deleteLbButton, newLbButton, titleEntry]):
    w.grid(row=1, column=n)

entries = {}
def addEntry(d):
    global lorebookStrings
    title = d['title']
    entry = d['entry']
    code = d['code']
    lorebookStrings[title] = entry
    
    f = tk.Frame(lbContainer, **frameSettings)
    entries[title] = [tk.Text(f, **textSettings), tk.Text(f, **textSettings), title, f]
    entries[title][0].pack()
    textInsert(entries[title][0], entry)
    entries[title][1].pack()
    textInsert(entries[title][1], code)
    lbContainer.add(f, text=f'  {d["title"]}  ')

activeEntries = []
defaultEntries = [
    {
        'title':'bunnies',
        'entry':'bunnies are running over the hills\n',
        'code':'keys:bunnies,hills'
        },
    {
        'title':'uw0tm8',
        'entry':'wats goin on over ere\n',
        'code':'active:rabbits\norder:1'
        },
    {
        'title':'rabbits',
        'entry':'rabbits prefer to just eat carrots though\n',
        'code':'keys:rabbits,carrots'
        }
    ]

def openListFile(filename):
    with open(filename, "r") as f:
        lst = json.load(f)
    return lst

names = [name for name in os.listdir(os.getcwd()) if 'LB___' in name]
if len(names) > 0:
    defaultEntries = openListFile(names[0])

tuple(map(addEntry, defaultEntries))

def convertCode(code):
    codeD = {}
    for line in code.split('\n'):
        parameter, _, values = line.partition(':')
        codeD[parameter] = values

    defaults = {
        'order':{
            'value':0,
            'conv':int
            },
        'position':{
            'value':'start',
            'conv':str
            }
        }

    for k,v in defaults.items():
        if k not in codeD.keys():
            codeD[k] = v['value']
        codeD[k] = v['conv'](codeD[k])
    
    return codeD

def runCode(codeList):
    global contextBlueprint, toSuppress
    contextBlueprint = {'beginning':[], 'middle':[partialD['string']], 'end':[]}
    context = partialD['string']
    codeList = sorted(codeList, key=lambda d:d['code']['order'])
    activeEntries = []
    toSuppress = []
    for stringList in contextBlueprint.values():
        for string in stringList:
            if string[0] == '$':
                title = string[1:]
                activeEntries.append(title)

    def evalSuppress(string, activeEntries, context, title):
        global toSuppress
        if len(string) == 0:
            return False
        if title not in activeEntries:
            return False
        
        for arg in string.split(','):
            toSuppress.append(arg)
        return True
    
    def evalKeys(string, activeEntries, context, title):
        #print(f'context: {context}')
        if len(string) == 0:
            return False
        for arg in string.split(','):
            if arg in context:
                return True
        return False

    def evalActive(string, activeEntries, context, title):
        # make sure + and , are not both used
        if "+" in string and "," in string:
            return False
        
        # split into args
        if '+' in string:
            args = string.split('+')
        elif ',' in string:
            args = string.split(',')
        elif len(string) == 0:
            return False
        else:
            if string[0] == '!':
                return string[1:] not in activeEntries
            else:
                return string in activeEntries
        
        # perform 'and' logic
        if '+' in string:
            for arg in args:
                if arg[0] == '!':
                    if arg[1:] in activeEntries:
                        return False
                else:
                    if arg not in activeEntries:
                        return False
            return True
        
        # perform 'or' logic
        elif "," in string:
            for arg in args:
                if arg[0] == '!':
                    if arg[1:] not in activeEntries:
                        return True
                else:
                    if arg in activeEntries:
                        return True
            return False

    currentOrder = 0
    toAdd = []
    def evalToAdd(currentContext, activeEntries):
        # this one just edits contextBlueprint
        global contextBlueprint
        for position, string, title in toAdd:
            if position == 'start':
                contextBlueprint['beginning'].append(f'${title}')
            if position == 'end':
                contextBlueprint['end'].append(f'${title}')
            activeEntries.append(title)
        applyBlueprint()

    for d in codeList:
        if 'skip' in d['code'].keys():
            if d['code']['skip'] == 'yes':
                continue
        
        title = d['title']
        entry = d['entry']
        code = d['code']
        
        order = code['order']
        position = code['position']
        
        if order > currentOrder:
            evalToAdd(context, activeEntries)
            context = fullPrompt
            toAdd = []
            currentOrder = order

        for parameter in ['keys', 'active', 'suppress']:
            # maps a function name (as used from within the gui) to a python function
            parToFunction = {'keys':evalKeys, 'active':evalActive, 'suppress':evalSuppress}
            if parameter in code.keys():
                activate = parToFunction[parameter](code[parameter], activeEntries, context, title)
                if activate:
                    activeEntries.append(title)
                    toAdd.append([position, entry, title])

        if activate:
            for l in entries.values():
                break
                if l[2] == title:
                    textAppend(l[1], '\nskip:yes')
        
        evalToAdd(context, activeEntries)
        context = fullPrompt
        
        toAdd = []

    activeEntries = []

def applyLorebookCode():
    global partialD, contextBlueprint, partialPrompt, lorebookStrings, fullPrompt, fullD
    if root.focus_get() == text:
        partialD['string'] = textGrab(text)
        partialPrompt = partialD['string']
        contextBlueprint['middle'] = [partialPrompt]
    
    for title, lst in entries.items():
        break
        entry = textGrab(lst[0])
        code = textGrab(lst[1])

    codeList = []
    for k,v in entries.items():
        entry, code, title = textGrab(v[0]), textGrab(v[1]), v[2]
        codeD = convertCode(code)
        codeList.append({'title':title, 'entry':entry, 'code':codeD})
        lorebookStrings[title] = entry
    applyBlueprint()
    runCode(codeList)
    contextHistory.append('\n---\n' + textGrab(text) + '\n---\n')
        

def viewContextHistory():
    print('******\n'+
          'This is a context history. It is updated every time you apply the lorebook code or generate text.\n\n'+
          '\n'.join(contextHistory)+
          '\n******'
          )

def togglePrompt(to=None):
    global partialD, fullD, contextBlueprint
    #print(f'partial: {partialD}, full: {fullD}')
    c1, c2 = partialD['showing'], fullD['showing']
    if c1 and c2 or (not c1 and not c2):
        exit('conditions have to be mutually exclusive dawg (inside def togglePrompt)')
        
    if partialD['showing'] == True:
        if to == 'partial':
            return 0
        textClear(text)
        partialD['showing'] = False
        textInsert(text, fullD['string'])
        fullD['showing'] = True
        mainNb.tab(text, text='  full context       ')
    else:
        if to == 'full':
            return 0
        textClear(text)
        fullD['showing'] = False
        textInsert(text, partialD['string'])
        partialD['showing'] = True
        mainNb.tab(text, text='  partial context  ')
    

hotkeys['Escape'] = applyLorebookCode
hotkeys['F1'] = viewContextHistory

root2.bind('<KeyRelease>', onKeyPress)

def onEnter(event):
    # makes sure that if the mouse is on the lorebook window, you see the full prompt,
    #   and if's on the main window, you see the partial prompt, aka 'story text'
    w = event.widget
    if w == root:
        togglePrompt('partial')
    if w == root2:
        togglePrompt('full')

root.bind('<Enter>', onEnter)
root2.bind('<Enter>', onEnter)

applyBlueprint()
root.mainloop()

















