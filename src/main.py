import sys

from lisa.image_converter import ImageConverter

if __name__ == "__main__":
  converter = ImageConverter("sample/street.jpg")
  converter.convert("output/street.jpg")