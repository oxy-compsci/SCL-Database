try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

import os, sys
from os import listdir
from os.path import isfile, join
import re

from flask import Flask, render_template, send_from_directory, request


app = Flask(__name__)

# FOLDER PATHS
Loading_zone = "loading_zone"
Text_path = "completed_text_files"
Dest_path = "completed_files"

# CHECKS IF MORE THAN ONE FILE EXISTS IN A FOLDER
def file_check(path):
    files_no_folders = [f for f in listdir(path) if isfile(join(path, f))]
    if len(files_no_folders) <= 1:
        return False
    else:
        return True

# IMAGE --> OCR STRING
def ocr_extract(file):
    ocr_text = pytesseract.image_to_string(Image.open(file))
    return ocr_text

# CREATES NEW .TXT FILE WITH STRING, FILENAME, AND PATH
def text_file_creator(string, filename, path):
    new_file = open(os.path.join(path, filename), "w")
    new_file.write(string)

# [ENTER DESCRIPTION HERE]
def write_metadata_file(file_name):
    file = open('metadata.txt', 'a')
    file.write('\n\nFile Name: {}\nBox Number: []\nDate Added (mm/dd/yyyy): []\nName of Uploader (Last, First): []'
               '\nComments/Notes about File: []'.format(str(file_name)))
    file.close()

# RETURNS FILE COUNT LOCATED IN METADATA
def next_file_name():
    metadata = open('metadata.txt', 'r')
    metastring = metadata.read()
    find_counter = re.search('File Counter = (.*)\n', metastring)
    filenumber = find_counter.group(1)
    return filenumber
next_file_name()

# RETURNS LIST OF FILE NAMES IN COMPLETED FILES FOLDER
def get_img_filenames():
    file_names = []
    dirs = os.listdir(Dest_path)
    for file in dirs:
        if file.startswith('document'):
            file_names.append(file)
    return file_names

# RETURNS LIST OF FILE NAMES IN COMPLETED TEXT FILES FOLDER
def get_txt_filenames():
    text_file_names = []
    dirs = os.listdir(Text_path)
    for file in dirs:
        if file.startswith('document'):
            text_file_names.append(file)
    return text_file_names

# RUNS IMAGE FILES LOCATED IN LOADING_ZONE THROUGH OCR EXTRACT,
# USES TEXT_FILE_CREATOR TO CREATE TEXT FILES FOR OCR STRINGS,
# MOVES COMPLETED IMAGES AND RESPECTIVE TEXT FILES TO PROPER FOLDERS
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
                print('this is the text name: {}'.format(text_name))
                image_title = "document" + str(count) + "image"
                image_file_dest = os.path.join(Dest_path, image_title)
                write_metadata_file(image_title)
                text = ocr_extract(filename)
                text_file_creator(text, text_name, Text_path)
                print("renaming {} to {}".format(filename, image_file_dest))
                os.rename(filename, image_file_dest)
            else:
                print("{} is not an image file".format(filename))

# VISITING THE HOMEPAGE RUNS SCRIPT ON LOADING ZONE
@app.route('/')
def display_homepage():
    run_image(Loading_zone)
    return render_template('home.html', text_file_names=get_img_filenames())

# TO FIX:
# when there is nothing following the backslash, this still runs and shouldn't (replaces <file_name> with favicon.ico)
@app.route('/<file_name>')
def display_images(file_name):
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
