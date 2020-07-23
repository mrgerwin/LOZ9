# pygame_functions

# Documentation at www.github.com/stevepaget/pygame_functions
# Report bugs at https://github.com/StevePaget/Pygame_Functions/issues


import pygame, math, sys, os
import random
from os import path
import base64

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()
spriteGroup = pygame.sprite.OrderedUpdates()
textboxGroup = pygame.sprite.OrderedUpdates()
gameClock = pygame.time.Clock()
musicPaused = False
hiddenSprites = pygame.sprite.OrderedUpdates()
screenRefresh = True
background = None

keydict = {"space": pygame.K_SPACE, "esc": pygame.K_ESCAPE, "up": pygame.K_UP, "down": pygame.K_DOWN,
           "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "return": pygame.K_RETURN,
           "a": pygame.K_a,
           "b": pygame.K_b,
           "c": pygame.K_c,
           "d": pygame.K_d,
           "e": pygame.K_e,
           "f": pygame.K_f,
           "g": pygame.K_g,
           "h": pygame.K_h,
           "i": pygame.K_i,
           "j": pygame.K_j,
           "k": pygame.K_k,
           "l": pygame.K_l,
           "m": pygame.K_m,
           "n": pygame.K_n,
           "o": pygame.K_o,
           "p": pygame.K_p,
           "q": pygame.K_q,
           "r": pygame.K_r,
           "s": pygame.K_s,
           "t": pygame.K_t,
           "u": pygame.K_u,
           "v": pygame.K_v,
           "w": pygame.K_w,
           "x": pygame.K_x,
           "y": pygame.K_y,
           "z": pygame.K_z,
           "1": pygame.K_1,
           "2": pygame.K_2,
           "3": pygame.K_3,
           "4": pygame.K_4,
           "5": pygame.K_5,
           "6": pygame.K_6,
           "7": pygame.K_7,
           "8": pygame.K_8,
           "9": pygame.K_9,
           "0": pygame.K_0}
screen = ""

base64dict = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7, "I":8, "J":9, "K":10, "L":11, "M":12, "N":13, "O":14, "P":15,
              "Q":16, "R":17, "S":18, "T":19, "U":20, "V":21, "W":22, "X":23, "Y":24, "Z":25, "a":26, "b":27, "c":28, "d":29, "e":30,
              "f":31, "g":32, "h":33, "i":34, "j":35, "k":36, "l":37, "m":38, "n":39, "o":40, "p":41, "q":42, "r":43, "s":44, "t":45, "u":46,
              "v":47, "w":48, "x":49, "y":50, "z":51, "0":52, "1":53, "2":54, "3":55, "4":56, "5":57, "6":58, "7":59, "8":60, "9":61, "+":62, "/":63}

class Background():
    """
    The Background class creates a background that does not interact with the sprites.  It can scroll.
    """
    def __init__(self):
        self.colour = pygame.Color("black")

    def setTiles(self, tiles):
        if type(tiles) is str:
            self.tiles = [[loadImage(tiles)]]
        elif type(tiles[0]) is str:
            self.tiles = [[loadImage(i) for i in tiles]]
        else:
            self.tiles = [[loadImage(i) for i in row] for row in tiles]
        self.stagePosX = 0
        self.stagePosY = 0
        self.tileWidth = self.tiles[0][0].get_width()
        self.tileHeight = self.tiles[0][0].get_height()
        screen.blit(self.tiles[0][0], [0, 0])
        self.surface = screen.copy()

    def scroll(self, x, y):
        self.stagePosX -= x
        self.stagePosY -= y
        col = (self.stagePosX % (self.tileWidth * len(self.tiles[0]))) // self.tileWidth
        xOff = (0 - self.stagePosX % self.tileWidth)
        row = (self.stagePosY % (self.tileHeight * len(self.tiles))) // self.tileHeight
        yOff = (0 - self.stagePosY % self.tileHeight)

        col2 = ((self.stagePosX + self.tileWidth) % (self.tileWidth * len(self.tiles[0]))) // self.tileWidth
        row2 = ((self.stagePosY + self.tileHeight) % (self.tileHeight * len(self.tiles))) // self.tileHeight
        screen.blit(self.tiles[row][col], [xOff, yOff])
        screen.blit(self.tiles[row][col2], [xOff + self.tileWidth, yOff])
        screen.blit(self.tiles[row2][col], [xOff, yOff + self.tileHeight])
        screen.blit(self.tiles[row2][col2], [xOff + self.tileWidth, yOff + self.tileHeight])

        self.surface = screen.copy()

    def setColour(self, colour):
        self.colour = parseColour(colour)
        screen.fill(self.colour)
        pygame.display.update()
        self.surface = screen.copy()

