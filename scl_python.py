try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

import os
from os import listdir
from os.path import isfile, join

import shutil

# My temp location of the picture files
scl_loading_zone = "/Volumes/Cal's HDD/Cal's Files/Google Drive/scl_testing/test_loading_zone"

# My temp location for generated text files
textpath = "/Volumes/Cal's HDD/Cal's Files/Google Drive/scl_testing/test_text_files"

# My temp location for generated text files
dest_path = "/Volumes/Cal's HDD/Cal's Files/Google Drive/scl_testing/test_completed_files"

# checks a specific folder and finds out if it is empty or not
def file_check(path):
    files_no_folders = [f for f in listdir(path) if isfile(join(path, f))]
    if len(files_no_folders) <= 1:
        return False
    else:
        return True

# takes an image, returns text based on OCR
def ocr_extract(file):
    ocr_text = pytesseract.image_to_string(Image.open(file))
    return ocr_text

# takes a string, file name, and path,
# creates a .txt file with the string
# as the body, and places it at end of path
def text_file_creator(string, filename, textpath):
    new_file = open(os.path.join(textpath, filename), "w")
    new_file.write(string)

# Puts it together -
# images in folder,
# OCR on images,
# create text file in different folder,
# original image gets moved to another folder.
def jpg_to_text(path):
    count = -1
    if file_check(path) is True:
        for filename in os.listdir(path):
            if filename.endswith(".JPG" or ".JPEG" or ".PNG" or ".GIF" or ".TIF"):
                count += 1
                text_name = "image" + str(count)
                text = ocr_extract(os.path.join(path, filename))
                text_file_creator(text, text_name, textpath)
                shutil.move(os.path.join(path, filename), dest_path)

jpg_to_text(scl_loading_zone)


# THIS IS A TEST!
