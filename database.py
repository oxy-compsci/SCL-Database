try:
    import Image
except ImportError:
    from PIL import Image
import imghdr
import os
import re
from copy import copy
import random
import pytesseract

# FOLDER PATHS
LOADING_ZONE = "loading_zone"
TEXT_PATH = "completed_text_files"
DEST_PATH = "completed_files"

# SPECIAL FILES
COUNT_FILE = "filecount.txt"
METADATA_FILE = "metadata.txt"

# METADATA FILES
METADATA_FILE_NAME_FIELD = "File Name"
METADATA_FIELDS = [
    METADATA_FILE_NAME_FIELD,
    "Box Number",
    "Date Added (mm/dd/yyyy)",
    "Name of Uploader (Last, First)",
    "Comments/Notes about File",
]

# DOCUMENT FUNCTIONS

class Document:
    def __init__(self, image_file):
        self.image_file = image_file
        self.image_path = os.path.join(DEST_PATH, image_file)
        self.filenumber = re.search("document(.*)image", self.image_path).group(1)
        self.text_path = os.path.join(TEXT_PATH, self.text_file_name())
        if self.has_text_file():
            with open(self.text_path) as file:
                self.text = file.read()
        else:
            self.text = ""
        self.metadata = {}
        self.search_text_matches = []
        # if self.search_text_matches:
            # self.search_text_choice = len(self.search_text_matches) // 2
            # self.search_text_left = self.search_text_choice - 100
            # self.search_text_right = self.search_text_choice + 100
        self.search_meta_matches = {}
    def text_file_name(self):
        return "document" + str(self.filenumber) + "text.txt"
    def has_image_file(self):
        return os.path.exists(self.image_path)
    def has_text_file(self):
        return os.path.exists(self.text_path)
    def has_files(self):
        return self.has_image_file() and self.has_text_file()
    def write_text_file(self):
        with open(self.text_path, "w") as file:
            file.write(self.text)
    def metadata_string(self):
        lines = []
        # add all defined fields first
        for field in METADATA_FIELDS:
            if field in self.metadata:
                lines.append(field + ": [" + self.metadata[field] + "]")
            else:
                lines.append(field + ": []")
        # then add the remainder alphabetically
        for field, value in sorted(self.metadata.items()):
            if field not in METADATA_FIELDS:
                lines.append(field + ": [" + value + "]")
        return "\n".join(lines)

def create_new_metadata(file):
    metadata = {}
    for field in METADATA_FIELDS:
        metadata[field] = ""
    metadata[METADATA_FILE_NAME_FIELD] = file
    return metadata

def metadata_to_dict(section):
    metadata = {}
    # FIXME assumes each line is a field
    for line in section.splitlines():
        line = line.strip()
        if line == "":
            continue
        field, value = line.split(":", maxsplit=1)
        # remove trailing spaces and the [brackets]
        value = value.strip()[1:-1]
        metadata[field] = value
    return metadata

def read_documents():
    documents = []
    with open(METADATA_FILE) as file:
        metadata_text = file.read()
    for section in metadata_text.split("\n\n"):
        if section.strip() == "":
            continue
        metadata = metadata_to_dict(section)
        # create the Document using the File Name
        doc = Document(metadata[METADATA_FILE_NAME_FIELD])
        doc.metadata = metadata
        # only add it to the list of documents if those files actually exist
        if doc.has_files():
            documents.append(doc)
    return documents

def search_term_in_metadata_and_text(term):
    matches = set()
    if term:
        term = term.lower()
        for instance in read_documents():
            index = 0
            for key in instance.metadata:
                if term in instance.metadata[key].lower():
                    instance.search_meta_matches[key] = instance.metadata[key]
                    if instance.image_file not in matches:
                        matches.add(instance)
            if term in instance.text.lower():
                while index < len(instance.text):
                    index = instance.text.lower().find(term, index)
                    if index == -1:
                        break
                    instance.search_text_matches.append(index)
                    index += len(term)
                if instance.image_file not in matches:
                    matches.add(instance)
    return matches

# OCR FUNCTIONS

def read_folder_metadata(path):
    for file in os.listdir(path):
        if file.endswith('.txt'):
            with open(os.path.join(path, file)) as file:
                return metadata_to_dict(file.read())

def request_new_file_number():
    with open(COUNT_FILE) as file:
        file_number = int(file.read())
    with open(COUNT_FILE, "w") as file:
        file.write(str(file_number + 1))
    return file_number

def ocr_extract(path):
    return pytesseract.image_to_string(Image.open(path))

def run_image(file, metadata):
    # create the new Document
    doc = Document(file)
    doc.metadata = metadata
    doc.metadata[METADATA_FILE_NAME_FIELD] = doc.image_file
    # run OCR, update the doc, and write the file
    text = ocr_extract(doc.image_path)
    doc.text = text
    doc.write_text_file()
    # update master metadata file
    with open(METADATA_FILE, "a") as file:
        file.write(doc.metadata_string())
        file.write("\n")
        file.write("\n")
    return doc

def run_folder_images(path):
    new_documents = []
    # FIXME this assumes there is a metadata file in the folder
    metadata = read_folder_metadata(path)
    for file in os.listdir(path):
        old_file_path = os.path.join(path, file)
        image_type = imghdr.what(old_file_path)
        if image_type:
            print('{} is a {} file'.format(file, image_type))
            # build the new file path
            file_ext = file.split(".")[1]
            count = request_new_file_number()
            new_file_name = 'document' + str(count) + 'image.' + file_ext
            new_file_path = os.path.join(DEST_PATH, new_file_name)
            # move the file first
            os.rename(old_file_path, new_file_path)
            # create a document and do OCR
            doc = run_image(new_file_name, copy(metadata))
            new_documents.append(doc)
        else:
            print("{} is not an image file".format(file))
    # FIXME delete the folder?
    return new_documents

def run_images():
    new_documents = []
    for folder in os.listdir(LOADING_ZONE):
        folder = os.path.join(LOADING_ZONE, folder)
        if os.path.isdir(folder):
            new_documents.extend(run_folder_images(folder))
    return new_documents

if __name__ == "__main__":
    run_images()
    #app.run(debug=True)