class Scene:
    """
    A Scene is a background that does interact with the sprites.  For instance
    there are walls that the sprites cannot pass through
    """
    def __init__(self, player, spriteSheetFileName, mapFileName, framesX=1, framesY=1):
        self.player = player
        spriteSheet = loadImage(spriteSheetFileName)
        self.originalWidth = spriteSheet.get_width() // framesX
        self.originalHeight = spriteSheet.get_height() // framesY
        frameSurf = pygame.Surface((self.originalWidth, self.originalHeight), pygame.SRCALPHA, 32)
        x = 0
        y = 0
        self.images = []
        for column in range(framesY):
            for frameNo in range(framesX):
                frameSurf = pygame.Surface((self.originalWidth, self.originalHeight), pygame.SRCALPHA, 32)
                frameSurf.blit(spriteSheet, (x, y))
                self.images.append(frameSurf.copy())
                x -= self.originalWidth
            y -=self.originalHeight
            x = 0
        #Other initialized parameters
        self.Wall_Tiles = []
        self.Ground_Tiles = []
        self.Enemies = []
        self.Projectiles = []
        self.Items=[]
        #Populate the lists
        game_folder = os.getcwd()
        map_data = []
        with open(path.join(game_folder, mapFileName), 'rt') as f:
            for line in f:
                map_data.append(line)
                
        i = 0
        for row, tiles in enumerate(map_data):
                for col, tile in enumerate(tiles):
                    if tile in base64dict:
                        thisWall = Wall(self.images[base64dict[tile]])
                        thisWall.move(col*32, row*32)
                        self.Wall_Tiles.append(thisWall)    
                    elif tile == "@":
                        enemy = Octorok()
                        enemy.rect.x=col*32
                        enemy.rect.y=row*32
                        self.Enemies.append(enemy)
                    if tile not in base64dict:
                        thisGround = Wall(self.images[2])
                        thisGround.move(col*32, row*32)
                        self.Ground_Tiles.append(thisGround)
        self.surface=screen.copy()
        background=self.surface
        #Methods for Scrolling the Scene
    def scroll(self, x, y):
        for enemy in self.Enemies:
            enemy.speed = 0
            hideSprite(enemy)
        for projectile in self.Projectiles:
            killSprite(projectile)
        self.Projectiles = []
        for item in self.Items:
            killSprite(item)
        self.Items = []
        for tile in self.all_wall_panels:
            tile.move(tile.rect.x+x, tile.rect.y+y)
        for tile in self.all_ground_tiles:
            tile.move(tile.rect.x+x, tile.rect.y+y)
class newSprite(pygame.sprite.Sprite):
    """
    The newSprite class is a abstract base class from which other sprites are made from
    """
    def __init__(self, filename, framesX=1, framesY=1):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        img = loadImage(filename)
        self.originalWidth = img.get_width() // framesX
        self.originalHeight = img.get_height() // framesY
        frameSurf = pygame.Surface((self.originalWidth, self.originalHeight), pygame.SRCALPHA, 32)
        x = 0
        y=0
        for Column in range(framesY):
            for frameNo in range(framesX):
                frameSurf = pygame.Surface((self.originalWidth, self.originalHeight), pygame.SRCALPHA, 32)
                frameSurf.blit(img, (x, y))
                self.images.append(frameSurf.copy())
                x -= self.originalWidth
            y -=self.originalHeight
            x=0
                #print(str(x))

        self.currentImage = 0
        self.image = pygame.Surface.copy(self.images[0])
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = 0
        self.scale = 1
        self.orientation = 0

    def addImage(self, filename, frames):
        img = loadImage(filename)
        self.originalWidth = img.get_width() // frames
        self.originalHeight = img.get_height()
        frameSurf = pygame.Surface((self.originalWidth, self.originalHeight), pygame.SRCALPHA, 32)
        x = 0
        for frameNo in range(frames):
            frameSurf = pygame.Surface((self.originalWidth, self.originalHeight), pygame.SRCALPHA, 32)
            frameSurf.blit(img, (x, 0))
            self.images.append(frameSurf.copy())
            x -= self.originalWidth
        self.image = pygame.Surface.copy(self.images[0])

    def move(self, xpos, ypos, centre=False):
        if centre:
            self.rect.center = [xpos, ypos]
        else:
            self.rect.topleft = [xpos, ypos]

    def changeImage(self, index):
        self.currentImage = index
        if self.angle == 0 and self.scale == 1:
            self.image = self.images[index]
        else:
            self.image = pygame.transform.rotozoom(self.images[self.currentImage], -self.angle, self.scale)
        oldcenter = self.rect.center
        self.rect = self.image.get_rect()
        originalRect = self.images[self.currentImage].get_rect()
        self.originalWidth = originalRect.width
        self.originalHeight = originalRect.height
        self.rect.center = oldcenter
        self.mask = pygame.mask.from_surface(self.image)
        if screenRefresh:
            updateDisplay()
            
