from codename_master.ocr.read_board import WordsByColor


def get_my_words(words_by_color: WordsByColor, my_color: str) -> list[str]:
    if my_color == 'red':
        return words_by_color.red_words
    if my_color == 'blue':
        return words_by_color.blue_words

    raise ValueError(f'Invalid my_color: {my_color}')


def get_opponent_words(words_by_color: WordsByColor, my_color: str) -> list[str]:
    if my_color == 'red':
        return words_by_color.blue_words
    if my_color == 'blue':
        return words_by_color.red_words

    raise ValueError(f'Invalid my_color: {my_color}')
