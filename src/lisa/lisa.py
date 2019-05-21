from tempfile import NamedTemporaryFile

import os
import tarfile

from .egopose import Egopose
from .image_converter import convert_image

from .proto import lisa_pb2

class Frame:
  def __init__(self, index):
    self.egopose = Egopose()
    self.pcd_file = None
    self.camera_files = {}
    self.index = index

  def __enter__(self):
    return self

  def __exit__(self, exception_type, exception_value, traceback):
    pass

  def add_image(self, camera_id, filepath):
    self.camera_files[camera_id] = filepath

  def save(self, tarfile):
    print(self.camera_files)
    # Save the camera files
    for name, file in self.camera_files.items():
      f = NamedTemporaryFile(delete=False)
      try:
        # Convert to jpg 70% quality
        w,h,data = convert_image(file, 70)
        f.write(data)
        f.close()

        arcname = "{}/{}.jpg".format(self.index, name)
        tarfile.add(f.name, arcname=arcname)
      finally:
        os.unlink(f.name)

    meta = lisa_pb2.Frame()
    self.egopose.apply(meta)
    print(meta)
    print(meta.SerializeToString())

    f = NamedTemporaryFile(delete=False)

    try:
      f.write(meta.SerializeToString())
      f.close()
      tarfile.add(f.name, arcname="%d/metadata.proto" % (self.index) )
      tarfile.add(self.pcd_file, arcname="%d/points.pcd" % (self.index) )
    finally:
      os.unlink(f.name)

class Lisa:
  def __init__(self):
    self.name = ""
    self.description = ""

    self.instructions = ""

    self.cameras = {}
    self.frames = []

    self.categories = {}


  """
    Get or create a new frame
    Return the frame if needed
  """
  def frame(self, index):
    if index < len(self.frames):
      return self.frames[index]
    else:
      l = index - len(self.frames)
      while(l >= 0):
        l -= 1
        self.frames.append(Frame(len(self.frames)))

      return self.frames[index]

  """
    Fetch a specific camera
  """
  def camera(self, name):
    cam = self[name]
    if cam == None :
      cam = self[name] = Camera()
    cam

  def add_category(self, index, label, instruction = ""):
    if (index>=0) and (index < 254) :
      self.categories[index] = (label,instruction)
    else:
      raise "Category must have index between [0 ... 254]"


  """
    Build the TAR file containing all the files
  """
  def save(self, file):
    tar = tarfile.open(file, "w")

    for f in self.frames:
      f.save(tar)

    meta = lisa_pb2.Lisa()
    meta.name = self.name
    meta.description = self.description
    meta.instructions = self.instructions
    meta.frame_count = len(self.frames)

    for k, (label, instruction) in self.categories.items():
      meta.categories[k].label = label
      meta.categories[k].instruction = instruction

    for key, v in self.cameras:
      cam = meta.cameras.add(v)

    f = NamedTemporaryFile(delete=False)

    try:
      f.write(meta.SerializeToString())
      f.close()
      tar.add(f.name, arcname = "metadata.proto")
    finally:
      os.unlink(f.name)

    tar.close()
    print("SAVED AS {}".format(file))