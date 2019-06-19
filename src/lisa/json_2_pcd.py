import numpy as np
import json
from pcd_writer import PCDFile

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
def get_boxes_from_json(boxes_json_file_name, number_of_frames):
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

    # STEP 1

    # prepare all keyframes so that we know which ones need interpolation
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
          dummy = 1 # do nothing
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

    # STEP 2

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

    # STEP 3

    # prepare matrices which will be used for checking points in every keyframe
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

def get_cloud_from_file(filename):
  pcd = PCDFile.load(filename)
  return pcd

def analyze_clouds_vs_boxes(input_directory, output_directory, number_of_frames, boxes, box_categories):
  # Iterate through input files
  file_counter = 0
  while (file_counter < number_of_frames):
    input_file_name = input_directory + "/" + str(file_counter) + ".pcd"

    print("###\nReading file " + input_file_name + "\n###")

    # Get PCD from the file
    pcd = get_cloud_from_file(input_file_name)
    
    # Check whether there is viewpoint defined in input files
    # WARNING - PCDFile currently ignores VIEWPOINT header in PCD
    try:
      ego_position = pcd.ego_position
    except:
      ego_position = (0.0, 0.0, 0.0)
    try:
      ego_quaternion = pcd.ego_quaternion
    except:
      ego_quaternion = (1.0, 0.0, 0.0, 0.0)

    # Determine if points in the cloud are with offset  
    if (ego_position[0] != 0 or ego_position[1] != 0 or ego_position[2] != 0 or ego_quaternion[0] != 1 or ego_quaternion[1] != 0 or ego_quaternion[2] != 0 or ego_quaternion[3] != 0):
      cloud_offset_exists = True
      cloud_transform_matrix = position_to_translation_matrix(ego_position) @ quaternion_to_rotation_matrix(ego_quaternion)
    else:
      cloud_offset_exists = False
      cloud_transform_matrix = None

    points = pcd.point_array
    number_of_points = len(points)
    number_of_boxes = len(boxes)

    # Preparing output file
    output_file_name = output_directory + "/" + str(file_counter) + ".pcd"
    output_file = PCDFile( ( ('x', 'f32'), ('y', 'f32'), ('z', 'f32'), ('intensity', 'u8'), ('category', 'u8') ) )

    points_in_categories = { "no_category" : 0 }

    print("###\nChecking " + str(number_of_points) + " " + ("point" if number_of_boxes == 1 else "points") + " against " + str(number_of_boxes) + " " + ("box" if number_of_boxes == 1 else "boxes") + ", please be patient...\n###")

    # Iteration through points in the current cloud
    point_counter = 0
    while point_counter < number_of_points:
      x, y, z, intensity = points[point_counter] # WARNING: Relies on assumption that point tuple is (x,y,z,intensity)
      new_point = (x, y, z, intensity, box_categories["no_category"]) # Assign no category by default to a new point

      # Create a proper 4x1 vector for calculation
      if cloud_offset_exists:
        point_vector = cloud_transform_matrix @ np.array([[x], [y], [z], [1]])
      else:
        point_vector = np.array([[x], [y], [z], [1]])

      # Iterate through all boxes for the current point of the current cloud
      box_counter = 0
      category_found = False
      str_file_counter = str(file_counter)
      while (not(category_found) and box_counter < number_of_boxes):
        box = boxes[box_counter]
        if ((not("broken" in box) or not(box["broken"])) and (str_file_counter in box["keyframes"])):
          try:
            if point_belongs_to_box(point_vector, box["keyframes"][str_file_counter]["inverse_matrix"]): # point is in the box
              new_point = (x, y, z, intensity, box_categories[box["category"]])
              category_found = True
              if box["category"] in points_in_categories:
                points_in_categories[box["category"]] += 1
              else:
                points_in_categories[box["category"]] = 0
          except:
            print("ERRONEOUS BOX: " + box["id"] + " at frame " + str_file_counter)
            print(box["lifespan"])
            print(box["keyframes"][str_file_counter])
            exit()
        box_counter += 1
      if not(category_found):
        points_in_categories["no_category"] += 1

      # Add new point to the output point array
      output_file.point_array.append(new_point)

      point_counter += 1

    # Comment this out if you don't need it
    print("Number of points detected by category:")
    for cat in points_in_categories:
      print("  " + cat + ": " + str(points_in_categories[cat]))

    # Save the file
    # WARNING - Breaks if there's no directory
    output_file.save(output_file_name);

    print("\nDone with " + str(file_counter + 1) + " of " + str(number_of_frames) + " file" + ("" if number_of_frames == 1 else "s") + "!\n\n")

    file_counter += 1


# Here's an example how to perform checks on Renault example

# my_boxes = get_boxes_from_json('../../sample/renault.json', 105)
# my_box_categories = get_box_categories(my_boxes)
# analyze_clouds_vs_boxes('../../sample/new-input-pcds', '../../output/pcds', 105, my_boxes, my_box_categories)