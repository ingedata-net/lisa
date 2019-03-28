from wand.image import Image

def convert_image(src, dest, quality = 80):
  '''
    Convert image from, shrink it to a specific quality and
    remove the exif data.
  '''
  with Image(filename=src) as img:
    img.strip()
    img.compression_quality = quality
    img.save(filename=dest)
