#!/usr/bin/python
# -*- coding: utf-8 -*-

# import modules used here -- sys is a very standard one
from PIL import Image, ImageFont, ImageDraw
import simplejson as json


tooltip_width = 0


# Gather our code in a main() function
def main(data):
    global tooltip_width
    obj = json.loads(data)
    tooltip_width = determine_width(obj) + 50 + 44 * 2

    name = obj["name"] if obj["name"] != "" else obj["typeLine"]
    print "Saving {}.png".format(name)
    make_tooltip(obj).save("images/" + name + ".png", "PNG")


def make_tooltip(item_obj):
    """
    Determine which components are necessary and assemble the tooltip
    :param item_obj: JSON object
    :return: PIL.Image.Image of final tooltip
    """
    type_info = [
        {"separator": "NormalSeparator.png", "header_end_width": 29},
        {"separator": "MagicSeparator.png", "header_end_width": 29},
        {"separator": "RareSeparator.png", "header_end_width": 44},
        {"separator": "UniqueSeparator.png", "header_end_width": 44},
        {"separator": "GemSeparator.png", "header_end_width": 29},
        {"separator": "CurrencySeparator.png", "header_end_width": 29},
        {"separator": "CurrencySeparator.png", "header_end_width": 29}
    ]

    item_colors = [(159, 158, 130),
                   (107, 136, 255),
                   (255, 255, 119),
                   (175, 96, 37),
                   (27, 162, 127),
                   (170, 143, 88),
                   (74, 162, 29)]

    info = type_info[item_obj["frameType"]]
    all_images = []
    global tooltip_width
    tooltip_width = determine_width(item_obj) + 50 + info["header_end_width"] * 2
    sep_src = Image.open("images/headers/" + info["separator"], "r")
    sep = create_row([sep_src], tooltip_width, 8)
    # header
    header = make_header(item_obj)
    all_images.append(header)
    # properties
    if "properties" in item_obj:
        for prop in item_obj["properties"]:
            new_prop = make_single_property(prop)
            all_images.append(new_prop)
        all_images.append(sep)

    #requirements
    if item_obj["frameType"] != 5 and "requirements" in item_obj:
        all_images.append(make_requirements(item_obj))
        all_images.append(sep)

    if "implicitMods" in item_obj:
        all_images.append(make_implicit_mods(item_obj))
        all_images.append(sep)

    if not item_obj["identified"]:
        all_images.append(create_row([("Unidentified", (204, 12, 12))], tooltip_width, 20))
        #implicit
    if "additionalProperties" in item_obj:
        make_experience_bar(item_obj)
        #explicits
    if "explicitMods" in item_obj:
        all_images.append(make_explicit_mods(item_obj))
    if "additionalProperties" in item_obj:
        all_images.append(sep)
        all_images.append(make_experience_bar(item_obj))

    if "descrText" in item_obj:
        all_images.append(sep)
        import textwrap

        for line in textwrap.wrap(item_obj["descrText"], tooltip_width / 7):
            row = create_row([(line, (99, 99, 99))], tooltip_width, 20)
            all_images.append(row)

    if "flavourText" in item_obj:
        all_images.append(sep)
        for line in item_obj["flavourText"]:
            row = create_row([(line, (175, 96, 37))], tooltip_width, 20)
            all_images.append(row)

    return merge_images(all_images, 1)


def determine_width(obj):
    """
    Determine width needed for tooltip to fit text
    :param obj: JSON object
    :return: the width
    """
    img = Image.new("RGB", (1, 1))
    img_drawer = ImageDraw.Draw(img)
    font = ImageFont.truetype("Fontin-SmallCaps.ttf", 18)
    name_width = img_drawer.textsize(obj["name"].encode("utf-8"), font)[0]
    typeline_width = img_drawer.textsize(obj["typeLine"].encode("utf-8"), font)[0]
    explicit_width = 0
    flavour_width = 0
    prop_width = 0
    if "properties" in obj:
        for p in obj["properties"]:
            text = p["name"]
            for v in p["values"]:
                text = text + " " + v[0]

            width = img_drawer.textsize(text)[0]
            if width > prop_width:
                prop_width = width

    if "explicitMods" in obj:
        for p in obj["explicitMods"]:
            width = img_drawer.textsize(p)[0]
            if width > explicit_width:
                explicit_width = width

    if "flavourText" in obj:
        for line in obj["flavourText"]:
            width = img_drawer.textsize(line)[0]
            if width > flavour_width:
                flavour_width = width

    return max(name_width, typeline_width, prop_width, explicit_width, flavour_width)