#Note that Wall inherits from pygame sprite not newSprite
class Wall(pygame.sprite.Sprite):
    """
    Walls are Scene Objects that most sprites cannot pass through
    """
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (0,0)
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = 9
        self.scale = 1
        self.x = self.rect.x
        self.y = self.rect.y
    def move(self, xpos, ypos, centre=False):
        if centre:
            self.rect.center = [xpos, ypos]
        else:
            self.rect.topleft = [xpos, ypos]
#PUT PLAYER CLASS HERE

class Player(newSprite):
    """
    Player is a sprite that can be controlled by the user.
    """
    def __init__(self):
        newSprite.__init__(self, "LinkSimple.png", 14)
        playMusic()
        self.rect.x = 500
        self.rect.y = 350
        self.speed = 4
        self.health = 3
    
    def move(self, frame):
        if self.orientation == 0:
            self.rect.y = self.rect.y + self.speed
            self.changeImage(0*2 + frame)
        elif self.orientation ==1:
            self.rect.y = self.rect.y - self.speed
            self.changeImage(1*2 + frame)
        elif self.orientation ==2:
            self.rect.x = self.rect.x + self.speed
            self.changeImage(2*2 + frame)
        else:
            self.rect.x = self.rect.x - self.speed
            self.changeImage(3*2 + frame)
    def hit(self):
        self.rect.y += 32
        self.health -= 1
        playSound(link_hit)
        if self.health == 0:
            killSprite(self)
            stopMusic()
            playSound(link_die)
class Sword(newSprite):
    """
    Sword is a weapon used by the Player
    """
    def __init__(self, player):
        newSprite.__init__(self, "WoodSword.png", 4, 2)
        self.player = player
        self.step = 0
    
    def swing(self):
        if self.player.orientation ==0:
            self.changeImage(0 + self.step*4)
            self.move(self.player.rect.x, self.player.rect.y+32)
        elif self.player.orientation ==1:
            self.changeImage(1 + self.step*4)
            self.move(self.player.rect.x, self.player.rect.y-32)
        elif self.player.orientation ==2:
            self.changeImage(2 + self.step*4)
            self.move(self.player.rect.x+32, self.player.rect.y)
        elif self.player.orientation ==3:
            self.changeImage(3 + self.step*4)
            self.move(self.player.rect.x-32, self.player.rect.y)
        showSprite(self)
        self.step += 1
        if self.step == 2:
            self.step = 0
        playSound(sword_slash)
        
    
class Enemy(newSprite):
    """
    Enemy is a generic base class used by more specific enemies
    """
    def __init__(self, filename, framesX=1, framesY=1):
        newSprite.__init__(self, filename, framesX, framesY)
        self.speed = 3
        self.rect.x = 400
        self.rect.y = 400
        self.health = 1
    def move(self, frame):
        if self.orientation == 0:
            self.rect.y = self.rect.y + self.speed
            self.changeImage(0 + frame *4)
        elif self.orientation ==1:
            self.rect.y = self.rect.y - self.speed
            self.changeImage(2 + frame*4)
        elif self.orientation ==2:
            self.rect.x = self.rect.x + self.speed
            self.changeImage(3 + frame*4)
        else:
            self.rect.x = self.rect.x - self.speed
            self.changeImage(1 + frame*4)
    def turn(self):
        self.orientation += 1
        self.orientation = self.orientation % 4
    def hit(self):
        self.health -=1
        playSound(enemy_hit)
        if self.health == 0:
            killSprite(self)
            playSound(enemy_die)
            
