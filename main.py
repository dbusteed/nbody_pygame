#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import pygame_gui as gui

from pygame import Rect
from pygame_gui.elements import (
    UIPanel, UILabel, UIButton, UIHorizontalSlider
)

import numpy as np
from random import choice, random, randint

pygame.init()

WIDTH = 1200
HEIGHT = 800

# UI stuff
PAN_SPEED = 5
SCALE_SPEED = 0.01
MIN_SCALE = 0.2
MAX_SCALE = 2.0
DELAY = 20

# constants for this universe
G = 1
MIN_R2 = 1
COLLISION_BUFFER = 5

center_x = WIDTH / 2
center_y = HEIGHT / 2

win = pygame.display.set_mode((WIDTH, HEIGHT))
ui = gui.UIManager((WIDTH, HEIGHT))

pygame.display.set_caption("")

# apologies for the long lines...but when has GUI code ever been fun to read?
start_menu_pad_x = (1/6 * WIDTH)
start_menu_pad_y = (3/16 * HEIGHT)
start_menu = UIPanel(Rect(start_menu_pad_x, start_menu_pad_y, WIDTH-(start_menu_pad_x*2), HEIGHT-(start_menu_pad_y*2)), starting_layer_height=1, manager=ui)
main_txt = UILabel(Rect(start_menu.rect.width / 2 - 150, 30, 300, 50), text="n-body simulation", manager=ui, container=start_menu)
sun_lbl = UILabel(Rect(start_menu.rect.width / 2 - 200, 100, 200, 50), text="sun", manager=ui, container=start_menu)
sun_btn = UIButton(Rect(start_menu.rect.width / 2, 112.5, 50, 25), text="on", manager=ui, container=start_menu)
nbody_lbl = UILabel(Rect(start_menu.rect.width / 2 - 200, 150, 200, 50), text="# of bodies", manager=ui, container=start_menu)
nbody_slider = UIHorizontalSlider(Rect(start_menu.rect.width / 2, 162.5, 150, 25), 20, (5, 100), manager=ui, container=start_menu)
nbody_lbl_2 = UILabel(Rect(start_menu.rect.width / 2 + 150, 162.5, 50, 25), text=f"{nbody_slider.get_current_value()}", manager=ui, container=start_menu)
start_btn = UIButton(Rect(start_menu.rect.width / 2 - 40, 300, 80, 40), text='START', manager=ui, container=start_menu)
hud_height = 100
no_margin = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
hud = UIPanel(Rect(5, HEIGHT-hud_height, WIDTH-10, hud_height), starting_layer_height=1, manager=ui, margins=no_margin)
hud.hide()
hide_hud = False
help_pnl_width = (1/3 * WIDTH)
help_pnl = UIPanel(Rect(0, 0, help_pnl_width, hud_height), starting_layer_height=1, manager=ui, container=hud, margins=no_margin)
info_pnl = UIPanel(Rect(help_pnl_width-5, 0, (WIDTH-help_pnl_width-5), 50), starting_layer_height=1, manager=ui, container=hud)
btns_pnl = UIPanel(Rect(help_pnl_width-5, hud_height-50-5, (WIDTH-help_pnl_width-5), 55), starting_layer_height=1, manager=ui, container=hud)
help_lbl_1 = UILabel(Rect(5, 10, help_pnl_width-10, 20), text="Left Click to select a body", manager=ui, container=help_pnl)
help_lbl_2 = UILabel(Rect(5, 30, help_pnl_width-10, 20), text="Right Click + Drag to pan camera", manager=ui, container=help_pnl)
help_lbl_3 = UILabel(Rect(5, 50, help_pnl_width-10, 20), text="Mouse Scroll to zoom", manager=ui, container=help_pnl)
help_lbl_4 = UILabel(Rect(5, 70, help_pnl_width-10, 20), text="Can also navigate with wasd/qe", manager=ui, container=help_pnl)
hud_lbl_1 = UILabel(Rect(5, 1, WIDTH-help_pnl_width-5, 20), text="", manager=ui, container=info_pnl)
hud_lbl_2 = UILabel(Rect(5, 21, WIDTH-help_pnl_width-5, 20), text="", manager=ui, container=info_pnl)
hide_hud_btn = UIButton(Rect(10, 10, 100, 30), text="Hide HUD", manager=ui, container=btns_pnl)
stop_btn = UIButton(Rect(120, 10, 100, 30), text="Restart", manager=ui, container=btns_pnl)
show_hud_btn = UIButton(Rect(WIDTH-35, HEIGHT-25, 35, 25), text="...", manager=ui)
show_hud_btn.hide()


