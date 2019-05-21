import xml.etree.ElementTree as ET

import glob
import re

from os.path import isfile

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