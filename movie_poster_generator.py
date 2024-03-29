# Script which gets average color of frames from video file, then converts it into different posters

from random import sample
import sys
import os
import cv2
import argparse
import numpy as np
from tqdm import tqdm
from distutils.util import strtobool
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument('--gui', default=True,
                    help='whether to use gui to select file or use args')
parser.add_argument('--video_path', type=str, help='file to be read')
parser.add_argument('--randomized_selection', default=True,
                    help='whether to process entire frames (slow) or randomly sample colors (quick)')
parser.add_argument('--sample_rate', type=float, default=0.01,
                    help='percentage of pixels to be randomly sampled')
parser.add_argument('--rotation', type=float, default=0.0,
                    help='degree to which the poster is rotated, 90 = wallpaper orientation')


def analyse_frames(movie_path, file_name, randomized_selection=True, sample_rate=0.01):
    '''Opens movie_path in cv2, gets frames each second, calculates average color of frame and writes it into file_name'''

    # how many frames to look at per second
    FRAME_PER_SEC = 1

    avg_colors = []

    video = cv2.VideoCapture(movie_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    video.set(cv2.CAP_PROP_POS_MSEC, 0)

    for i in tqdm(range(int(total_frames/(fps/FRAME_PER_SEC))), "Frames analyzed: "):
        # only want one fps, skip the rest
        for _ in range(0, int(fps/FRAME_PER_SEC)):
            video.grab()
        _, frame = video.retrieve()

        if frame is not None:
            if randomized_selection:
                avg_color = sample_avg_color(frame, sample_rate)
            else:
                avg_color = full_avg_color(frame)

            avg_colors.append(",".join(map(str, avg_color)))

    with open(file_name, "w") as file:
        file.write("\n".join(avg_colors))


def sample_avg_color(frame, sample_rate=0.01):
    ''' computes average rgb color of sample_rate randomly chosen pixels from frame '''

    total_size = frame.shape[0]*frame.shape[1]
    num_samples = int(sample_rate*total_size)
    frame = np.reshape(frame, (total_size, 3))

    rand_vec = np.random.randint(
        low=0, high=total_size, size=num_samples, dtype=int)

    avg_color = frame[rand_vec].mean(axis=0, dtype=int)
    return list(reversed(avg_color.tolist()))


def full_avg_color(frame):
    ''' computes average rgb color of frame '''

    avg_color = frame.mean(axis=(0, 1), dtype=int)
    return list(reversed(avg_color.tolist()))


def file_len(file_name):
    ''' returns line number of file '''

    return sum(1 for line in open(file_name))


def get_color_brightness(c):
    '''calculates perceived brightness of color by converting to greyscale, returns float from 0 - 1'''
    return ((c[0] * 0.2989) + (c[1] * 0.5870) + (c[2] * 0.114))/255


def create_barcode_poster(file_name, rotation):
    '''creates png with pixel height equal to the analysed frames, width is 2/3 of height (standard poster format).
    Then draws a horizontal line with color of every frame'''

    height = file_len(file_name)
    width = int(height / 1.5)

    img = Image.new('RGB', (width, height), color='white')
    with open(file_name) as file:
        lines = file.readlines()
        color_list = [tuple(map(int, i.split(','))) for i in lines[:-1]]
    draw = ImageDraw.Draw(img)
    for counter, color in enumerate(color_list):
        left = (0, counter)
        right = (width, counter)
        draw.line([left, right], fill=color)
    del draw

    out = img.rotate(rotation, expand=1)
    img.save("Images/" + file_name.split('/')[1] + "_barcode.png")
    print("Successfully rendered barcode_poster")


def create_wave_poster(file_name, rotation):
    '''creates png with pixel height equal to the analysed frames, width is 2/3 of height (standard poster format)
    Then draws a line each loop whose width depends on relative brightness of frame to create wave effect'''

    # how much the brightness affects the length of a line, exponential
    BRIGHTNESS_COEFF = 0.3
    # how much the length between the actual and last line should differ, linear
    LINE_VARIATION = 40

    with open(file_name) as file:
        lines = file.readlines()
        color_list = [tuple(map(int, i.split(','))) for i in lines[:-1]]

    height = int(file_len(file_name) * 1.2)
    width = int(height / (1 + 7/9))
    mid = int(width / 2)
    min_line_width = int(width / 20)
    img = Image.new('RGB', (width, height), color=(26, 28, 33, 0))

    counter = int(file_len(file_name) * 0.1)
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

    out = img.rotate(rotation, expand=1)
    out.save("Images/" + file_name.split('/')[1] + "_wave.png")
    print("Successfully rendered wave_poster")


def create_average_poster(file_name, rotation):
    '''averages a number of frame then draws a polygon for each color, length depending on previous and following brightness'''
    # sets number of frames to average colors together
    NUM_FRAMES_GROUPED = 30
    # how much the brightness affects the length of a line, exponential
    BRIGHTNESS_COEFF = 0.3

    with open(file_name) as file:
        lines = file.readlines()
        color_list = [tuple(map(int, i.split(',')))
                      for i in lines[:-1]]

    height = int(file_len(file_name) * 1.2)
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

    counter = int(file_len(file_name) * 0.1)
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

    out = img.rotate(rotation, expand=1)
    out.save("Images/" + file_name.split('/')[1] + "_average.png")
    print("Successfully rendered average_poster")


def resize_image(file, max_length):
    img = Image.open(file)
    img.thumbnail((max_length, max_length), Image.LANCZOS)
    img.save(file)


def str_to_bool(s):
    if isinstance(s, bool):
        return s
    return strtobool(s)


if __name__ == "__main__":
    args = vars(parser.parse_args())

    if not os.path.exists(sys.path[0]+"/Images/"):
        os.makedirs(sys.path[0]+"/Images/")
    if not os.path.exists(sys.path[0]+"/ColorFiles/"):
        os.makedirs(sys.path[0]+"/ColorFiles/")

    if str_to_bool(args['gui']):
        video_path = askopenfilename()
        file_name = "ColorFiles/" + os.path.basename(video_path).split('.')[0]
        rand_sel = True
        sample_rate = 0.01
        rot = 90
    else:
        video_path = args['video_path']
        file_name = "ColorFiles/" + os.path.basename(video_path).split('.')[0]
        rand_sel = str_to_bool(args['randomized_selection'])
        sample_rate = args['sample_rate']
        rot = args['rotation']

    if not(os.path.isfile(sys.path[0]+"/ColorFiles/"+file_name)):
        analyse_frames(video_path, file_name,
                       randomized_selection=rand_sel, sample_rate=sample_rate)

    create_average_poster(file_name, rot)
    create_wave_poster(file_name, rot)
    create_barcode_poster(file_name, rot)
