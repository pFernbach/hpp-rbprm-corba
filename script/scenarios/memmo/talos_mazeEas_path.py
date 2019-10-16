from hpp.corbaserver.rbprm.talos_abstract import Robot
from hpp.gepetto import Viewer
from hpp.corbaserver import Client
from hpp.corbaserver import ProblemSolver
import time

Robot.urdfName += "_large"

vMax = 0.3# linear velocity bound for the root
aMax = 0.1 # linear acceleration bound for the root
extraDof = 6
mu=0.5# coefficient of friction
# Creating an instance of the helper class, and loading the robot
rbprmBuilder = Robot()
# Define bounds for the root : bounding box of the scenario
root_bounds = [0,12,0.,2., 0.98, 0.98]
rbprmBuilder.setJointBounds ("root_joint", root_bounds)
# As this scenario only consider walking, we fix the DOF of the torso :
rbprmBuilder.setJointBounds ('torso_1_joint', [0,0])
rbprmBuilder.setJointBounds ('torso_2_joint', [0.006761,0.006761])

# The following lines set constraint on the valid configurations:
# a configuration is valid only if all limbs can create a contact with the corresponding afforcances type
rbprmBuilder.setFilter(['talos_lleg_rom','talos_rleg_rom'])
rbprmBuilder.setAffordanceFilter('talos_lleg_rom', ['Support',])
rbprmBuilder.setAffordanceFilter('talos_rleg_rom', ['Support'])
# We also bound the rotations of the torso. (z, y, x)
rbprmBuilder.boundSO3([-4.,4.,-0.1,0.1,-0.1,0.1])
# Add 6 extraDOF to the problem, used to store the linear velocity and acceleration of the root
rbprmBuilder.client.robot.setDimensionExtraConfigSpace(extraDof)
# We set the bounds of this extraDof with velocity and acceleration bounds (expect on z axis)
rbprmBuilder.client.robot.setExtraConfigSpaceBounds([-vMax,vMax,-vMax,vMax,0,0,-aMax,aMax,-aMax,aMax,0,0])
indexECS = rbprmBuilder.getConfigSize() - rbprmBuilder.client.robot.getDimensionExtraConfigSpace()

# Creating an instance of HPP problem solver
ps = ProblemSolver( rbprmBuilder )
# define parameters used by various methods : 
ps.setParameter("Kinodynamic/velocityBound",vMax)
ps.setParameter("Kinodynamic/accelerationBound",aMax)
# force the orientation of the trunk to match the direction of the motion
ps.setParameter("Kinodynamic/forceYawOrientation",True)
ps.setParameter("DynamicPlanner/sizeFootX",0.2)
ps.setParameter("DynamicPlanner/sizeFootY",0.12)
ps.setParameter("DynamicPlanner/friction",mu)
# sample only configuration with null velocity and acceleration :
ps.setParameter("ConfigurationShooter/sampleExtraDOF",False)
ps.setParameter("PathOptimization/RandomShortcut/NumberOfLoops",100)

# initialize the viewer :
from hpp.gepetto import ViewerFactory
vf = ViewerFactory (ps)

# load the module to analyse the environnement and compute the possible contact surfaces
from hpp.corbaserver.affordance.affordance import AffordanceTool
afftool = AffordanceTool ()
afftool.setAffordanceConfig('Support', [0.5, 0.03, 0.00005])
afftool.loadObstacleModel ("hpp_environments", "multicontact/maze_easy", "planning", vf)
v = vf.createViewer(displayArrows = True)
#afftool.visualiseAffordances('Support', v, v.color.lightBrown)
v.addLandmark(v.sceneName,1)


'''
# Setting initial configuration
q_init = rbprmBuilder.getCurrentConfig ();
q_init[8] = 0.006761 # torso 2 position in reference config
q_init [0:3] = [-0.9,1.5,0.98]
q_init[-6:-3] = [0.07,0,0]
v (q_init)
ps.setInitialConfig (q_init)
# set goal config
rbprmBuilder.setCurrentConfig (q_init)
q_goal = q_init [::]
q_goal[0:3] = [2,2.6,0.98]
q_goal[-6:-3] = [0.1,0,0]
v(q_goal)
'''

import numpy as np

def generate_random_point(bounds):
    return np.random.rand(3,1)*(bounds[:,1:]-bounds[:,0:1]) + bounds[:,0:1]

def generate_random_conf(bounds):
    q = rbprmBuilder.getCurrentConfig ();
    while True:
        xyz = generate_random_point(np.array(root_bounds).reshape(-1,2))[:,0]
        angle = 0#np.random.rand()*np.pi*0.7
        quat = np.array([0,0,np.sin(angle/2), np.cos(angle/2)])
        q[0:3] = xyz
        q[3:7] = quat
	q[8] = 0.006761
        q[-6:-3] = [0.1*np.cos(angle),0.1*np.sin(angle),0]
	v(q)
        status,message = rbprmBuilder.isConfigValid(q)
        if status:
            return q
	else:
	    print "Getting invalid config. try again."
	    print message
#set init
q_init = generate_random_conf(root_bounds)
v (q_init)
ps.setInitialConfig (q_init)
print "Press ENTER to continue"
raw_input()
#set goal
q_goal = generate_random_conf(root_bounds)
v (q_goal)
print "Press ENTER to continue"
raw_input()

ps.resetGoalConfigs()
ps.addGoalConfig (q_goal)



# Choosing RBPRM shooter and path validation methods.
ps.selectConfigurationShooter("RbprmShooter")
ps.addPathOptimizer ("RandomShortcutDynamic")
ps.selectPathValidation("RbprmPathValidation",0.05)
# Choosing kinodynamic methods :
ps.selectSteeringMethod("RBPRMKinodynamic")
ps.selectDistance("Kinodynamic")
ps.selectPathPlanner("DynamicPlanner")

# Solve the planning problem :
#ps.setMaxIterPathPlanning(1000)
t = ps.solve ()
print "Guide planning time : ",t


# display solution : 
from hpp.gepetto import PathPlayer
pp = PathPlayer (v)
pp.dt=0.1
pp.displayVelocityPath(1)
v.client.gui.setVisibility("path_1_root","ALWAYS_ON_TOP")
pp.dt = 0.01
pp(1)

pathId = ps.numberPaths()-1
# move the robot out of the view before computing the contacts
q_far = q_init[::]
q_far[2] = -2
v(q_far)

#tStart = time.time()
#for i in range(1000):
#    rbprmBuilder.isConfigValid(q_init)
#tot = time.time() - tStart
#print "avg time : ",tot/1000.

