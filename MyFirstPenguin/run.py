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

def chooseAction(body):
    action = PASS
    #bonusTiles = findBonusTiles(body) # Returns a dictionary with the power-ups as keys and an array of their coordinates as tuples i.g. bonusTiles["strength"] => [(1, 2), (7, 3)]
    #nearestCorner = findNearestCorner(body) # On the form (x, y, air_distance)        
    action = steek(body)
    
    
    return action

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

def inCorner(body):
    xValuePlayer = body["you"]["x"]
    yValuePlayer = body["you"]["y"]
    walls = body["walls"]
    horizontal = doesCellContainWall(walls, xValuePlayer - 1, yValuePlayer) or doesCellContainWall(walls, xValuePlayer + 1, yValuePlayer)
    vertical = doesCellContainWall(walls, xValuePlayer, yValuePlayer - 1) or doesCellContainWall(walls, xValuePlayer, yValuePlayer + 1)
    return horizontal and vertical

def findBonusTiles(body): 
    bonusTiles = {"strength": [], "weapon-power": [], "weapon-range": []}
    for bonus in body["bonusTiles"]:
        bonusTiles[bonus["type"]].append((bonus["x"], bonus["y"]))
    return bonusTiles

def findNearestCorner(body):
    xValuePlayer = body["you"]["x"]
    yValuePlayer = body["you"]["y"]
    top_left_distance = math.sqrt(xValuePlayer ** 2 + yValuePlayer ** 2)
    top_right_distance = math.sqrt((body["mapWidth"] - xValuePlayer) ** 2 + yValuePlayer ** 2)
    bottom_left_distance = math.sqrt(xValuePlayer ** 2 + (body["mapHeight"] - yValuePlayer) ** 2)
    bottom_right_distance = math.sqrt((body["mapWidth"] - xValuePlayer) ** 2 + (body["mapHeight"] - yValuePlayer) ** 2)
    choices = [(0, 0, top_left_distance), (body["mapWidth"], 0, top_right_distance), (0, body["mapHeight"], bottom_left_distance), (body["mapWidth"], body["mapHeight"], bottom_right_distance)]
    return choices.sort(key=lambda tup: tup[2])[0]

env = os.environ
req_params_query = env['REQ_PARAMS_QUERY']
responseBody = open(env['res'], 'w')

response = {}
returnObject = {}
if req_params_query == "info":
    returnObject["name"] = "Pingu"
    returnObject["team"] = "Team Python"
elif req_params_query == "command":    
    body = json.loads(open(env["req"], "r").read())
    returnObject["command"] = chooseAction(body)

response["body"] = returnObject
responseBody.write(json.dumps(response))
responseBody.close()

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

def steek(body):
    xValueEnemies = body["enemies"]["x"]
    yValueEnemies = body["enemies"]["y"]
    bodyDirectionE = body["enemies"]["direction"]
    WeaponrangeE = body["enemies"]["weaponRange"]
    
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
    
    if (bodyDirectionE == "top") and (xValuePlayer == xValueEnemies) and (0 < (yValueEnemies - yValuePlayer) <= WeaponrangeE):
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
        
    if (bodyDirectionE == "left") and (yValuePlayer == yValueEnemies) and (0 < (xValueEnemies - xValuePlayer) <= WeaponrangeE):
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
            
    if (bodyDirectionE == "right") and (yValuePlayer == yValueEnemies) and (0 < (xValuePlayer - xValueEnemies) <= WeaponrangeE):
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