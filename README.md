# Feature detection and matching example

This is an example to show how feature point detection can be used to find a registered planer object from video images.

![demoimage](demoimage.png)

## Prerequisite

Python 3.5 and OpenCV 3.

1. Download and install Anaconda3-4.2 (64bit version, python 3.5) from https://repo.continuum.io/archive/. (Note: Not the latest version)
1. Open Anaconda Prompt as administrator.
1. Install OpenCV.
   
   ```
   > conda install -c mempo opencv3
   ```

## How to use

1. Run the example code.

   ```
   > python object_detection.py
   ```

1. Press 'r' to register a query image with a target (textured planer) object. Then object detection will start.
1. Press 'q' to quit the detection.

