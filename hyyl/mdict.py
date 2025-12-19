from readmdict import MDX, MDD
import re
import json

# read an mdd file
filename = "中国海洋鱼类图鉴.mdd"
items = MDD(filename).items()
pic = {}
for filename, content in items:
    with open("img/%s"%(filename.decode().replace("\\","")), 'wb') as f:
        f.write(content)

filename = "中国海洋鱼类图鉴.mdx"
headwords = [*MDX(filename).header]
print(headwords[:10])  # fisrt 10 in bytes format
fishes = {}

items = [*MDX(filename).items()]
for (key, val) in items:
    if not re.match("\<a href.*\>.*\</a\>", val.decode()):
        cols = re.split("[<>]", val.decode())
        image_name=re.split("\"",cols[33])[1]
        desc = cols[38]
        category = cols[26].replace("&nbsp;"," ")

        atts ={"formal":"",
               "category":category,
               "name":key.decode(),
               "desc":desc,
               "img":"img/%s"%(image_name)
               }
        fishes[key.decode()] = atts

for (key, val) in items:
    if re.match("\<a href.*\>.*\</a\>", val.decode()):
        name = re.split("[<>]", val.decode())[2]
        if name in fishes:
            fishes[name]["formal"]=key.decode()

            
with open("fishes.json", "w", encoding="utf-8") as f:
    json.dump(list(fishes.values()), f, indent=2)
