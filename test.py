from PIL import Image
from ocr import OCR
import numpy as np
import pandas as pd


def group_text_proximity(dataframe, y_threshold=0.1, x_threshold=0.2):
    # Ensure the input is a DataFrame
    if isinstance(dataframe, tuple):
        dataframe = dataframe[0]

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected input to be a pandas DataFrame")

    # Extract columns and convert to numpy arrays for easier manipulation
    content = np.array(dataframe["Content"].tolist())
    x = np.array(dataframe["x"].tolist())
    y = np.array(dataframe["y"].tolist())
    w = np.array(dataframe["Length"].tolist())

    # Initialize variables for grouping
    grouped_text = []
    temp_group = [content[0]]
    prev_y = y[0]
    prev_x = x[0]

    # Iterate through the elements
    for i in range(1, len(content)):
        # Debug: Print current and previous positions
        print(
            f"Comparing: content='{content[i]}', x={x[i]}, y={y[i]} with prev_x={prev_x}, prev_y={prev_y}"
        )

        # Check if the current text is close enough to the previous one
        if abs(y[i] - prev_y) <= y_threshold and abs(x[i] - prev_x) <= x_threshold:
            temp_group.append(content[i])
        else:
            # Join and store the current group, then start a new one
            grouped_text.append(" ".join(temp_group))
            print(f"Group ended. Group text: {grouped_text[-1]}")
            temp_group = [content[i]]

        # Update previous values
        prev_y = y[i]
        prev_x = x[i]

    # Append the last group
    if temp_group:
        grouped_text.append(" ".join(temp_group))
        print(f"Final group text: {grouped_text[-1]}")

    return grouped_text


# Make sure to unpack recognized_sentences if it's a tuple


image = Image.open("page_1.jpg")
ocr_instance = OCR(image=image)
recognized_sentences = ocr_instance.recognize()
if recognized_sentences:
    if isinstance(recognized_sentences, dict):
        recognized_sentences = pd.DataFrame(recognized_sentences)
        print("Converted recognized_sentences to DataFrame")
    else:
        raise TypeError("Expected recognized_sentences to be a dictionary")
    grouped_sentences = group_text_proximity(
        recognized_sentences, y_threshold=0.1, x_threshold=0.2
    )
    print(grouped_sentences)