class Octorok(Enemy):
    """
    Octorok is a specific enemy with health 2 and random movements
    """
    def __init__(self):
        Enemy.__init__(self,"Octorok.png", 4, 2)
        self.orientation = random.randint(0,3)
        self.step = 0
        self.health = 2
    def move(self, frame):
        if self.step == 25:
            self.speed = 0
            
        if self.step == 40:
            self.orientation = random.randint(0,3)
            self.speed = 3
            self.step = 0
        if self.orientation == 0:
            self.rect.y = self.rect.y + self.speed
            self.changeImage(0 + frame *4)
        elif self.orientation ==1:
            self.rect.y = self.rect.y - self.speed
            self.changeImage(2 + frame*4)
        elif self.orientation ==2:
            self.rect.x = self.rect.x + self.speed
            self.changeImage(3 + frame*4)
        else:
            self.rect.x = self.rect.x - self.speed
            self.changeImage(1 + frame*4)
        self.step += 1

class newTextBox(pygame.sprite.Sprite):
    """
    newTextBox is an object that is a input type text box
    """
    def __init__(self, text, xpos, ypos, width, case, maxLength, fontSize):
        pygame.sprite.Sprite.__init__(self)
        self.text = ""
        self.width = width
        self.initialText = text
        self.case = case
        self.maxLength = maxLength
        self.boxSize = int(fontSize * 1.7)
        self.image = pygame.Surface((width, self.boxSize))
        self.image.fill((255, 255, 255))
        pygame.draw.rect(self.image, (0, 0, 0), [0, 0, width - 1, self.boxSize - 1], 2)
        self.rect = self.image.get_rect()
        self.fontFace = pygame.font.match_font("Arial")
        self.fontColour = pygame.Color("black")
        self.initialColour = (180, 180, 180)
        self.font = pygame.font.Font(self.fontFace, fontSize)
        self.rect.topleft = [xpos, ypos]
        newSurface = self.font.render(self.initialText, True, self.initialColour)
        self.image.blit(newSurface, [10, 5])

    def update(self, keyevent):
        key = keyevent.key
        unicode = keyevent.unicode
        if key > 31 and key < 127 and (
                self.maxLength == 0 or len(self.text) < self.maxLength):  # only printable characters
            if keyevent.mod in (1, 2) and self.case == 1 and key >= 97 and key <= 122:
                # force lowercase letters
                self.text += chr(key)
            elif keyevent.mod == 0 and self.case == 2 and key >= 97 and key <= 122:
                self.text += chr(key - 32)
            else:
                # use the unicode char
                self.text += unicode

        elif key == 8:
            # backspace. repeat until clear
            keys = pygame.key.get_pressed()
            nexttime = pygame.time.get_ticks() + 200
            deleting = True
            while deleting:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_BACKSPACE]:
                    thistime = pygame.time.get_ticks()
                    if thistime > nexttime:
                        self.text = self.text[0:len(self.text) - 1]
                        self.image.fill((255, 255, 255))
                        pygame.draw.rect(self.image, (0, 0, 0), [0, 0, self.width - 1, self.boxSize - 1], 2)
                        newSurface = self.font.render(self.text, True, self.fontColour)
                        self.image.blit(newSurface, [10, 5])
                        updateDisplay()
                        nexttime = thistime + 50
                        pygame.event.clear()
                else:
                    deleting = False

        self.image.fill((255, 255, 255))
        pygame.draw.rect(self.image, (0, 0, 0), [0, 0, self.width - 1, self.boxSize - 1], 2)
        newSurface = self.font.render(self.text, True, self.fontColour)
        self.image.blit(newSurface, [10, 5])
        if screenRefresh:
            updateDisplay()

    def move(self, xpos, ypos, centre=False):
        if centre:
            self.rect.topleft = [xpos, ypos]
        else:
            self.rect.center = [xpos, ypos]

    def clear(self):
        self.image.fill((255, 255, 255))
        pygame.draw.rect(self.image, (0, 0, 0), [0, 0, self.width - 1, self.boxSize - 1], 2)
        newSurface = self.font.render(self.initialText, True, self.initialColour)
        self.image.blit(newSurface, [10, 5])
        if screenRefresh:
            updateDisplay()


