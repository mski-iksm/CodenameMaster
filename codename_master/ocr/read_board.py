import easyocr
import numpy as np
from PIL import Image
from pydantic import BaseModel


class WordsByColor(BaseModel):
    blue_words: list[str]
    red_words: list[str]
    black_words: list[str]
    white_words: list[str]


def _read_words(image: Image) -> dict[str, list[list[int]]]:
    reader = easyocr.Reader(['ja'])
    readtexts = reader.readtext(np.array(image))
    return {readtext[1]: readtext[0] for readtext in readtexts}


RED_RGB = [235, 76, 25]
BLUE_RGB = [20, 153, 180]
BLACK_RGB = [64, 64, 64]
WHITE_RGB = [240, 209, 167]


def _find_color(bbox: list[list[int]], image: Image) -> str:
    bbox_height = bbox[2][1] - bbox[0][1]
    search_window_l = bbox[0][0]
    search_window_r = bbox[1][0]
    search_window_u = bbox[0][1] - bbox_height
    search_window_d = bbox[0][1]

    window_image_array = np.array(image)[search_window_u:search_window_d, search_window_l:search_window_r]
    window_median_R = np.median(window_image_array[:, :, 0])
    window_median_G = np.median(window_image_array[:, :, 1])
    window_median_B = np.median(window_image_array[:, :, 2])
    window_median_RGB = [window_median_R, window_median_G, window_median_B]

    # 色の差をユークリッド距離で計算
    distance_to_red = np.linalg.norm(np.array(RED_RGB) - np.array(window_median_RGB), ord=2)
    distance_to_blue = np.linalg.norm(np.array(BLUE_RGB) - np.array(window_median_RGB), ord=2)
    distance_to_black = np.linalg.norm(np.array(BLACK_RGB) - np.array(window_median_RGB), ord=2)
    distance_to_white = np.linalg.norm(np.array(WHITE_RGB) - np.array(window_median_RGB), ord=2)

    closest_color_distance = min(distance_to_red, distance_to_blue, distance_to_black, distance_to_white)
    if closest_color_distance == distance_to_red:
        return 'red'
    if closest_color_distance == distance_to_blue:
        return 'blue'
    if closest_color_distance == distance_to_black:
        return 'black'
    return 'white'


def read_board(image: Image) -> WordsByColor:
    read_words = _read_words(image=image)

    # 各文字の所定の場所の色を探す
    word2color = {word: _find_color(bbox=bbox, image=image) for word, bbox in read_words.items()}

    red_words = [word for word, color in word2color.items() if color == 'red']
    blue_words = [word for word, color in word2color.items() if color == 'blue']
    black_words = [word for word, color in word2color.items() if color == 'black']
    white_words = [word for word, color in word2color.items() if color == 'white']
    return WordsByColor(blue_words=blue_words, red_words=red_words, black_words=black_words, white_words=white_words)
