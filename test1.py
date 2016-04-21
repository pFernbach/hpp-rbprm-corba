# Importing helper class for setting up a reachability planning problem
from hpp.corbaserver.rbprm.rbprmbuilder import Builder

# Importing Gepetto viewer helper class
from hpp.gepetto import Viewer

rootJointType = 'freeflyer'
packageName = 'hpp-rbprm-corba'
meshPackageName = 'hpp-rbprm-corba'
# URDF file describing the trunk of the robot HyQ
urdfName = 'hyq_trunk_large'
# URDF files describing the reachable workspace of each limb of HyQ
urdfNameRom = ['hyq_lhleg_rom','hyq_lfleg_rom','hyq_rfleg_rom','hyq_rhleg_rom']
urdfSuffix = ""
srdfSuffix = ""

# Creating an instance of the helper class, and loading the robot
rbprmBuilder = Builder ()
rbprmBuilder.loadModel(urdfName, urdfNameRom, rootJointType, meshPackageName, packageName, urdfSuffix, srdfSuffix)
rbprmBuilder.setJointBounds ("base_joint_xyz", [-2,5, -1, 1, 0.3, 4])
# The following lines set constraint on the valid configurations:
# a configuration is valid only if all limbs can create a contact ...
rbprmBuilder.setFilter(['hyq_rhleg_rom', 'hyq_lfleg_rom', 'hyq_rfleg_rom','hyq_lhleg_rom'])
# ... and only if a contact surface includes the gravity
rbprmBuilder.setAffordanceFilter('hyq_lhleg_rom', ['Support',])
rbprmBuilder.setAffordanceFilter('hyq_rfleg_rom', ['Support',])
rbprmBuilder.setAffordanceFilter('hyq_lfleg_rom', ['Support',])
rbprmBuilder.setAffordanceFilter('hyq_rhleg_rom', ['Support', 'Lean'])
# We also bound the rotations of the torso.
rbprmBuilder.boundSO3([-0.4,0.4,-3,3,-3,3])

# Creating an instance of HPP problem solver and the viewer
from hpp.corbaserver.rbprm.problem_solver import ProblemSolver
ps = ProblemSolver( rbprmBuilder )
r = Viewer (ps)

# Setting initial and goal configurations
q_init = rbprmBuilder.getCurrentConfig ();
q_init [0:3] = [-2, 0, 0.63]; rbprmBuilder.setCurrentConfig (q_init); r (q_init)
q_goal = q_init [::]
q_goal [0:3] = [3, 0, 0.63]; r (q_goal)

# Choosing a path optimizer
ps.addPathOptimizer("RandomShortcut")
ps.setInitialConfig (q_init)
ps.addGoalConfig (q_goal)

# Choosing RBPRM shooter and path validation methods.
# Note that the standard RRT algorithm is used.
ps.client.problem.selectConFigurationShooter("RbprmShooter")
ps.client.problem.selectPathValidation("RbprmPathValidation",0.05)
r.loadObstacleModel (packageName, "darpa", "planning")

from hpp.corbaserver.affordance import Client
c = Client ()
c.affordance.analyseAll ()

objs = c.affordance.getAffordancePoints ("Support")

import random
count = 0
for aff in objs:
	colour = random.random()
	for tri in aff:
		r.client.gui.addTriangleFace('tri' + str(count), tri[0], tri[1], tri[2], [colour, 1, 0.5, 1])
		r.client.gui.addToGroup('tri' + str(count), 'planning')
		count += 1

# Solve the problem
t = ps.solve ()

# Playing the computed path
from hpp.gepetto import PathPlayer
pp = PathPlayer (rbprmBuilder.client.basic, r)
pp (1)
