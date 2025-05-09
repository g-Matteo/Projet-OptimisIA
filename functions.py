"""
This file contains the functions that are in common
between theclassification pipeline, the evaluation
pipeline, and the verbatim generator
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from json_schema import build_JSON_SCHEMA

debug = False
english = False
schema = False

if english:
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL  = "Neutral"
    NOT_MENTIONED = "Not mentioned"
    NO_FEEDBACK = "No feedback."
    POSITIVE_OR_NEGATIVE = "Positive or Negative"
    TRUE_POSITIVES = "True Positive"
    FALSE_POSITIVES = "False Positive"
    TRUE_NEGATIVES = "True Negative"
    FALSE_NEGATIVES = "False Negative"
    ZERO_SHOT_PATH = "prompts/zero_shot_prompt_english.txt"
    PROMPT_CHAINING_PATH = "prompts/prompt_chaining_prompt_english.txt"
    REFLEXION_PATH = "prompts/reflexion_and_action_prompt_english.txt"
    EVALUATION_PATH = "prompts/evaluation_prompt_english.txt"
    VERBATIM_GENERATOR_PATH = "prompts/verbatim_generator_prompt_english.txt"
    CATEGORIES_PATH = "json/categories_english.json"
    DETAILED_CATEGORIES_PATH = "json/detailed_categories_english.json"
else:
    POSITIVE = "Positif"
    NEGATIVE = "Négatif"
    NEUTRAL  = "Neutre"
    NOT_MENTIONED = "Pas mentionné"
    NO_FEEDBACK = "Pas de feedback."
    POSITIVE_OR_NEGATIVE = "Positif ou Négatif"
    TRUE_POSITIVES = "Vrais Positifs"
    FALSE_POSITIVES = "Faux Positifs"
    TRUE_NEGATIVES = "Vrais Négatifs"
    FALSE_NEGATIVES = "Faux Négatifs"
    ZERO_SHOT_PATH = "prompts/zero_shot_prompt.txt"
    PROMPT_CHAINING_PATH = "prompts/prompt_chaining_prompt.txt"
    REFLEXION_PATH = "prompts/reflexion_and_action_prompt.txt"
    EVALUATION_PATH = "prompts/evaluation_prompt.txt"
    VERBATIM_GENERATOR_PATH = "prompts/verbatim_generator_prompt.txt"
    CATEGORIES_PATH = "json/categories.json"
    DETAILED_CATEGORIES_PATH = "json/detailed_categories.json"

if schema : feedback_schema=build_JSON_SCHEMA(english)

#True Positive, False Positive, True Negative, False Negative
TP, FP, TN, FN = 0, 1, 2, 3
BIS = 4

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("API_ENDPOINT"),
    api_key=os.environ.get("API_KEY"),
)

def substitute(s : str, substitutions : dict[str, str]) -> str:
    """Takes a string and some substitutions, and applies these substitutions.

    The parameters are:
    - s is the string we want to modify
    - substitutions is a dictionary

    For instance, when given a dictionary {"a" : "b"}, it returns the same string
    where every instance of "a" is replaced by an instance of "b". This function
    is useful in order to add verbatims and other informations to a prompt.
    """
    for key in substitutions:
        s = s.replace(key, str(substitutions[key]))
    return s

def file_to_str(filename : str, substitutions : dict[str, str] = {}) -> str:
    """Takes a filename, and outputs its content as a string.

    Optionally, a substitution can be applied.
    """
    res = ""
    with open(filename, "r") as fd:
        res = "".join(fd.readlines())
    return substitute(res, substitutions)

def LLM_query(prompt : str, substitutions : dict[str, str] = {}, is_json : bool = False) -> str:
    """Queries the LLM.

    Optionally, we can decide whether the output should be a json file or not.
    """
    prompt = substitute(prompt, substitutions)
    if is_json:
        repeat=True
        while repeat:
            if schema: 
                response = client.beta.chat.completions.parse(
                    model=os.environ.get("MODEL"),
                    messages=[{"role": "user", "content": prompt}],
                    response_format=feedback_schema
                )
            else:
                response = client.chat.completions.create(
                    model=os.environ.get("MODEL"),
                    messages=[{"role": "user", "content": prompt}],
                    stream=False,
                    response_format={"type": "json_object"}
                )
            res = response.choices[0].message.content

            try:
                res = json.loads(res[res.index("{"):res.index("}")+1])
                repeat=False
            except ValueError as e:
                repeat=True
                print("retry")

        if debug:
            print(f"\n---\n{res}\n---\n")

        return res
    else:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL"),
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response.choices[0].message.content

def list_to_JSON(l1 : list, l2 : list = None) -> str:
    """Converts lists to JSON strings

    For instance, list_to_JSON([1, 2, 3, 4], [5, 6, 7, 8]) gives the following string:
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
    if l2 is None:
        l2 = [""]*len(l1)
    res = "{\n"
    for i in range(len(l1)):
        res += f'    "{l1[i]}": "{l2[i]}"{"," if i!=len(l1)-1 else ""}\n'
    return res + "}"
