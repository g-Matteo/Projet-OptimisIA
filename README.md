# Projet-OptimisIA

## Installer poetry
```
curl -sSL https://install.python-poetry.org | python3 -
```

## Ajouter la poubelle de poetry à $PATH
```
PATH=$PATH:/home/ubuntu/.local/bin
```

## Installer venv pour faire des environnements virtuels
```
sudo apt install python3.12-venv
```

## Créer un environnement virtuel pour faire les importations pip
```
python3 -m venv .venv
source .venv/bin/activate
```

## installer dotenv
```
python3 -m pip install python-dotenv
```

## Installer openai
```
python3 -m pip install openai
```

## Installer jsonschema
```
python3 -m pip install jsonschema
```

## Exemple de .env (à mettre dans la racine de ce dossier)
```
API_ENDPOINT=http://localhost:11434/v1/
API_KEY=api-key
MODEL_NAME=llama3-70b
```
## Exécuter le pipeline de classification
```
python classification_pipeline.py input.txt output.txt
```
## Exécuter le pipeline d'évaluation
```
python evaluation_pipeline.py input.txt
```