class Body:
    def __init__(self, mass='random', radius=0, pos='normal', vel='random', acc=[0, 0], sun=False, max_init_vel=2):
        if mass == 'random':
            self.mass = self.random_mass()
        else:
            self.mass = mass
        
        if radius:
            self.radius = radius
        else:
            self.radius = self.mass / 2
        
        if pos == 'normal':
            self.pos = self.normal_pos()
        else:
            self.pos = np.array(pos, dtype=float)
        
        self.max_init_vel = max_init_vel
        if vel == 'orbit':
            self.vel = self.orbit_vel()
        elif vel == 'random':
            self.vel = self.random_vel()
        else:
            self.vel = np.array(vel, dtype=float)
        
        self.acc = np.array(acc, dtype=float)
        self.color = (randint(50, 255), randint(50, 255), randint(50, 255))
        self.sun = sun
        self.follow = False

    def orbit_vel(self):
        vel = self.max_init_vel
        if (self.pos[0] * self.pos[1]) > 0:
            return choice([-1, 1]) * np.array([random() * -vel, random() * vel], dtype=float)
        else:
            return choice([-1, 1]) * np.array([random() * vel, random() * vel], dtype=float)

    def random_vel(self):
        vel = self.max_init_vel
        return np.array([random() * choice([vel, -vel]), random() * choice([vel, -vel])])

    def normal_pos(self):
        x = np.random.normal(0, init_spread_x)
        y = np.random.normal(0, init_spread_y)
        return np.array([(abs(x) + init_padding) * (x / abs(x)), (abs(y) + init_padding) * (y / abs(y))], dtype=float)
    
    def random_mass(self):
        return randint(5, 20)

    def accelerate(self, bodies):
        """
        Update accelerate of the body given a list of
        the other bodies in the system
        """
        # if not self.sun:
        self_i = [i for i, b in bodies.items() if b == self][0]
        bodies = {i:b for i, b in bodies.items() if b != self}
        acc = []
        for i, body in bodies.items():
            r2 = (body.pos[0] - self.pos[0])**2 + (body.pos[1] - self.pos[1])**2
            if (self.radius + body.radius) > (np.sqrt(r2) + COLLISION_BUFFER):
                col = (self_i, i) if self.mass > body.mass else (i, self_i)
                collisions.add(col)
            
            if r2 > MIN_R2:
                F = G * ((body.mass * self.mass) / r2)
                f = ((body.pos - self.pos) / np.sqrt(r2)) * F
                acc.append(f / self.mass)
            else:
                acc.append(np.array([0., 0.]))

        self.acc = sum(acc)
        self.vel += self.acc

    def __str__(self):
        return f"m: {round(self.mass, 2)}, r: {round(self.radius, 2)}, " \
            f"vel: {'['+', '.join(map(lambda x: '{: .2f}'.format(x), self.vel))+']'}, " \
            f"acc: {'['+', '.join(map(lambda x: '{: .2f}'.format(x), self.acc))+']'}"
            

# TODO make these GUI options
init_padding = 50
init_spread_x = 400
init_spread_y = 200

bodies = {}
collisions = set()

cam_offset_x = 0
cam_offset_y = 0
scale = 1

sim_running = False

dragging = False
click_point = (0, 0)

app_running = True
clock = pygame.time.Clock()

