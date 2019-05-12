#!/usr/bin/env python

import numpy as np

from pycrazyswarm import *
import uav_trajectory


formations = [
    {   
        # V formation
        'drone_0': (1.25, 2.26, 1.0, 0.0),
        'drone_1': (1.43, 2.76, 1.0, 0.0),
        'drone_2': (1.59, 3.26, 1.0, 0.0),
        'drone_3': (2.38, 2.26, 1.0, 0.0),
        'drone_4': (2.21, 2.76, 1.0, 0.0),
        'drone_5': (2.07, 3.26, 1.0, 0.0),
        'drone_6': (1.82, 3.76, 1.0, 0.0),
    },

    {
        # Pre-A formation
        'drone_0': (1.25, 2.26, 1.0, 0.0),
        'drone_1': (1.43, 2.76, 1.21, 0.0),
        'drone_2': (1.59, 3.26, 1.46, 0.0),
        'drone_3': (2.38, 2.26, 1.0, 0.0),
        'drone_4': (2.21, 2.76, 1.22, 0.0),
        'drone_5': (2.07, 3.26, 1.46, 0.0),
        'drone_6': (1.82, 3.76, 1.8, 0.0),
    },

    {
        # A formation
        'drone_0': (1.23, 3.88, 0.89, 0.0),
        'drone_1': (1.43, 3.85, 1.21, 0.0),
        'drone_2': (1.62, 3.82, 1.51, 0.0),
        'drone_3': (2.38, 3.92, 0.88, 0.0),
        'drone_4': (2.21, 3.88, 1.19, 0.0),
        'drone_5': (2.03, 3.82, 1.51, 0.0),
        'drone_6': (1.82, 3.76, 1.8, 0.0),
    },

    {
        # deform A formation
        'drone_0': (1.23, 3.88, 0.89, 0.0),
        'drone_1': (1.43, 3.36, 1.21, 0.0),
        'drone_2': (1.62, 2.85, 1.51, 0.0),
        'drone_3': (2.38, 3.92, 0.88, 0.0),
        'drone_4': (2.21, 3.37, 1.19, 0.0),
        'drone_5': (2.03, 2.85, 1.51, 0.0),
        'drone_6': (1.84, 2.44, 1.8, 0.0),
    },

    {
        # pre-V formation
        'drone_0': (1.23, 3.88, 1.88, 0.0),
        'drone_1': (1.43, 3.36, 1.49, 0.0),
        'drone_2': (1.62, 2.85, 1.2, 0.0),
        'drone_3': (2.38, 3.92, 1.86, 0.0),
        'drone_4': (2.21, 3.37, 1.5, 0.0),
        'drone_5': (2.03, 2.85, 1.2, 0.0),
        'drone_6': (1.84, 2.44, 0.95, 0.0),
    },

    {
        # V formation
        'drone_0': (1.23, 3.2, 1.88, 0.0),
        'drone_1': (1.43, 3.21, 1.57, 0.0),
        'drone_2': (1.62, 3.21, 1.24, 0.0),
        'drone_3': (2.38, 3.19, 1.9, 0.0),
        'drone_4': (2.21, 3.2, 1.58, 0.0),
        'drone_5': (2.03, 3.21, 1.24, 0.0),
        'drone_6': (1.84, 3.22, 0.93, 0.0),
    },

    {
        # deform V formation
        'drone_0': (1.23, 2.71, 1.88, 0.0),
        'drone_1': (1.43, 3.1, 1.57, 0.0),
        'drone_2': (1.62, 3.48, 1.24, 0.0),
        'drone_3': (2.38, 2.7, 1.9, 0.0),
        'drone_4': (2.21, 3.08, 1.58, 0.0),
        'drone_5': (2.03, 3.46, 1.24, 0.0),
        'drone_6': (1.84, 3.88, 0.93, 0.0),
    },

    # {
    #     # pre-landing
    #     'drone_0': (1.54, 2.71, 1.38, 0.0),
    #     'drone_1': (1.57, 3.1, 1.26, 0.0),
    #     'drone_2': (1.62, 3.48, 1.11, 0.0),
    #     'drone_3': (2.08, 2.7, 1.37, 0.0),
    #     'drone_4': (2.07, 3.08, 1.27, 0.0),
    #     'drone_5': (2.03, 3.46, 1.09, 0.0),
    #     'drone_6': (2.01, 3.88, 0.93, 0.0),
    # },
    
]

if __name__ == "__main__":
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs


    TRIALS = 1
    TIMESCALE = 1.0
    for i in range(TRIALS):

        timeHelper.sleep(3)

        allcfs.takeoff(targetHeight=1.0, duration=2.0)
        timeHelper.sleep(2.5)

        for cf in allcfs.crazyflies:
            pos = np.array(cf.initialPosition) + np.array([0, 0, 1.0])
            cf.goTo(pos, 0, 3.0)
        timeHelper.sleep(3.5)



        for formation in formations:
            for i, cf in enumerate(allcfs.crazyflies):
                visual_name = 'drone_' + str(i)
                x, y, z, yaw = formation[visual_name]

                pos = [x, y, z]
                cf.goTo(pos, yaw, 3.0)
            timeHelper.sleep(3.5)


        for cf in allcfs.crazyflies:
            pos = np.array(cf.initialPosition) + np.array([0, 0, 1.0])
            cf.goTo(pos, 0, 3.0)
        timeHelper.sleep(3.5)


        allcfs.land(targetHeight=0.06, duration=2.0)
        timeHelper.sleep(3.0)

