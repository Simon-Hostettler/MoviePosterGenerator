# Script which gets average color of frames from video file, then converts it into different posters

import sys
import os
import cv2
import regex as re
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageDraw

MOVIE_TITLE = "placeholder"


def analyse_frames(movie_path):
    # Opens video in cv2, gets frames each second, calculates average color of frame and writes it into file
    # how many frames to look at per second
    FRAME_PER_SEC = 1

    with open(MOVIE_TITLE, "w") as file:
        video = cv2.VideoCapture(movie_path)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(video.get(cv2.CAP_PROP_FPS))
        video.set(cv2.CAP_PROP_POS_MSEC, 0)

        for i in progressbar(range(int(total_frames/(fps/FRAME_PER_SEC))), "Frames analyzed: "):
            # only want one fps, skip the rest
            for _ in range(0, int(fps/FRAME_PER_SEC)):
                video.grab()
            _, frame = video.retrieve()

            # this code gets the average framecolor in BGR, replaces whitespaces with commas,
            # splits the three colors, inverses them to RGB and then joins them again with commas
            if frame is not None:
                color = ",".join(reversed((re.sub("\s+", ",", str(frame.mean(axis=(0, 1), dtype=int))[
                    1:-1].strip())).split(",")))
                file.write(color + "\n")


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
    print("Successfully rendered barcode_poster")


def create_wave_poster():
    # creates png with pixel height equal to the analysed frames, width is 2/3 of height (standard poster format)
    # draws a line each loop whose width depends on relative brightness of frame to create wave effect

    # how much the brightness affects the length of a line, exponential
    BRIGHTNESS_COEFF = 0.3
    # how much the length between the actual and last line should differ, linear
    LINE_VARIATION = 40

    with open(MOVIE_TITLE) as file:
        lines = file.readlines()
        color_list = [tuple(map(int, i.split(','))) for i in lines[:-1]]

    height = int(file_len(MOVIE_TITLE) * 1.2)
    width = int(height / (1 + 7/9))
    mid = int(width / 2)
    min_line_width = int(width / 20)
    img = Image.new('RGB', (width, height), color="black")

    counter = int(file_len(MOVIE_TITLE) * 0.1)
    draw = ImageDraw.Draw(img)
    brightness = get_color_brightness(color_list[0])
    # brightness = value between 0&1, by converting color to grayscale
    last_length = int(min_line_width ** (1 + BRIGHTNESS_COEFF * brightness))

    for color in color_list:
        brightness = get_color_brightness(color)
        length = int(min_line_width ** (1 + BRIGHTNESS_COEFF * brightness))

        # if line brighter than last, extend it, else shorten it
        if length > last_length:
            length = int(
                ((last_length + 3 + LINE_VARIATION*brightness) + last_length) / 2)
        else:
            length = int(
                ((last_length - 3 - LINE_VARIATION*brightness) + last_length) / 2)

        last_length = length
        left = (mid - length, counter)
        right = (mid + length, counter)
        draw.line([left, right], fill=color)

        counter += 1
    del draw
    img.save(MOVIE_TITLE + "_wave.png")
    print("Successfully rendered wave_poster")


def create_average_poster():
    # averages a number of frame then draws a polygon for each color, length depending on previous and following brightness

    # sets number of frames to average colors together
    NUM_FRAMES_GROUPED = 30
    # how much the brightness affects the length of a line, exponential
    BRIGHTNESS_COEFF = 0.3

    with open(MOVIE_TITLE) as file:
        lines = file.readlines()
        color_list = [tuple(map(int, i.split(',')))
                      for i in lines[:-1]]

    height = int(file_len(MOVIE_TITLE) * 1.2)
    width = int(height / (1.5))
    mid = int(width / 2)
    min_line_width = int(width / 20)
    img = Image.new('RGB', (width, height), color=(26, 28, 33, 0))

    # Setting up list of averaged colors
    reduced_colors = []
    count_colors = 0
    tuplecolor = (color_list[0])
    for x in range(1, len(color_list)):
        if count_colors < NUM_FRAMES_GROUPED:
            tuplecolor = tuple(map(sum, zip(tuplecolor, color_list[x])))
            count_colors += 1
        else:
            reduced_colors.append(
                tuple(int(ti/NUM_FRAMES_GROUPED) for ti in tuplecolor))
            tuplecolor = tuple(map(sum, zip((0, 0, 0), color_list[x])))
            count_colors = 0

    counter = int(file_len(MOVIE_TITLE) * 0.1)
    draw = ImageDraw.Draw(img)
    brightness = get_color_brightness(reduced_colors[0])
    # brightness = value between 0&1, by converting color to grayscale
    last_length = int(min_line_width ** (1 + BRIGHTNESS_COEFF * brightness))
    next_length = int(min_line_width ** (1 + BRIGHTNESS_COEFF *
                                         get_color_brightness(reduced_colors[1])))

    for x in range(len(reduced_colors)-1):
        brightness = get_color_brightness(reduced_colors[x])
        length = int(min_line_width ** (1 + BRIGHTNESS_COEFF * brightness))
        next_length = int(min_line_width ** (1 + BRIGHTNESS_COEFF *
                                             get_color_brightness(reduced_colors[x+1])))
        last_length = length

        top_left = (mid - last_length, counter)
        top_right = (mid + last_length, counter)
        bot_left = (mid - next_length, counter + NUM_FRAMES_GROUPED)
        bot_right = (mid + next_length, counter + NUM_FRAMES_GROUPED)
        draw.polygon([top_left, top_right, bot_right, bot_left],
                     fill=reduced_colors[x])

        counter += NUM_FRAMES_GROUPED
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
    video_path = askopenfilename()
    MOVIE_TITLE = os.path.basename(video_path).split('.')[0]
    try:
        if not(os.path.isfile(sys.path[0]+"/"+MOVIE_TITLE)):
            analyse_frames(video_path)
    except Exception as e:
        print(e)
    create_average_poster()
    create_wave_poster()
    create_barcode_poster()
