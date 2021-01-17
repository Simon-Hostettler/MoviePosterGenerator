# Script which gets average color of frames from video file, then converts it into different posters

import sys
import os
import cv2
import numpy as np
import PIL
from PIL import Image, ImageDraw

VIDEO_PATH = "/home/simon/Videos/eoe.mkv"

# Title of file in which average colors will be written
MOVIE_TITLE = "NGE"


def analyse_frames(movie_path):
    # Opens video in cv2, gets frame every second, calculates average color of frame and writes it into file
    try:
        with open(MOVIE_TITLE, "w") as file:
            counter = 0
            video = cv2.VideoCapture(movie_path)
            total_seconds = int(video.get(
                cv2.CAP_PROP_FRAME_COUNT)/video.get(cv2.CAP_PROP_FPS))
            _, frame = video.read()
            for i in progressbar(range(total_seconds), "Frames analyzed: "):
                video.set(cv2.CAP_PROP_POS_MSEC, (counter*1000))
                _, frame = video.read()
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                color = str(img.mean(axis=(0, 1), dtype=int))[
                    1:-1].strip().replace("   ", " ").replace("  ", " ").replace(" ", ", ")
                file.write(color + "\n")
                counter += 1
    except:
        print("Couldn't read movie file.")


def file_len(file_name):
    # returns line number of file
    return sum(1 for line in open(file_name))


def get_color_brightness(c):
    # calculates perceived brightness of color by converting to greyscale, returns float from 0 - 1
    return ((c[0] * 0.2989) + (c[1] * 0.5870) + (c[2] * 0.114))/255


def create_barcode_poster():
    # creates png with pixel height equal to the analysed frames, width is 2/3 of height (standard poster format)
    # draws a horizontal line with color of every frame
    height = file_len(MOVIE_TITLE)
    width = int(height / 1.5)

    img = Image.new('RGB', (width, height), color='white')
    with open(MOVIE_TITLE) as file:
        lines = file.readlines()
        color_list = [tuple(map(int, i.split(','))) for i in lines[:-1]]
    draw = ImageDraw.Draw(img)
    for counter, color in enumerate(color_list):
        left = (0, counter)
        right = (width, counter)
        draw.line([left, right], fill=color)
    del draw
    img.save(MOVIE_TITLE + "_barcode.png")
    print("Succesfully rendered barcode_poster")


def create_wave_poster():
    # creates png with pixel height equal to the analysed frames, width is 2/3 of height (standard poster format)
    # draws a line each loop whose width depends on relative brightness of frame to create wave effect
    with open(MOVIE_TITLE) as file:
        lines = file.readlines()
        color_list = [tuple(map(int, i.split(','))) for i in lines[:-1]]

    height = int(file_len(MOVIE_TITLE) * 1.2)
    width = int(height / (1 + 7/9))
    mid = int(width / 2)
    min_line_width = int(width / 20)
    img = Image.new('RGB', (width, height), color='black')

    counter = int(file_len(MOVIE_TITLE) * 0.1)
    draw = ImageDraw.Draw(img)
    brightness = get_color_brightness(color_list[0])
    # brightness = value between 0&1, by converting color to grayscale
    last_len = int(min_line_width ** (1 + 0.3 * brightness))

    for color in color_list:
        brightness = get_color_brightness(color)
        actual_len = int(min_line_width ** (1 + 0.3 * brightness))
        if actual_len > last_len:
            actual_len = int(((last_len + 3 + 40*brightness) + last_len) / 2)
        else:
            actual_len = int(((last_len - 3 - 40*brightness) + last_len) / 2)
        last_len = actual_len
        left = (mid - actual_len, counter)
        right = (mid + actual_len, counter)
        draw.line([left, right], fill=color)
        counter += 1
    del draw
    img.save(MOVIE_TITLE + "_wave.png")
    print("Succesfully rendered wave_poster")


def create_average_poster():
    # averages a number of frame then draws a polygon for each color, length depending on previous and following brightness

    # sets number of frames to average together
    NUM_COLORS_AVERAGED = 30
    with open(MOVIE_TITLE) as file:
        lines = file.readlines()
        color_list = [tuple(map(int, i.split(',')))
                      for i in lines[:-1]]

    height = int(file_len(MOVIE_TITLE) * 1.2)
    width = int(height / (1.5))
    mid = int(width / 2)
    min_line_width = int(width / 20)
    img = Image.new('RGB', (width, height), color='black')

    # Setting up list of averaged colors
    smaller_color_list = []
    count_colors = 0
    tuplecolor = (color_list[0])
    for x in range(1, len(color_list)):
        if count_colors < NUM_COLORS_AVERAGED:
            tuplecolor = tuple(map(sum, zip(tuplecolor, color_list[x])))
            count_colors += 1
        else:
            smaller_color_list.append(
                tuple(int(ti/NUM_COLORS_AVERAGED) for ti in tuplecolor))
            tuplecolor = tuple(map(sum, zip((0, 0, 0), color_list[x])))
            count_colors = 0

    counter = int(file_len(MOVIE_TITLE) * 0.1)
    draw = ImageDraw.Draw(img)
    brightness = get_color_brightness(smaller_color_list[0])
    # brightness = value between 0&1, by converting color to grayscale
    last_len = int(min_line_width ** (1 + 0.3 * brightness))
    next_len = int(
        int(min_line_width ** (1 + 0.3 * get_color_brightness(smaller_color_list[1]))))

    for x in range(len(smaller_color_list)-1):
        brightness = get_color_brightness(smaller_color_list[x])
        actual_len = int(min_line_width ** (1 + 0.3 * brightness))
        next_len = int(int(min_line_width ** (1 + 0.3 *
                                              get_color_brightness(smaller_color_list[x+1]))))
        last_len = actual_len
        top_left = (mid - last_len, counter)
        top_right = (mid + last_len, counter)
        bot_left = (mid - next_len, counter + NUM_COLORS_AVERAGED)
        bot_right = (mid + next_len, counter+NUM_COLORS_AVERAGED)
        draw.polygon([top_left, top_right, bot_right, bot_left],
                     fill=smaller_color_list[x])
        counter += NUM_COLORS_AVERAGED
    del draw
    img.save(MOVIE_TITLE + "_average.png")
    print("Succesfully rendered average_poster")


def resize_image(file, max_length):
    img = Image.open(file)
    img.thumbnail((max_length, max_length), Image.LANCZOS)
    img.save(file)


def progressbar(iterator, pre="", size=60, file=sys.stdout):
    count = len(iterator)
    def clear(): return os.system('clear')

    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (pre, "#"*x, "."*(size-x), j, count))
        file.flush()
    show(0)
    for i, item in enumerate(iterator):
        yield item
        clear()
        show(i+1)
        file.write("\n")
        file.flush()


if __name__ == "__main__":
    # if not(os.path.isfile(sys.path[0]+"/"+MOVIE_TITLE)):
    analyse_frames(VIDEO_PATH)
    create_average_poster()
    create_wave_poster()
    create_barcode_poster()
