try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

import os, sys
from os import listdir
from os.path import isfile, join

import shutil

from os import chdir
from os.path import dirname, realpath
import random

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# My temp location of the picture files
# scl_loading_zone = "/Volumes/Cal's HDD/Cal's Files/Google Drive/scl_testing/test_loading_zone"
scl_loading_zone = "test_loading_zone"
# My temp location for generated text files
textpath = "test_text_files"
#textpath = "/Volumes/Cal's HDD/Cal's Files/Google Drive/scl_testing/test_text_files"
# My temp location for generated text files
dest_path = "test_completed_files"
# dest_path = "/Volumes/Cal's HDD/Cal's Files/Google Drive/scl_testing/test_completed_files"

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
'''
def get_data():
    file_names = []
    path = "/var/www/html/"
    dirs = os.listdir( path )
    for file in dirs:
        file_names.append(file)
    return file_names

Make a front page:
-


@app.route('/')
def display_homepage():
    return render_template('home.html', file_names=get_data())
'''
@app.route('/')
def display_homepage():
    return 'Hello'
'''
#
#@app.route('/test_completed_files/<file>')
#def uploaded_file(file):
#    return render_template('base.html', file=file)

#@app.route('/test_completed_files/<file>')
#def send_file(file):
#    return send_from_directory('test_completed_files', file)


# THIS IS A TEST!
# PART 2
'''

if __name__ == "__main__":
    app.run(debug=True)