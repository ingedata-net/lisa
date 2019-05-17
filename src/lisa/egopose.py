from pyquaternion import Quaternion
from .geo_converter import geo_convert

def quaternion_from_matrix(x):
  q = Quaternion(matrix=x)
  return (q.w, q.x, q.y, q.z)

class Egopose:
  def __init__(self, position=(0, 0, 0), quaternion=(0, 0, 0, 1), timestamp=0 ):
    self.position = position
    self.quaternion = quaternion
    self.timestamp = timestamp

  def set_position(self, x, y, z, in_proj=None, out_proj='epsg:6510'):
    if in_proj != None:
      x,y,z = geo_convert(in_proj, x,y,z, out_proj)
    self.position = (x, y, z)

  """
    Apply to a lisa's frame object
  """
  def apply(self, frame):
    frame.timestamp = self.timestamp

    frame.x = self.position[0]
    frame.y = self.position[1]
    frame.z = self.position[2]

    frame.qx = self.quaternion[0]
    frame.qy = self.quaternion[1]
    frame.qz = self.quaternion[2]
    frame.qw = self.quaternion[3]

    return self
