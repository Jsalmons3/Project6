from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3, CollisionHandlerEvent
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Missile
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval,LerpHprInterval
from direct.interval.IntervalGlobal import Sequence, Parallel, Func
from direct.particles.ParticleEffect import ParticleEffect
import re

class Spaceship(SphereCollideObject):
    def __init__(self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], traverser, modelPath:str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scalevec: float):
        super().__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1)
        self.taskMgr = taskMgr
        self.accept = accept
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scalevec)
        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self. modelNode.setTexture(tex, 1)

        self.taskManager = taskMgr
        self.accept = accept
        self.render = parentNode
        self.SetParticles()
        self.SetKeyBindings()
        self.EnableHUD()

        self.reloadTime = .25
        self.missileDistance = 4000 # Until the missile explodes.
        self.missileBay = 1 # Only one misslile in the missile bay to be launched.
        self.loader = loader

        self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)

        self.cntExplode = 0
        self.explodeIntervals = {}

        self.traverser = traverser

        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)

        self.normalSpeed = 5
        self.boostSpeed = 10
        self.boosting = False

        self.backflipDistance = 500
        self.backflipDuration = 1.0
        self.backflipping = False
        self.backflipInterval = None
        
        
    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward()) # The direction the spaceship is facing.
            # Normalizing a vector makes it consistant all the time.
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile' + str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront # Spawn the missile in front of the nose of the ship.
            # Create our missile.
            currentMissile = Missile(self.loader, "./Assets/Phaser/phaser.egg", self.render, tag, posVec, 4.0)
            # "fluid = 1" makes collision be checked between the last interval and this interval to make sure there's nothing in-betwwn both checks that wasn't hit.
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
            self.traverser.addCollider(currentMissile.collisionNode, self.handler)
        else:
            # If we aren't reloading, we want to start reloading.
            if not self.taskMgr.hasTaskNamed('reload'):
                print('Initializing reload...')
                # Call the reload method on no delay.
                self.taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont

    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        print("fromNode: " + fromNode)
        intoNode = entry.getIntoNodePath().getName()
        print("intoNode: " + intoNode)
        intoPosition = Vec3(entry.getSurfacePoint(self.render))
        tempVar = fromNode.split('_')
        print("tempVar: " + str(tempVar))
        shooter = tempVar[0]
        print("shooter: " + str(shooter))
        tempVar = intoNode.split('_')
        print("tempVar1: " + str(tempVar))
        tempVar = intoNode.split('_')
        print("tempVar2: " + str(tempVar))
        victim = tempVar[0]
        print("victim: " + str(victim))
        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', victim)
        if (strippedString == "Drone" or strippedString == "Planet" or strippedString == "Space Station"):
            print(victim, 'hit at,', intoPosition)
            self.DestroyObject(victim, intoPosition)

        print(shooter + ' is DONE.')
        Missile.Intervals[shooter].finish()

    def DestroyObject(self, hitID, hitPosition):
        nodeID = self.render.find(hitID)
        nodeID.detachNode()

        self.explodeNode.setPos(hitPosition)
        self.Explode()

    def Explode(self):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, duration = 4.0)
        self.explodeIntervals[tag].start()

    def ExplodeLight(self, t):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()

        elif t == 0:
            self.explodeEffect.start(self.explodeNode)

    def SetParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig("./Assets/Part-Efx/basic_xpld_efx.ptf")
        self.explodeEffect.setScale(20)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')
    
    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay =+ 1
            print("Reload complete.")
            if self.missileBay > 1:
                self.missileBay = 1
            return Task.done
        elif task.time <= self.reloadTime:
            print("Reload Proceeding...")
            return Task.cont

    def CheckIntervals(self, task):
        for i in Missile.Intervals:
            # isPlaying returns true or false to see if the missile has gotten to the end of its path.
            if not Missile.Intervals[i].isPlaying():
                # if its path is done, we get rid of everything to do with that missile.
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()
                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + " has reached the end of its fire solution.")
                # We break because when things are deleted from a dictionary, we have to refactor the dictionary so we can reuse it. This is because when we delete things, there's a gap at that point.
                break
        return Task.cont

    def EnableHUD(self):
        self.Hud = OnscreenImage(image = "./Assets/Hud/Reticle3b.png", pos = Vec3(0, 0, 0), scale = 0.1)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)
    
    def SetKeyBindings(self):
        # All of out key bindings for our spaceship's movement
        self.accept('space', self.Thrust, [1])
        self.accept('space-up', self.Thrust, [0])
        self.accept('arrow_left', self.LeftTurn, [1])
        self.accept('arrow_left-up', self.LeftTurn, [0])
        self.accept('arrow_right', self.RightTurn, [1])
        self.accept('arrow_right-up', self.RightTurn, [0])
        self.accept('arrow_up', self.UpTurn, [1])
        self.accept('arrow_up-up', self.UpTurn, [0])
        self.accept('arrow_down', self.DownTurn, [1])
        self.accept('arrow_down-up', self.DownTurn, [0])
        self.accept('q', self.RollLeft, [1])
        self.accept('q-up', self.RollLeft, [0])
        self.accept('e', self.RollRight, [1])
        self.accept('e-up', self.RollRight, [0])
        self.accept('f', self.Fire)
        self.accept('b', self.Backflip)
        self.accept('z', self.SpeedBoost, [1])
        self.accept('z-up', self.SpeedBoost, [0])
        
    def LeftTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyLeftTurn, 'left-turn')
        else:
            self.taskManager.remove('left-turn')
    
    def ApplyLeftTurn(self, task):
        rate = .5
        self.modelNode.setH(self.modelNode.getH() + rate)
        return Task.cont
    
    def RightTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyRightTurn, 'right-turn')
        else:
            self.taskManager.remove('right-turn')
    
    def ApplyRightTurn(self, task):
        rate = .5
        self.modelNode.setH(self.modelNode.getH() - rate)
        return Task.cont
    
    def UpTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyUpTurn, 'up-turn')
        else:
            self.taskManager.remove('up-turn')
    
    def ApplyUpTurn(self, task):
        rate = .5
        self.modelNode.setP(self.modelNode.getP() + rate)
        return Task.cont
    
    def DownTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyDownTurn, 'down-turn')
        else:
            self.taskManager.remove('down-turn')
    
    def ApplyDownTurn(self, task):
        rate = .5
        self.modelNode.setP(self.modelNode.getP() - rate)
        return Task.cont
    
    def RollLeft(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyRollLeft, 'roll-left')
        else:
            self.taskManager.remove('roll-left')
    
    def ApplyRollLeft(self, task):
        rate = .5
        self.modelNode.setR(self.modelNode.getR() + rate)
        return Task.cont
    
    def RollRight(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyRollRight, 'roll-right')
        else:
            self.taskManager.remove('roll-right')
    
    def ApplyRollRight(self, task):
        rate = .5
        self.modelNode.setR(self.modelNode.getR() - rate)
        return Task.cont
    
    def Thrust(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyThrust, 'forward-thrust')
        else:
            self.taskManager.remove('forward-thrust')
    
    def ApplyThrust(self, task):
        if self.backflipping:
            return Task.cont

        if self.boosting:
            rate = self.boostSpeed
        else:
            rate = self.normalSpeed

        trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()

        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

        return Task.cont

    def SpeedBoost(self, keyDown):
        if keyDown:
            self.boosting = True
            print("Speed boost activated!")
        else:
            self.boosting = False
            print("Speed boost deactivated.")

    def Backflip(self):
        if self.backflipping:
            return

        self.backflipping = True
        print("Do a flip!")
        startPos = self.modelNode.getPos()
        startHpr = self.modelNode.getHpr()

        backward = self.render.getRelativeVector(self.modelNode, -Vec3.forward())

        backward.normalize()

        endPos = startPos + (backward * self.backflipDistance)

        endHpr = startHpr + Vec3(0, 360, 0)

        self.backflipInterval = Sequence(Parallel(LerpPosInterval(self.modelNode, self.backflipDuration, endPos, startPos = startPos), LerpHprInterval(self.modelNode, self.backflipDuration, endHpr, startHpr = startHpr)), Func(self.FinishBackflip, startHpr))

        self.backflipInterval.start()

    def FinishBackflip(self, startHpr):
        self.modelNode.setHpr(startHpr)
        self.backflipping = False
        print('Nailed it!')