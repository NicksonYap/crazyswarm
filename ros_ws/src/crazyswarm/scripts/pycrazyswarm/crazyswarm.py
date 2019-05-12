import argparse

from . import genericJoystick

class Crazyswarm:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--sim", help="Run using simulation", action="store_true")
        parser.add_argument("--vis", help="(sim only) Visualization backend [mpl]", choices=['mpl', 'vispy'], default="mpl")
        parser.add_argument("--frame_interval", help="(sim only) Intervals between frame updates, 0 for max framerate [0.01s]", type=float, default=0.01)
        parser.add_argument("--speed", help="(sim only) Playback speed, 2 to speed up 0.5 to slow down [1]", type=float, default=1)
        parser.add_argument("--writecsv", help="Enable CSV output (only available in simulation)", action="store_true")
        args, unknown = parser.parse_known_args()

        if args.sim:
            import crazyflieSim
            self.timeHelper = crazyflieSim.TimeHelper(args.vis, args.frame_interval, args.writecsv, args.speed)
            self.allcfs = crazyflieSim.CrazyflieServer(self.timeHelper)
        else:
            import crazyflie
            self.allcfs = crazyflie.CrazyflieServer()
            self.timeHelper = crazyflie.TimeHelper()
            if args.writecsv:
                print("WARNING: writecsv argument ignored! This is only available in simulation.")
        self.input = genericJoystick.Joystick(self.timeHelper)
