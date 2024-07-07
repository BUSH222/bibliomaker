import urllib.request
import os

dir_path = os.path.dirname(os.path.realpath(__file__)) + r"\bibliomaker.exe"

if os.path.isfile(dir_path):
    os.remove(dir_path)
else:
    print("Error: %s file not found" % dir_path)

urllib.request.urlretrieve("https://github.com//BUSH222/bibliomaker/releases/download/v1.2/bibliomaker.exe", "bibliomaker.exe")