class newLabel(pygame.sprite.Sprite):
    """
    newLabel is an object that displays text but does not allow input
    """
    def __init__(self, text, fontSize, font, fontColour, xpos, ypos, background):
        pygame.sprite.Sprite.__init__(self)
        self.text = text
        self.fontColour = parseColour(fontColour)
        self.fontFace = pygame.font.match_font(font)
        self.fontSize = fontSize
        self.background = background
        self.font = pygame.font.Font(self.fontFace, self.fontSize)
        self.renderText()
        self.rect.topleft = [xpos, ypos]

    def update(self, newText, fontColour, background):
        self.text = newText
        if fontColour:
            self.fontColour = parseColour(fontColour)
        if background:
            self.background = parseColour(background)

        oldTopLeft = self.rect.topleft
        self.renderText()
        self.rect.topleft = oldTopLeft
        if screenRefresh:
            updateDisplay()

    def renderText(self):
        lineSurfaces = []
        textLines = self.text.split("<br>")
        maxWidth = 0
        maxHeight = 0
        for line in textLines:
            lineSurfaces.append(self.font.render(line, True, self.fontColour))
            thisRect = lineSurfaces[-1].get_rect()
            if thisRect.width > maxWidth:
                maxWidth = thisRect.width
            if thisRect.height > maxHeight:
                maxHeight = thisRect.height
        self.image = pygame.Surface((maxWidth, (self.fontSize + 1) * len(textLines) + 5), pygame.SRCALPHA, 32)
        self.image.convert_alpha()
        if self.background != "clear":
            self.image.fill(parseColour(self.background))
        linePos = 0
        for lineSurface in lineSurfaces:
            self.image.blit(lineSurface, [0, linePos])
            linePos += self.fontSize + 1
        self.rect = self.image.get_rect()


def loadImage(fileName, useColorKey=False):
    """
    This function handles file names needed to load images
    """
    if os.path.isfile(fileName):
        image = pygame.image.load(fileName)
        image = image.convert_alpha()
        # Return the image
        return image
    else:
        raise Exception("Error loading image: " + fileName + " - Check filename and path?")


