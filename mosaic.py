"""
Creates a photomosaic from a directory of photos, in attempt to
recreate a target photo
"""
import os
import math
import cv2 as cv
from sklearn.feature_selection import chi2
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
    Given two array (of equal dimension), returns the mean squared error between them
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

def subdivide_sqr_image(img, blocks):

    assert img.shape[0] == img.shape[1] #Image is indeed square

    subblock_size = int(img.shape[0]/blocks)

    split_img = np.array_split(img, blocks, axis=0)
    split_img = [np.array_split(block, blocks, axis=1) for block in split_img]
    return np.asarray(split_img).reshape((blocks**2, subblock_size, subblock_size, -1))

def mosaic(target, directory, thumb_size):
    """
    Given a target image (as PNG) and a starting directory of png files, recreates
    the target image from the files in the directory
    """

    target = Image.open(target).convert("RGB")
    target = np.array(target)

    thumbnails = []
    for file_name in os.listdir(directory):
        file_name = os.path.join(directory, file_name)
        thumbnail = Image.open(file_name).convert("RGB")
        thumbnail = np.array(thumbnail)
        thumbnails.append(thumbnail)


    num_blocks = int(target.shape[0]/thumb_size)

    split_target = subdivide_sqr_image(target, num_blocks)

    final_thumbs = []
    
    for i in range(split_target.shape[0]):
            target_chunk = split_target[i]
            target_hist = cv.calcHist([target_chunk], [0, 1, 2], None, [8, 8, 8],
		        [0, 256, 0, 256, 0, 256])
            target_hist = cv.normalize(target_hist, target_hist).flatten()
            min_dist = math.inf
            for thumbnail in thumbnails:
                thumb_hist = cv.calcHist([thumbnail], [0, 1, 2], None, [8, 8, 8],
		            [0, 256, 0, 256, 0, 256])
                thumb_hist = cv.normalize(thumb_hist, thumb_hist).flatten()
                chi2distance = cv.compareHist(target_hist,thumb_hist,cv.HISTCMP_CHISQR)
                if chi2distance < min_dist:
                    min_dist = chi2distance
                    final_thumb = thumbnail
            final_thumbs.append(final_thumb)

    final_array = np.asarray(final_thumbs)
    
    final_array = np.reshape(final_array, (num_blocks, num_blocks, thumb_size, thumb_size, -1))
    final_array = np.transpose(final_array,(0,2,1,3,4))
    final_array = np.reshape(final_array, (num_blocks*thumb_size, num_blocks*thumb_size, -1))

    final_image = Image.fromarray(final_array)
    final_image.save("/Users/erb/Desktop/CS/photo-mosaic/images/final/Mosiac.png")


def main():
    size = 20
    # Note, after running once, comment out the "thumbnail" line, as
    # csv generation takes some time
    #thumbnail_gen('images/original', size)
    target_gen('images/original/helens.png', size)
    mosaic('images/final/target.png', 'png', 20)


if __name__ == "__main__":
    main()
