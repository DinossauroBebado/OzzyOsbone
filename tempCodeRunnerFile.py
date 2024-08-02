from comSerial import * 
import time 
import cv2
from utils import * 

import threading

import pyaudio
import numpy as np

# from rob_ozzy import * 

from head_kinematic import * 


def ozzy_mind():
    print("run thread")
    # main()

class Ozzy_manager():
    def __init__(self) -> None:

        self.rest_pan = 50
        self.rest_tilt_left = 90 
        self.rest_tilt_right = 90 
        self.close_mouth = 30 