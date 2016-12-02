import shutil
import webbrowser
from os import makedirs
from os.path import dirname, join, exists, realpath

import requests
import flickrapi

USERNAME = "justinnhli12"

SPECIAL_ALBUMS = set(['Auto Upload', 'master'])

LOADING_ZONE = "loading_zone"

def indent_print(message, indent):
    print(4 * indent * " " + message)

def get_current_path():
    return dirname(realpath(__file__))

def get_user_id(user):
    flickr = authenticate_flickr()
    userid = flickr.people.findByUsername(username=user)
    return userid.find('user').get('nsid')

def get_original_photo_url(flickr, photo_id):
    photo = flickr.photos.getInfo(photo_id=photo_id).find("photo")
    url_template = "https://farm{farm}.staticflickr.com/{server}/{id}_{originalsecret}_o.{originalformat}"
    return url_template.format(**dict(photo.items()))

def get_photo_url(flickr, photo_id, size='medium'):
    # for sizes, see https://www.flickr.com/services/api/misc.urls.html
    if size == 'thumbnail':
        suffix = 't'
    elif size == 'small':
        suffix = 'm'
    elif size == 'medium':
        suffix = 'z'
    elif size == 'large':
        suffix = 'b'
    photo = flickr.photos.getInfo(photo_id=photo_id).find("photo")
    url_template = "https://farm{farm}.staticflickr.com/{server}/{id}_{secret}_{size_suffix}.{originalformat}"
    return url_template.format(size_suffix=suffix, **dict(photo.items()))

def read_flickr_keys():
    if not exists("api_keys"):
        print("ERROR: Unable to read Flickr API keys")
        print("Please contact Justin Li <justinnhli@oxy.edu> for support")
        exit(1)
    with open("api_keys") as fd:
        key, secret = fd.read().splitlines()
    return key.strip(), secret.strip()

def download_file(url, save_path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

def authenticate_flickr():
    # Read the API keys
    api_key, api_secret = read_flickr_keys()
    # Create a (potentially temporary) FlickrAPI instance
    flickr = flickrapi.FlickrAPI(api_key, api_secret, username=USERNAME)
    # Only do this if we don't have a valid token already
    if not flickr.token_valid(perms="delete"):
        # Get a request token out-of-band (OOB)
        flickr.get_request_token(oauth_callback="oob")
        # Open a browser at the authentication URL. Do this however
        # you want, as long as the user visits that URL.
        authorize_url = flickr.auth_url(perms="delete")
        webbrowser.open_new_tab(authorize_url)
        # Get the verifier code from the user. Do this however you
        # want, as long as the user gives the application the code.
        verifier = str(input("Verifier code: "))
        # Trade the request token for an access token
        flickr.get_access_token(verifier)
    return flickr

def download_flickr_images():
    indent_print("Downloading photos from Flickr...", indent=0)
    # FIXME make sure directory is correct
    flickr = authenticate_flickr()
    user_id = get_user_id(USERNAME)
    albums = flickr.photosets.getList(user_id=user_id).find("photosets")
    for album in albums:
        album_title = album.find("title").text
        if album_title in SPECIAL_ALBUMS:
            continue
        directory = join(get_current_path(), LOADING_ZONE, album_title)
        if not exists(directory):
            makedirs(directory)
        indent_print("Downloading album {}..".format(album_title), indent=1)
        for photo in flickr.walk_set(album.get("id")):
            url = get_original_photo_url(flickr, photo.get('id'))
            filename = url.split("/")[-1]
            download_file(url, join(directory, filename))
            indent_print("Downloaded {}".format(filename), indent=2)
            flickr.photos.delete(photo_id=photo.get('id'))
        flickr.photosets.delete(photoset_id=album.get('id'))

def upload_image(path):
    path = realpath(path)
    flickr = authenticate_flickr()
    user_id = get_user_id(USERNAME)
    albums = flickr.photosets.getList(user_id=user_id).find("photosets")
    master_album = None
    for album in albums:
        album_title = album.find("title").text
        if album_title != "master":
            continue
        master_album = album
        break
    photo_id = flickr.upload(filename=path).find("photoid").text
    if master_album is None:
        rsp = flickr.photosets.create(
                title="master",
                primary_photo_id=photo_id,
        )
        master_album = rsp.find('photoset')
    else:
        flickr.photosets.addPhoto(
                photoset_id=master_album.get('id'),
                photo_id=photo_id,
        )
    url = flickr.photos.getInfo(photo_id=photo_id).find('photo').find('urls').find('url').text
    thumbnail_link = get_photo_url(flickr, photo_id, size='thumbnail')
    preview_link = get_photo_url(flickr, photo_id, size='medium')
    return {
            'Flickr URL':url,
            'Thumbnail Link':thumbnail_link,
            'Preview Link':preview_link,
    }

def upload_images(paths):
    urls = []
    for path in paths:
        urls.append(upload_image(path))
    return urls

def main():
    flickr = authenticate_flickr()
    user_id = get_user_id(USERNAME)
    albums = flickr.photosets.getList(user_id=user_id).find("photosets")
    for album in albums:
        album_title = album.find("title").text
        if album_title in SPECIAL_ALBUMS:
            continue
        print(album_title)
        for photo in flickr.walk_set(album.get("id")):
            print("    " + get_original_photo_url(flickr, photo.get("id")))

if __name__ == "__main__":
    main()
