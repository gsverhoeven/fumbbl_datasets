import json

def read_json_file(fname):

    if fname is None:
        return "fname missing"

    with open(fname, mode = "r", encoding='UTF-8') as f:
        json_object = json.load(f)

    return json_object