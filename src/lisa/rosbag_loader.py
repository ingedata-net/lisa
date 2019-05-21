from os import listdir, system
from os.path import isfile, join
from tempfile import TemporaryDirectory

"""
Currently not implement in Python.
While there's a rosbag reader in python, it's related to all the ROS framework
which might be overkill/difficult to install just to convert ros file.

Therefore and temporarly, we use a nodejs reader to simplify the installation
workflow
"""
def rosbag_to_each_pcd(filename):
  convert = 'node src/bag_reader.js %s %s' %  ( filename, output_dir )
  os.system(convert)

  with TemporaryDirectory() as tmpdirname:
    tmpdirname

  tmpdirname
  for f in listdir(mypath) if isfile(join(mypath, f))
    yield(f)
