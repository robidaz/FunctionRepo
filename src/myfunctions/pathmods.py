from os.path import *
from shutil import move
import time

def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')
def newest_file(path, extension=None):
    download_wait(path)
    files = os.listdir(path)
    if extension:
        paths = [os.path.join(path, basename)
                 for basename in files if splitext(basename)[1] == extension]
    else:
        paths = [os.path.join(path, basename)
                 for basename in files]
    if not paths:
        raise FileNotFoundError
    return max(paths, key=os.path.getctime)


def download_wait(path_to_downloads):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < 20:
        time.sleep(0.5)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 0.5
    return seconds
    
def move_newest_downloaded_file(
        self, filename, destination_dir=None, check_name=False):
    name, extension = splitext(filename)
    download_wait(get_download_path())
    new_file = newest_file(get_download_path(), extension)
    new_file_base, extension = splitext(basename(new_file))
    destination = join(destination_dir, filename)
    os.makedirs(destination_dir, exist_ok=True)
    if check_name is False:
        move(
            join(
                get_download_path(),
                new_file_base + extension), destination)
    else:
        move(
            join(
                get_download_path(),
                name + extension), destination)

    return destination