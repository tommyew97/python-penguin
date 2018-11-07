import os
import json
import random
import math

ROTATE_LEFT = "rotate-left"
ROTATE_RIGHT = "rotate-right"
ADVANCE = "advance"
RETREAT = "retreat"
SHOOT = "shoot"
PASS = "pass"

MOVE_UP =  {"top" : ADVANCE, "bottom" : ROTATE_LEFT, "right" : ROTATE_LEFT ,"left" : ROTATE_RIGHT }
MOVE_DOWN =  {"top" : ROTATE_LEFT, "bottom" : ADVANCE, "right" : ROTATE_RIGHT ,"left" : ROTATE_LEFT }
MOVE_RIGHT = {"top" : ROTATE_RIGHT, "bottom" : ROTATE_LEFT, "right" : ADVANCE ,"left" : ROTATE_LEFT }
MOVE_LEFT = {"top" : ROTATE_LEFT, "bottom" : ROTATE_RIGHT, "right" : ROTATE_RIGHT,"left" : ADVANCE }

# --------------- Find/test-methods ---------------
def doesCellContainWall(walls, x, y):
    for wall in walls:
        if wall["x"] == x and wall["y"] == y:
            return True
    return False


def wallInFrontOfPenguin(body):
    xValueToCheckForWall = body["you"]["x"]
    yValueToCheckForWall = body["you"]["y"]
    bodyDirection = body["you"]["direction"]

    if bodyDirection == "top":
        yValueToCheckForWall -= 1
    elif bodyDirection == "bottom":
        yValueToCheckForWall += 1
    elif bodyDirection == "left":
        xValueToCheckForWall -= 1
    elif bodyDirection == "right":
        xValueToCheckForWall += 1
    return doesCellContainWall(body["walls"], xValueToCheckForWall, yValueToCheckForWall)


def wallBehindPenguin(body):
    xValueToCheckForWall = body["you"]["x"]
    yValueToCheckForWall = body["you"]["y"]
    bodyDirection = body["you"]["direction"]

    if bodyDirection == "top":
        yValueToCheckForWall += 1
    elif bodyDirection == "bottom":
        yValueToCheckForWall -= 1
    elif bodyDirection == "left":
        xValueToCheckForWall += 1
    elif bodyDirection == "right":
        xValueToCheckForWall -= 1
    return doesCellContainWall(body["walls"], xValueToCheckForWall, yValueToCheckForWall)


def inCorner(body):
    xValuePlayer = body["you"]["x"]
    yValuePlayer = body["you"]["y"]
    walls = body["walls"]
    if xValuePlayer == 0 and yValuePlayer ==0:
        return True
    elif (xValuePlayer, yValuePlayer) == (body["mapWidth"] - 1, 0):
        return True
    elif (xValuePlayer, yValuePlayer) == (0, body["mapWidth"] - 1):
        return True
    elif (xValuePlayer, yValuePlayer) == (body["mapWidth"] - 1, body["mapWidth"] - 1):
        return True
    else:
        return False


def standOf(body):
    bodyDirection = body["you"]["direction"]
    xValuePlayer = body["you"]["x"]
    yValuePlayer = body["you"]["y"]
    weaponRangePlayer = body["you"]["weaponRange"]

    for enemy in body["enemies"]:
        if enemy["x"] == xValuePlayer:
            if bodyDirection == "top":
                return 0 < yValuePlayer - enemy["y"] <= weaponRangePlayer
            elif bodyDirection == "bottom":
                return 0 < yValuePlayer - enemy["y"] <= weaponRangePlayer
        elif enemy["y"] == yValuePlayer:
            if bodyDirection == "left":
                return 0 < xValuePlayer - enemy["x"] <= weaponRangePlayer
            elif bodyDirection == "right":
                return 0 < enemy["y"] - xValuePlayer <= weaponRangePlayer
    return False


def findBonusTiles(body): 
    bonusTiles = {"strength": [], "weapon-power": [], "weapon-range": []}
    for bonus in body["bonusTiles"]:
        bonusTiles[bonus["type"]].append((bonus["x"], bonus["y"]))
    del bonusTiles['strength']
    return bonusTiles


