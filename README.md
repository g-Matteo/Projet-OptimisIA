# Projet-OptimisIA


## Install venv to use virtual environments (example with apt package manager)
```
sudo apt install python3.12-venv
```

## Create an environment to use pip importations
```
python3 -m venv .venv
```
We need to activate the environment before launching any code:
```
source .venv/bin/activate
```

## Install dependencies
```
python3 -m pip install -r requirements.txt
```

## Example of .env (to put at the root of the folder)
```
API_ENDPOINT=http://localhost:11434/v1/
API_KEY=api-key
MODEL=llama3-70b
```

## Generate fake verbatims
This program generates new verbatims and their real tones.
```
python verbatim_generator.py output_file.txt number_of_verbatims
```

## Launch the classification pipeline
The program takes as an input two arguments:
- The path of an input file, in which there is, for every line, a verbatim
- The path of an output file, which will be overwritten with the corresponding classifications.
```
python classification_pipeline.py input.txt output.txt
```

## Launch the evaluation pipeline
This program takes as an input a single argument:
- The path of an input file, which contains for each line a list of tones and a verbatim

An example of input file can be found in `generated_verbatims.txt`

The output will be given on the stdout. It will show metrics of all the prompt methods.
```
python evaluation_pipeline.py input.txt
```

## Settings
In the function.py file, few parameters are available:
- debug : If set to True, prints debug information.
- english : Set to True if the verbatims to classify are in English instead of French.
- schema : Set to True to enables the use of a JSON Schema as a parameter for the LLM API. The LLM must support structured outputs to use this feature.

