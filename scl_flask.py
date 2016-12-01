from flask import Flask, render_template, send_from_directory, request
from database import read_documents, search_term_in_metadata_and_text

app = Flask(__name__)

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
            if len(instance.text) >= 150:
                description = instance.text[0:150]
            else:
                description = instance.text
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
            return render_template('image.html',
                                   image_file=instance.image_file,
                                   text_file=instance.text_file,
                                   text_content=instance.text,
                                   metadata=instance.metadata)

@app.route('/completed_files/<file_name>')
def image_file(file_name):
    return send_from_directory('completed_files', file_name)

if __name__ == "__main__":
    app.run(debug=True)

