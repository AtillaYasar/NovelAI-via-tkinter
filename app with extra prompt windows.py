# if you dont want to log in via the app every time, set login to False and put your authorization token here, after printing them
login = True
printAuthorization = False
authorizationToken = 'Bearer a_secret_string'

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

def openListFile(filename):
    with open(filename, "r") as f:
        lst = json.load(f)
    return lst

# styling
textSettings = {'bg':'black', 'insertbackground':'red', 'fg':'light blue', 'height':'9', 'font':('comic sans', '11')}
labelSettings = {'font':('comic sans', '10'), 'bg':'black', 'fg':'light blue'}


# login is set at the top, for convenience
# if you set it to False, you have to put the authorization token up there or it won't work
if login == True:
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
           'authorization': f'Bearer {authorizationToken}'
           }
# in case you want to skip the login section and manually put the header in the code
if printAuthorization:
    print(f"your authorization token is: {headers['authorization']}")

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

# making calls with the NovelAI API, and storing results. (it generates text using an AI)
def apiCall(payload, storeStuff=1):

    # for simulating the wait of an api call, to practice queueing and multi threading without actually using NAI's compute
    if 0:
        time.sleep(2)
        return payload

    # for making sure everything is working as expected.
    debug = False
    if debug:
        print({'payload':payload} ,'\n')

    url = "https://api.novelai.net/ai/generate"
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    
    content = response.content
    
    if debug:
        print({'content':content} ,'\n')
    
    decodedContent = content.decode()
    decodedContent = decodedContent.replace("null", "0.0000")
    stringified = ast.literal_eval(decodedContent)
    
    output = stringified["output"]

    if 'storage' in os.listdir(os.getcwd()) and storeStuff == 1:
        timestamp = uniqueTime()
        listToFile({'payload':payload,'output':output}, os.getcwd()+'\\storage\\'+timestamp+'.json')
        if 'logprobs' in stringified:
            listToFile({'logprobs':logprobs}, os.getcwd()+'\\storage\\'+timestamp+' lps.json')
        
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

# executes a given function on a new thread, so that the app doesn't freeze while it is running
# because API calls take time.
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

# uses a settings string (from the 'settings' tab) and context to put together the payload for the API request
def assemblePayload(settings, context):
    if '\n\n' in settings:
        settings = settings.partition('\n\n')[2]

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
        settingName, _, givenValue = line.partition(' = ')
        
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

    # for implementing 'bracket ban', i think..
    bad_words_ids = [[60],[62],[544],[683],[696],[880],[905],[1008],[1019],[1084],[1092],[1181],[1184],[1254],[1447],[1570],[1656],[2194],[2470],[2479],[2498],[2947],[3138],[3291],[3455],[3725],[3851],[3891],[3921],[3951],[4207],[4299],[4622],[4681],[5013],[5032],[5180],[5218],[5290],[5413],[5456],[5709],[5749],[5774],[6038],[6257],[6334],[6660],[6904],[7082],[7086],[7254],[7444],[7748],[8001],[8088],[8168],[8562],[8605],[8795],[8850],[9014],[9102],[9259],[9318],[9336],[9502],[9686],[9793],[9855],[9899],[9955],[10148],[10174],[10943],[11326],[11337],[11661],[12004],[12084],[12159],[12520],[12977],[13380],[13488],[13663],[13811],[13976],[14412],[14598],[14767],[15640],[15707],[15775],[15830],[16079],[16354],[16369],[16445],[16595],[16614],[16731],[16943],[17278],[17281],[17548],[17555],[17981],[18022],[18095],[18297],[18413],[18736],[18772],[18990],[19181],[20095],[20197],[20481],[20629],[20871],[20879],[20924],[20977],[21375],[21382],[21391],[21687],[21810],[21828],[21938],[22367],[22372],[22734],[23405],[23505],[23734],[23741],[23781],[24237],[24254],[24345],[24430],[25416],[25896],[26119],[26635],[26842],[26991],[26997],[27075],[27114],[27468],[27501],[27618],[27655],[27720],[27829],[28052],[28118],[28231],[28532],[28571],[28591],[28653],[29013],[29547],[29650],[29925],[30522],[30537],[30996],[31011],[31053],[31096],[31148],[31258],[31350],[31379],[31422],[31789],[31830],[32214],[32666],[32871],[33094],[33376],[33440],[33805],[34368],[34398],[34417],[34418],[34419],[34476],[34494],[34607],[34758],[34761],[34904],[34993],[35117],[35138],[35237],[35487],[35830],[35869],[36033],[36134],[36320],[36399],[36487],[36586],[36676],[36692],[36786],[37077],[37594],[37596],[37786],[37982],[38475],[38791],[39083],[39258],[39487],[39822],[40116],[40125],[41000],[41018],[41256],[41305],[41361],[41447],[41449],[41512],[41604],[42041],[42274],[42368],[42696],[42767],[42804],[42854],[42944],[42989],[43134],[43144],[43189],[43521],[43782],[44082],[44162],[44270],[44308],[44479],[44524],[44965],[45114],[45301],[45382],[45443],[45472],[45488],[45507],[45564],[45662],[46265],[46267],[46275],[46295],[46462],[46468],[46576],[46694],[47093],[47384],[47389],[47446],[47552],[47686],[47744],[47916],[48064],[48167],[48392],[48471],[48664],[48701],[49021],[49193],[49236],[49550],[49694],[49806],[49824],[50001],[50256],[0],[1]]
    
    # the payload that the API will use to generate text
    payload = {
        'input':context,
        'model':actualSettings['model'],
        'parameters':{
            'bad_words_ids':bad_words_ids,
            'use_string':True,
            'prefix':actualSettings['prefix'],
            'temperature':actualSettings['temperature'],
            'min_length':actualSettings['min_length'],
            'max_length':actualSettings['max_length']
            }
        }
    
    return payload

