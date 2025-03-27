from functions import *
from random import randint

def verbatim_generator():
    """Generates new verbatims and their real tones.

    The verbatims and their tones are appended in "generated_verbatims.txt".
    """
    detailed_categories_str = file_to_str("detailed_categories.json")
    n_categories = 21
    prompt = file_to_str("verbatim_generator_prompt.txt", {"<detailed_categories>" : detailed_categories_str})

    with open("generated_verbatims.txt", "a") as fd:
        for i in range(1):
            tones = [["Positif", "Négatif", "Neutre", "Pas mentionné"][randint(0, 3)] for _ in range(n_categories)]
            verbatim = LLM_query(prompt, {"<tones>" : str(tones)}).replace('\n', ' ').replace('\r', '')
            fd.write(f"{tones} {verbatim}\n")

if __name__ == '__main__':
    verbatim_generator()