def make_header(obj):
    """
    Create the header of the tooltip
    :param obj: JSON object
    :return: the header image
    """
    headers = {
        0: [Image.open("images/headers/NormalHeaderLeft.png"),
            Image.open("images/headers/NormalHeaderMiddle.png"),
            Image.open("images/headers/NormalHeaderRight.png")],
        1: [Image.open("images/headers/MagicHeaderLeft.png"),
            Image.open("images/headers/MagicHeaderMiddle.png"),
            Image.open("images/headers/MagicHeaderRight.png")],
        2: [Image.open("images/headers/RareHeaderLeft.png"),
            Image.open("images/headers/RareHeaderMiddle.png"),
            Image.open("images/headers/RareHeaderRight.png")],
        3: [Image.open("images/headers/UniqueHeaderLeft.png"),
            Image.open("images/headers/UniqueHeaderMiddle.png"),
            Image.open("images/headers/UniqueHeaderRight.png")],
        4: [Image.open("images/headers/GemHeaderLeft.png"),
            Image.open("images/headers/GemHeaderMiddle.png"),
            Image.open("images/headers/GemHeaderRight.png")],
        5: [Image.open("images/headers/CurrencyHeaderLeft.png"),
            Image.open("images/headers/CurrencyHeaderMiddle.png"),
            Image.open("images/headers/CurrencyHeaderRight.png")],
        6: [Image.open("images/headers/QuestHeaderLeft.png"),
            Image.open("images/headers/QuestHeaderMiddle.png"),
            Image.open("images/headers/QuestHeaderRight.png")],
    }
    unid_headers = {
        2: [Image.open("images/headers/RareHeaderSingleLineLeft.png"),
            Image.open("images/headers/RareHeaderSingleLineMiddle.png"),
            Image.open("images/headers/RareHeaderSingleLineRight.png")],
        3: [Image.open("images/headers/UniqueHeaderSingleLineLeft.png"),
            Image.open("images/headers/UniqueHeaderSingleLineMiddle.png"),
            Image.open("images/headers/UniqueHeaderSingleLineRight.png")],
    }
    cur_header = headers[obj["frameType"]]
    needs_unid_header = not obj["identified"] and (obj["frameType"] == 2 or obj["frameType"] == 3)
    if needs_unid_header:
        cur_header = unid_headers[obj["frameType"]]
    header_tile_width, header_tile_height = cur_header[0].size
    frame_type = obj["frameType"]

    name = obj["name"]
    typeLine = obj["typeLine"]

    img = Image.new('RGBA', (10, 10))
    font = ImageFont.truetype("Fontin-SmallCaps.ttf", 20)
    image_drawer = ImageDraw.Draw(img)
    name_width, _ = image_drawer.textsize(name, font)
    type_width, _ = image_drawer.textsize(typeLine, font)

    global tooltip_width
    num = int(tooltip_width / header_tile_width) + 1
    header = Image.new('RGBA', (tooltip_width, header_tile_height))
    inc = 0
    for i in range(0, num):
        if needs_unid_header:
            header.paste(unid_headers[frame_type][1], (inc * header_tile_width, 0))
        else:
            header.paste(headers[frame_type][1], (inc * header_tile_width, 0))
        inc += 1

    # if item is unidentified and needs special 1 line header (magic, rare)
    if needs_unid_header:
        header.paste(unid_headers[frame_type][0], (0, 0))
        header.paste(unid_headers[frame_type][2], (tooltip_width - header_tile_width, 0))
    else:
        header.paste(headers[frame_type][0], (0, 0))
        header.paste(headers[frame_type][2], (tooltip_width - header_tile_width, 0))

    item_colors = [(159, 158, 130),
                   (107, 136, 255),
                   (255, 255, 119),
                   (175, 96, 37),
                   (27, 162, 127),
                   (170, 143, 88),
                   (74, 162, 29)]

    image_drawer = ImageDraw.Draw(header)
    # Currency, gems, etc are only generic types and have 1 line headers so they use only typeLine
    if name != "":
        image_drawer.text((tooltip_width / 2 - name_width / 2, header_tile_height / 4 / 2 - 2), name, font=font,
                          fill=item_colors[frame_type])
        image_drawer.text((tooltip_width / 2 - type_width / 2, header_tile_height - (header_tile_height / 2) + 2),
                          typeLine,
                          font=font, fill=item_colors[frame_type])
    else:
        font = ImageFont.truetype("Fontin-SmallCaps.ttf", 16)
        type_width, _ = image_drawer.textsize(typeLine, font)
        image_drawer.text((tooltip_width / 2 - type_width / 2, header_tile_height - (header_tile_height) + 8), typeLine,
                          font=font, fill=item_colors[frame_type])

    return header