if 'personal settings.txt' in os.listdir(os.getcwd()):
    defaultSettings = readTxt('personal settings.txt')
else:
    defaultSettings = '''
for the model, type krake, euterpe, sigurd or calliope

model = calliope
module = vanilla
temperature = 1
minimum length = 1
maximum length = 50
'''[1:-1]
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
if 'personal prompt.txt' in os.listdir(os.getcwd()):
    defaultPrompt = readTxt('personal prompt.txt')
else:
    defaultPrompt = '''
A young man is sitting on a horse, trotting quietly through the forest.
'''[1:-1]

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
helpfulTab.insert(1.0, '''
F3 to multi-generate.
    Then you can choose which output to continue with. If you select text before pressing F3, it will add only that text to the context.

F1 to open a new window for extra prompting
    in the new window:
    - press Escape to make it stay 'on top' or stop staying on top.
    - press F3 to generate text (3 times), the outputs will appear in the 'outputs' tab.
    - if you type {maincontext}, before generating it will replace that with the text you have in the main context window

Below are the names of modules you can use in the 'settings' tab
'''[1:-1] + '\n'.join(prefixes) + '''\n\n
Extra stuff:
    - If you make a txt file named "personal prompt" and/or a txt file named "personal settings" it will use that as the defaults
    - Youtube link showing how the app works: https://www.youtube.com/watch?v=k7Di4LKmm6I&feature=youtu.be&ab_channel=AtillaCodesStuff
'''[1:-1])
experimental = tk.Text(mainNb, **textSettings)
experimentalOutbox = tk.Text(mainNb, **textSettings)
text = tk.Text(mainNb, **textSettings)
settingsText = tk.Text(mainNb, **textSettings)
mainBtn = tk.Button(mainFrame, text='multi generate (f3 works too)') # I will set the command down below, after defining multiGenerate
mainNb.add(text, text='  main context  ')
mainNb.add(settingsText, text='  settings  ')
#mainNb.add(experimental, text='  experimental  ')
#mainNb.add(experimentalOutbox, text='  outbox  ')
mainNb.add(helpfulTab, text='  helpful stuff  ')

miniCodeParameters = ['inbox', 'edit', 'function', 'args', 'outbox']
textInsert(experimental, '\n'.join(map(lambda s:s+':', miniCodeParameters)))

textInsert(settingsText, defaultSettings)
textInsert(text, defaultPrompt)

hotkeys = {}

mainFrame.pack(pady=5)
mainNb.grid(row=0, column=1)
mainBtn.grid(row=1, column=1)

if 'tabDefaults.json' in os.listdir(os.getcwd()):
    tabDefaults = {}
    for title, entry in openListFile('tabDefaults.json').items():
        tabDefaults[title] = entry
else:
    tabDefaults = {}

extraTabs = []
def makeTab(title, entry):
    extraTabs.append(tk.Text(mainNb, **textSettings))
    mainNb.add(extraTabs[-1], text=f'  {title}  ')
    extraTabs[-1].insert(1.0, entry)