def screenSize(sizex, sizey, xpos=None, ypos=None, fullscreen=False):
    """
    This function makes new screens of a particular size
    """
    global screen
    global background
    if xpos != None and ypos != None:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (xpos, ypos + 50)
    else:
        windowInfo = pygame.display.Info()
        monitorWidth = windowInfo.current_w
        monitorHeight = windowInfo.current_h
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % ((monitorWidth - sizex) / 2, (monitorHeight - sizey) / 2)
    if fullscreen:
        screen = pygame.display.set_mode([sizex, sizey], pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode([sizex, sizey])
    background = Background()
    screen.fill(background.colour)
    pygame.display.set_caption("Graphics Window")
    background.surface = screen.copy()
    pygame.display.update()
    return screen


def moveSprite(sprite, x, y, centre=False):
    """
    This function moves sprites and updates the display
    """
    sprite.move(x, y, centre)
    if screenRefresh:
        updateDisplay()


def rotateSprite(sprite, angle):
    """
    This function has been deprecated
    """
    print("rotateSprite has been deprecated. Please use transformSprite")
    transformSprite(sprite, angle, 1)


def transformSprite(sprite, angle, scale, hflip=False, vflip=False):
    """
    This function is used to rotate, flip, and scale sprites
    """
    oldmiddle = sprite.rect.center
    if hflip or vflip:
        tempImage = pygame.transform.flip(sprite.images[sprite.currentImage], hflip, vflip)
    else:
        tempImage = sprite.images[sprite.currentImage]
    if angle != 0 or scale != 1:
        sprite.angle = angle
        sprite.scale = scale
        tempImage = pygame.transform.rotozoom(tempImage, -angle, scale)
    sprite.image = tempImage
    sprite.rect = sprite.image.get_rect()
    sprite.rect.center = oldmiddle
    sprite.mask = pygame.mask.from_surface(sprite.image)
    if screenRefresh:
        updateDisplay()


def killSprite(sprite):
    """
    This function kills sprites.  Do not forget to remove them
    from a list
    """
    sprite.kill()
    if screenRefresh:
        updateDisplay()


def setBackgroundColour(colour):
    """
    This function sets the background color however, background sprites will be drawn over it.
    """
    background.setColour(colour)
    if screenRefresh:
        updateDisplay()


def setBackgroundImage(img):
    """
    This function sets the bg image but bg sprites will be drawn overtop
    """
    global background
    background.setTiles(img)
    if screenRefresh:
        updateDisplay()


def hideSprite(sprite):
    """
    The function hides sprites.  Manages hidden sprites and sprite groups
    """
    hiddenSprites.add(sprite)
    spriteGroup.remove(sprite)
    if screenRefresh:
        updateDisplay()


def hideAll():
    """
    hides all sprites
    """
    hiddenSprites.add(spriteGroup.sprites())
    spriteGroup.empty()
    if screenRefresh:
        updateDisplay()


def unhideAll():
    """
    unhides all sprites
    """
    spriteGroup.add(hiddenSprites.sprites())
    hiddenSprites.empty()
    if screenRefresh:
        updateDisplay()


def showSprite(sprite):
    """
    Shows one sprite
    """
    spriteGroup.add(sprite)
    if screenRefresh:
        updateDisplay()

def showBackground(background):
    """
    Shows background sprites
    """
    for sprite in background.Wall_Tiles:
        showSprite(sprite)
        
    for sprite in background.Ground_Tiles:
        showSprite(sprite)

def makeSprite(filename, framesX=1, framesY=1 ):
    """
    Calls the newSprite constructor
    """
    thisSprite = newSprite(filename, framesX, framesY)
    return thisSprite


def addSpriteImage(sprite, image):
    """
    Calls the add image method from sprite class
    """
    sprite.addImage(image)


def changeSpriteImage(sprite, index):
    """
    Changes which image on the sprite sheet is used
    """
    sprite.changeImage(index)


def nextSpriteImage(sprite):
    """
    Just goes to the next sprite image on the sprite sheet
    """
    sprite.currentImage += 1
    if sprite.currentImage > len(sprite.images) - 1:
        sprite.currentImage = 0
    sprite.changeImage(sprite.currentImage)


def prevSpriteImage(sprite):
    """
    Just goes to the previous image on the sprite sheet
    """
    sprite.currentImage -= 1
    if sprite.currentImage < 0:
        sprite.currentImage = len(sprite.images) - 1
    sprite.changeImage(sprite.currentImage)


def makeImage(filename):
    """
    Same thing as loadImage
    """
    return loadImage(filename)


def touching(sprite1, sprite2):
    """
    Checks if two sprite are colliding
    """
    collided = pygame.sprite.collide_mask(sprite1, sprite2)
    return collided


def allTouching(spritename):
    """
    Returns a list of sprites that are colliding.  Or empty list if none are colliding
    """
    if spriteGroup.has(spritename):
        collisions = pygame.sprite.spritecollide(spritename, spriteGroup, False, collided=pygame.sprite.collide_mask)
        collisions.remove(spritename)
        return collisions
    else:
        return []


def pause(milliseconds, allowEsc=True):
    """
    updates display and then pauses game.  Clears out events.
    """
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()
    waittime = current_time + milliseconds
    updateDisplay()
    while not (current_time > waittime or (keys[pygame.K_ESCAPE] and allowEsc)):
        pygame.event.clear()
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_ESCAPE] and allowEsc):
            pygame.quit()
            sys.exit()
        current_time = pygame.time.get_ticks()


def drawRect(xpos, ypos, width, height, colour, linewidth=0):
    """
    Draws a Rectangle, does not return anything
    """
    global bgSurface
    colour = parseColour(colour)
    thisrect = pygame.draw.rect(screen, colour, [xpos, ypos, width, height], linewidth)
    if screenRefresh:
        pygame.display.update(thisrect)


def drawLine(x1, y1, x2, y2, colour, linewidth=1):
    """
    Draws a Line, does not return anything
    """
    global bgSurface
    colour = parseColour(colour)
    thisrect = pygame.draw.line(screen, colour, (x1, y1), (x2, y2), linewidth)
    if screenRefresh:
        pygame.display.update(thisrect)


