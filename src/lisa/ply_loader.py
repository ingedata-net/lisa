from plyfile import PlyData, PlyElement
import numpy as np

from .pcd_writer import write_pcd

def ply2pcd(
  input_file,
  output_file,
  normalize_intensity=True,
  scale_intensity_factor=256
  ):
  plydata = PlyData.read(input_file)

  xvalue = plydata['vertex']['x']
  yvalue = plydata['vertex']['y']
  zvalue = plydata['vertex']['z']
  ivalue = plydata['vertex']['intensity']

  if not isinstance(ivalue, np.ndarray):
    ivalue = plydata['vertex']['i']

  catch_intensity = isinstance(ivalue, np.ndarray)

  if catch_intensity:
    if normalize_intensity:
      max = np.amax(ivalue)
      ivalue = np.true_divide(ivalue, max)
    else:
      ivalue = np.multiply(ivalue, 1 / scale_intensity_factor)

    ivalue = np.clip(ivalue, 0, 1.0)

    buff = np.column_stack((xvalue, yvalue, zvalue, ivalue)).flatten()
  else:
    buff = np.column_stack((xvalue, yvalue, zvalue, np.full(len(zvalue), 1.0) )).flatten()

  write_pcd(output_file, buff)
  output_file.close()