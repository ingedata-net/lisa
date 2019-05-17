import os

"""
Currently not implement in Python.
While there's a rosbag reader in python, it's related to all the ROS framework
which might be overkill to install only for converting ros file.

Therefore and temporarly, we use a nodejs reader to simplify the installation
workflow
"""
def rosbag_to_pcd(filename, output_dir):
  convert = 'node src/bag_reader.js %s %s' %  ( filename, output_dir )

  os.system(convert)


if __name__ == "__main__":
    rosbag_to_pcd("sample/renault/renault.bag", "sample/pcd")