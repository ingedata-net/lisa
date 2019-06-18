import struct
import re
import numpy as np

from collections import defaultdict

class PCDFile:
  def __init__(self, fields = (('x','f32'),('y','f32'),('z','f32')) ):
    self.point_array = []
    self.field_struct = fields
    self.build_field_index()
    self.format = 'binary'
    self.little_endian = True

  """
    Rebuild field index for fast access
  """
  def build_field_index(self):
    self.field_index = dict()
    for idx, field in enumerate(self.field_struct):
      self.field_index[field[0]] = idx

  def get_header_field_sizes(self):
    sizes = {
      'u8': 1,
      's8': 1,
      'u16': 2,
      's16': 2,
      'f32': 4,
      'u32': 4,
      's32': 4,
      'f64': 8,
      'u64': 8,
      's64': 8
    }

    print(self.field_struct)
    return " ".join( map( lambda x : str(sizes[x[1]]), self.field_struct ) )

  def parse_header(self, command, *words):
    if command=="VERSION":
      if not (len(words) == 1 and words[0] == ".7"):
        raise Exception("Bad PCD version: Must be .7 but {} given".format(words))
    elif command=="FIELDS":
      self.field_struct = list(map( lambda x: [x, 'u'], words)) # < u stands for 'unknown'
    elif command=="SIZE":
      for index, w in enumerate(words):
        self.field_struct[index][1] = 'u' + str(int(w)*8)
    elif command=="TYPE":
      for index, w in enumerate(words):
        m = {'U': 'u', 'I': 's', 'F': 'f'}
        self.field_struct[index][1] = self.field_struct[index][1].replace("u", m[w])
      print(self.field_struct)
    elif command=="COUNT":
      # not used
      pass
    elif command=="WIDTH":
      # Assuming always N
      pass
    elif command=="HEIGHT":
      # Assuming always 1
      pass
    elif command=="POINTS":
      self.total_points = int(words[0])
      pass
    else:
      raise Exception("Unknown header: {}".format(command))

  def get_header_field_types(self):
    types = {
      'u8': 'U',
      'u16': 'U',
      'u32': 'U',
      'u64': 'U',

      's8': 'I',
      's16': 'I',
      's32': 'I',
      's64': 'I',

      'f32': 'F',
      'f64': 'F',
    }

    return " ".join( map( lambda x : types[x[1]], self.field_struct ) )

  def read_header(self, stream):
    while True:
      l = stream.readline(512)

      if not l:
        raise Exception("ERROR: Cannot Read PCD HEADER.")

      l = l.decode().strip() # Transform from bytes-like to string

      command, *params = l.split(' ')

      if command == "DATA":
        if params[0] != "binary":
          raise Exception("Currently support only binary PCD files")
        print(self.pack_pattern())
        self.read_binary_data(stream)
        break

      print(command, *params)
      self.parse_header(command, *params)


  def get_header_counts(self):
    return " ".join( ['1'] * len(self.field_struct) )

  def write_pcd_header(self, stream):
    nb_points = len(self.point_array)


    fields = self.field_index.keys()

    stream.write("VERSION .7\n".encode())
    stream.write("FIELDS {}\n".format(" ".join(fields) ).encode())
    stream.write("SIZE {}\n".format(self.get_header_field_sizes()).encode())
    stream.write("TYPE {}\n".format(self.get_header_field_types()).encode())
    stream.write("COUNT {}\n".format(self.get_header_counts()).encode())
    stream.write("WIDTH {}\n".format(nb_points).encode())
    stream.write("HEIGHT 1\n".encode())
    stream.write("POINTS {}\n".format(nb_points).encode())
    stream.write("DATA {}\n".format(self.format).encode())

  def read_binary_data(self, stream):
    pack_fmt = self.pack_pattern()
    pack_size = self.pack_size()

    for i in range(0, self.total_points):
      buff = stream.read(pack_size)
      tuple = struct.unpack(pack_fmt, buff)
      self.point_array.append(tuple)

  def pack_pattern(self):
    pack = {
      'u8': 'B',
      's8': 'b',
      'u16': 'H',
      's16': 'h',
      'f32': 'f',
      'u32': 'I',
      's32': 'i',
      'f64': 'd',
      'u64': 'Q',
      's64': 'q'
    }

    pack_pattern = ['<'] if self.little_endian else ['>']

    for v in self.field_struct:
      pack_pattern.append(pack[v[1]])

    return "".join(pack_pattern)

  def pack_size(self):
    pack = {
      'u8': 1,
      's8': 1,
      'u16': 2,
      's16': 2,
      'f32': 4,
      'u32': 4,
      's32': 4,
      'f64': 8,
      'u64': 8,
      's64': 8
    }

    return sum(map( lambda x : pack[x[1]], self.field_struct ), 0)

  def write_content(self, stream):
    pattern = self.pack_pattern()

    for data in self.point_array:
      stream.write(struct.pack(pattern, *data))
    stream.flush()

  """
    Set structure of the PCD:

    ```
    pcd.set_struct( ('x', 'f32'), ('y', 'f32'), ('z', 'f32') )
    ```
  """
  def set_struct(*tuple):
    self.field_struct = tuple
    self.build_field_index()

  """
    Return field index for a specific field
  """
  def get_field_index(name):
    return self.field_index[name] or -1

  def get_value(type, index):
    return self.point_array[index][self.get_field_index(type)]

  """
    Iterate through all the value of a specific field for the points.

    ```
    for x,y,z in pcd.get_values('x', 'y', 'z'):
      print(x,y,z)
    ```
  """
  def get_values(*types):
    indices = map(lambda x: self.get_field_index(x), types)

    for value in self.point_array:
      yield tuple( map(lambda x: value[x], value ) )

  """
    Read a PCD from stream and return a
  """
  def read(self, stream):
    self.read_header(stream)
    self.build_field_index()

  def write(self, stream):
    self.write_pcd_header(stream)
    self.write_content(stream)

  def load(filename):
    f = open(filename, "rb")
    self = PCDFile()
    self.read(f)
    f.close()
    return self

  def save(self, filename):
    f = open(filename, "wb+")
    self.write(f)
    f.close()
