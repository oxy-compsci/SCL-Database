try:
    import Image
except ImportError:
    from PIL import Image
import imghdr
import os
import re
from os import listdir, rename
from os.path import join
import math

from flask import Flask, render_template, send_from_directory, request
from database import *

app = Flask(__name__)

# VISITING THE HOMEPAGE RUNS ALL OF THE IMAGE-->OCR CODE ON FILES IN THE LOADING ZONE
@app.route('/')
def display_homepage():
    search_term = request.args.get('search')
    filenames = []
    result_filenames = []
    description = ''
    result_instances = search_term_in_metadata_and_text(search_term)
    for instance in result_instances:
        metamatches = []
        for key in instance.search_meta_matches:
            metamatches.append(key)
        if not metamatches:
            metamatches.append('No metadata matches found.')
        text_match_indices_list = instance.search_text_matches
        if text_match_indices_list:
            index = len(text_match_indices_list) // 2
            description = get_text_preview(text_match_indices_list[index], instance.text_path)
        elif not text_match_indices_list:
            description = 'No text matches found.'
        result_filenames.append([instance.image_file, description, metamatches])
    for instance in read_documents():
        filenames.append(instance.image_file)
    return render_template('home.html', filenames=filenames, results=result_filenames)


@app.route('/scl/<file_name>')
def display_images(file_name):
    for instance in read_documents():
        if instance.image_file == file_name:
            image_file = instance.image_file
            text_file = instance.text_path
            text_content = instance.text
            metadata = instance.metadata
    return render_template('image.html',
                           image_file=image_file,
                           text_file=text_file,
                           text_content=text_content,
                           metadata=metadata)

@app.route('/completed_files/<file_name>')
def image_file(file_name):
    return send_from_directory('completed_files', file_name)

if __name__ == "__main__":
    run_images()
    app.run(debug=True)

