# module imports
import json, requests, threading, ast, os, time
import tkinter as tk
from tkinter import ttk


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

# uses argon_hash and getAuth to get an authorization key, which is basically logging in.
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

# styling
textSettings = {'bg':'black', 'insertbackground':'red', 'fg':'light blue', 'height':'9', 'font':('comic sans', '15')}
labelSettings = {'font':('comic sans', '10'), 'bg':'black', 'fg':'light blue'}

# login section
if 'login info.txt' not in os.listdir(os.getcwd()):
    loginWindow = tk.Tk()
    loginWindow.config(bg='black')
    
    label = tk.Label(loginWindow, text='please enter your email and password', **labelSettings)
    entries = []
    for default in ['your_email@goose.ca', 'honk!letmein!']:
        entries.append(tk.Entry(loginWindow, width=30))
        entries[-1].insert(0, default)
        
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
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@''')
    
    i = tk.IntVar()
    i.set(1)
    c = tk.Checkbutton(loginWindow, text = "store login info in txt file for later", variable=i, **labelSettings, selectcolor='blue')
    
    def submit():
        global email, password
        email, password = entries[0].get(), entries[1].get()
        auth = getAuth(email, password)
        
        if i.get() == 1:
            createTxt('login info.txt', f'email:{email}\npassword:{password}')

        loginWindow.destroy()
    
    btn = tk.Button(loginWindow, command=submit, text='click here or hit enter to submit', **labelSettings)
    loginWindow.bind('<Return>', lambda *args:submit())

    for w in [label, *entries, btn, c, goose]:
        w.pack()
    loginWindow.mainloop()
else:
    info = readTxt('login info.txt')
    email, password = map(lambda s:s.partition(':')[2], info.split('\n'))


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
    
    return output

def textGrab(textWidget):
    text = textWidget.get(1.0, 'end')[:-1]
    return text

def textClear(widget):
    widget.delete(1.0, 'end')

def textInsert(widget, insertion):
    widget.insert(1.0, insertion)

# basic multithreading
def newThread(function):
    threading.Thread(target=function).start()





###
# this little section is for setting the amount of tabs in the middle and bottom layer, via textColumns in setVars()
#   which effectively sets the number of generations. the app will close and launch the actual app once that's done

initialApp = tk.Tk()
initialApp.configure(background = 'black')

f = tk.Frame(initialApp, bg='black')
l1 = tk.Label(f, text='- set the amount of output windows/generations\n- then press enter', **labelSettings)
e = tk.Entry(f, background='black', insertbackground='white', fg='light blue')

e.insert(0, '3')

f.pack()
l1.pack()
e.pack()

# set textColumns and close the window.
def setVars():
    global textColumns
    textColumns = int(e.get())
    initialApp.destroy()

initialApp.bind('<Return>', lambda *args:setVars())

initialApp.mainloop()

###
# now that textColumns is set, the actual app can launch.






root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(background = 'black')

explanation = tk.Label(root, text='press f2 to generate off the prompt, f3 for the followup prompt, and f10 to clear the middle layer', **labelSettings)
explanation2 = tk.Label(root, text='', **labelSettings)

explanation.pack()
#explanation2.pack()

def setTabTitle(nbIndex, tabIndex, title):
    notebooks[nbIndex].tab(tabIndex, text=title)

# create ttk.Notebook widgets, which will let me use tabs. 3 rows of tabs, so 3 Notebook widgets.
notebookRows = 3
notebooks = []
for _ in range(notebookRows):
    notebooks.append(ttk.Notebook(root))

# make first layer's tabs and tk.Text widgets
texts = {}
texts[0] = {}
topLayerTitles = ['settings', 'prompt', 'followup prompt', 'some helpful stuff']
for j in range(len(topLayerTitles)):
    # create and add Text widget
    texts[0][j] = tk.Text(root, **textSettings)
    notebooks[0].add(texts[0][j])

    title = '  ' + topLayerTitles[j] + '  '
    setTabTitle(0, j, title)

# make second and third layer's tabs and tk.Text widgets
for i in range(1, notebookRows):
    texts[i] = {}
    for j in range(textColumns):
        # create and add Text widget
        texts[i][j] = tk.Text(root, **textSettings)
        notebooks[i].add(texts[i][j])

        if i == 1:
            title = ''.join(map(str,['  base ', j, '  ']))
        if i == 2:
            title = ''.join(map(str,['  followup ', j, '  ']))            
        setTabTitle(i, j, title)

# adding a bit of extra clarification in a tab at the top
clarification = texts[0][topLayerTitles.index('some helpful stuff')]
clarification.config(font = ('comic sans', 12))
textInsert(clarification, '''
f2
Generates multiple times using the base prompt.
Outputs go in the middle layer.

f3
Makes new prompts by combining the base prompt, the outputs, and the followup prompt, generates with that.
Outputs go in the bottom layer.
'''[1:-1] + '\n\nmodules:\n' + '\n'.join(prefixes))



if 'personal settings.txt' in os.listdir(os.getcwd()):
    defaultSettings = readTxt('personal settings.txt')
else:
    defaultSettings = '''
for the model, type krake, euterpe, sigurd or calliope
for module, click the 'some helpful stuff' tab to see how those are written

