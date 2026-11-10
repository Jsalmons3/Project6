from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
import DefensePaths as defensePaths
import SpaceJamClasses as spaceJamClasses
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from Player import Spaceship

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

    def SetupScene(self):
        self.Universe = spaceJamClasses.Unvierse(self.loader, "./Assets/Universe/Universe/Universe.x", self.render, "Universe", "./Assets/Universe/Universe.jpg", (0, 0, 0), 15000)
        self.Planet1 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet1", "./Assets/Planets/Mars.jpg", (-600, 5000, 67), 350)
        self.Planet2 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet2", "./Assets/Planets/Ceres.jpg", (-400, -200, -800), 400)
        self.Planet3 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet3", "./Assets/Planets/Haumea.jpg", (2500, -2500, 2500), 600)
        self.Planet4 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet4", "./Assets/Planets/Makemake.jpg", (-2700, -5000, 6700), 200)
        self.Planet5 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet5", "./Assets/Planets/Eris.jpg", (3400, -1000, -2000), 100)
        self.Planet6 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet6", "./Assets/Planets/Jupiter.jpg", (4500, 5000, 67), 500)
        self.Spacestation = spaceJamClasses.SpaceStation(self.loader, "./Assets/Space Station/SpaceStation1B/spaceStation.x", self.render, "Space Station", "./Assets/Space Station/SpaceStation1B/SpaceStation1_Dif2.png", (6000, 1000, 67), 200)
        self.Ship = Spaceship(self.loader, self.taskMgr, self.accept, "./Assets/Spaceships/Dumbledore/Dumbledore.x", self.render, "Ship", "./Assets/Spaceships/Dumbledore/spacejet_C.png", Vec3(0, 0, 100), 50)

        self.cTrav = CollisionTraverser()
        self.cTrav.traverse(self.render)
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.Ship.collisionNode, self.Ship.modelNode)
        self.cTrav.addCollider(self.Ship.collisionNode, self.pusher)
        self.cTrav.showCollisions(self.render)


        fullCycle = 60

        for j in range(fullCycle):
            spaceJamClasses.Drone.droneCount += 1
            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)

            self.DrawCloudDefense(self.Planet2, nickName)
            self.DrawBaseballSeams(self.Planet1, nickName, j, fullCycle, 2)
            self.DrawCircleXDefense(self.Planet6, nickName, j, fullCycle, 3)
            self.DrawCircleYDefense(self.Spacestation, nickName, j, fullCycle, 10)
            self.DrawCircleZDefense(self.Planet5, nickName, j, fullCycle, 2)

    def SetCamera(self):
        self.disableMouse()
        self.camera.reparentTo(self.Ship.modelNode)
        self.camera.setFluidPos(0, 1, 0)
        self.Ship.SetKeyBindings()

    def DrawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        unitVec = defensePaths.BaseballSeams(step, numSeams, B = 0.4)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def DrawCloudDefense(self, centralObject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 500 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 10)

    def DrawCircleXDefense(self, centralObject, droneName, step, numDrones, radius = 1):
        unitVec = defensePaths.CircleX(step, numDrones, radius)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def DrawCircleYDefense(self, centralObject, droneName, step, numDrones, radius = 1):
        unitVec = defensePaths.CircleY(step, numDrones, radius)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def DrawCircleZDefense(self, centralObject, droneName, step, numDrones, radius = 1):
        unitVec = defensePaths.CircleZ(step, numDrones, radius)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)
        
app = MyApp()
app.SetupScene()
app.SetCamera()
app.run()

#credits: https://www.solarsystemscope.com/textures/ Solar System Scope - All 6 planets
#credits: https://www.pinterest.com/pin/207024914124205138/ BLINK_SOFT - The universe