def make_single_property(obj):
    """
    Make a property row
    :param obj: JSON object
    :return: row image for the property
    """
    name = obj["name"]
    values = obj["values"]

    value_colors = [(255, 255, 255), # White
                    (107, 136, 255), # Supplemented
                    (99, 99, 99), # Grey
                    (99, 99, 99), # Gray
                    (150, 1, 2), # Fire dmg
                    (31, 100, 146), # Cold dmg
                    (255, 201, 3)]      # Light damage

    grey = (99, 99, 99)
    global tooltip_width
    property_images = []
    if obj["displayMode"] != 3:
        #Create name image
        if values and name != "":
            name += ": "
        image = make_text_image(name, value_colors[2])
        property_images.append(image)

        if values:
            #Iterate through values, determine colors, and create images
            for (count, value) in enumerate(values):
                value_text = value[0]

                text_color = value_colors[value[1]]
                image = make_text_image(value_text, text_color)
                property_images.append(image)
                if len(values) > 1 and count < len(values) - 1:
                    image = make_text_image(", ", grey)
                    property_images.append(image)

        return create_row(property_images, tooltip_width, 20)
    else:
        name_words = name.split(" ")
        words_colors = []
        import re

        expr = re.compile(r"%\d+")
        matched = 0
        for w in name_words:
            if expr.match(w):
                color = value_colors[values[matched][1]]
                words_colors.append((values[matched][0], color))
                matched += 1
                continue
            words_colors.append((w, (99, 99, 99)))

        word_images = []
        for w in words_colors:
            word_images.append(make_text_image(w[0], w[1]))
            word_images.append(make_text_image(" ", (255, 255, 255)))

        row = create_row(word_images, tooltip_width, 20)
        return row


def make_properties(data):
    properties = None
    return properties


def make_requirements(data):
    """
    Create the requirements row image
    :param data:
    :return:
    """
    obj = data["requirements"]
    requirements = obj

    value_colors = [(255, 255, 255), #White
                    (107, 136, 255), #Supplemented
                    (99, 99, 99), #Grey
                    (99, 99, 99), #Gray
                    (150, 1, 2), #Fire dmg
                    (31, 100, 146), #Cold dmg
                    (255, 201, 3)]      #Light damage

    grey = (99, 99, 99)
    global tooltip_width
    property_images = []
    #Create name image
    name = "Requires "
    image = make_text_image(name, value_colors[2])
    property_images.append(image)
    texts = [(name, (99, 99, 99))]
    for (count, requirement) in enumerate(requirements):
        requirement_name = requirement["name"]
        requirement_value = requirement["values"][0][0]
        display_mode = requirement["displayMode"]

        if display_mode == 1:
            image = make_text_image(requirement_value + " ", (255, 255, 255))
            property_images.append(image)
            texts.append((requirement_value + " ", (255, 255, 255)))
            image = make_text_image(requirement_name, (99, 99, 99))
            texts.append((requirement_name, (99, 99, 99)))
            property_images.append(image)
        elif display_mode == 0:
            image = make_text_image(requirement_name + " ", (99, 99, 99))
            texts.append((requirement_name + " ", (99, 99, 99)))
            property_images.append(image)
            image = make_text_image(requirement_value, (255, 255, 255))
            texts.append((requirement_value, (255, 255, 255)))
            property_images.append(image)

        if len(requirements) > 1 and count < len(requirements) - 1:
            image = make_text_image(", ", grey)
            texts.append((", ", (99, 99, 99)))
            property_images.append(image)

    return create_row(texts, tooltip_width, 20)


