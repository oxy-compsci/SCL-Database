try:
    import Image
except ImportError:
    from PIL import Image
import os
import re
from os import listdir
from os.path import isfile, join

import pytesseract
from flask import Flask, render_template, send_from_directory

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

# ADDS A SET OF METADATA CATEGORIES FOR A FILENAME
def write_metadata_file(file_name):
    file = open('metadata.txt', 'a')
    file.write('\n\nFile Name: [{}]'
               '\nBox Number: []'
               '\nDate Added (mm/dd/yyyy): []'
               '\nName of Uploader (Last, First): []'
               '\nComments/Notes about File: []'
               .format(str(file_name)))
    file.close()

# RETURNS FILE COUNT LOCATED IN FILECOUNT.TXT
def check_file_number():
    string = open('filecount.txt', 'r')
    number = string.read()
    return number

# ADDS ONE TO FILE COUNT IN FILECOUNT.TXT
def count_plus_one():
    current_num = check_file_number()
    current_num = int(current_num)
    next_num = current_num + 1
    update = open('filecount.txt', 'w')
    update.write(str(next_num))

# RETURNS TRUE IF FILE NAME ALREADY EXISTS IN METADATA, FALSE IF NOT.
def metacheck(filenum):
    metadata = open('metadata.txt', 'r')
    metastring = metadata.read()
    filenum = str(filenum)
    find_filename = metastring.find('document' + filenum + 'image')
    if find_filename is not -1:
        return True
    else:
        return False

# FINDS METADATA FOR FILE NAME, RETURNS NESTED LIST OF CATEGORY INPUTS
def pull_metadata(filenum):
    lines = []
    if metacheck(filenum) is True:
        metadata = open('metadata.txt', 'r')
        metastring = metadata.read()
        filenum = str(filenum)
        find_filename = metastring.find('document' + filenum + 'image')
        current_location = find_filename - 12
        string = ''
        record = False
        category_count = 0
        for index, char in enumerate(metastring[current_location:]):
            if category_count < 5:
                if char is ']':
                    record = False
                    lines.append(string)
                    string = ''
                    category_count += 1
                if record is True:
                    string = string + char
                if char is '[':
                    record = True
    return lines

# ZIPS METADATA CATEGORIES AND RESPECTIVE METADATA INTO NESTED LISTS
def zip_names(file_number):
    categories = ['File Name:',
                  'Box Number:',
                  'Date Added (mm/dd/yyyy):',
                  'Name of Uploader (Last, First):',
                  'Notes/Comments:']
    entries = pull_metadata(file_number)
    info_list = zip(categories, entries)
    for i in info_list:
        print(i)
    return info_list

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
    if file_check(path):
        for filename in os.listdir(path):
            if filename.endswith(".jpg" or ".jpeg" or ".png" or ".gif" or ".tif"):
                print("{} is an image file".format(filename))
                filename = os.path.join(path, filename)
                count = check_file_number()
                text_name = "document" + str(count) + "text"
                image_title = "document" + str(count) + "image"
                image_file_dest = os.path.join(Dest_path, image_title)
                write_metadata_file(image_title)
                text = ocr_extract(filename)
                text_file_creator(text, text_name, Text_path)
                os.rename(filename, image_file_dest)
                count_plus_one()
            else:
                print("{} is not an image file".format(filename))

# VISITING THE HOMEPAGE RUNS ALL OF THE IMAGE-->OCR CODE ON FILES IN THE LOADING ZONE
@app.route('/')
def display_homepage():
    run_image(Loading_zone)
    return render_template('home.html', text_file_names=get_img_filenames())

# TO FIX:
# when there is nothing following the backslash, this still runs and shouldn't (replaces <file_name> with favicon.ico)
@app.route('/scl/<file_name>')
def display_images(file_name):
    file_number = re.search('document(.*)image', file_name)
    file_number = file_number.group(1)
    image_file_name = 'document' + str(file_number) + 'image.jpg'
    text_file_name = 'document' + str(file_number) + 'text'
    text_location = "completed_text_files/" + text_file_name
    with open(text_location, "r") as f:
        txt_content = f.read()
    metadata = pull_metadata(file_number)
    return render_template('image.html',
                           image_file_name=image_file_name,
                           text_file_name=text_file_name,
                           txt_content=txt_content,
                           metadata=metadata)

@app.route('/completed_files/<file_name>')
def image_file(file_name):
    return send_from_directory('completed_files', file_name)

if __name__ == "__main__":
    app.run(debug=True)
