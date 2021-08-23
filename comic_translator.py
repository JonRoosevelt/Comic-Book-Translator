from PIL import Image
from translate import Translator
from deep_translator import GoogleTranslator
import cv2 as cv
import pytesseract as ocr
from pre_processing import get_grayscale
from dataclasses import dataclass
import unidecode
import numpy as np
import sys
if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
    try:
        ocr.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    except FileNotFoundError as err:
        raise (
            'Se você está utilizando o sistema Windows, favor instalar o Tesseract-OCR',
            err)

def translate(word) -> str:
    try:
        word_translated = GoogleTranslator('en', 'pt').translate(word)
        removed_unwanted_characters = unidecode.unidecode(word_translated)  # remove weird shit
        print(removed_unwanted_characters)
    except Exception:
        removed_unwanted_characters = word
    finally:
        return removed_unwanted_characters

def file_writer(num: int, img: Image) -> None:
    cv.imwrite(f'Page Translated{num}.jpg', img)
    print(f'PAGE {num} COMPLETED')

@dataclass
class FileData:
    img: Image

    def get_data_from_file(self) -> str:
        custom_config = r'--oem 3 --psm 12'
        data = ocr.image_to_data(self.img, lang="eng", config=custom_config)
        print(data)
        return data
                           

@dataclass
class TextPlacer:
    data: str
    img: Image

    def put_text_in_page(self) -> None:
        font = cv.FONT_HERSHEY_COMPLEX_SMALL
        for x, b in enumerate(self.data.splitlines()):
            if x != 0:
                b = b.split()
            if len(b) == 12:
                x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
                cv.rectangle(self.img, (x, y), (w+x, h+y), (255, 255, 255), -1)
                word = b[11]
                try:
                    word_translated = translate(word)
                except ValueError as err:
                    print(str(err))
                    continue
                cv.putText(self.img, word_translated, (x-7, y+20),
                            font, 1, (0, 0, 0), 1)  # put text on the screen

@dataclass
class ComicTranslator:
    file_path: str
    initial_page: int
    final_page: int
    target_lang: str

    def translate_comic(self) -> None:
        while self.initial_page < self.final_page:
            num = self.initial_page
            img = cv.imread(self.file_path)
            img = get_grayscale(img)
            data = FileData(img).get_data_from_file()
            textPlacer = TextPlacer(data, img)
            textPlacer.put_text_in_page()

            file_writer(num, img)

            self.initial_page += 1

        print('COMIC-BOOK TRANSLATED SUCCESSFULLY!')