def findNearestCorner(body):
    xValuePlayer = body["you"]["x"]
    yValuePlayer = body["you"]["y"]
    top_left_distance = math.sqrt(xValuePlayer ** 2 + yValuePlayer ** 2)
    top_right_distance = math.sqrt((body["mapWidth"] - 1 - xValuePlayer) ** 2 + yValuePlayer ** 2)
    bottom_left_distance = math.sqrt(xValuePlayer ** 2 + (body["mapHeight"] - 1 - yValuePlayer) ** 2)
    bottom_right_distance = math.sqrt((body["mapWidth"] - 1 - xValuePlayer) ** 2 + (body["mapHeight"] - 1 - yValuePlayer) ** 2)
    choices = [(0, 0, top_left_distance), (body["mapWidth"] - 1, 0, top_right_distance), (0, body["mapHeight"] - 1, bottom_left_distance), (body["mapWidth"] - 1, body["mapHeight"] - 1, bottom_right_distance)]
    return sorted(choices, key=lambda tup: tup[2])[0]


def nearestBonusTiles(body):
    tiles = findBonusTiles(body)
    youX = body["you"]["x"]
    youY = body["you"]["y"]
    x = 100
    for key in tiles:
        if len(tiles[key]) > 0:
            tup = tiles[key]
            avstand = (abs(tup[0] - youX) + abs(tup[1] - youY))
            if avstand < x:
                x = avstand
                minst = tup
    return minst

# --------------- Move-methods ---------------
def moveTowardsBonusTiles(body):
    (x, y) = nearestBonusTiles(body)
    return moveTowardsPoint(body, x, y)


def moveTowardsPoint(body, pointX, pointY):
    penguinPositionX = body["you"]["x"]
    penguinPositionY = body["you"]["y"]
    plannedAction = PASS
    bodyDirection = body["you"]["direction"]

    if penguinPositionX < pointX:
        plannedAction =  MOVE_RIGHT[bodyDirection]
    elif penguinPositionX > pointX:
        plannedAction = MOVE_LEFT[bodyDirection]
    elif penguinPositionY < pointY:
        plannedAction = MOVE_DOWN[bodyDirection]
    elif penguinPositionY > pointY:
        plannedAction = MOVE_UP[bodyDirection]

    if plannedAction == ADVANCE and wallInFrontOfPenguin(body):
        plannedAction = SHOOT
    return plannedAction

def moveTowardsCenterOfMap(body):
    centerPointX = math.floor(body["mapWidth"] / 2)
    centerPointY = math.floor(body["mapHeight"] / 2)
    return moveTowardsPoint(body, centerPointX, centerPointY)


def moveTowardsNearestCorner(body):
    (xCorner, yCorner, distance) = findNearestCorner(body)
    return moveTowardsPoint(body, xCorner, yCorner)


def turnFromCorner(body):
    penguinPositionX = body["you"]["x"]
    penguinPositionY = body["you"]["y"]
    bodyDirectionP = body["you"]["direction"]

    if (penguinPositionX, penguinPositionY) == (0, 0):
        if bodyDirectionP == "top":
            return ROTATE_RIGHT
        if bodyDirectionP == "left":
            return  ROTATE_LEFT
    if (penguinPositionX, penguinPositionY) == (body["mapWidth"] - 1, 0):
        if bodyDirectionP == "top":
            return ROTATE_LEFT
        if bodyDirectionP == "right":
            return ROTATE_RIGHT
    if (penguinPositionX, penguinPositionY) == (0, body["mapWidth"] - 1):
        if bodyDirectionP == "bottom":
            return ROTATE_LEFT
        if bodyDirectionP == "left":
            return ROTATE_RIGHT
    if (penguinPositionX, penguinPositionY) == (body["mapWidth"] - 1, body["mapWidth"] - 1):
        if bodyDirectionP == "bottom":
            return ROTATE_RIGHT
        if bodyDirectionP == "right":
            return ROTATE_LEFT
    return turnTowardsEnemy(body)

def turnTowardsEnemy(body):
    plannedAction = SHOOT
    xValuePlayer = body["you"]["x"]
    yValuePlayer = body["you"]["y"]
    bodyDirectionP = body["you"]["direction"]

    for enemy in body["enemies"]:
        dx = abs(xValuePlayer-enemy["x"])
        dy = abs(yValuePlayer-enemy["y"])

        if (xValuePlayer, yValuePlayer) == (0, 0):
            if dx < dy:
                plannedAction = SHOOT if bodyDirectionP == "bottom" else ROTATE_LEFT
            else: 
                plannedAction = SHOOT if bodyDirectionP == "right" else ROTATE_RIGHT
        if (xValuePlayer, yValuePlayer) == (body["mapWidth"] - 1, 0):
            if dx < dy:
                plannedAction = SHOOT if bodyDirectionP == "bottom" else ROTATE_LEFT
            else: 
                plannedAction = SHOOT if bodyDirectionP == "left" else ROTATE_RIGHT
        if (xValuePlayer, yValuePlayer) == (0, body["mapWidth"] - 1):
            if dx < dy:
                plannedAction = SHOOT if bodyDirectionP == "top" else ROTATE_LEFT
            else: 
                plannedAction = SHOOT if bodyDirectionP == "right" else ROTATE_RIGHT
        if (xValuePlayer, yValuePlayer) == (body["mapWidth"] - 1, body["mapWidth"] - 1):
            if dx < dy:
                plannedAction = SHOOT if bodyDirectionP == "left" else ROTATE_LEFT
            else: 
                plannedAction = SHOOT if bodyDirectionP == "top" else ROTATE_RIGHT
        return plannedAction


