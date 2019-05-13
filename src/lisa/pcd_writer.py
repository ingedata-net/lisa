from struct import pack

def write_pcd_header(stream, buffer, egopose):
  nb_points = len(buffer)

  stream.write("VERSION .7\n")
  stream.write("FIELDS x y z intensity\n")
  stream.write("SIZE 4 4 4 4\n")
  stream.write("COUNT 1 1 1 1\n")
  stream.write(format("WIDTH {}\n", nb_points))
  stream.write(format("HEIGHT 1\n"))
  stream.write("VIEWPOINT %f %f %f %f %f %f %f\n" %
    *egopose.position,
    *egopose.quaternion
  )
  stream.write(format("POINTS {}\n", nb_points))
  stream.write("DATA binary\n")

"""
Output binary PCD from a byte array
"""
def write_pcd(stream, buffer, egopose):
  write_pcd_header(stream, buffer, egopose)
  stream.write( pack("<%df" % len(buffer), buffer) )