model:euterpe
module:theme_generalfantasy
temperature:1
minimum length:1
maximum length:100
'''[1:-1]
textInsert(texts[0][0], defaultSettings)


if 'personal prompt.txt' in os.listdir(os.getcwd()):
    defaultPrompt = readTxt('personal prompt.txt')
else:
    defaultPrompt = '''
    [ Genre: adventure; Tags: dungeon ]
    [ Theme: ominous and dangerous ]
    Summary: An adventurer just entered a cave, and sees a dragon laying there, asleep.
    ***
    In the distance, at the far end of the cave there rests a dragon. It appears to be asleep.. Its body is moving up and down slowly, the deep rumble of its breath echoing off the walls, a faint drip of water rhythmically hitting the cavern floor.
    '''[1:-1]
textInsert(texts[0][1], defaultPrompt)

defaultFollowup1 = '''

3 possible continuations of the above story:
1) You
'''[1:-1]
defaultFollowup2 = '''

Yo dawg that story is dope af! I got so hype in that moment when the
'''[1:-1]
textInsert(texts[0][2], defaultFollowup1)

notebooks[0].select(texts[0][1])
notebooks[1].select(texts[1][0])
notebooks[2].select(texts[2][0])

for i in range(len(notebooks)):
    notebooks[i].pack()

label = tk.Label(root, **labelSettings)
label.pack()

  

# the queue contains functions. the queueHandler will make each call and remove that element from the queue, until empty.
queue = []
def labelUpdate():
    global label
    r = len(queue)
    if r == 0:
        label.config(text = 'ready')
    else:
        label.config(text=f"{r} remaining")
   
labelUpdate()

count = 0
queueRunning = False
def startQueue():
    global queueRunning, count, label
    labelUpdate()
    queueRunning = True
    while len(queue) > 0:
        queue[0]()
        del queue[0]

        if 0:
            r = len(queue)
            label.config(text=f"{r} remaining")
        else:
            labelUpdate()
    

    queueRunning = False

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

# putting all tk.Text content into a dictionary
textsContent = {}
def updateTextsContent():
    global textsContent
    for r, lst in texts.items():
        textsContent[r] = {}
        for c, w in lst.items():
            textsContent[r][c] = textGrab(w)

# this function is for filling the queue when f3 is pressed, onF3 is for when f3 is pressed.
def fillQueue():
    # adding the api calls to the queue, which will fill the second row with outputs
    for i in range(textColumns):
        
        # the function that needs to be called when it's this element's turn in the queue
        def callAndInsert(payload, destination):
            result = apiCall(payload)
            textClear(destination)
            textInsert(destination, result)
            

        # setting a specific payload for the api call, and a specific destination tk.Text widget for the response            
        params = textsContent[0][0]
        context = textsContent[0][1]
        payload = assemblePayload(params, context)

        # for some reason i needed to do this for destination to be frozen at a specific widget
        def setFunction(payload, destination, loc):
            def nameless():
                callAndInsert(payload, destination)
                #notebooks[loc[0]].select(texts[loc[0]][loc[1]])
            return nameless
        
        toQueue = setFunction(payload, texts[1][i], (1,i))

        queue.append(toQueue)


# for doing multi-generations off the initial prompt. will put things in a queue and call the function that manages the queue
# it's on a new thread to prevent the app from freezing while waiting for the AI, but each API call is still done sequentially

# (can't be called if another queue is still running (the app will give a warning), because I haven't figured out how to do queue stuff properly)
def onF2():
    for i in range(textColumns):
        textClear(texts[2][i])
    if not queueRunning:
        updateTextsContent()

        queue.append(lambda:fillQueue())

        newThread(startQueue)
    else:
        label.config(text = 'queue still running')

# for attaching the followup prompt to the output, and getting new generations off of that. pretty much the same as onF2()

# (same as above, can't be called if another queue is running)
def onF3():
    if not queueRunning:
        def f1(firstOutput, secondOutput):
            firstPrompt = textGrab(texts[0][1])
            secondPrompt = textGrab(texts[0][2])
            
            payload = assemblePayload(textGrab(texts[0][0]), firstPrompt+firstOutput+secondPrompt)
            response = apiCall(payload)
            
            textClear(secondOutput)
            textInsert(secondOutput, response)

        def f2(firstOutput, secondOutput):
            def f3():
                f1(firstOutput, secondOutput)
            return f3
        
        for i in range(textColumns):
            queue.append(f2(textGrab(texts[1][i]), texts[2][i]))

        newThread(startQueue)
    else:
        label.config(text = 'queue still running')

# clears the second row, where the first outputs land
def onF10():
    for i in range(textColumns):
        textClear(texts[1][i])

root.bind('<KeyPress-F2>', lambda *args:onF2())
root.bind('<KeyPress-F3>', lambda *args:onF3())
root.bind('<KeyPress-F10>', lambda *args:onF10())
# for jumping to the same column of row 2 in the Notebook if something in row 1 is clicked and vice versa
def onClick(event):
    nb = event.widget
    
    t = nb.select()
    
    nbi = notebooks.index(nb)

    ti = notebooks[nbi].index(t)

    notebooks[1].select(ti)
    notebooks[2].select(ti)
    
for i in range(1, len(notebooks)):
    notebooks[i].bind('<ButtonRelease-1>', onClick)

def onF1():
    t = textGrab(root.focus_get())
    texts[0][1].insert('end', t)

root.bind('<KeyPress-F1>', lambda *args:onF1())



root.mainloop()

















