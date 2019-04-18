import xml.etree.ElementTree as ET

import os
import glob
from os import listdir
from os.path import isfile, join, isdir
import re

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

class PointCloud:
  def __init__(self):
    self.point_cloud_proto = None
    pass

  def attach_lidar_data(self, frame_index, converter):
    pass

  def attach_image(self, frame_index, image):
    pass

  def save(self, path):
    pass
