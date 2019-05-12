import os
import math
import numpy as np

from vispy import scene, app, io
from vispy.color import Color
from vispy.visuals import transforms
from vispy.scene.cameras import TurntableCamera
from vispy.visuals.filters import Alpha

CAM_CENTER = (1.82, 3.01, 1.5)

MESH_SCALE = (0.001, 0.001, 0.001) #convert to meters

CF_MESH_PATH = os.path.join(os.path.dirname(__file__), "crazyflie2.obj.gz")

ENV_MESH_PATH = os.path.join(os.path.dirname(__file__), "environment.obj")
ENV_MESH_COLOR = (0.3, 0.3, 0.3, 1.0)



class VisVispy:
    def __init__(self):
        self.canvas = scene.SceneCanvas(title='Crazyswarm', keys='interactive', size=(1024, 768), show=True, config=dict(samples=4), resizable=True)

        self.visual_dragging = None
        self.canvas.events.mouse_press.connect(self.mouse_handler)
        self.canvas.events.mouse_release.connect(self.mouse_handler)
        self.canvas.events.mouse_move.connect(self.mouse_handler)
    
        self.canvas.events.key_press.connect(self.key_pressed_handler)
        self.canvas.events.key_release.connect(self.key_released_handler)

        # Set up a viewbox to display the cube with interactive arcball
        self.view = self.canvas.central_widget.add_view()
        self.view.bgcolor = '#333'
        # self.view.camera = TurntableCamera(fov=40.0, elevation=30.0, azimuth=280.0)
        self.view.camera = TurntableCamera(fov=40.0, elevation=0.0, azimuth=0)
        self.view.camera.center = CAM_CENTER

        # add a colored 3D axis for orientation
        axis = scene.visuals.XYZAxis(parent=self.view.scene)
        self.cf_data = {}
        self.cf_mesh = {}

        ground = scene.visuals.Plane(6.0, 6.0, direction="+z",
            color=(0.3, 0.3, 0.3, 1.0), parent=self.view.scene)


        if ENV_MESH_PATH:
            verts, faces, normals, texcoords = io.read_mesh(ENV_MESH_PATH)
            env_mesh = scene.visuals.Mesh(parent=self.view.scene,
                vertices=verts, faces=faces,
                color=ENV_MESH_COLOR, shading='smooth')
            env_mesh.transform = transforms.MatrixTransform()
            env_mesh.transform.scale(MESH_SCALE)
            # env_mesh.ambient_light_color = ENV_MESH_COLOR
            env_mesh.ambient_light_color = (1,1,1)

        # Instructions
        print("LMB on CF: Moves CF on X & Y Axis")
        print("RMB on CF: Moves CF on Y & Z Axis")
        print("LMB: orbits the view around its center point")
        print("RMB or scroll: change scale_factor (i.e. zoom level)")
        print("SHIFT + LMB: translate the center point")
        print("SHIFT + RMB: change FOV")
         
    def visual_drag_end(self):
        self.visual_dragging = None

    def visual_drag_start(self, visual, metadata):
        self.visual_dragging = {
            'visual': visual,
            'metadata': metadata,
        }

    def is_visual_dragging(self):
        return self.visual_dragging is not None

    def mouse_handler(self, event):
        ## handles all types of mouse input events
        mouse_pos = {'x': event.pos[0], 'y': event.pos[1]}
        is_dragging = event.is_dragging

        is_left_click = event.button == 1

        if is_dragging:
            #ref: https://github.com/vispy/vispy/issues/1336
            self.view.interactive = False
            at_visual = self.canvas.visual_at(event.pos)
            at_visuals = self.canvas.visuals_at(event.pos, radius=10)
            self.view.interactive = True

            if ((at_visual is None) & len(at_visuals) != 0):
                # print(at_visuals)
                at_visual = at_visuals[0]

            if ( (at_visual is not None) & (self.is_visual_dragging() is False) ):
                metadata = {
                    'start_mouse_pos': mouse_pos, 
                    'start_transform': at_visual.transform
                }
                # print(at_visual.name, metadata)
                self.visual_drag_start(at_visual, metadata)
        else:
            if self.is_visual_dragging():
                # dragging has ended
                dragging_visual = self.visual_dragging['visual']
                visual_name = dragging_visual.name

                #restore color
                actual_color = self.cf_data[visual_name]['color']
                dragging_visual.color = (actual_color[0], actual_color[1], actual_color[2], 1)

                #confirm the delta_xyz
                confirmed_delta_xyz = self.cf_data[visual_name].get('confirmed_delta_xyz', (0 ,0 ,0))
                pending_delta_xyz = self.cf_data[visual_name].get('pending_delta_xyz', (0 ,0 ,0))
                self.cf_data[visual_name]['confirmed_delta_xyz'] = self.add_tuples(confirmed_delta_xyz, pending_delta_xyz)
                self.cf_data[visual_name]['pending_delta_xyz'] = (0,0,0)

            self.visual_drag_end()


        if self.is_visual_dragging():
            self.view.camera.interactive = False

            dragging_visual = self.visual_dragging['visual']
            visual_name = dragging_visual.name
            metadata = self.visual_dragging['metadata']

            start_mouse_pos = metadata['start_mouse_pos']
            start_transform = metadata['start_transform']

            mouse_delta_y = float(mouse_pos['y'] - start_mouse_pos['y'])
            mouse_delta_x = float(mouse_pos['x'] - start_mouse_pos['x'])

            if is_left_click:
                delta_x = mouse_delta_x/100
                delta_y = -mouse_delta_y/100
                delta_z = 0
            else:
                delta_x = mouse_delta_x/100
                delta_y = 0
                delta_z = -mouse_delta_y/100
            
            # print(visual_name, start_transform, delta_x , delta_y, delta_z)
            
            actual_color = self.cf_data[visual_name]['color']
            dragging_visual.color = (actual_color[0], actual_color[1], actual_color[2], 0.5)
            self.cf_data[visual_name]['pending_delta_xyz'] = (delta_x, delta_y, delta_z)

        else:
            
            self.view.camera.interactive = True

    def add_tuples(self, tuple_a, tuple_b):
        ## #add tuples with each other https://stackoverflow.com/a/498103/3553367
        return tuple(map(sum, zip(tuple_a, tuple_b)))

    def key_pressed_handler(self, event):
        ## handles all types of mouse input events
        print('key_press', event.key)

    def key_released_handler(self, event):
        ## handles all types of mouse input events
        print('key_release', event.key)
        

    def init_cf_mesh(self, crazyflies):
        if bool(self.cf_mesh) is False:
            verts, faces, normals, texcoords = io.read_mesh(CF_MESH_PATH)
            for i, cf in enumerate(crazyflies):
                visual_name = 'drone_' + str(i)
                mesh = scene.visuals.Mesh(parent=self.view.scene,
                    vertices=verts, faces=faces, shading='smooth', name=visual_name)
                mesh.ambient_light_color = (1,1,1)
                mesh.transform = transforms.MatrixTransform()
                mesh.interactive = True
                self.cf_mesh[visual_name] = mesh
                self.cf_data[visual_name] = {}

    def update(self, t, crazyflies):
        # print('time: ', round(t, 6))
        self.init_cf_mesh(crazyflies)

        self.canvas.app.process_events()

        for i in range(0, len(self.cf_mesh)):
            visual_name = 'drone_' + str(i)
            x, y, z = crazyflies[i].position()
            roll, pitch, yaw = crazyflies[i].rpy()
            color = crazyflies[i].ledRGB

            self.cf_mesh[visual_name].transform.reset()
            self.cf_mesh[visual_name].transform.scale(MESH_SCALE)
            self.cf_mesh[visual_name].transform.rotate(90, (1, 0, 0))
            self.cf_mesh[visual_name].transform.rotate(math.degrees(roll), (1, 0, 0))
            self.cf_mesh[visual_name].transform.rotate(math.degrees(pitch), (0, 1, 0))
            self.cf_mesh[visual_name].transform.rotate(math.degrees(yaw), (0, 0, 1))


            confirmed_delta_xyz = self.cf_data[visual_name].get('confirmed_delta_xyz', (0 ,0 ,0))
            pending_delta_xyz = self.cf_data[visual_name].get('pending_delta_xyz', (0 ,0 ,0))

            delta_x, delta_y, delta_z = self.add_tuples(confirmed_delta_xyz, pending_delta_xyz)

            self.cf_mesh[visual_name].transform.translate((x + delta_x, y + delta_y, z + delta_z))

            # if color was not set, or color has changed
            # vispy does not do this check
            if (self.cf_data[visual_name].get('color', None) is None) or (color != self.cf_data[visual_name]['color']): 
                self.cf_mesh[visual_name].color = color
                self.cf_data[visual_name]['color'] = color
