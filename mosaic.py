"""
Creates a photomosaic from a directory of photos, in attempt to
recreate a target photo
"""
import os
import math
from image_tools import ImageTools
import numpy as np
from PIL import Image
import itertools


def thumbnail_gen(directory, size):
    """
    Given a directory and size, saves a csv for each image, each with
    specified dimensions
    """
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        it = ImageTools(f)
        it.convert_thumb(size)


def target_gen(file_name, size):
    """
    Given an image of choice and size, saves a square, greyscale image and csv
    cropped to a multiple of the inputted dimension
    """
    it = ImageTools(file_name)
    it.convert_target(size)


def csv2array(file_name):
    """
    Converts a csv to an array
    """
    with open(file_name) as f:
        array = np.loadtxt(f, delimiter=",")
    return array


def mse(A, B):
    """
    Given two arrays, returns the mean squared error between them
    (the lower the better!)
    """
    mse = ((A - B)**2).mean(axis=None)
    return mse


def array2pic(array, file_name):
    """
    Given an array and file save location, saves the array as a png image
    """
    file_name = file_name + '.png'
    size = len(array[0]), len(array)
    image = Image.new("L", size)

    print("Writing", size[0], 'x', size[1], "image to file", file_name)

    data = list(itertools.chain.from_iterable(array))
    image.putdata(data)

    try:
        image.save(file_name)
    except IOError as e:
        print(e)
    except Exception:
        print("Unexpected error writing file", file_name)


def mosaic(target, directory):
    """
    Given a target image and a starting directory of csv files, recreates
    the target image from the files in the directory
    """
    thumb_size = 20
    target_csv = csv2array(target)

    thumbnails = []
    for file_name in os.listdir(directory):
        f = os.path.join(directory, file_name)
        thumbnail = csv2array(f)
        thumbnails.append(thumbnail)

    length = int(len(target_csv)/thumb_size)
    final_thumbs = []
    final_array = np.zeros((length*thumb_size, length*thumb_size))
    for i in range(length):
        for j in range(length):
            target_chunk = target_csv[i*thumb_size:(i+1)*thumb_size,
                                      j*thumb_size:(j+1)*thumb_size]
            min_mse = math.inf
            for thumbnail in thumbnails:
                thumb_mse = mse(thumbnail, target_chunk)
                if thumb_mse < min_mse:
                    min_mse = thumb_mse
                    final_thumb = thumbnail
            final_thumbs.append(final_thumb)
            final_array[i*thumb_size:(i+1)*thumb_size,
                        j*thumb_size:(j+1)*thumb_size] = final_thumb

    array2pic(final_array, 'images/final/mosaic')


def main():
    size = 20
    # Note, after running once, comment out the "thumbnail" line, as
    # csv generation takes some time
    # thumbnail_gen('images/original', size)
    target_gen('images/original/helens.png', size)
    mosaic('images/final/target.csv', 'csv')


if __name__ == "__main__":
    main()