def make_explicit_mods(data):
    global tooltip_width
    explicit = data["explicitMods"]
    explicits = []
    for e in explicit:
        real_text_img = create_row([(e, (107, 136, 255))], tooltip_width, 20)
        explicits.append(real_text_img)

    return merge_images(explicits, 1)


def make_implicit_mods(data):
    global tooltip_width
    implicit = data["implicitMods"]
    implicits = []
    for e in implicit:
        real_text_img = create_row([(e, (107, 136, 255))], tooltip_width, 20)
        implicits.append(real_text_img)

    return merge_images(implicits, 1)


def create_row(part_list, width, height):
    images = []

    if isinstance(part_list[0], Image.Image):
        for t in part_list:
            images.append(t)
    else:
        for t in part_list:
            img = make_text_image(t[0], t[1])
            images.append(img)

    full_text_img = merge_images(images, 0)
    row_img = Image.new("RGB", (width, height), (0, 0, 0))
    row_img.paste(full_text_img, (width / 2 - full_text_img.size[0] / 2, height / 2 - full_text_img.size[1] / 2))

    return row_img


#Orientation: 0 horiz, 1 vert
def merge_images(images, orientation):
    merged = None
    if orientation == 0:
        height = images[0].size[1]
        width = 0
        for i in images:
            width += i.size[0]

        merged = Image.new("RGB", (width, height))
        cur_pos = 0
        for i in images:
            merged.paste(i, (cur_pos, 0), i)
            cur_pos += i.size[0]
    elif orientation == 1:
        height = 0
        width = images[0].size[0]
        for i in images:
            height += i.size[1]

        merged = Image.new("RGB", (width, height))
        cur_pos = 0
        for i in images:
            merged.paste(i, (0, cur_pos))
            cur_pos += i.size[1]
    return merged


def make_experience_bar(data):
    obj = data["additionalProperties"][0]
    bar_back = Image.open("images/headers/GemExperienceBar.jpg")
    bar_fill = Image.open("images/headers/GemExperienceFill2.jpg")
    new_img = Image.new("RGBA", (1, 13))
    new_img.paste(bar_fill, (0, 0))
    cur_pos = 4
    progress = obj["progress"]
    num = int(205 * progress)
    for i in range(0, num):
        bar_back.paste(bar_fill, (cur_pos, 3))
        cur_pos += 1

    progress_text = make_text_image(" " + obj["values"][0][0], color=(255, 255, 255))

    global tooltip_width
    bar_back = bar_back.convert("RGBA")
    exp_row = create_row([bar_back, progress_text], tooltip_width, 20)
    return exp_row


def make_text_image(text, color, font="Fontin-SmallCaps.ttf", font_size=14):
    font = ImageFont.truetype(font, font_size)
    img = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
    img_drawer = ImageDraw.Draw(img)
    text_size = img_drawer.textsize(text, font)
    img = img.resize(text_size)
    img_drawer = ImageDraw.Draw(img)
    pos = (0, 0)
    if text == ", ": # 0,0 doesn't work since tail goes backwards (guess), tail is 2 pixels wide
        pos = (2, 0)
    img_drawer.text(pos, text, color, font)
    return img


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        f = open("json.txt")
        main(f.read())
