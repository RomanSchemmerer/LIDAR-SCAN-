import pyrealsense2 as rs
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
import cv2
import time

 #Class to establish a pipeline with the L515, including some methods to read out (and somehow process) the data.
class L515(object):
    def __init__(self, rgb_size=None, depth_size=None):

        """
        rgb_size: tuple or list of integers, of form [width, height]; if None, no color stream is started
        depth_size: tuple or list of integers, of form [width, height]; if None, no depth stream is started
        """
        # Create a context object. This object owns the handles to all connected realsense devices
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # Get device product line in case ... whatever
        pipeline_profile = self.config.resolve(rs.pipeline_wrapper(self.pipeline))
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))
        print(f"> connected to Intel RealSense {device_product_line}")

        if depth_size is not None:

            # set resolution of camera and depth sensor
            self.config.enable_stream(stream_type=rs.stream.depth, width=depth_size[0], height=depth_size[1],
                                      format=rs.format.z16, framerate=30)

        if rgb_size is not None:

            # check if camera provides RGB (nice to have)
            found_rgb = False

            for s in device.sensors:

                if s.get_info(rs.camera_info.name) == 'RGB Camera':

                    found_rgb = True
                    break

            if not found_rgb:

                raise NotImplementedError("No RGB Camera found")

            self.config.enable_stream(rs.stream.color, rgb_size[0], rgb_size[1], rs.format.bgr8, 30)

        self.open = False
        self.profile = None  # defined at start()

    def start(self):

        # Start streaming
        self.config.resolve(p=self.pipeline)  # just an optional check
        self.profile = self.pipeline.start(self.config)
        self.open = True

    def get_depth_scale(self):

        # get depth scale for optional filtering
        depth_sensor = self.profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()  # threshold = threshold in meters / depth_scale
        return depth_scale

    def plot_colored_pointcloud(self):

        if self.open is False:

            self.start()

        # alignment object, if we want to map color to pointcloud
        align_to = rs.stream.color
        align = rs.align(align_to)

        try:

            # Create a pipeline object. This object configures the streaming camera and owns it's handle
            frames = self.pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth = aligned_frames.get_depth_frame()
            color = aligned_frames.get_color_frame()

            depth_np = np.asanyarray(depth.get_data())
            #depth_np = np.multiply(depth_np, 0.25)         #Activate to scale in mm, or try def scale
            color_np = np.asanyarray(color.get_data())
            
            # plot colorized scatter plot
            intrinsics = rs.video_stream_profile(depth.profile).get_intrinsics()
            points = []
            point_colors = []

            # TODO: vectorize ... or maybe switch to list comprehensions

            for i in range(depth_np.shape[0]):

                for j in range(depth_np.shape[1]):

                    p = rs.rs2_deproject_pixel_to_point(intrinsics, [float(j), float(i)], depth.get_distance(j, i))

                    if p[-1] > 0.0:

                       points.append(p)
                       point_colors.append(color_np[i, j, :]/255)

            points_np = np.array(points)
            fig = plt.figure()
            axes = Axes3D(fig)
            axes.scatter(points_np[:, 0], points_np[:, 2], points_np[:, 1]*-1, s=0.05, c=point_colors)
            plt.show()

        finally:
            self.pipeline.stop()



    def get_png(self):

       # if self.open is False:

       #     self.start()

        # alignment object, if we want to map color to pointcloud
        align_to = rs.stream.color
        align = rs.align(align_to)  #align-function is super important, otherwise depth and color image do not fit
        #Intel Realsense solution would be a reshape function :'-D, this is not working

        #try:

            # Create a pipeline object. This object configures the streaming camera and owns it's handle
        frames = self.pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth = aligned_frames.get_depth_frame()
        color = aligned_frames.get_color_frame()
        depth_np = np.asanyarray(depth.get_data())
                #depth_np = np.around(np.multiply(depth_np, 0.25))  #Activate to scale in mm, but image representation gets worse, idk why
        color_np = np.asanyarray(color.get_data())         
        
        
        
        return depth_np, color_np

        #finally:
            #self.pipeline.stop()

    def get_ply(self,y): 
        # Declare pointcloud object, for calculating pointclouds and texture mappings
        pc = rs.pointcloud()
        # We want the points object to be persistent so we can display the last cloud when a frame drops
        points = rs.points()

        # Declare RealSense pipeline, encapsulating the actual device and sensors
        pipe = rs.pipeline()
        config = rs.config()
        # Enable depth stream
        config.enable_stream(rs.stream.depth)

        # Start streaming with chosen configuration
        pipe.start(config)

        # We'll use the colorizer to generate texture for our PLY
        # (alternatively, texture can be obtained from color or infrared stream)
        colorizer = rs.colorizer()

        try:
            # Wait for the next set of frames from the camera
            frames = pipe.wait_for_frames()
            colorized = colorizer.process(frames)

            # Create save_to_ply object
            ply = rs.save_to_ply("LIDAR_Scan6\PLY\TXT%d9.ply" %y)               #CHANGE HERE

            # Set options to the desired values
            # In this example we'll generate a textual PLY with normals (mesh is already created by default)
            ply.set_option(rs.save_to_ply.option_ply_binary, False)  #False  
            ply.set_option(rs.save_to_ply.option_ply_normals, True)    #True

            print("Saving to %d.ply..." %y)
            # Apply the processing block to the frameset which contains the depth frame and the texture
            ply.process(colorized)


            ply = rs.save_to_ply("LIDAR_Scan6\PLY\BIN%d9.ply" %y)               #CHANGE HERE

            # Set options to the desired values
            # In this example we'll generate a textual PLY with normals (mesh is already created by default)
            ply.set_option(rs.save_to_ply.option_ply_binary, True)  #True for binary  
            ply.set_option(rs.save_to_ply.option_ply_normals, True)    #True

            #print("Saving to %d.ply..." %y)
            # Apply the processing block to the frameset which contains the depth frame and the texture
            ply.process(colorized)
            print("Done")
        finally:
            pipe.stop()



