"""This code was inspired from the playground code: https://github.com/ERIOS-project/Playground-GenAI-CLI"""

from functions import *
from random import randint


detailed_categories_str = file_to_str("detailed_categories.json")
n_categories = 21
prompt = file_to_str("verbatim_generator_prompt.txt", {"<detailed_categories>" : detailed_categories_str})

with open("generated_verbatims.txt", "a") as fd:
    for i in range(1):
        tones = [["Positif", "Négatif", "Neutre", "Pas mentionné"][randint(0, 3)] for _ in range(n_categories)]
        verbatim = LLM_query(prompt, {"<tones>" : str(tones)}).replace('\n', ' ').replace('\r', '')
        fd.write(f"{tones} {verbatim}\n")
