"""
To install cairoSVG please follow these instructions : https://cairosvg.org/documentation/#installation
"""
import cairosvg
import os
from glob import glob


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


if __name__ == "__main__":
    paths = get_paths_files_with_extension_from_folder("../Images", extension='svg')
    for path in paths:
        svg_to_png(path)
