from pygame_functions7 import *

screenSize(1024,768)
setAutoUpdate(False)
link = Player()
sword = Sword(link)

scene1 = Scene(link, "ZeldaMapTilesBrown.png", "map.txt", 6,8)
showBackground(scene1)

showSprite(link)
for enemy in scene1.Enemies:
    showSprite(enemy)

nextFrame = clock()
frame = 0

while True:
    if clock() >nextFrame:
        frame= (frame + 1)%2
        nextFrame += 80
        pause(10)
        
        for wall in scene1.Wall_Tiles:
            if touching(wall, link):
                link.speed = -link.speed
                link.move(frame)
                link.speed = - link.speed
        
        if keyPressed("down"):
            
            link.orientation =0
            link.move(frame)
        elif keyPressed("up"):
            link.orientation =1
            link.move(frame)
        elif keyPressed("right"):
            link.orientation =2
            link.move(frame)
        elif keyPressed("left"):
            link.orientation =3
            link.move(frame)
        elif keyPressed("space"):
            changeSpriteImage(link, link.orientation + 8)
        #Sword Swing Code
            sword.swing()
            for enemy in scene1.Enemies:
                if touching(sword, enemy):
                    enemy.hit()
        if not keyPressed("space") or keyPressed("left") or keyPressed("right") or keyPressed("up") or keyPressed("down"):
            hideSprite(sword)
        if keyPressed("h"):
            changeSpriteImage(link, frame+12)
        
        for enemy in scene1.Enemies:
            enemy.move(frame)            
            if touching(enemy, link):
                link.hit()
            for wall in scene1.Wall_Tiles:
                if touching(enemy, wall):
                    enemy.turn()
        updateDisplay()

endWait()