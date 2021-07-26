from mcpi.minecraft import Minecraft
import time
from PIL import Image
from fast_calc import fast_calc
import json

scale = 0.4

img = Image.open("example\\cat.jpg")
size = img.size
print(size)

mc = Minecraft.create()

# mc.setBlocks(-49, 4, -194, size[0], size[1], -194, 0)
time.sleep(2)

img = img.resize((round(size[0] * scale), round(size[1] * scale)), Image.ANTIALIAS)
pixels = img.load()
size = img.size
print(size)

necess_blocks = ["planks", "terracota", "concrete", "wool"]
with open('data_blocks_color.json', "r") as data_file:
    data_loaded = json.load(data_file)

active_blocks = dict()
for name in data_loaded.keys():
    for pattern in necess_blocks:
        if pattern in name:
            break
    else:
        continue
    if data_loaded[name]["id"] != "":
        active_blocks[name] = data_loaded[name]


def id_convert(id_bl):
    data = id_bl.split()
    if len(data) > 1:
        return int(data[0]), int(data[1])
    else:
        return int(data[0]), 0


# mc.player.setPos(-49, 4, -195)
for y in range(size[1]):
    for x in range(size[0]):
        min_dist = 1000000
        id_block = 0
        name_block = ""
        col = pixels[x, y]
        for name in active_blocks:
            col1 = active_blocks[name]["color"]

            dist = fast_calc[
                (col[0] - col1[0]) ** 2 + (col[1] - col1[1]) ** 2 + (col[2] - col1[2]) ** 2]

            if min_dist > dist:
                name_block = name
                min_dist = dist

        # print(-49 + (size[0] - x), 4 + (size[1] - y), -194, id_block)
        # print(name_block)
        mc.setBlock(-751 + (size[0] - x), 0, -1154 + (size[1] - y),
                    *id_convert(active_blocks[name_block]["id"]))
        # mc.postToChat("")
        # time.sleep(0.25)
# (-49, 4, -194)
