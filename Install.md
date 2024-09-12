import os
import json
import pandas as pd
from collections import defaultdict
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askdirectory
import dateparser
____________________________________________________________________

# Google Chat Count
Extração e contagem de recursos do Email do Gmail

1 - Para fazer a execução do projeto, primeiramente você tem que acessar o site "https://takeout.google.com/" e programar o download dos arquivos do seu próprio Google Chat.
2 - Com o arquivo compactado em mãos, extraia o mesmo e pegue apenas a pasta chamada "Groups" e deixe na área de trabalho.
3 - Execute o projeto "GooglechatCount" 
4 - Selecione a PASTA chamada Groups na área de trabalho.
5 - Por fim, tenha o arquivo um Excel dos seus dados do Google Chat em um Excel.
