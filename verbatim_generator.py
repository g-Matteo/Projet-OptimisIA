from functions import *
from random import randint

def verbatim_generator():
    """Generates new verbatims and their real tones.

    This function takes as input two arguments:
    - The path of the output file (mostly "generated_verbatims.txt")
    - The number of verbatims that we want to generate

    We create a table of 21 tones randomly (IID) set to "Positif",
    "Négatif", "Neutre", "Pas mentionné". Then, we ask the LLM
    (using "prompts/verbatim_generator_prompt.txt") to generate a verbatim
    matching these tones. Finally, we store the tones and the verbatim
    in the output file.

    For an example of what the output of this program looks like, see
    the file "generated_verbatims.txt".
    """
    if len(sys.argv)!=3:
        exit(f"Usage: {sys.argv[0]} output_file.txt number_of_verbatims")
    
    detailed_categories_str = file_to_str("detailed_categories.json")
    prompt = file_to_str("prompts/verbatim_generator_prompt.txt", {"<detailed_categories>" : detailed_categories_str})

    with open(sys.argv[1], "a") as fd:
        for i in range(int(sys.argv[2])):
            tones = [["Positif", "Négatif", "Neutre", "Pas mentionné"][randint(0, 3)] for _ in range(21)]
            verbatim = LLM_query(prompt, {"<tones>" : str(tones)}).replace('\n', ' ').replace('\r', '')
            fd.write(f"{tones} {verbatim}\n")

if __name__ == '__main__':
    verbatim_generator()