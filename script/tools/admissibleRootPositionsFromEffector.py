from hpp.corbaserver.rbprm.rbprmbuilder import Builder
from hpp.corbaserver.rbprm.rbprmfullbody import FullBody
from hpp.gepetto import Viewer


from . import quaternion as quat

packageName = "hrp2_14_description"
meshPackageName = "hrp2_14_description"
rootJointType = "freeflyer"
##
#  Information to retrieve urdf and srdf files.
urdfName = "hrp2_14"
urdfSuffix = "_reduced"
srdfSuffix = ""

fullBody = FullBody ()
 
fullBody.loadFullBodyModel(urdfName, rootJointType, meshPackageName, packageName, urdfSuffix, srdfSuffix)

from hpp.corbaserver.rbprm.problem_solver import ProblemSolver

nbSamples = 50000

ps = ProblemSolver( fullBody )

rootName = 'base_joint_xyz'

#~ AFTER loading obstacles
rLegId = 'rLeg'
rLeg = 'RLEG_JOINT0'
rfoot = 'RLEG_JOINT5'
rLegOffset = [0,-0.105,0,]
rLegNormal = [0,1,0]
rLegx = 0.09; rLegy = 0.05
fullBody.addLimb(rLegId,rLeg,rfoot,rLegOffset,rLegNormal, rLegx, rLegy, nbSamples, 0.01)

lLegId = 'lLeg'
lLeg = 'LLEG_JOINT0'
lfoot = 'LLEG_JOINT5'
lLegOffset = [0,-0.105,0]
lLegNormal = [0,1,0]
lLegx = 0.09; lLegy = 0.05
fullBody.addLimb(lLegId,lLeg,lfoot,lLegOffset,rLegNormal, lLegx, lLegy, nbSamples, 0.01)

rarmId = 'rArm'
rarm = 'RARM_JOINT0'
rHand = 'RARM_JOINT5'
rArmOffset = [-0.05,-0.050,-0.050]
rArmNormal = [1,0,0]
rArmx = 0.024; rArmy = 0.024
fullBody.addLimb(rarmId,rarm,rHand,rArmOffset,rArmNormal, rArmx, rArmy, nbSamples, 0.01)

larmId = 'lArm'
larm = 'LARM_JOINT0'
lHand = 'LARM_JOINT5'
lArmOffset = [-0.05,-0.050,-0.050]
lArmNormal = [1,0,0]
lArmx = 0.024; lArmy = 0.024
fullBody.addLimb(larmId,larm,lHand,lArmOffset,lArmNormal, lArmx, lArmy, nbSamples, 0.01)


#make sure this is 0
q_0 = fullBody.getCurrentConfig ()
q_0[0:7] = [0,0,0, 1, 0, 0, 0]
fullBody.setCurrentConfig (q_0)

import numpy as np
effectorName = rfoot
limbId = rLegId
q = fullBody.getSample(limbId, 1)
fullBody.setCurrentConfig(q) #setConfiguration matching sample
qEffector = fullBody.getJointPosition(effectorName)
q0 = quat.Quaternion(qEffector[3:7])
rot = q0.toRotationMatrix() #compute rotation matrix world -> local
p = qEffector[0:3] #(0,0,0) coordinate expressed in effector fram
rm=np.zeros((4,4))
for i in range(0,3):
	for j in range(0,3):
		rm[i,j] = rot[i,j]
for i in range(0,3):
	rm[i,3] = qEffector[i]
rm[3,3] = 1
invrm = np.linalg.inv(rm)
p = invrm.dot([0,0,0,1])



def printRootPosition(limbId, effectorName, nbSamples):
	f1=open('../data/roms/com'+limbId+'.erom', 'w+')
	for i in range(0,nbSamples-1):
		q = fullBody.getSample(limbId, i)
		fullBody.setCurrentConfig(q) #setConfiguration matching sample
		qEffector = fullBody.getJointPosition(effectorName)
		q0 = quat.Quaternion(qEffector[3:7])
		rot = q0.toRotationMatrix() #compute rotation matrix world -> local
		p = qEffector[0:3] #(0,0,0) coordinate expressed in effector fram
		rm=np.zeros((4,4))
		for i in range(0,3):
			for j in range(0,3):
				rm[i,j] = rot[i,j]
		for i in range(0,3):
			rm[i,3] = qEffector[i]
		rm[3,3] = 1
		invrm = np.linalg.inv(rm)
		p = invrm.dot([0,0,0,1])
		f1.write(str(p[0]) + "," + str(p[1]) + "," + str(p[2]) + "\n")
	f1.close()

printRootPosition(rLegId, rfoot, nbSamples)
printRootPosition(lLegId, lfoot, nbSamples)
printRootPosition(rarmId, rHand, nbSamples)
printRootPosition(larmId, lHand, nbSamples) 
