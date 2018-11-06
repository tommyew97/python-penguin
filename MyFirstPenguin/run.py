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
    if standOf(body):
        action = SHOOT
    return action

def standOf(body):
    xValuePlayer = body["you"]["x"]
    yValuePlayer = body["you"]["y"]
    bodyDirection = body["you"]["direction"]

    for enemy in body["enemies"]:
        if bodyDirection == "top":
            return abs((yValuePlayer - enemy["y"])) < 6
        elif bodyDirection == "bottom":
            return abs((enemy["y"] - yValuePlayer)) < 6
        elif bodyDirection == "left":
            return abs((xValuePlayer - enemy["y"])) < 6
        elif bodyDirection == "right":
            return abs((enemy["y"] - xValuePlayer)) < 6
    return False

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