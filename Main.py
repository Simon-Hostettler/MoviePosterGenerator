# Script which gets average color of frames from video file, then converts it into different posters

import sys
import cv2
import PIL
from PIL import Image, ImageDraw

VIDEO_PATH = "x"

# Title of file in which average colors will be written
MOVIE_TITLE = "x"


def analyse_frames():
    # Opens video in cv2, gets frame every 100ms, converts it to PIL Image, then writes average color into file
    try:
        with open(MOVIE_TITLE,"w") as file:
            counter = 0
            video = cv2.VideoCapture(VIDEO_PATH)
            video.set(cv2.CAP_PROP_POS_AVI_RATIO,1)
            total_seconds = video.get(cv2.CAP_PROP_POS_MSEC)
            video.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
            succeeded, frame = video.read()
            succeeded = True
            while succeeded:
                video.set(cv2.CAP_PROP_POS_MSEC, (counter*100))
                succeeded, frame = video.read()
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img)
                img_pil = img_pil.resize((1, 1))
                color = img_pil.getpixel((0, 0))
                color = str(color)
                color = color[1:-1]
                file.write((str(color) + "\n"))
                counter += 1
                print("Tenth of Seconds analyzed: {} / {}".format(counter, int(total_seconds / 100)))
    except:
        print("Error occured.")


def file_len(file_name):
    # returns line number of file
    lines = sum(1 for line in open(file_name))
    return lines


def get_color_brightness(c):

    # calculates perceived brightness of color by converting to greyscale, returns float from 0 - 1
    brightness = (c[0] * 0.2989) + (c[1] * 0.5870) + (c[2] * 0.114)
    brightness = brightness / 255
    return brightness


def create_barcode_poster():
    # creates png with pixel height equal to the analysed frames, width is 2/3 of height (standard poster format)
    # draws a horizontal line with color of every frame
    height = file_len(MOVIE_TITLE)
    width = int(height / 1.5)
    img = Image.new('RGB', (width, height), color = 'white')
    with open(MOVIE_TITLE) as file:
        color_list = [tuple(map(int, i.split(','))) for i in file]
    counter = 0
    draw = ImageDraw.Draw(img)
    for color in color_list:
        left = (0, counter)
        right = (width, counter)
        draw.line([left, right], fill=color)
        counter += 1
        print(counter)
    del draw
    img.save(MOVIE_TITLE + "_barcode.png")


def create_wave_poster():
    # creates png with pixel height equal to the analysed frames, width is 2/3 of height (standard poster format)
    # draws a line each loop whose width depends on relative brightness of frame to create wave effect
    height = int(file_len(MOVIE_TITLE) * 1.2)
    width = int(height / (1 + 7/9))
    mid = int(width / 2)
    min_line_width = int(width / 20)
    img = Image.new('RGB', (width, height), color='black')
    with open(MOVIE_TITLE) as file:
        color_list = [tuple(map(int, i.split(','))) for i in file]
    counter = int(file_len(MOVIE_TITLE) * 0.1)
    draw = ImageDraw.Draw(img)
    brightness = get_color_brightness(color_list[0])
    last_len = int(min_line_width ** (1 + 0.3 * brightness)) # brightness = value between 0&1, by converting color to grayscale
    for color in color_list:
        brightness = get_color_brightness(color)
        actual_len = int(min_line_width ** (1 + 0.3 * brightness))
        if actual_len > last_len:
            actual_len = int(((last_len + 3 + 40*brightness) + last_len) /2)
        else:
            actual_len = int(((last_len - 3 - 40*brightness) + last_len) /2)
        last_len = actual_len
        left = (mid - actual_len, counter)
        right = (mid + actual_len, counter)
        draw.line([left, right], fill=color)
        counter += 1
        print(counter)
    del draw
    img.save(MOVIE_TITLE + "_wave.png")


def create_average_poster():
    # averages a number of frame then draws a polygon for each color, length depending on previous and following brightness

    # sets number of frames to average together
    NUM_COLORS_AVERAGED = 30
    height = int(file_len(MOVIE_TITLE) * 1.2)
    width = int(height / (1.5))
    mid = int(width / 2)
    min_line_width = int(width / 20)
    img = Image.new('RGB', (width, height), color='black')
    with open(MOVIE_TITLE) as file:
        color_list = [tuple(map(int, i.split(','))) for i in file]
    smaller_color_list = []
    count_colors = 0
    tuplecolor = (color_list[0])
    for x in range(1, len(color_list)):
        if count_colors < NUM_COLORS_AVERAGED:
            tuplecolor = tuple(map(sum,zip(tuplecolor, color_list[x])))
            count_colors += 1
        else:
            smaller_color_list.append(tuple(int(ti/NUM_COLORS_AVERAGED) for ti in tuplecolor))
            tuplecolor = (0,0,0)
            tuplecolor = tuple(map(sum, zip(tuplecolor, color_list[x])))
            count_colors = 0
    counter = int(file_len(MOVIE_TITLE) * 0.1)
    draw = ImageDraw.Draw(img)
    brightness = get_color_brightness(smaller_color_list[0])
    last_len = int(min_line_width ** (1 + 0.3 * brightness)) # brightness = value between 0&1, by converting color to grayscale
    next_len = int(int(min_line_width ** (1 + 0.3 * get_color_brightness(smaller_color_list[1]))))
    for x in range(len(smaller_color_list)-1):
        brightness = get_color_brightness(smaller_color_list[x])
        actual_len = int(min_line_width ** (1 + 0.3 * brightness))
        next_len = int(int(min_line_width ** (1 + 0.3 * get_color_brightness(smaller_color_list[x+1]))))
        last_len = actual_len
        left1 = (mid - last_len, counter)
        right1 = (mid + last_len, counter)
        left2 = (mid - next_len, counter +NUM_COLORS_AVERAGED)
        right2 = (mid + next_len, counter+NUM_COLORS_AVERAGED)
        draw.polygon([left1,right1,right2,left2], fill=smaller_color_list[x])
        counter += NUM_COLORS_AVERAGED
        print(counter)
    del draw
    img.save(MOVIE_TITLE + "_average.png")


def resize_image(file, max_length):
    img = Image.open(file)
    img.thumbnail((max_length, max_length), Image.LANCZOS)
    img.save(file)

if __name__ == "__main__":

    #analyse_frames()
    create_average_poster()
