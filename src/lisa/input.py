import xml.etree.ElementTree as ET

import os
import glob
from os import listdir
from os.path import isfile, join, isdir
import re

from .proto.input_pb2 import Lisa, LidarDataPoint, LidarDataFrame, EgoPose, ImageData

from .image_converter import convert_image

def tree(file_path = "."):
  for file in glob.glob(file_path + "/**", recursive=True):
    if isfile(file):
      yield file

def with_xml(regexp):
  for file in tree():
    match = re.search(regexp, file)
    if match != None:
      xml = ET.parse(file)
      yield(xml, match)

"""
  Wrapper for pb Frame object
"""
class PointCloudFrame:
  def __init__(self, pbframe):
    self.pbframe = pbframe

  def __enter__(self):
    return self

  def __exit__(self, exception_type, exception_value, traceback):
    pass

  def set_image(self, key, path):
    pass

  def set_lidar(self, lidar_data):
    pass

  def set_coordinates(self, coordinates):
    pass

class PointCloud:
  def __init__(self):
    self.proto_lisa = Lisa()

  def frame(self, index):
    if index < len(self.proto_lisa.frames):
      return PointCloudFrame(self.proto_lisa.frames[index])
    else:
      l = index - len(self.proto_lisa.frames)
      while(l >= 0):
        l -= 1
        self.proto_lisa.frames.add()

      return PointCloudFrame(self.proto_lisa.frames[index])

  def attach_lidar_data(self, frame_index, converter):
    pass

  def attach_image(self, frame_index, image):
    pass

  def save(self, path):
    data = self.proto_lisa.SerializeToString()

    f = open(path, "wb")
    f.write(data)
    f.close()
