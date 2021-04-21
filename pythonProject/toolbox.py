"""
To install cairoSVG please follow these instructions : https://cairosvg.org/documentation/#installation
"""
import cairosvg
import os
from glob import glob
import requests
import time

def svg_to_png(svg_path):
    """
    :param svg_path: Path to a svg file
    :return: Nothing
    """
    cairosvg.svg2png(url=svg_path, write_to=svg_path.replace(".svg", ".png"))


def get_paths_files_with_extension_from_folder(folder, extension='svg'):
    """
    :param extension: Extension of the files you are searching, default is svg
    :param folder: Folder in which searching files
    :return list of path to svg files without extension:
    """
    list_paths_to_files = [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.' + extension))]
    for i in range(len(list_paths_to_files)):
        list_paths_to_files[i] = list_paths_to_files[i].replace("\\", "/")
    return list_paths_to_files


def beautify_string(string):
    string_no_slash = string.replace("\\", "")
    string_remove_last_char = string_no_slash[:-1]
    string_remove_first_char = string_remove_last_char[1:]
    return string_remove_first_char


def get_new_captcha(path, /, **keywords):
    print(keywords)
    if 'text' in keywords:
        if 'color' in keywords:
            r = requests.get(
                'http://localhost:8080/captcha/{text}/{color}'.format(text=keywords['text'], color=keywords['color']))
        else:
            r = requests.get(
                'http://localhost:8080/captcha/{text}'.format(text=keywords['text']))

    if r.status_code == 200:
        byte_string = beautify_string(r.content.decode("utf8"))
        cairosvg.svg2png(bytestring=byte_string, write_to=path + ".png")
        return 0
    return 1




if __name__ == "__main__":
    start_time = time.time()
    get_new_captcha("./coucou", text="A38hCNp8", color="green")
    get_new_captcha("./coucou2", text="Ici8letr")
    print("--- %s seconds ---" % (time.time() - start_time))