def main(y):
    col_w = 1280    #Do not touch these parameters
    col_h = 720
    dep_w = 1024
    dep_h = 768
    

    new_instance = L515(rgb_size=[col_w, col_h],depth_size=[dep_w, dep_h])



    new_instance.start()
    #dep matrix has range from 0-inf, col 0-255. both have 3 channels and 1280x720 shape
     

    for x in range (5):

        dep, col = new_instance.get_png()
        # Pointcloud viewer, but RealsenseViewer might be better in this case
        #new_instance.plot_colored_pointcloud()

        # Depth_jet is nicer to view, because of color, Values are scaled on 0-255
        depth_jet = cv2.applyColorMap(cv2.convertScaleAbs(dep, alpha=0.03), cv2.COLORMAP_JET)

        # Safe the images
        #cv2.imwrite("LIDAR_Test\Depth_RAW1\DepthSample_RAW2_%d%d.png" %(y,x), dep)
        np.save("LIDAR_Scan6\Depth_RAW\Depth_RAW_%d%d" %(y,x), dep)                 #CHANGE HERE
        np.save("LIDAR_Scan6\Color_RAW\Color_RAW_%d%d" %(y,x), col)                 #CHANGE HERE
        cv2.imwrite("LIDAR_Scan6\Image\Color_%d%d.png" %(y,x), col)                 #CHANGE HERE
        cv2.imwrite("LIDAR_Scan6\Depth_JET\Depth_JET_%d%d.png" %(y,x), depth_jet)   #CHANGE HERE
        print("Bilder: %d%d" %(y,x))
        time.sleep(1) 


    #print("depth shape:", dep.shape, "MaxVal:", np.amax(dep))
    #print("deph_jet shape:", depth_jet.shape, "MaxVal:", np.amax(depth_jet))
    #print("color shape:", col.shape, "MaxVal:", np.amax(col))




if __name__ == "__main__":
    for y in range(9, 10, 1):    # when finished 31-60; 61-99

        main(y) 
        
        L515.get_ply(None, y) #new_instance.get_ply(x)
    
    
