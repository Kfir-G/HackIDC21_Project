from flask import Flask
from os import listdir
from os.path import isfile, join

app = Flask(__name__)


@app.route("/")
def get():
    path = "C:/Users/Shai Raz/OneDrive/מסמכים/HACKIDC/python/json_output"
    return {"files": get_files(path)}


def get_files(path):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    json_arr = []
    for file in files:
        f = open(path + "/" + file, "r")
        json_arr.append(f.read())
        f.close()
    print(json_arr)

    return json_arr