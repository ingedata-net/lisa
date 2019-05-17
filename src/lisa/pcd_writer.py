from struct import pack

def write_pcd_header(stream, buffer):
  nb_points = len(buffer) / 4

  stream.write("VERSION .7\n".encode())
  stream.write("FIELDS x y z intensity\n".encode())
  stream.write("SIZE 4 4 4 4\n".encode())
  stream.write("COUNT 1 1 1 1\n".encode())
  stream.write("WIDTH {}\n".format(nb_points).encode())
  stream.write("HEIGHT 1\n".encode())
  stream.write("POINTS {}\n".format(nb_points).encode())
  stream.write("DATA binary\n".encode())

"""
Output binary PCD from a byte array containing all the points
"""
def write_pcd(stream, buffer):
  write_pcd_header(stream, buffer)
  print(len(buffer))
  print(buffer)
  stream.write( pack("<%df" % len(buffer), *buffer) )