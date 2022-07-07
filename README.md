# LIDAR-SCAN
Adopted from Intel RealSense https://www.intelrealsense.com/

This Python-script is designed for the Intel RealSense LIDAR L515. 

Each second a RGB and Depth image is taken. Additionally the raw data is stored as npy. 
The Depth-images are colored in JET. 

After ten seconds a .ply-pointcloud is created. The pointcloud only contains the structural mesh, not any coloring. 