def drawPolygon(pointlist, colour, linewidth=0):
    """
    Draws a Polygon, does not return anything
    """
    global bgSurface
    colour = parseColour(colour)
    thisrect = pygame.draw.polygon(screen, colour, pointlist, linewidth)
    if screenRefresh:
        pygame.display.update(thisrect)


def drawEllipse(centreX, centreY, width, height, colour, linewidth=0):
    """
    Draws an Oval, does not return anything
    """
    global bgSurface
    colour = parseColour(colour)
    thisrect = pygame.Rect(centreX - width / 2, centreY - height / 2, width, height)
    pygame.draw.ellipse(screen, colour, thisrect, linewidth)
    if screenRefresh:
        pygame.display.update(thisrect)


def drawTriangle(x1, y1, x2, y2, x3, y3, colour, linewidth=0):
    """
    Draws a Triangle, does not return anything
    """
    global bgSurface
    colour = parseColour(colour)
    thisrect = pygame.draw.polygon(screen, colour, [(x1, y1), (x2, y2), (x3, y3)], linewidth)
    if screenRefresh:
        pygame.display.update(thisrect)


def clearShapes():
    """
    Draws the background overtop the shapes
    """
    global background
    screen.blit(background.surface, [0, 0])
    if screenRefresh:
        updateDisplay()


def updateShapes():
    """
    redisplays everything on the screen
    """
    pygame.display.update()


def end():
    """
    Closes program
    """
    pygame.quit()


def makeSound(filename):
    """
    Loads in Sound File.  Returns Sound Object
    """
    pygame.mixer.init()
    thissound = pygame.mixer.Sound(filename)

    return thissound


def playSound(sound, loops=0):
    """
    Plays sound object.  Can loop.
    """
    sound.play(loops)


def stopSound(sound):
    """
    Stops sound object
    """
    sound.stop()


def playSoundAndWait(sound):
    """
    Plays sound; checks for events every 10 ms
    """
    sound.play()
    while pygame.mixer.get_busy():
        # pause
        pause(10)


def makeMusic(filename):
    """
    Loads mp3, returns music object
    """
    pygame.mixer.music.load(filename)


def playMusic(loops=0):
    """
    Plays music object.  Can Loop
    """
    global musicPaused
    if musicPaused:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.play(loops)
    musicPaused = False


def stopMusic():
    """
    Stops music object. Rewinds it
    """
    pygame.mixer.music.stop()


def pauseMusic():
    """
    Stops music object. Doesn't rewind
    """
    global musicPaused
    pygame.mixer.music.pause()
    musicPaused = True


def rewindMusic():
    """
    rewinds music object. 
    """
    pygame.mixer.music.rewind()


def endWait():
    """
    Allows proper closing of the program if esc key is pressed
    """
    updateDisplay()
    print("Press ESC to quit")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == keydict["esc"]):
                waiting = False
    pygame.quit()
    exit()



def keyPressed(keyCheck=""):
    """
    Checks if certain key pressed event occurred
    """
    global keydict
    keys = pygame.key.get_pressed()
    if sum(keys) > 0:
        if keyCheck == "" or keys[keydict[keyCheck.lower()]]:
            return True
    return False


def makeLabel(text, fontSize, xpos, ypos, fontColour='black', font='Arial', background="clear"):
    """
    Makes a text sprite
    """
    thisText = newLabel(text, fontSize, font, fontColour, xpos, ypos, background)
    return thisText


def moveLabel(sprite, x, y):
    """
    Moves a text sprite
    """
    sprite.rect.topleft = [x, y]
    if screenRefresh:
        updateDisplay()


def changeLabel(textObject, newText, fontColour=None, background=None):
    """
    Makes changes to a text sprite
    """
    textObject.update(newText, fontColour, background)
    # updateDisplay()


def waitPress():
    """
    Program halts until key is pressed.
    returns the key pressed
    """
    pygame.event.clear()
    keypressed = False
    thisevent = pygame.event.wait()
    while thisevent.type != pygame.KEYDOWN:
        thisevent = pygame.event.wait()
    return thisevent.key


