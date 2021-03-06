from mcpi.minecraft import Minecraft
import time
from PIL import Image, ImageCms
from fast_calc import fast_calc
import json

scale = 0.4  # scale of the picture when transferring

img = Image.open("example/uraraka.jpg")  # the picture that will be moved to minecraft
size = img.size

img = img.resize((round(size[0] * scale), round(size[1] * scale)), Image.NEAREST)
pixels = img.load()
size = img.size
print(size)

srgb_p = ImageCms.createProfile("sRGB")
lab_p = ImageCms.createProfile("LAB")
rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")
lab2rgb = ImageCms.buildTransformFromOpenProfiles(lab_p, srgb_p, "LAB", "RGB")

time.sleep(2)

necess_blocks = ["planks", "terracota", "concrete", "wool", "lapis_block", "gold_block",
                 "iron_block", "purpur_block", "diamond_block",
                 "emerald_block", "quartz_block",
                 "coal_block"]  # blocks that will be used to build the pixelart
not_in_name = ["structure", "bone", "command", "grass_block", "mushroom",
               "hay_block", "magma"]  # exclusion blocks

with open('data_blocks_color_v2.json', "r") as data_file:
    data_loaded = json.load(data_file)
active_blocks = dict()
for name in data_loaded.keys():
    for pattern in necess_blocks:
        if pattern in name:
            break
    else:
        continue
    no_blcok = False
    for pattern in not_in_name:
        if pattern in name:
            no_blcok = True
            break
    if no_blcok:
        continue

    if data_loaded[name]["id"] != "":
        temp_img = Image.new("RGB", (1, 1), tuple(data_loaded[name]["color"]))
        color_temp = ImageCms.applyTransform(temp_img, rgb2lab).load()[0, 0]
        active_blocks[name] = {"color_rgb": data_loaded[name]["color"], "color_lab": color_temp,
                               "id": data_loaded[name]["id"]}


def id_convert(id_bl):
    data = id_bl.split()
    if len(data) > 1:
        return int(data[0]), int(data[1])
    else:
        return int(data[0]), 0


def nearest_palette_color(color_pix):
    temp_img = Image.new("RGB", (1, 1), color_pix)
    color_pix = ImageCms.applyTransform(temp_img, rgb2lab).load()[0, 0]
    min_dist = 1000000
    for nid in active_blocks.keys():
        color_temp = tuple(active_blocks[nid]["color_lab"])
        pre_val = (color_pix[0] - color_temp[0]) ** 2 + (color_pix[1] - color_temp[1]) ** 2 + (
            color_pix[2] - color_temp[2]) ** 2
        dist = fast_calc.get(pre_val, pow(pre_val, 0.5))

        if min_dist > dist:
            name_block = nid
            min_dist = dist

    return name_block, active_blocks[name_block]


res_img = img.copy()
res_img_pixels = res_img.load()

dither_FS = [16, ((0, 1), 7), ((1, -1), 3), ((1, 0), 5), ((1, 1), 1)]
dither_JJN = [48, ((0, 1), 7), ((0, 2), 5), ((1, -2), 3), ((1, -1), 5), ((1, 0), 7), ((1, 1), 5),
              ((1, 2), 3), ((2, -2), 1), ((2, -1), 3), ((2, 0), 5), ((2, 1), 3), ((2, 2), 1)]
dither_Stucki = [42, ((0, 1), 8), ((0, 2), 4), ((1, -2), 2), ((1, -1), 4), ((1, 0), 8), ((1, 1), 4),
                 ((1, 2), 2), ((2, -2), 1), ((2, -1), 2), ((2, 0), 4), ((2, 1), 2), ((2, 2), 1)]
dither_Burkes = [32, ((0, 1), 8), ((0, 2), 4), ((1, -2), 2), ((1, -1), 4), ((1, 0), 8), ((1, 1), 4),
                 ((1, 2), 2)]
dither_Atkinson = [8, ((0, 1), 1), ((1, -1), 1), ((1, 0), 1), ((1, 1), 1), ((0, 2), 1), ((2, 0), 1)]
dither_Sierra = [32, ((0, 1), 5), ((0, 2), 3), ((1, -2), 2), ((1, -1), 4), ((1, 0), 5), ((1, 1), 4),
                 ((1, 2), 2), ((2, -1), 2), ((2, 0), 3), ((2, 1), 2)]
dither_Two_Row_Sierra = [16, ((0, 1), 4), ((0, 2), 3), ((1, -2), 1), ((1, -1), 2), ((1, 0), 3),
                         ((1, 1), 2), ((1, 2), 1)]
dither_Sierra_Lite = [4, ((0, 1), 2), ((1, -1), 1), ((1, 0), 1)]

active_dither = dither_FS
divider = active_dither[0]

mc = Minecraft.create()
matrix = list()
player_pos = mc.player.getPos()
for y in range(size[1]):
    for x in range(size[0]):
        red, green, blue = res_img_pixels[x, y]
        block = nearest_palette_color(res_img_pixels[x, y])
        color = tuple(block[1]["color_rgb"])
        value_r, value_g, value_b = color

        for sh in active_dither[1:]:
            if y + sh[0][0] in range(size[1]) and x + sh[0][1] in range(size[0]):

                color_r = round((red - value_r) * sh[1] / divider) + res_img_pixels[
                    x + sh[0][1], y + sh[0][0]][0]
                color_g = round((green - value_g) * sh[1] / divider) + res_img_pixels[
                    x + sh[0][1], y + sh[0][0]][1]
                color_b = round((blue - value_b) * sh[1] / divider) + res_img_pixels[
                    x + sh[0][1], y + sh[0][0]][2]
                color_r = max(min(color_r, 255), 0)
                color_g = max(min(color_g, 255), 0)
                color_b = max(min(color_b, 255), 0)
                res_img_pixels[x + sh[0][1], y + sh[0][0]] = (color_r, color_g, color_b)

        res_img_pixels[x, y] = color
        matrix.append(
            (block[0], round(player_pos.x) + (size[0] - x), 0, round(player_pos.z) + (size[1] - y),
             *id_convert(active_blocks[block[0]]["id"])))

matrix.sort(key=lambda s: s[0])
for y in range(size[1] * size[0]):
    mc.setBlock(*matrix[y][1:])
    time.sleep(0.0023)