def steek(body):
    for enemy in body["enemies"]:
        xValueEnemies = enemy["x"]
        yValueEnemies = enemy["y"]
        bodyDirectionE = enemy["direction"]
        WeaponrangeE = enemy["weaponRange"]
    
        xValuePlayer = body["you"]["x"]
        yValuePlayer = body["you"]["y"]
        bodyDirectionP = body["you"]["direction"]
    
        if (bodyDirectionE == "bottom") and (xValuePlayer == xValueEnemies) and (0 < (yValuePlayer - yValueEnemies) <= WeaponrangeE):
            if bodyDirectionP == "left" or "right":
                if wallInFrontOfPenguin(body) == False:
                    return ADVANCE
                elif wallBehindPenguin(body) == False:
                    return RETREAT
                else:
                    if bodyDirectionP == "left":
                        return ROTATE_RIGHT
                    else:
                        return ROTATE_LEFT
            if bodyDirectionP == "bottom":
                if wallInFrontOfPenguin(body) == False:
                    return ADVANCE
                else:
                    return ROTATE_LEFT
    
        elif (bodyDirectionE == "top") and (xValuePlayer == xValueEnemies) and (0 < (yValueEnemies - yValuePlayer) <= WeaponrangeE):
            if bodyDirectionP == "left" or "right":
                if wallInFrontOfPenguin(body) == False:
                    return ADVANCE
                elif wallBehindPenguin(body) == False:
                    return RETREAT
                else:
                    if bodyDirectionP == "left":
                        return ROTATE_LEFT
                    else:
                        return ROTATE_RIGHT
            if bodyDirectionP == "top":
                if wallInFrontOfPenguin(body) == False:
                    return ADVANCE
                else:
                    return ROTATE_LEFT
        
        elif (bodyDirectionE == "left") and (yValuePlayer == yValueEnemies) and (0 < (xValueEnemies - xValuePlayer) <= WeaponrangeE):
            if bodyDirectionP == "top" or "bottom":
                if wallInFrontOfPenguin(body) == False:
                    return ADVANCE
                elif wallBehindPenguin(body) == False:
                    return RETREAT
                else:
                    if bodyDirectionP == "top":
                        return ROTATE_RIGHT
                    else:
                        return ROTATE_LEFT
            if bodyDirectionP == "left":
                if wallInFrontOfPenguin(body) == False:
                    return ADVANCE
                else:
                    return ROTATE_LEFT
            
        elif (bodyDirectionE == "right") and (yValuePlayer == yValueEnemies) and (0 < (xValuePlayer - xValueEnemies) <= WeaponrangeE):
            if bodyDirectionP == "top" or "bottom":
                if wallInFrontOfPenguin(body) == False:
                    return ADVANCE
                elif wallBehindPenguin(body) == False:
                    return RETREAT
                else:
                    if bodyDirectionP == "bottom":
                        return ROTATE_RIGHT
                    else:
                        return ROTATE_LEFT
            if bodyDirectionP == "right":
                if wallInFrontOfPenguin(body) == False:
                    return ADVANCE
                else:
                    return ROTATE_LEFT

# --------------- Main-method ---------------
def chooseAction(body):  
    if inCorner(body):
        print("In corner")
        action = turnFromCorner(body)
    else:
        print("Not in corner")
        action = moveTowardsNearestCorner(body)
    # action = moveTowardsBonusTiles(body)
    # action = steek(body)
    return action

env = os.environ
req_params_query = env['REQ_PARAMS_QUERY']
responseBody = open(env['res'], 'w')

response = {}
returnObject = {}
if req_params_query == "info":
    returnObject["name"] = "Pingu"
    returnObject["team"] = "Error 500"
elif req_params_query == "command":    
    body = json.loads(open(env["req"], "r").read())
    returnObject["command"] = chooseAction(body)

response["body"] = returnObject
responseBody.write(json.dumps(response))
responseBody.close()
