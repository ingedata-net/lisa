import numpy as np;

epsilon = np.finfo(float).eps

def normalize_quaternion(q):
  qw, qx, qy, qz = q

  len = np.sqrt(qw*qw + qx*qx + qy*qy + qz*qz)
  if len == 0:
    return (1, 0, 0, 0)
  else:
    s = 1.0 / np.sqrt((qw*qw + qx*qx + qy*qy + qz*qz))
    return (qw * s, qx * s, qy * s, qz * s)

def position_to_translation_matrix(pos):
  x, y, z = pos
  return np.array([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])

def quaternion_to_rotation_matrix(q):
  qw, qx, qy, qz = q

  s = 1.0 / (qw*qw + qx*qx + qy*qy + qz*qz)

  matrix = np.array([[1 - 2*s*(qy*qy+qz*qz), 2*s*(qx*qy-qz*qw), 2*s*(qx*qz+qy*qw), 0], [2*s*(qx*qy+qz*qw), 1 - 2*s*(qx*qx+qz*qz), 2*s*(qy*qz-qx*qw), 0], [2*s*(qx*qz-qy*qw), 2*s*(qy*qz+qx*qw), 1 - 2*s*(qx*qx+qy*qy), 0], [0, 0, 0, 1]])

  return matrix

def scale_to_scale_matrix(sc):
  x, y, z = sc
  return np.array([[x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0], [0, 0, 0, 1]])

def interpolate_vector3(v1, v2, t):
  x1, y1, z1 = v1
  x2, y2, z2 = v2

  if t == 0:
    return (x1, y1, z1)
  elif t == 1:
    return (x2, y2, z2)
  else:
    return ( x1 + t * (x2-x1), y1 + t * (y2-x1), z1 + t * (z2-z1) )

def interpolate_quaternion(q1in, q2in, t):
  global epsilon
  if t == 0:
    return q1in
  elif t == 1:
    return q2in
  else:
    # Copying input quaternions because of passing by reference
    q1 = (q1in[0], q1in[1], q1in[2], q1in[3])
    q2 = (q2in[0], q2in[1], q2in[2], q2in[3])

    x,y,z,w = q1
    x2,y2,z2,w2 = q2

    cos_half_theta = w * w2 + x * x2 + y * y2 + z * z2

    if cos_half_theta < 0:
      q2 = ( -w2, -x2, -y2, -z2 )
      cos_half_theta = -cos_half_theta
    else:
      q2 = ( w2, x2, y2, z2 )

    if cos_half_theta >= 1.0:
      return (w, x, y, z)

    x2,y2,z2,w2 = q2

    sqr_sin_half_theta = 1.0 - cos_half_theta * cos_half_theta

    if sqr_sin_half_theta <= epsilon:
      s = 1 - t

      w = s * w - t * w2
      x = s * x - t * x2
      y = s * y - t * y2
      z = s * z - t * z2

      return normalize_quaternion( (w, x, y, z) )

    sin_half_theta = np.sqrt( sqr_sin_half_theta )
    half_theta = np.arctan2( sin_half_theta, cos_half_theta )
    ratio_a = np.sin( ( 1 - t ) * half_theta ) / sin_half_theta
    ratio_b = np.sin( t * half_theta ) / sin_half_theta

    return ( w * ratio_a + w2 * ratio_b,
      x * ratio_a + x2 * ratio_b,
      y * ratio_a + y2 * ratio_b,
      z * ratio_a + z2 * ratio_b
    )

def point_belongs_to_box(point_vector, box_matrix):
	local_point = box_matrix @ point_vector
	return (np.absolute(local_point[0,0]) <= 0.5 and np.absolute(local_point[1,0]) <= 0.5 and np.absolute(local_point[2,0]) <= 0.5)

