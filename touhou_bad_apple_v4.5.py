import cv2
import time
import sys
from PIL import Image
from multiprocessing import Process
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import fpstimer
import moviepy.editor as mp


ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", " "]

frame_size = int(os.get_terminal_size().lines * 1.33)

frame_interval = 1.0 / 30.75

ASCII_LIST = []


def play_audio(path):
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()


def play_video(total_frames):
    # os.system('color F0')
    # os.system('mode 150, 500')

    timer = fpstimer.FPSTimer(30)

    start_frame = 0

    clearscreen()

    for frame in ASCII_LIST:
        text = frame
        lines = len(text.splitlines())
        output(1, 1,"\r" + text)
        timer.sleep()

    # os.system('color 07')

def output(y, x, text):
    print("\033[%d;%dH" % (y, x) + text)

def clearscreen():
    os.system('clear' if os.name == 'posix' else 'cls' )
    ...

# Extract frames from video
def extract_transform_generate(video_path, start_frame, number_of_frames=1000):
    capture = cv2.VideoCapture(video_path)
    capture.set(1, start_frame)  # Points cap to target frame
    current_frame = start_frame
    frame_count = 1
    ret, image_frame = capture.read()
    while ret and frame_count <= number_of_frames:
        ret, image_frame = capture.read()
        if image_frame is None:
            continue
        image = Image.fromarray(image_frame)
        ascii_characters = pixels_to_ascii(greyscale(resize_image(image)))  # get ascii characters
        pixel_count = len(ascii_characters)
        ascii_image = "".join(
            ["\n" + ascii_characters[index:(index + frame_size)] for index in range(0, pixel_count, frame_size)])

        ASCII_LIST.append(ascii_image)


        progress_bar(frame_count, number_of_frames)

        frame_count += 1  # increases internal frame counter
        current_frame += 1  # increases global frame counter

    capture.release()


# Progress bar code is courtesy of StackOverflow user: Aravind Voggu.
# Link to thread: https://stackoverflow.com/questions/6169217/replace-console-output-in-python
def progress_bar(current, total, barLength=25):
    progress = float(current) * 100 / total
    arrow = '#' * int(progress / 100 * barLength - 1)
    spaces = ' ' * (barLength - len(arrow))
    sys.stdout.write('\rProgress: [%s%s] %d%% Frame %d of %d frames' % (arrow, spaces, progress, current, total))


# Resize image
def resize_image(image_frame):
    global frame_size
    term = os.get_terminal_size()

    new_height = term.lines -2 

    frame_size = term.columns -2 

    resized_image = image_frame.resize((frame_size, new_height))
    # print('Aspect ratio: %f' % aspect_ratio)
    # print('New dimensions %d %d' % resized_image.size)
    return resized_image


# Greyscale
def greyscale(image_frame):
    return image_frame.convert("L")


# Convert pixels to ascii
def pixels_to_ascii(image_frame):
    pixels = image_frame.getdata()
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters


# Open image => Resize => Greyscale => Convert to ASCII => Store in text file
def ascii_generator(image_path, start_frame, number_of_frames):
    current_frame = start_frame
    while current_frame <= number_of_frames:
        path_to_image = image_path + '/BadApple_' + str(current_frame) + '.jpg'
        image = Image.open(path_to_image)
        ascii_characters = pixels_to_ascii(greyscale(resize_image(image)))  # get ascii characters
        pixel_count = len(ascii_characters)
        ascii_image = "".join(
            [ascii_characters[index:(index + frame_size)] for index in range(0, pixel_count, frame_size)])
        file_name = r"TextFiles/" + "bad_apple" + str(current_frame) + ".txt"
        try:
            with open(file_name, "w") as f:
                f.write(ascii_image)
        except FileNotFoundError:
            continue
        current_frame += 1


def preflight_operations(path):
    if os.path.exists(path):
        path_to_video = path.strip()
        cap = cv2.VideoCapture(path_to_video)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        video = mp.VideoFileClip(path_to_video)
        path_to_audio = 'audio.mp3'
        video.audio.write_audiofile(path_to_audio)

        frames_per_process = int(total_frames / 4)

        process1_end_frame = frames_per_process
        process2_start_frame = process1_end_frame + 1
        process2_end_frame = process2_start_frame + frames_per_process
        process3_start_frame = process2_end_frame + 1
        process3_end_frame = process3_start_frame + frames_per_process
        process4_start_frame = process3_end_frame + 1
        process4_end_frame = total_frames - 1

        start_time = time.time()
        sys.stdout.write('Beginning ASCII generation...\n')
        extract_transform_generate(path_to_video, 1, process4_end_frame)
        execution_time = time.time() - start_time
        sys.stdout.write('ASCII generation completed! ASCII generation time: ' + str(execution_time))

        return total_frames

    else:
        sys.stdout.write('Warning file not found!\n')


def main():
    clearscreen()
    user_input = 'BadApple.mp4'
    total_frames = preflight_operations(user_input)
    play_audio('audio.mp3')
    play_video(total_frames=total_frames)


if __name__ == '__main__':
    main()
