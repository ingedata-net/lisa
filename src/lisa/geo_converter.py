from pyproj import Proj, transform

def geo_convert(code, x, y):
  inProj = Proj(init=code)
  outProj = Proj(init='epsg:6510')
  x, y = transform(inProj,outProj, float(x), float(y))
  return x, y

