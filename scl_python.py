import os
import re

try:
    import Image
except ImportError:
    from PIL import Image
from flask import Flask, render_template, send_from_directory
import pytesseract

app = Flask(__name__)


# FOLDER LOCATIONS


Loading_zone = "loading_zone"
Text_path = "completed_text_files"
Dest_path = "completed_files"


# CHECKS FOR FILES IN FOLDER


def file_check(path):
    files_no_folders = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if len(files_no_folders) <= 1:
        return False
    else:
        return True


# IMAGE TO OCR STRING


def ocr_extract(file):
    ocr_text = pytesseract.image_to_string(Image.open(file))
    return ocr_text


# STRING TO TEXT FILE CREATOR


def text_file_creator(string, filename, path):
    new_file = open(os.path.join(path, filename), "w")
    new_file.write(string)


# IMAGE CONVERTER USING ABOVE FUNCTIONS

def run_image(path):
    count = -1
    if file_check(path):
        for filename in os.listdir(path):
            print("checking if {} is an image file".format(filename))
            if filename.endswith(".jpg" or ".jpeg" or ".png" or ".gif" or ".tif"):
                filename = os.path.join(path, filename)
                count += 1
                text_name = "document" + str(count) + "text"
                image_rename = os.path.join(Dest_path, "document" + str(count) + "image")
                text = ocr_extract(filename)
                text_file_creator(text, text_name, Text_path)
                print("renaming {} to {}".format(filename, image_rename))
                os.rename(filename, image_rename)


run_image(Loading_zone)


# DESCRIPTION NEEDED


def get_img_filenames():
    file_names = []
    path = "completed_files"
    dirs = os.listdir(path)
    for file in dirs:
        if file.startswith('document'):
            file_names.append(file)
    return file_names


# DESCRIPTION NEEDED


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
    file_number = re.search('document(.*)image', file_name)
    file_number = file_number.group(1)
    image_file_name = 'document' + str(file_number) + 'image.jpg'
    text_file_name = 'document' + str(file_number) + 'text'
    return render_template('image.html', image_file_name=image_file_name, text_file_name=text_file_name)


@app.route('/completed_files/<file_name>')
def image_file(file_name):
    return send_from_directory('completed_files', file_name)


@app.route('/completed_text_files/<file_name>')
def text_file(file_name):
    return send_from_directory('completed_text_files', file_name)


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
#@app.route('/completed_files/<file>')
#def uploaded_file(file):
#    return render_template('base.html', file=file)

#@app.route('/completed_files/<file>')
#def send_file(file):
#    return send_from_directory('completed_files', file)


'''


if __name__ == "__main__":
    app.run(debug=True)
