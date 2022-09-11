# module imports
import json, requests, threading, ast, os, time
import tkinter as tk
from tkinter import ttk

# modules for the login feature
from hashlib import blake2b
from base64 import urlsafe_b64encode, b64encode, b64decode
from argon2 import low_level

# copypasted from Aedial's code, for logging in
def argon_hash(email: str, password: str, size: int, domain: str) -> str:
    pre_salt = password[:6] + email + domain

    # salt
    blake = blake2b(digest_size = 16)
    blake.update(pre_salt.encode())
    salt = blake.digest()

    raw = low_level.hash_secret_raw(password.encode(), salt, 2, int(2000000/1024), 1, size, low_level.Type.ID)
    hashed = urlsafe_b64encode(raw).decode()

    return hashed

# copypasted from Aedial's code, for logging in
def get_access_key(email: str, password: str) -> str:
    return argon_hash(email, password, 64, "novelai_data_access_key")[:64]

# uses argon_hash and get_access_key to get an authorization key from email and password, which is basically logging in.
def getAuth(email, password):
    accessKey = get_access_key(email, password)
    url = r"https://api.novelai.net/user/login"
    response = requests.request("POST", url, headers={'Content-Type': 'application/json'}, data = json.dumps({'key':accessKey}))

    if response.status_code != 201:
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
        print(self.optionLists, self.route)
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
       
email, password = map(lambda s:s.partition(':')[2], readTxt('login info.txt').split('\n'))
authorizationToken = getAuth(email, password)

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

    # for making sure everything is working as expected. a bit below is another debug bit.
    debug = True
    if debug:
        print({'payload':payload} ,'\n')

    url = "https://api.novelai.net/ai/generate"
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))

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
textSettings = {'bg':'black', 'insertbackground':'red', 'fg':'light blue', 'height':'9', 'font':('comic sans', '15')}
labelSettings = {'font':('comic sans', '10'), 'bg':'black', 'fg':'light blue'}

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

model:sigurd
module:vanilla
temperature:1
minimum length:1
maximum length:100
'''[1:-1]

if 'personal settings.txt' in os.listdir(os.getcwd()):
    defaultPrompt = readTxt('personal prompt.txt')
else:
    defaultPrompt = '''
This is a story about a lone adventurer,
'''[1:-1]

# root --> frame --> notebook (containing tabs) --> text, parameters
mainFrame = tk.Frame(root, bg='black')
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

experimental = tk.Text(mainNb, **textSettings)
experimentalOutbox = tk.Text(mainNb, **textSettings)
text = tk.Text(mainNb, **textSettings)
settingsText = tk.Text(mainNb, **textSettings)
mainBtn = tk.Button(mainFrame, text='multi generate (f3 works too)') # I will set the command down below, after defining multiGenerate
mainNb.add(text, text='initial prompt')
mainNb.add(settingsText, text='settings')
mainNb.add(experimental, text='experimental')
mainNb.add(experimentalOutbox, text='outbox')

miniCodeParameters = ['input', 'edit', 'function', 'args', 'outbox']
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

def expF():
    interpretation = {k:v for k,v in map( lambda s:s.split(':'),textGrab(experimental).split('\n') )}

    # functions you need to call to get the right thing. so do conversions[key]() to get the right value.
    # for example conversions['functions']() will return the function that i mapped to a specific string
    stringToFunction = {'shorten':expShorten,
                        'replace':expReplace}

    inboxes = [text, *[w for w in tempWidgets if w == tk.Text()]]
    outboxes = experimentalOutbox
    editables = [*inboxes, *outboxes]
    
    conversions = {'inbox':lambda:accessibleWidgets[ int(interpretation['inbox']) ],
                   'edit':lambda:outboxes[ int(editables['edit']) ],
                   'function':lambda:stringToFunction[interpretation['function']],
                   'args':lambda:interpretation['args'].split('$$'),
                   'outbox':lambda:outboxes[ int(interpretation['outbox']) ]
                   }
    
    values = {k:conversions[k]() for k in conversions.keys()}
    # for easy selection from values
    shortened = {'in':'inbox', 'fun':'function', 'args':'args', 'out':'outbox', 'ed':'edit'}
    sel = lambda short:values[shortened[short]]

    # pass arguments to the designated function
    sel('fun')(sel('args'))

root.bind('<Escape>', lambda *args:expF())

tempTextWidgets = []
tempWidgets = []
def clearTempWidgets():
    global tempTextWidgets, tempWidgets
    for w in tempWidgets:
        w.destroy()
    tempWidgets = []
    tempTextWidgets = []

def multiGenerate(context):
    clearTempWidgets()
    tree.choose([context],0)
    queue = []
    for i in range(multiAmount):
        settings = textGrab(settingsText)
        payload = assemblePayload(settings, context)
        queue.append(removeArguments(printResponse, [payload]))
    executeQueue(queue)
hotkeys['F3'] = lambda:multiGenerate(textGrab(text))
mainBtn.config(command = lambda:multiGenerate(textGrab(text)))

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

def printResponse(payload):
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
        
        oldPrompt = textGrab(text)
        outputOptions = list(map(lambda w:textGrab(w), tempTextWidgets))
        tree.choose(outputOptions, choiceIndex)
        
        chosenOutput = textGrab(t)
        textAppend(text, chosenOutput)
        newPrompt = textGrab(text)

        multiGenerate(newPrompt)
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
    # returns a function without arguments
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

root.mainloop()

















