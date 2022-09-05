import kivy
kivy.require('2.1.0')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.label import Label
import sympy
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from random import randint, uniform
from sympy import isprime, factorint
from math import asin, sin, cos, sqrt, pi, degrees
from copy import copy
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

#将背景调成白色
Window.clearcolor = (1, 1, 1, 1)

############## Player Class ################

class Player(Widget):
    score = NumericProperty(0)


############# Ball Widget ################


       
class PrimeBall(Widget):
    value = NumericProperty(0)
    split_value = ListProperty([])
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity).rotate(uniform(-0.05,0.05)) + self.pos


############## Main Screen ###################

class PrimeSmash(Widget):
    p_balls = []
    p_ball = ObjectProperty(None)
    player = ObjectProperty(None)
    splited = False
    missed = False

    def add_ball(self):
        self.p_balls.append(PrimeBall())
        self.add_widget(self.p_balls[-1])


    def fall_ball(self, ball):
        number=150
        if self.player.score<0:
            number=100
        if self.player.score<100 and self.player.score>=0:
            number=250
        if self.player.score<1000 and self.player.score>=100:
            number=500
        if self.player.score<10000 and self.player.score>=1000:
            number=1000
        if self.player.score<100000 and self.player.score>=10000:
            number=2000
        if self.player.score<200000 and self.player.score>=100000:
            number=5000
        if self.player.score>=200000:
            number=10000
        ball.value = randint(2,number)
        ball.center = (randint(ball.width/4,self.width-ball.width/4), ball.height/4)
        ball.velocity = Vector(0, 15)

    def split_ball(self,ball):
        self.splited = False
        self.p_balls.append(PrimeBall())
        self.p_balls.append(PrimeBall())
        self.p_balls[-1].center = ball.center
        self.p_balls[-2].center = ball.center

        fac = factorint(ball.value)
        a = 1
        b = ball.value
        for key in fac:
            while fac[key] > 0 and a < b and b//key != 1:
                a *= key
                b //= key
                fac[key] -= 1
        ball.split_value = [a,b]

    def bounce_ball(self):
        for ball1 in self.p_balls:
            for ball2 in self.p_balls:
                if (ball1.x == ball2.x) and (ball1.y == ball2.y):
                    continue
                else:
                    if ball1.collide_widget(ball2):
                        r1 = sqrt((ball1.velocity_x**2) + (ball1.velocity_y**2))
                        r2 = sqrt((ball2.velocity_x**2) + (ball2.velocity_y**2))
                        r = sqrt((ball1.y-ball2.y)**2 + (ball1.x-ball2.x)**2)
                        theata = asin((ball1.y-ball2.y)/r)
                        if ball1.x-ball2.x < 0:
                            theata = pi - theata
                        phi1 = asin(ball1.velocity_y/r1)
                        if ball1.velocity_x < 0:
                            phi1 = pi - phi1
                        phi2 = asin(ball2.velocity_y/r2)
                        if ball2.velocity_x < 0:
                            phi2 = pi - phi2
                        v1x = r2*cos(phi2-theata)*cos(theata) - r2*sin(phi2-theata)*sin(theata)
                        v1y = r2*cos(phi2-theata)*sin(theata) + r2*sin(phi2-theata)*cos(theata)
                        v2x = r1*cos(phi1-theata)*cos(theata) - r1*sin(phi1-theata)*sin(theata)
                        v2y = r1*cos(phi1-theata)*sin(theata) + r1*sin(phi1-theata)*cos(theata)
                        v1 = copy(ball1.velocity)
                        v2 = copy(ball2.velocity)
                        print(ball1.velocity, ball2.velocity)
                        ball1.velocity_x *= -1
                        ball2.velocity_x *= -1
                        print(ball1.velocity, ball2.velocity)

                        

############# Updating Screen ################

    def update(self, dt):
        if len(self.p_balls) < 2:
            self.add_ball()
            self.fall_ball(self.p_balls[-1])
        
        if len(self.p_balls) > 1:
            if self.p_balls[-1].collide_widget(self.p_balls[-2]) == False:
                self.splited = True
            else:
                self.p_balls[-1].velocity_x += 0.01
                self.p_balls[-2].velocity_x -= 0.01
        
        if self.splited:
            self.bounce_ball()

        for ball in self.p_balls:
            ball.move()

            if ball.top > self.top:
                ball.velocity_y *= -1
            
            if (ball.x < self.x) or (ball.right > self.right):
                ball.velocity_x *= -1

            if ball.top < self.y:
                self.player.score -= ball.value
                self.remove_widget(ball)
                self.p_balls.remove(ball)
                '''self.missed = True
                self.label = Label(color=[0,0,0,2],text = "-"+str(ball.value),font_size=40, center = self.center)'''
    
    def isMissed(self,dt):
        if self.missed:
            self.remove_widget(self.label)
    def isnotMissed(self,dt):
        if not self.missed:
            return


#################### Get Prime Ball ######################

    def on_touch_down(self, touch):
        for ball in self.p_balls:
            if ball.collide_point(touch.x, touch.y):
                if isprime(ball.value):
                    self.missed=True
                    self.label = Label(color=[0,0,0,2],text = "+"+str(ball.value),font_size=40, center = self.center)
                    self.player.score += ball.value
                    self.remove_widget(ball)
                    self.p_balls.remove(ball)
                else:
                    
                    self.player.score -= ball.value
                    self.missed = True
                    self.label = Label(color=[0,0,0,2],text = "-"+str(ball.value), font_size=40,center = self.center)
                    self.add_widget(self.label)
                    self.remove_widget(ball)
                    self.p_balls.remove(ball)
            
            else:
                touch.grab(self)


#################### Split Non Prime Ball ######################

    def on_touch_move(self, touch):
        for ball1 in self.p_balls:
            for ball2 in self.p_balls:
                if ball1 == ball2:
                    continue
                if ball1.collide_widget(ball2):
                    return

            if ball1.collide_point(touch.x, touch.y):
                if touch.grab_current is self:
                    if isprime(ball1.value) == False:
                        self.missed=True
                        self.label = Label(color=[0,0,0,2],text = "+"+str(ball1.value),font_size=40, center = self.center)
                        self.player.score += int(ball1.value/2)
                        self.split_ball(ball1)
                        self.p_balls[-1].value = ball1.split_value[0]
                        self.p_balls[-2].value = ball1.split_value[1]
                        self.p_balls[-1].velocity = Vector(1.5,15)
                        self.p_balls[-2].velocity = Vector(-1.5,15)
                        self.add_widget(self.p_balls[-1])
                        self.add_widget(self.p_balls[-2])
                        self.remove_widget(ball1)
                        self.p_balls.remove(ball1)
                    else:
                        self.player.score -= ball1.value
                        self.missed = True
                        self.label = Label(color=[0,0,0,2],text = "-"+str(ball1.value),font_size=40, center = self.center)
                        self.add_widget(self.label)
                        self.remove_widget(ball1)
                        self.p_balls.remove(ball1)



    
################################################################################
############################### Building App ###################################

class PrimeApp(App):
    def build(self):
        game = PrimeSmash()
        game.p_balls.append(game.p_ball)
        game.fall_ball(game.p_balls[-1])
        Clock.schedule_interval(game.update, 1.0/60.0)
        Clock.schedule_interval(game.isMissed, 1.0)
        Clock.schedule_interval(game.isnotMissed, 1.0)
        return game

if __name__ == "__main__":
    PrimeApp().run()
