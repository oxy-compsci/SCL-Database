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

# Creating variables for the location
# of the image loading zone, completed
# files, and text files
scl_loading_zone = "test_loading_zone"
textpath = "test_text_files"
dest_path = "test_completed_files"


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

def get_data():
    file_names = []
    path = "test_completed_files"
    dirs = os.listdir( path )
    for file in dirs:
        file_names.append(file)
    return file_names

def get_text_data():
    text_file_names = []
    path = 'test_text_files'
    dirs = os.listdir(path)
    for file in dirs:
        text_file_names.append(file)
    return text_file_names





@app.route('/')
def display_homepage():
    return render_template('home.html', file_names=get_data())

# make a lopp that goes through all the files in the folder, then adds them to the page
@app.route('/<file_name>')
def display_images(file_name):
    image_file_names = get_data()
    text_file_names = get_text_data()
    nested_list = list(zip(image_file_names, text_file_names))
    length = len(nested_list)
    for index in range(length):
        pairing = nested_list[index]
    return render_template('image.html', image_file_name=pairing[0], text_file_name=pairing[1])


@app.route('/test_completed_files/<file_name>')
def image_file(file_name):
    return send_from_directory('test_completed_files', file_name)

'''
    length = len(students)
    for index in range(len(students)):
        student = students[index]
        if username == student.username:
            current_student = student
            prev_student = students[index - 1]
            if index + 1 == len(students):
                next_student = students[0]
            else:
                next_student = students[index + 1]
'''

'''
@app.route('/')
def display_homepage():
    return 'Hello'



if __name__ == '__main__':
    app.run(debug=True)
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