def makeTextBox(xpos, ypos, width, case=0, startingText="Please type here", maxLength=0, fontSize=22):
    """
    makes textbox object
    """
    thisTextBox = newTextBox(startingText, xpos, ypos, width, case, maxLength, fontSize)
    textboxGroup.add(thisTextBox)
    return thisTextBox


def textBoxInput(textbox, functionToCall=None, args=[]):
    """
    starts grabbing key inputs, putting into textbox until enter pressed
    """
    global keydict
    textbox.text = ""
    returnVal = None
    while True:
        updateDisplay()
        if functionToCall:
            returnVal = functionToCall(*args)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    textbox.clear()
                    if returnVal:
                        return textbox.text, returnVal
                    else:
                        return textbox.text
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    textbox.update(event)
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def clock():
    """
    Returns how many ticks have occurred
    """
    current_time = pygame.time.get_ticks()
    return current_time


def tick(fps):
    """
    Checks if esc key was pressed and then does tick event.
    returns fps
    """
    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN and event.key == keydict["esc"]) or event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    gameClock.tick(fps)
    return gameClock.get_fps()


def showLabel(labelName):
    """
    shows label sprite
    """
    textboxGroup.add(labelName)
    if screenRefresh:
        updateDisplay()


def hideLabel(labelName):
    """
    hides label sprite
    """
    textboxGroup.remove(labelName)
    if screenRefresh:
        updateDisplay()


def showTextBox(textBoxName):
    """
    shows textbox sprite
    """
    textboxGroup.add(textBoxName)
    if screenRefresh:
        updateDisplay()


def hideTextBox(textBoxName):
    """
    hides textbox sprite
    """
    textboxGroup.remove(textBoxName)
    if screenRefresh:
        updateDisplay()


def updateDisplay():
    """
    draws all visible sprites and text objects
    """
    global background
    spriteRects = spriteGroup.draw(screen)
    textboxRects = textboxGroup.draw(screen)
    pygame.display.update()
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_ESCAPE]):
        pygame.quit()
        sys.exit()
    spriteGroup.clear(screen, background.surface)
    textboxGroup.clear(screen, background.surface)


def mousePressed():
    """
    Returns true or false.  Was the mouse clicked?
    """
    mouseState = pygame.mouse.get_pressed()
    if mouseState[0]:
        return True
    else:
        return False


def spriteClicked(sprite):
    """
    Returns true or false.  Was the sprite clicked?
    """
    
    mouseState = pygame.mouse.get_pressed()
    if not mouseState[0]:
        return False  # not pressed
    pos = pygame.mouse.get_pos()
    if sprite.rect.collidepoint(pos):
        return True
    else:
        return False


def parseColour(colour):
    """
    returns white color if given an invalid pygame color
    """
    if type(colour) == str:
        # check to see if valid colour
        return pygame.Color(colour)
    else:
        colourRGB = pygame.Color("white")
        colourRGB.r = colour[0]
        colourRGB.g = colour[1]
        colourRGB.b = colour[2]
        return colourRGB


def mouseX():
    """
    Gets X position of mouse
    """
    x = pygame.mouse.get_pos()
    return x[0]


def mouseY():
    """
    Gets Y position of mouse
    """
    y = pygame.mouse.get_pos()
    return y[1]


def scrollBackground(x, y):
    """
    Only works if background is set as a color or image.  Does not move bg sprites
    """
    global background
    background.scroll(x, y)


def setAutoUpdate(val):
    """
    Sets when screenRefreshes occur
    """
    global screenRefresh
    screenRefresh = val

def setIcon(iconfile):
    """
    Can change the icon in the pygame window
    """
    gameicon = pygame.image.load(iconfile)
    pygame.display.set_icon(gameicon)

def setWindowTitle(string):
    """
    Sets title for pygame window
    """
    pygame.display.set_caption(string)

link_die = makeSound("LOZ_Link_Die.wav")
link_hit = makeSound("LOZ_Link_Hurt.wav")
enemy_die = makeSound("LOZ_Enemy_Die.wav")
enemy_hit = makeSound("LOZ_Enemy_Hit.wav")
sword_slash = makeSound("LOZ_Sword_Slash.wav")
music = makeMusic("linkMusic.mp3")


if __name__ == "__main__":
    print(""""pygame_functions is not designed to be run directly.
    See the wiki at https://github.com/StevePaget/Pygame_Functions/wiki/Getting-Started for more information""")
