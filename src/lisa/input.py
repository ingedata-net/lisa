import xml.etree.ElementTree as ET

from pyproj import Proj, transform

import os
import glob
import re

from os import listdir
from os.path import isfile, join, isdir

from .proto.input_pb2 import Lisa, LidarDataPoint, LidarDataFrame, EgoPose

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

  def set_image(self, key, path, direction = [1,0,0,0]):
    image = self.pbframe.images[key]

    image.direction.x = direction[0]
    image.direction.y = direction[1]
    image.direction.z = direction[2]
    image.direction.w = direction[3]

    image.width, image.height, image.data = convert_image(path)

  def set_lidar_data(self, lidar_data):
    for idx, (x,y,z,i) in enumerate(lidar_data):
      self.pbframe.lidar.points.add(x=x, y=y, z=z, i=i)

  def set_position(self, coordinates, elevation = 0,
    refid=None, outid='epsg:6510'):

    if refid != None:
      inProj = Proj(init=refid)
      outProj = Proj(init='epsg:6510')
      x, y = transform(inProj,outProj, coordinates[0], coordinates[1])
    else:
      x, y = (coordinates[0], coordinates[1])

    self.pbframe.egopose.x = x
    self.pbframe.egopose.y = y
    self.pbframe.egopose.z = elevation #Todo: elevation

class PointCloud:
  def __init__(self):
    self.proto_lisa = Lisa()

  def add_category(self, id, label):
    kv_pair = self.proto_lisa.categories.add()
    kv_pair.id = id
    kv_pair.label = label
    return self

  def add_categories(self, dict):
    for key, value in dict.items():
      self.add_category(value, key)
    return self

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
