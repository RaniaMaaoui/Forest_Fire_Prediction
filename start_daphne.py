import os
import sys
from daphne.cli import CommandLineInterface

# Définir la variable d'environnement GDAL_LIBRARY_PATH
os.environ['GDAL_LIBRARY_PATH'] = r'C:\Users\moham\OneDrive\Bureau\fire_detection_web\.env\Lib\site-packages\osgeo'

# Imprimer pour vérification
print("GDAL_LIBRARY_PATH:", os.environ.get('GDAL_LIBRARY_PATH'))

# Passer les arguments de la ligne de commande à Daphne
sys.argv = ["daphne", "-p", "8000", "project.asgi:application"]
CommandLineInterface.entrypoint()
