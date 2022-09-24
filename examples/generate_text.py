import json, requests, ast

context = "bruh you wont believe what happened yesterday to my aunt"
payload = {
    "input": context,
    "model": "2.7B", #2.7B, 6B-v4, euterpe-v2, krake-v2
    "parameters":{
        "use_string":True,
        "prefix":"style_hplovecraft", # or vanilla for no module. find more at https://github.com/wbrown/novelai-research-tool
        "temperature":1,
        "max_length":100,
        "min_length":1
        }
    }

secret_authorization_key = 'monkaS'
headers = {'Content-Type': 'application/json',
           'authorization': f'Bearer {secret_authorization_key}'
           }

def generateText(payload, headers):
    url = "https://api.novelai.net/ai/generate"
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    content = response.content
    
    decodedContent = content.decode()
    decodedContent = decodedContent.replace("null", "0.0000")
    stringified = ast.literal_eval(decodedContent)
    output = stringified["output"]

    if 'logprobs' in stringified:
        logprobs = stringified["logprobs"]
    
    return output

print(generateText(payload, headers))
