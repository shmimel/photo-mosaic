"""
This class is made for simple image processing, mainly recoloring and resizing
"""
from PIL import Image, ImageOps
import os


class ImageTools:
    def __init__(self, file_path):
        """
        Given a file path (must be an openable image), opens and
        assigns properties of the image to variables
        """
        try:
            image_file = Image.open(file_path).convert("RGB")
        except IOError as e:
            print(e)
            return
        except Exception:
            print("Unexpected error reading file", file_path)
            return

        self.image_file = image_file

        width, height = image_file.size
        self.width = width
        self.height = height

        path_without_extension, extension = os.path.splitext(file_path)
        self.input_filename = os.path.basename(path_without_extension)

    def center_crop(self, image):
        """
        Given an image, crops a square in the center, with the shorter side
        of the image becoming the new dimensions for the cropped image
        """
        if self.width > self.height:
            crop = self.height
        else:
            crop = self.width

        # If the image is an odd number of pixels, the crop will round down
        if crop % 2 != 0:
            crop += 1

        left = (self.width - crop)/2
        top = (self.height - crop)/2
        right = (self.width + crop)/2
        bottom = (self.height + crop)/2
        image = image.crop((left, top, right, bottom))

        return image

    def make_grid(self, image):
        """
        Given an image in png form, returns an array of the values of the
        pixels in the image, ranging from 0 to 255
        """
        width, height = image.size
        data = list(image.getdata())
        grid = []
        for r in range(height):
            row_start = r * width
            row = data[row_start:row_start + width]

            grid.append(row)
        return grid

    def write_grid(self, file_name, pixel_grid):
        """
        Given a file output name and an array, saves a png image file with
        pixels corresponding to the numbers in the grid, ranging from 0 to 255
        """
        output_file = open(file_name, 'w')

        for row in pixel_grid:
            output_file.write(str(row[0]))
            for column in range(1, len(row)):
                output_file.write(', ' + str(row[column]).rjust(3))
            output_file.write('\n')

        output_file.close()

    def convert_target(self, thumb_size, greyscale=False):
        """
        Given an image, saves a cropped, greyscale png of the image
        """
        image = self.center_crop(self.image_file)
        wi, hi = image.size
        rounded = wi - (wi % thumb_size)
        image.thumbnail((rounded, rounded))
        
        if greyscale:
            image = ImageOps.grayscale(image)

        image.save('images/final/target.png')

    def convert_thumb(self, thumb_size, greyscale=False, csv = False):
        """
        Given an image and size to be cropped to, saves a cropped, greyscale
        csv of the image
        """
        image = self.center_crop(self.image_file)
        image.thumbnail((thumb_size, thumb_size))
        if greyscale:
            image = ImageOps.grayscale(image)

        if csv:
            thumb_grid = self.make_grid(image)
            file_name = os.path.join('csv', self.input_filename + '.csv')
            self.write_grid(file_name, thumb_grid)
        else:
            file_name = os.path.join('png', self.input_filename + '.png')
            image.save(file_name)
        

