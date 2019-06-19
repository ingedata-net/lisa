import numpy as np
import json

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

# Reading JSON file with box data and returning a prepared tuple of boxes
def get_boxes(boxes_json_file_name, number_of_frames):
  if (boxes_json_file_name == None or len(boxes_json_file_name) == 0):
    print("No filename provided")
    return
  if (number_of_frames == None or number_of_frames < 0):
    print("You need to provide the number of frames")

  json_file = open(boxes_json_file_name)
  boxes_json = json.load(json_file)
  json_file.close()

  boxes_with_errors = {}
  box_counter = 0
  number_of_boxes = len(boxes_json["batch"]["objects"])

  print("###\nPreparing data for " + str(number_of_boxes) + " " + ("box" if number_of_boxes == 1 else "boxes") + "...\n###")
  
  while box_counter < number_of_boxes:
    box = boxes_json["batch"]["objects"][box_counter]

    if (box["lifespan"]["start"] == None): box["lifespan"]["start"] = 0
    if (box["lifespan"]["end"] == None): box["lifespan"]["end"] = number_of_frames - 1

    # prepare all keyframes
    current_frame = box["lifespan"]["start"]
    recorded_frames = []
    while (current_frame <= box["lifespan"]["end"]):
      str_current_frame = str(current_frame) # Necessary because frame indexes in keyframes are strings
      if str_current_frame in box["keyframes"]:
        # indicate it doesn't need interpolation
        box["keyframes"][str_current_frame]["needs_interpolation"] = False
        # convert position, quaternion and scale to tuples
        box["keyframes"][str_current_frame]["position"] = (box["keyframes"][str_current_frame]["position"]["x"], box["keyframes"][str_current_frame]["position"]["y"], box["keyframes"][str_current_frame]["position"]["z"])
        box["keyframes"][str_current_frame]["quaternion"] = (box["keyframes"][str_current_frame]["quaternion"]["w"], box["keyframes"][str_current_frame]["quaternion"]["x"], box["keyframes"][str_current_frame]["quaternion"]["y"], box["keyframes"][str_current_frame]["quaternion"]["z"])
        box["keyframes"][str_current_frame]["scale"] = (box["keyframes"][str_current_frame]["scale"]["x"], box["keyframes"][str_current_frame]["scale"]["y"], box["keyframes"][str_current_frame]["scale"]["z"])
        if len(recorded_frames) == 0:
          dummy = 1
        elif len(recorded_frames) == 1:
          aux_current_frame = box["lifespan"]["start"]
          while aux_current_frame < current_frame:
            str_aux_current_frame = str(aux_current_frame)
            if box["keyframes"][str_aux_current_frame]["needs_interpolation"]:
              box["keyframes"][str_aux_current_frame]["left_frame"] = recorded_frames[0]
              box["keyframes"][str_aux_current_frame]["right_frame"] = current_frame
            aux_current_frame += 1
        else:
          aux_current_frame = recorded_frames[len(recorded_frames) - 1]
          while aux_current_frame < current_frame:
            str_aux_current_frame = str(aux_current_frame)
            if box["keyframes"][str_aux_current_frame]["needs_interpolation"]:
              box["keyframes"][str_aux_current_frame]["left_frame"] = recorded_frames[len(recorded_frames) - 1]
              box["keyframes"][str_aux_current_frame]["right_frame"] = current_frame
            aux_current_frame += 1
        recorded_frames.append(current_frame)
      else:
        # create and indicate it needs interpolation
        box["keyframes"][str_current_frame] = {}
        box["keyframes"][str_current_frame]["needs_interpolation"] = True
      current_frame += 1

    # ensure loose end is interpolated 
    if (box["keyframes"][str(box["lifespan"]["end"])]["needs_interpolation"]):
      current_frame = recorded_frames[len(recorded_frames) - 1]
      while (current_frame <= box["lifespan"]["end"]):
        str_current_frame = str(current_frame)
        if box["keyframes"][str_current_frame]["needs_interpolation"]:
          box["keyframes"][str_current_frame]["right_frame"] = recorded_frames[len(recorded_frames) - 1]
          if len(recorded_frames) > 1:
            box["keyframes"][str_current_frame]["left_frame"] = recorded_frames[len(recorded_frames) - 2]
          else:
            box["keyframes"][str_current_frame]["left_frame"] = box["keyframes"][str_current_frame]["right_frame"]
        current_frame += 1

    # perform interpolation in keyframes which need it
    current_frame = box["lifespan"]["start"]
    while (current_frame <= box["lifespan"]["end"]):
      str_current_frame = str(current_frame)
      if box["keyframes"][str_current_frame]["needs_interpolation"]:
        left_frame = box["keyframes"][str_current_frame]["left_frame"]
        right_frame = box["keyframes"][str_current_frame]["right_frame"]
        str_left_frame = str(left_frame)
        str_right_frame = str(right_frame)
        if right_frame > left_frame:
          box["keyframes"][str_current_frame]["position"] = interpolate_vector3(box["keyframes"][str_left_frame]["position"], box["keyframes"][str_right_frame]["position"], (current_frame - left_frame) / (right_frame - left_frame))
          box["keyframes"][str_current_frame]["quaternion"] = interpolate_quaternion(box["keyframes"][str_left_frame]["quaternion"], box["keyframes"][str_right_frame]["quaternion"], (current_frame - left_frame) / (right_frame - left_frame))
          box["keyframes"][str_current_frame]["scale"] = interpolate_vector3(box["keyframes"][str_left_frame]["scale"], box["keyframes"][str_right_frame]["scale"], (current_frame - left_frame) / (right_frame - left_frame))
        else:
          box["keyframes"][str_current_frame]["position"] = box["keyframes"][str_left_frame]["position"]
          box["keyframes"][str_current_frame]["quaternion"] = box["keyframes"][str_left_frame]["quaternion"]
          box["keyframes"][str_current_frame]["scale"] = box["keyframes"][str_left_frame]["scale"]
      current_frame += 1

    # prepare matrices in every keyframe
    current_frame = 0 
    while (current_frame < number_of_frames):
      str_current_frame = str(current_frame)
      if (current_frame >= box["lifespan"]["start"] and current_frame <= box["lifespan"]["end"]):
        translation_matrix = position_to_translation_matrix(box["keyframes"][str_current_frame]["position"])
        rotation_matrix = quaternion_to_rotation_matrix(box["keyframes"][str_current_frame]["quaternion"])
        scale_matrix = scale_to_scale_matrix(box["keyframes"][str_current_frame]["scale"])
        box["keyframes"][str_current_frame]["matrix"] = translation_matrix @ rotation_matrix @ scale_matrix
        try:
          box["keyframes"][str_current_frame]["inverse_matrix"] = np.linalg.inv(box["keyframes"][str(current_frame)]["matrix"])
        except:
          box["broken"] = True
          boxes_with_errors[box["id"]] = True
      elif str_current_frame in box["keyframes"]:
        # Delete keyframe date which is out of lifespan of the box
        del box["keyframes"][str_current_frame]
      current_frame += 1;

    box_counter += 1

  if len(boxes_with_errors) > 0:
    print("These boxes have errors and will be omitted in analysis:")
    for boxid in boxes_with_errors:
      print("    " +  boxid)

  boxes_to_return = []
  box_counter = 0
  while box_counter < number_of_boxes:
    box = boxes_json["batch"]["objects"][box_counter]
    if (not("broken" in box) or not(box["broken"])):
      boxes_to_return.append(box)
    box_counter += 1

  return boxes_to_return

# Taking tuple of boxes and returning a hash containing all categories and their corresponding indices
def get_box_categories(boxes):
  box_categories = { "no_category" : 255 }
  last_category_index = 0
  number_of_boxes = len(boxes)

  box_counter = 0
  while box_counter < number_of_boxes:
    box = boxes[box_counter]

    if not(box["category"] in box_categories):
      box_categories[box["category"]] = last_category_index
      last_category_index += 1

    box_counter += 1

  return box_categories

# get_boxes('../../sample/renault.json', 105)