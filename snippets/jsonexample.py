
import re, json
jsonString = """
//EnMAP-Box Configuration File
//see https://bitbucket.org/hu-geomatics/enmap-box/src/master/example.json for other options
//EnMAP-Box Project 
{
  "level_1_id": {
    "names":  ["impervious", "vegetation", "soil",        "water"],
    "colors": [[230, 0, 0],  [56, 168, 0], [168, 112, 0], [0,100,255]]
  },
  "level_2_id": {
    "names":  ["impervious", "low vegetation", "tree",       "soil",        "water"],
    "colors": [[230, 0, 0],  [152, 230, 0],    [38, 115, 0], [168, 112, 0], [0,100,255]]
  },
  "level_3_id": {
    "names":  ["roof",      "pavement",      "low vegetation", "tree",       "soil",        "water"],
    "colors": [[230, 0, 0], [156, 156, 156], [152, 230, 0],    [38, 115, 0], [168, 112, 0], [0,100,255]]
  }
}
"""

json2 = """
{
    "level_1_id": {
        "classsificationscheme": [
                ["unclassified", [230, 0, 0]],
                ["pavement", [156, 156, 156]],
                ["low vegetation", [152, 230, 0]]            
            ]
    }
}
"""
json3 = """
{
    "level_1_id": {
        "classsificationscheme": [
                ["unclassified", "black"],
                ["pavement", [156, 156, 156]],
                ["low vegetation", [152, 230, 0, 64]]            
            ]
    }
}
"""
from qgis.PyQt.QtGui import QColor
for name, colorArgs in json.loads(json3)['level_1_id']['classsificationscheme']:
    if isinstance(colorArgs, str):
        color = QColor(colorArgs)
    else:
        color = QColor(*colorArgs)
    print("{}={}".format(name, color.name()))



for key, value in json.loads(json2).items():
    print("{}={}".format(key, value))

import re, json
maskedJson = ''.join([l for l in jsonString.splitlines()
                      if not re.search(r'^[ ]*//', l)])

data = json.loads(maskedJson)
for key, value in data.items():
    print("{}={}".format(key, data))

print(json.dumps(data, indent=1))