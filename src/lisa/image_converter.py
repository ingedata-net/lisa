from wand.image import Image

def convert_image(src, quality = 80):
  '''
    Convert image to jpeg, shrink it to a specific quality and
    remove the exif data.

    @returns a blob
  '''
  with Image(filename=src) as img:
    img.strip()
    img.compression_quality = quality
    with img.convert('jpg') as converted:
      print("CONVERTED?!")
      return (converted.width, converted.height, converted.make_blob())
