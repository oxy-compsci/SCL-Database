import os
import re

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
import re

app = Flask(__name__)


# Loading_zone is where image files are to uploaded, Text_path is a folder to save completed OCR text files, and
# Dest_path is the folder for the images after they are run through OCR.


Loading_zone = "loading_zone"
Text_path = "completed_text_files"
Dest_path = "completed_files"


# file_check takes a given file as an argument, returns false if that folder contains less than or equal to one file,
# otherwise, returns true.

def file_check(path):
    files_no_folders = [f for f in listdir(path) if isfile(join(path, f))]
    if len(files_no_folders) <= 1:
        return False
    else:
        return True


# ocr_extract takes an (image) file, runs it through OCR, and returns a string of text

def ocr_extract(file):
    ocr_text = pytesseract.image_to_string(Image.open(file))
    return ocr_text


# text_file_creator takes a string of text, a filename and a path (folder) and saves the string into the designated
# with the designated filename

def text_file_creator(string, filename, path):
    new_file = open(os.path.join(path, filename), "w")
    new_file.write(string)


# run_image combines the above functions, it takes a folder, if that folder has more than one file in it, the function
# loops through each file. If that file is a JPEG, PNG, GIF or TIF image, the image will be run through OCR, and the
# associated text file and the original image will be saved to Dest_path, or the completed files folder in Python.

def run_image(path):
    count = -1
    if file_check(path):
        for filename in os.listdir(path):
            print("checking if {} is an image file".format(filename))
            if filename.endswith(".jpg" or ".jpeg" or ".png" or ".gif" or ".tif"):
                print("{} is an image file".format(filename))
                filename = os.path.join(path, filename)
                count += 1
                text_name = "document" + str(count) + "text"
                image_rename = os.path.join(Dest_path, "document" + str(count) + "image")
                text = ocr_extract(filename)
                text_file_creator(text, text_name, Text_path)
                print("renaming {} to {}".format(filename, image_rename))
                os.rename(filename, image_rename)
            else:
                print("{} is not an image file".format(filename))


run_image(Loading_zone)


# get_img_filenames creates a list of all the file names beginning with the word "document" within the "completed_files"
# folder


def get_img_filenames():
    file_names = []
    path = "completed_files"
    dirs = os.listdir(path)
    for file in dirs:
        if file.startswith('document'):
            file_names.append(file)
    return file_names


# get_txt_filenames creates a list of all the file names beginning with the word "document" within the
# "completed_text_files" folder

def get_txt_filenames():
    text_file_names = []
    dirs = os.listdir(Text_path)
    for file in dirs:
        if file.startswith('document'):
            text_file_names.append(file)
    print(text_file_names)
    return text_file_names


@app.route('/')
def display_homepage():
    return render_template('home.html', text_file_names=get_img_filenames())


# make a loop that goes through all the files in the folder, then adds them to the page
@app.route('/<file_name>')
def display_images(file_name):
    image_file_names = get_img_filenames()
    text_file_names = get_txt_filenames()
    nested_list = list(zip(image_file_names, text_file_names))
    length = len(nested_list)
    for index in range(length):
        pairing = nested_list[index]
    file_number = re.search('document(.*)image', file_name)
    file_number = file_number.group(1)
    image_file_name = 'document' + str(file_number) + 'image.jpg'
    text_file_name = 'document' + str(file_number) + 'text'
    text_location = "completed_text_files/" + text_file_name
    with open(text_location, "r") as f:
        txt_content = f.read()
    return render_template('image.html', image_file_name=image_file_name, text_file_name=text_file_name, txt_content=txt_content)




@app.route('/completed_files/<file_name>')
def image_file(file_name):
    return send_from_directory('completed_files', file_name)


@app.route('/completed_text_files/<file_name>')
def text_file(file_name):
    return send_from_directory('completed_text_files', file_name)


if __name__ == "__main__":
    app.run(debug=True)
