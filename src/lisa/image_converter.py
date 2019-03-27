from wand.image import Image

class ImageConverter:
  """
    # ImageConverter

    Import images and convert in a format which remove the exif data; blur
    faces if found using Haar Cascade
  """
  def __init__(self, image_path):
    self.image_path = image_path

  def convert(self, output):
    with Image(filename=self.image_path) as img:
      img.compression_quality = 99
      img.save(filename=output)


