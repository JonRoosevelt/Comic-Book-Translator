from cv2.typing import MatLike
from deep_translator import GoogleTranslator
import cv2 as cv
import pytesseract as ocr
from pre_processing import get_grayscale
from dataclasses import dataclass
import unidecode
import sys

if sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
    try:
        ocr.pytesseract.tesseract_cmd = (
            "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        )
    except FileNotFoundError as err:
        raise Exception(
            "Se você está utilizando o sistema Windows, favor instalar o Tesseract-OCR",
            err,
        )


def translate(sentence) -> str | None:
    try:
        sentence_translated = GoogleTranslator("en", "pt").translate(sentence)
        removed_unwanted_characters = unidecode.unidecode(sentence_translated)
        print(removed_unwanted_characters)
        return removed_unwanted_characters
    except Exception:
        removed_unwanted_characters = sentence


def file_writer(num: int, img: MatLike) -> None:
    cv.imwrite(f"Page Translated{num}.jpg", img)
    print(f"PAGE {num} COMPLETED")


@dataclass
class FileData:
    img: MatLike

    def get_data_from_file(self) -> str:
        custom_config = r"--oem 1 --psm 12"
        data = ocr.image_to_data(self.img, lang="eng", config=custom_config)
        print(data)
        return data


@dataclass
class Sentence:
    words = []
    coords = []

    def add_word(self, word, coord):
        self.words.append(word)
        self.coords.append(coord)

    def translate(self):
        sentence = " ".join(self.words)
        return translate(sentence)

    def avg_coords(self):
        avg_x = sum(x for x, _ in self.coords) // len(self.coords)
        avg_y = sum(y for _, y in self.coords) // len(self.coords)
        return avg_x, avg_y

    def reset(self):
        self.words = []
        self.coords = []


@dataclass
class TextPlacer:
    data: str
    img: MatLike

    def put_text_in_page(self) -> None:
        font = cv.FONT_HERSHEY_COMPLEX_SMALL
        sentences = []
        current_sentence = Sentence()
        previous_position = None
        threshold = 50

        for x, b in enumerate(self.data.splitlines()):
            if x != 0:
                b = b.split()
            if len(b) == 12:
                x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
                cv.rectangle(self.img, (x, y), (w + x, h + y), (255, 255, 255), -1)
                word = b[11]
                if previous_position is None or abs(x - previous_position) < threshold:
                    current_sentence.add_word(word, (x, y))
                else:
                    sentences.append(
                        (current_sentence.translate(), current_sentence.avg_coords())
                    )
                    current_sentence.reset()
                    current_sentence.add_word(word, (x, y))
                previous_position = x

        if current_sentence.words:
            sentences.append(
                (current_sentence.translate(), current_sentence.avg_coords())
            )

        for sentence, (x, y) in sentences:
            cv.putText(
                self.img,
                sentence,
                (x - 7, y + 20),
                font,
                1,
                (0, 0, 0),
                1,
            )


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
            gray = get_grayscale(img)
            _, binary_image = cv.threshold(gray, 150, 255, cv.THRESH_BINARY)
            denoised = cv.medianBlur(binary_image, 3)
            data = FileData(denoised).get_data_from_file()
            textPlacer = TextPlacer(data, img)
            textPlacer.put_text_in_page()

            file_writer(num, img)

            self.initial_page += 1

        print("COMIC-BOOK TRANSLATED SUCCESSFULLY!")
