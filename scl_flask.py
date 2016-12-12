from flask import Flask, render_template, send_from_directory, request
from database import read_documents, search_term_in_metadata_and_text

app = Flask(__name__)

@app.route('/')
def display_homepage():
    search_term = request.args.get('search')
    filenames = []
    result_instances = search_term_in_metadata_and_text(search_term)
    for instance in read_documents():
        filenames.append(instance)
    return render_template('home.html', filenames=filenames, results=result_instances, search_term=search_term)

@app.route('/scl/<file_name>')
def display_images(file_name):
    for instance in read_documents():
        if instance.image_file == file_name:
            return render_template('image.html',
                                   image_file=instance.image_file,
                                   text_file=instance.text_file,
                                   text_content=instance.text,
                                   metadata=instance.metadata,
                                   metadata_list=instance.get_metadata_list(),
                                   )

@app.route('/completed_files/<file_name>')
def image_file(file_name):
    return send_from_directory('completed_files', file_name)

if __name__ == "__main__":
    app.run(debug=True)
