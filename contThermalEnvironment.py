# Based on CartPoleEnvironment by Thomas Rueckstiess, ruecksti@in.tum.de

import simpleThermal as simpTh # Contains easy to use Gaussian function

from matplotlib.mlab import rk4
from math import sin, cos, sqrt, pow, pi, floor
import time
from scipy import eye, matrix, random, asarray

from pybrain.rl.environments.environment import Environment


class contThermEnvironment(Environment):
    """ 
        Provides a simple Gaussian "goodness" function        
    """
    
    # the number of action values the environment accepts
    # The input is cos(theta), where theta is the angle from a line drawn from the plane to the center of the thermal
    # - To illustrate, the input is 1 if the plane travels directly towards the thermal, and 0 if it travels at right angles    
    indim = 1 
    
    # The number of sensor values the environment produces
    # Distance to estimated center of thermal is currently provided
    outdim = 1

    # We set the distance of the plane from the center of the thermal randomly
    randomInitialization = False

    def __init__(self, maxPlaneStartDist, stepSize, numAngles, thermRadius):
        # distPlaneRange specifies the maximum distance the plane can be from the center on startup
        self.maxPlaneStartDist = maxPlaneStartDist
        
        # stepSize is how far the plan moves each time
        self.stepSize = stepSize
                
        # numAngles is the number of discrete directions the plane can move
        self.numAngles = numAngles        
       
        # Sets standard deviation of normal shaped reward function
        self.thermRadius = thermRadius
        
        # initialize the environment (randomly)
        self.reset()
        self.action = 0.0
        self.delay = False

    def getSensors(self):
        return [self.sensors] # Returns (unrounded) distance to center

    # Performs a provided action
    # The action is theta, where theta is the angle (in radians) from a line drawn from the plane to the center of the thermal
    # - To illustrate, the input is 0 if the plane travels directly towards the thermal, and pi/2 if it travels at a right angle to the thermal center    
    def performAction(self, action):   
        self.action = action # This updates theta (angle to move on)
        self.step()

    # Update sensor values (update value of goodness after plane has moved)
    # Uses the current values of self.action
    def step(self):
        # Determine the new distance from the center
        oldDist = self.sensors

        # We need to convert the action into radians
        # Assume we have numAngles = n+1
        # Index 0           ->      0 radians
        # Index last (n)    ->      pi radians
        # Index a           ->      a/n*pi radians = a/(numAngles-1)*pi
        
        # Check:  (with three choices)
        # action 0 -> 0 radians
        # action 1 -> 1/(2)*pi        
        theta = self.action/(self.numAngles-1)*pi;
        stepSize = self.stepSize
                        
        deltaTempX = oldDist - stepSize*cos(theta)
        deltaTempY = sin(theta)*stepSize
        newDist = sqrt(pow(deltaTempX,2)+ pow(deltaTempY,2))
        self.sensors = newDist
        
        # Reset is called when environment is constructed
    def reset(self):
        """ re-initializes the environment, setting the plane back at a random distance from the center of the thermal
        """
        if self.randomInitialization:
            planeDist = random.uniform(0, self.maxPlaneStartDist) # The distance the plane is from the center of the thermal
        else:
            planeDist = self.maxPlaneStartDist
            
        # Initialize sensors
        self.sensors = planeDist
        
    # Returns the distance of the plane from the center of goodness
    def distPlane(self):
        return self.sensors

