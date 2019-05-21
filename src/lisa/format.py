import tarfile

from .egopose import Egopose
import .proto.lisa_pb2

class Frame:
  def __init__(self, file, egopose=Egopose()):
    self.proto_frame = lisa_pb2.Frame()

    self.egopose = egopose
    self.index = 0
    self.file = file

class Lisa:
  def __init__(self):
    self.frames = []
    pass

  def add_frame(self, pcd_file, egopose, index = -1):
    self.frames[index] = ( egopose, pcd_file )
    pass

  def save(self, file):

    tar = tarfile.open(file, "w")
    for frame in self.frames:
      tar.add(frame.file, arcname=('%d.pcd' % (frame.index)) )
    pass