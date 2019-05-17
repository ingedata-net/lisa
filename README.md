# lisa

**LI**dar **S**egmentation and **A**nnotation File Format

## Purpose

`lisa` is a free file format created to facilitate scene annotation
LIDAR by a third party company.

This module allows to transform the inputs into lisa files, and to re-transform
the annotated data in the format you want output.

The objective is to be able to simplify exchanges by using a format
open, free and accessible to all.

lisa uses protobuf to efficiently encode the data required for annotation.

```
+ compression (gzip, bzip etc..)
  + <tarfile root>
    - scene.metadata (protobuf)
    - ./frames
      - 1.metadata (protobuf)
      - 1.pcd (pcd)
      - 1.main.jpg (main front camera)
      - 1.rear.jpg (rear camera)
      - ...
```

lisa simplifies the calibration of a part annotation workflow:
- Egopose:
  - Standardization of geographical coordinates to cartesian ( map ) coordinates
  - Standardisation of rotations: use of quaternion
- Compression and standardization of image files
- Deletion of unnecessary data such as some calibration data, ring-indexes etc.... This type of data has no interest in an annotation workflow.
- Normalization of the sensor intensity level
- A lisa file contains a complete scene to be annotated, is encoded in binary, then compressed via gzip.

## How to use

TBD