for k,v in tabDefaults.items():
    makeTab(k, v)

multiAmount = 3

tempTextWidgets = []
tempWidgets = []
def clearTempWidgets():
    global tempTextWidgets, tempWidgets
    for w in tempWidgets:
        w.destroy()
    tempWidgets = []
    tempTextWidgets = []

contextHistory = []
def multiGenerate(context):
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
    multiGenerate(textGrab(text))
    
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

def printResponse(payload):
    # this is the only place in the code where an API call is made.
    
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

        ## Tree class stuff for later
        #   outputOptions = list(map(lambda w:textGrab(w), tempTextWidgets))
        #   tree.choose(outputOptions, choiceIndex)

        # for appending the selection, if there is one.
        ranges = t.tag_ranges("sel")
        if ranges == ():
            selection = textGrab(t)
        else:
            selection = t.selection_get()
        if selection != '':
            chosenOutput = selection
        else:
            chosenOutput = textGrab(t)
        
        textAppend(text, chosenOutput)

        multiGenerate(textGrab(text))
        clearTempWidgets()
        
    b = tk.Button(f, text='choose', command=lambda:bf())
    t.bind('<KeyPress-F3>', lambda *a:bf())
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

def extraPrompts():
    queue = []
    fullContext = textGrab(text)
    def payloadToDest(payload, dest):
        output = apiCall(payload)
        textAppend(dest, output)
    for w in extraTabs:
        prompt = textGrab(w)
        if prompt == '':
            continue
        prompt = prompt.replace('{maincontext}', fullContext)
        payload = assemblePayload(textGrab(settingsText), prompt)
        queue.append(removeArguments(payloadToDest, [payload, w]))
    executeQueue(queue)

def reset():
    for n, w in enumerate(extraTabs):
        textClear(w)
        textInsert(w, list(tabDefaults.values())[n])

hotkeys['F2'] = lambda:tree.show()
hotkeys['F4'] = extraPrompts
hotkeys['Escape'] = reset

def stringToWidget(string):
    mapping = {
        'main context':text,
        }
    return mapping[string]

def addWindow():
    window = tk.Toplevel()

    window.attributes('-topmost', True)
    window.title('on top')
        
    window.configure(background='black')
    
    frame = tk.Frame(window, **frameSettings)
    nb = ttk.Notebook(frame)

    # to generate text on F3 and put it in the 'output' window
    def generate(event):
        def g():
            settings = textGrab(texts['settings'])
            
            maincontext = textGrab(texts['context'])
            textAppend(texts['output'], f'=== input: ===\n{maincontext}\n=== outputs: ===\n')
            contextToUse = textGrab(texts['output'])

            payload = assemblePayload(settings, maincontext.replace('{maincontext}', textGrab(text)))
                
            iterations = 3
            for i in range(iterations):
                response = apiCall(payload)
                textAppend(texts['output'], response+'\n------\n')

            #textAppend(texts['output'], '======\n\n')
            nb.select(texts['output'])
            texts['output'].yview('end')
        multiThread(g)
    
    # creating tk.Text widgets
    styling = {k:v for k,v in textSettings.items()}
    styling['height'] = 15
    styling['width'] = 45
    titles = ['context', 'output', 'settings']
    texts = {string:tk.Text(nb, **styling) for string in titles}

    # puttng them in ttk.Notebook tabs
    for string, widget in texts.items():
        nb.add(widget, text=f' {string} ')

    # inserting default text
    defaultContext = '{maincontext}\n***\nIn my opinion, the story above should have'
    textInsert(texts['context'], defaultContext)
    textInsert(texts['settings'], textGrab(settingsText))

    for w in texts.values():
        w.bind('<KeyRelease-F3>', generate)

    frame.pack()
    nb.pack()

    # toggling the window being 'on top' or not. also changes title.
    def toggleTopmost():
        tup = window.attributes()
        ix = tup.index('-topmost')
        if tup[ix+1] == 1:
            window.attributes('-topmost', False)
            window.title('not on top')
        else:
            window.attributes('-topmost', True)
            window.title('on top')

    window.bind('<Escape>', lambda *a:toggleTopmost())
    window.bind('<KeyRelease-F1>', lambda *a:addWindow())
        
hotkeys['F1'] = addWindow


root.mainloop()

#listToFile(tabDefaults, 'tabDefaults.json', 1)















