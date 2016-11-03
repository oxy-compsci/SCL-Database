try:
    import Image
except ImportError:
    from PIL import Image
import imghdr
import re
from os import listdir, rename
from os.path import isfile, join

import pytesseract
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
    new_file = open(join(path, filename), "w")
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
def metacheck(filename):
    metadata = open('metadata.txt', 'r')
    metastring = metadata.read()
    find_filename = metastring.find(filename)
    return find_filename is not -1

# FINDS METADATA FOR FILE NUMBER, RETURNS NESTED LIST OF CATEGORY INPUTS
def pull_metadata(filename):
    lines = []
    if metacheck(filename) is True:
        metadata = open('metadata.txt', 'r')
        metastring = metadata.read()
        find_filename = metastring.find(filename)
        current_location = find_filename - 12
        string = ''
        record = False
        category_count = 0
        for char in metastring[current_location:]:
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

def get_all_metadata():
    lines = []
    all_lines = []
    file = open('filecount.txt', 'r')
    count = int(file.read())
    counter = 0
    index = 0
    for x in range(count):
        filename = 'document' + str(counter) + 'image'
        counter += 1
        if metacheck(filename) is True:
            metadata = open('metadata.txt', 'r')
            metastring = metadata.read()
            find_filename = metastring.find(filename)
            current_location = find_filename - 12
            string = ''
            record = False
            category_count = 0
            for char in metastring[current_location:]:
                if category_count < 5:
                    if char is ']':
                        record = False
                        lines.append(string)
                        string = ''
                        category_count += 1
                        if category_count == 5:
                            all_lines.append(lines)
                            lines = []
                            category_count = 0
                    if record is True:
                        string = string + char
                    if char is '[':
                        record = True
        return all_lines

def search_word(term):
    all_lines = get_all_metadata()
    matching = [x for x in all_lines if term in x]
    filenames = [x[0] for x in matching]
    return filenames

# ZIPS METADATA CATEGORIES AND RESPECTIVE METADATA INTO NESTED LISTS
def zip_names(filename):
    categories = ['File Name:',
                  'Box Number:',
                  'Date Added (mm/dd/yyyy):',
                  'Name of Uploader (Last, First):',
                  'Notes/Comments:']
    entries = pull_metadata(filename)
    info_list = zip(categories, entries)
    result = []
    for each in info_list:
        result.append(each)
    return result

# RETURNS LIST OF FILE NAMES IN COMPLETED FILES FOLDER
def get_img_filenames():
    file_names = []
    dirs = listdir(Dest_path)
    for file in dirs:
        if file.startswith('document'):
            file_names.append(file)
    return file_names

# RETURNS LIST OF FILE NAMES IN COMPLETED TEXT FILES FOLDER
def get_txt_filenames():
    text_file_names = []
    dirs = listdir(Text_path)
    for file in dirs:
        if file.startswith('document'):
            text_file_names.append(file)
    return text_file_names


# RUNS IMAGE FILES LOCATED IN LOADING_ZONE THROUGH OCR EXTRACT,
# USES TEXT_FILE_CREATOR TO CREATE TEXT FILES FOR OCR STRINGS,
# MOVES COMPLETED IMAGES AND RESPECTIVE TEXT FILES TO PROPER FOLDERS
def run_image():
    file_pairs = []
    if file_check(Loading_zone):
        for filename in listdir(Loading_zone):
            filename_path = join(Loading_zone, filename)
            image_type = imghdr.what(filename_path)
            if image_type:
            # if filename.endswith(".jpg" or ".jpeg" or ".png" or ".gif" or ".tif"):
                print("{} is a {} file".format(filename, image_type))
                filename = join(Loading_zone, filename)
                count = check_file_number()
                extension = filename.split(".",1)
                extension = "." + extension[1]
                text_name = "document" + str(count) + "text"
                image_title = "document" + str(count) + "image" + extension
                image_file_dest = join(Dest_path, image_title)
                write_metadata_file(image_title)
                text = ocr_extract(filename)
                text_file_creator(text, text_name, Text_path)
                rename(filename, image_file_dest)
                count_plus_one()
            else:
                print("{} is not an image file".format(filename))

run_image()

def search_text(term):
    filelist = []
    filenums = []
    for filename in listdir(Text_path):
        filepath = join(Text_path, filename)
        text = open(filepath, 'r')
        ocr_text = text.read()
        if term is not None:
            if term in ocr_text:
                filelist.append(filename)
    for filename in filelist:
        file_number = re.search('document(.*)text', filename)
        file_number = file_number.group(1)
        filenums.append(file_number)
    return filenums

def get_image_names_from_num(filenumbers):
    matches = []
    for filename in listdir(Dest_path):
        for each in filenumbers:
            if each in filename:
                matches.append(filename)
    return matches

'''
class Metadata:
    data_count = 0
    instance_list = []
    metadata = open('metadata.txt', 'r')
    metastring = metadata.read()

    def __init__(self, filename, boxnumber,
                 dateadded, uploader, comments):
        self.filename = filename
        self.boxnumber = boxnumber
        self.dateadded = dateadded
        self.uploader = uploader
        self.comments = comments
        Metadata.data_count += 1
        self.instance_list.append(self)



def read_metadata():
    metastring = Metadata.metastring
    category_count = 0
    record = False
    string = ''
    lines = []
    start_index = metastring.find('File Name:')
    for index, character in enumerate(metastring[start_index:-1]):
        if category_count < 5:
            if character is ']':
                record = False
                lines.append(string)
                print(lines)
                string = ''
                category_count += 1
            if record is True:
                string = string + character
            if character is '[':
                record = True
        if category_count >= 5:
            category_count = 0
            string = ''
            name = lines[0]
            print(lines[0])
            name = Metadata('boo', lines[1], lines[2], lines[3], lines[4])
            lines = []

read_metadata()
'''

# VISITING THE HOMEPAGE RUNS ALL OF THE IMAGE-->OCR CODE ON FILES IN THE LOADING ZONE
@app.route('/')
def display_homepage():
    search = request.args.get('search')
    meta_results = search_word(search)
    ocr_result_nums = search_text(search)
    ocr_results = get_image_names_from_num(ocr_result_nums)
    meta_set = set(meta_results)
    print("Combining search matches from metadata and OCR text files:")
    print("meta_set: {}".format(meta_set))
    ocr_set = set(ocr_results)
    print("ocr_set: {}".format(ocr_set))
    subtract_duplicates = ocr_set - meta_set
    print("All filenames here should be distinct from any in meta_set: {}".format(subtract_duplicates))
    results_no_duplicates = meta_results + list(subtract_duplicates)
    print("This is the final result with no duplicates: {}".format(results_no_duplicates))
    return render_template('home.html', text_file_names=get_img_filenames(),
                           results=results_no_duplicates)


@app.route('/scl/<file_name>')
def display_images(file_name):
    file_number = re.search('document(.*)image', file_name)
    file_number = file_number.group(1)
    image_file_name = 'document' + str(file_number) + 'image.jpg'
    text_file_name = 'document' + str(file_number) + 'text'
    text_location = "completed_text_files/" + text_file_name
    with open(text_location, "r") as f:
        txt_content = f.read()
    metadata = zip_names(image_file_name)
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