while app_running:
    time_delta = clock.tick(60) / 1000.0
    pygame.time.delay(DELAY)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app_running = False

        elif event.type == pygame.USEREVENT:
            if event.user_type == gui.UI_BUTTON_PRESSED:
                if event.ui_element == sun_btn:
                    if sun_btn.text == 'on':
                        sun_btn.set_text('off')
                    else:
                        sun_btn.set_text('on')

                elif event.ui_element == start_btn:
                    sim_running = True
                    bodies = {i+1: b for i, b in enumerate(bodies)}
                    
                    n_body = nbody_slider.get_current_value()
                    bodies = [Body(pos='normal', vel='orbit') for _ in range(n_body)]
                    
                    if sun_btn.text == 'on':
                        bodies.append(Body(1000, 15, [0, 0], [0, 0], sun=True))
                    
                    cam_offset_x = 0
                    cam_offset_y = 0
                    scale = 1

                    bodies = {i+1: b for i, b in enumerate(bodies)}
                    collisions = set()
                    
                    hud_lbl_1.set_text(f"# of bodies: {len(bodies)}")
                    start_menu.hide()
                    hud.show()

                elif event.ui_element == stop_btn:
                    sim_running = False
                    nbody_slider.set_current_value(20)
                    nbody_lbl_2.set_text('20')
                    sun_btn.set_text('on')
                    hud.hide()
                    start_menu.show()

                elif event.ui_element == hide_hud_btn:
                    hud.hide()
                    show_hud_btn.show()
                
                elif event.ui_element == show_hud_btn:
                    show_hud_btn.hide()
                    hud.show()

            elif event.user_type == gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == nbody_slider:
                    nbody_lbl_2.set_text(str(nbody_slider.get_current_value()))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # TODO optimize this
                pos_x = (event.pos[0] / scale) - center_x - cam_offset_x + center_x*(1-(1/scale))
                pos_y = (event.pos[1] / scale) - center_y - cam_offset_y + center_y*(1-(1/scale))
                for body in bodies.values():
                    if ((pos_x - body.pos[0])**2 + (pos_y - body.pos[1])**2) <= (body.radius**2):
                        body.follow = True
                    else:
                        body.follow = False
                    
                    # TODO have global for following, and only unset
                    # if True. have that state shown in GUI. and set to false
            elif event.button == 3:
                dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                cam_offset_x += (event.rel[0] / scale)
                cam_offset_y += (event.rel[1] / scale)

        elif event.type == pygame.MOUSEWHEEL:
            scale = np.clip(scale + (event.y * .01), MIN_SCALE, MAX_SCALE)
    
        ui.process_events(event)

    ui.update(time_delta)

    # keyboard input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        cam_offset_x += (PAN_SPEED * (1 / scale))
    if keys[pygame.K_d]:
        cam_offset_x -= (PAN_SPEED * (1 / scale))
    if keys[pygame.K_w]:
        cam_offset_y += (PAN_SPEED * (1 / scale))
    if keys[pygame.K_s]:
        cam_offset_y -= (PAN_SPEED * (1 / scale))
    if keys[pygame.K_e]:
        scale = np.clip(scale + SCALE_SPEED, MIN_SCALE, MAX_SCALE)
    if keys[pygame.K_q]:
        scale = np.clip(scale - SCALE_SPEED, MIN_SCALE, MAX_SCALE)

    # clear the screen each iteration
    win.fill((0, 0, 0))

    # this is where the actual simulation
    # stuff is happening
    if sim_running:

        # STEP 1
        #   - update gravitaional accelerations (and velocities)
        for body in bodies.values():
            body.accelerate(bodies)

        # STEP 2
        #  - update positions (using velocities)
        #  - adjust the camera focus if a body has been selected       
        for body in bodies.values():
            body.pos += body.vel
            if body.follow:
                cam_offset_x, cam_offset_y = -body.pos

                # TODO remove selection if no one is being followed anymore
                hud_lbl_2.set_text('selection: '+str(body))

        # STEP 3
        #  - draw the bodies on the screen
        for body in bodies.values(): 
            pygame.draw.circle(win,
                               body.color,
                               [(body.pos[0] + center_x + cam_offset_x + (-center_x*(1-(1/scale)))) * scale, 
                               (body.pos[1] + center_y + cam_offset_y + (-center_y*(1-(1/scale)))) * scale],
                               (body.radius) * scale)
        
        # STEP 4
        #  - handle any collisions
        for c in collisions:
            try:
                bodies[c[0]].mass += bodies[c[1]].mass
                bodies[c[0]].vel = ((bodies[c[0]].mass * bodies[c[0]].vel) + (bodies[c[1]].mass * bodies[c[1]].vel)) / bodies[c[0]].mass

                if bodies[c[0]].sun:
                    bodies[c[0]].radius += bodies[c[1]].radius / 10
                else:
                    bodies[c[0]].radius += bodies[c[1]].radius / 5
                del bodies[c[1]]
            except:
                pass

        collisions = set()

    # update the UI / screen
    hud_lbl_1.set_text(f"# of bodies: {len(bodies)}")
    ui.draw_ui(win)
    pygame.display.update() 

# quit PyGame when the loop exits
pygame.quit()
