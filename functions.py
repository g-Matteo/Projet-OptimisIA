import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("API_ENDPOINT"),
    api_key=os.environ.get("API_KEY"),
)

def file_to_str(filename):
    res = ""
    with open(filename, "r") as fd:
        res = "".join(fd.readlines())
    return res

#Takes a string and a dictionary {"a" : "b"}, and returns the same string where every instance of "a" is replaced by an instance of "b"
def substitute(s, substitutions):
    for key in substitutions:
        s = s.replace(key, substitutions[key])## on remplace tous les key dans s par  substitution[key]
    return s

#Takes the filename of a prompt, and outputs the prompt
def get_prompt(filename, substitutions = {}):
    return substitute(file_to_str(filename), substitutions)

#Makes a query to the LLM
def LLM_query(prompt, substitutions = {}, is_json = False):
    prompt = substitute(prompt, substitutions)
    if is_json:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL"),
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    else:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL"),
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response.choices[0].message.content


"""
list_to_JSON([1, 2, 3, 4], [5, 6, 7, 8]) gives the following string:
{
    "1": "5",
    "2": "6",
    "3": "7",
    "4": "8"
}

and list_to_JSON([1, 2, 3, 4]) gives the following string:
{
    "1": "",
    "2": "",
    "3": "",
    "4": ""
}
"""
def list_to_JSON(l1, l2 = None): ## on transefère l1 et l2 en format de json
    if l2 is None:
        l2 = [""]*len(l1)
    res = "{\n"
    for i in range(len(l1)):
        res += f'    "{l1[i]}": "{l2[i]}"{"," if i!=len(l1)-1 else ""}\n'
    return res + "}"
