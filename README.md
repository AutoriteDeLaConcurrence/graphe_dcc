# Network of the merger decisions

Network of the links between merger decision published by the French Competition Authority (here-after FCA). 

## Purpose

This project aimed at extending the work done on antitrust decisions (see the code [here](https://github.com/AutoriteDeLaConcurrence/publication_sen-codex_networkgraph)) wich lead to an [article](https://www.autoritedelaconcurrence.fr/sites/default/files/2023-01/Stanford-Computational-Antitrust-en.pdf) published in `Computationnal Antitrust`. 
Here, our main subject are merger decisions, which are more frequent than antitrust's (more than 200 a year) but are often simplified procedure, which means that the final decision is empty and contains no quotes. 


## Result

TBC : Screenshot of the graph : French version and English version

## How to run it :

1. Create a virtual environnment and install the dependencies : 

```sh
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

2. Run the application using gunicorn

```sh
gunicorn --workers=1 --threads=1 -b 0.0.0.0:8000 app:server
```
