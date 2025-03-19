"""This file contains the functions that are in common between the classification pipeline, the evaluation pipeline, and the verbatim generator"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("API_ENDPOINT"),
    api_key=os.environ.get("API_KEY"),
)

def substitute(s, substitutions):
    """Takes a string and some substitutions, and applies these substitutions

    - s is the string we want to modify
    - substitutions is a dictionary

    For instance, when given a dictionary {"a" : "b"}, it returns the same string
    where every instance of "a" is replaced by an instance of "b". This function
    is useful in order to add verbatims and other informations to a prompt.
    """
    for key in substitutions:
        s = s.replace(key, substitutions[key])
    return s

def file_to_str(filename, substitutions = {}):
    """Takes a filename, and outputs its content as a string.

    Optionally, a substitution can be applied.
    """
    res = ""
    with open(filename, "r") as fd:
        res = "".join(fd.readlines())
    return substitute(res, substitutions)

#Makes a query to the LLM
def LLM_query(prompt, substitutions = {}, is_json = False):
    """Queries the LLM

    Optionally, we can decide whether the output should be a json file or not.
    """
    prompt = substutute(prompt, substitutions)
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
def list_to_JSON(l1, l2 = None):
    if l2 is None:
        l2 = [""]*len(l1)
    res = "{\n"
    for i in range(len(l1)):
        res += f'    "{l1[i]}": "{l2[i]}"{"," if i!=len(l1)-1 else ""}\n'
    return res + "}"
