from pyquaternion import Quaternion

def quaternion_from_matrix(x):
  q = Quaternion(matrix=x)
  return (q.w, q.x, q.y, q.z)

class Egopose:
  def __init__(self, position=(0,0,0),quaternion=(1,0,0,0)):
    self.position = position
    self.quaternion = quaternion