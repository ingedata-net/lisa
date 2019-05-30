from pyproj import Proj, transform

def geo_convert(code, x, y, z = 0, out='epsg:6510'):
  inProj = Proj(init=code)
  outProj = Proj(init=out)
  x, y = transform(inProj, outProj, float(x), float(y))
  return x, y, z
