from tkinter import *
import tkinter.messagebox
import tkinter.simpledialog
import numpy as np
import copy

def init(data):
    #initialize screen
    data.screen = "splashScreen"; data.grid = []; data.created= False
    data.choices = []; data.tempDict = dict(); data.currentType = None
    data.currentX, data.currentY = None,None; data.connected = dict()
    data.source= []; data.resistor= []; data.wire = []; data.ground = []
    #initialize node connected
    data.startX,data.startY = None,None; data.reverseConnected = dict()
    data.nodeRow,data.nodeCol = None, None; data.forwardConnected= dict()
    data.selected = None; data.changed = None; data.hover = None;
    data.unknown = 1; data.hoverX,data.hoverY = None,None; data.rows = 30
    data.node = []; data.currEq= []; data.currConstant = [];data.cols=35
    #initialize solving data
    data.voltConstant=[]; data.solution = None; data.unknownNode = []
    #buttons
    data.splashButton = [(data.width/2,data.height/2+10*10*2,"Solve a Circuit"),
                (data.width/2,data.height/2+10*10*2+10*10,"Instructions")]
    data.solveButton= [(data.width-10*10*2-10*10/2,10*10/2,"New Circuit"),
(data.width-10*10-10*10/2,10*10/2,"Help"),(data.width-10*10/2,10*10/2,"Exit"),
(data.width-10*10*(2+2+1)-10*2,10*10/2,"Solve"),
        (data.width-10*10*2*2+10*2,10*10/2,"Demo")]
    data.instructionButton = (data.width-10*10,10*10/2,"Exit")
    data.needToSolve= None; data.circleDir = []; data.demo = False
    data.multiply=0;data.circleCreated=False;data.storeX,data.storeY=None,None

#when user hovers over an element
def mouseMotion(event,data):
    canvas = event.widget.canvas
    for element in data.resistor+data.source:
        x0,y0,x1,y1 = getBound(element)
        #check boundary
        if x0<=event.x<=x1 and y0<=event.y<=y1:
            data.hover = element
            data.hoverX,data.hoverY = event.x, event.y; return
    data.hover = None

#splash screen buttons
def hitSplashButton(event,data):
    for button in data.splashButton:
        (cx,cy,text) = button
        #when users chooses to solve a circuit
        if text == "Solve a Circuit":
            width,height = 634,55
            x0,y0,x1,y1 = cx-width/2,cy-height/2,cx+width/2,cy+height/2
            if x0<=event.x<=x1 and y0<=event.y<=y1:
                data.screen = "solveScreen"; return True
        #when user hits instructions
        elif text == "Instructions":
            width,height = 606,54
            x0,y0,x1,y1 = cx-width/2,cy-height/2,cx+width/2,cy+height/2
            if x0<=event.x<=x1 and y0<=event.y<=y1:
                data.screen = "instructionScreen"; return True
    return False

#react to the user clicking on buttons
def checkButton(width,height,cx,cy,text,event,data):
    x0,y0,x1,y1 = cx-width/2,cy-height/2,cx+width/2,cy+height/2
    if x0<=event.x<=x1 and y0<=event.y<=y1:
        #buttons in solve screen
        if text == "New Circuit": init(data); data.screen = "solveScreen"
        elif text == "Exit": data.screen = "splashScreen"; data.selected = None
        elif text == "Solve": solve(data)
        elif text == "Help": data.screen = "helpScreen"
        elif text == "Demo": data.demo = True
        return True
    else: return False

#check if user hits a button in solve screen
def hitSolveButton(event,data):
    for button in data.solveButton:
        (cx,cy,text)=button
        # different button size
        if text == "New Circuit": width,height = 94,53
        elif text == "Exit": width,height = 80,52
        elif text== "Solve": width,height = 128,57
        elif text== "Help": width,height = 97,55
        elif text == "Demo": width,height = 130,53
        #check if hit a button
        hit = checkButton(width,height,cx,cy,text,event,data)
        if hit: return True
    if data.demo: checkDemoSpeed(event,data)
    return False

#check if users want to change demo speed
def checkDemoSpeed(event,data):
    leftRectX,leftRectY = data.width-10*10*2*2+10*2-10*10/2-10*10/2,10*10
    rightRectX,rightRectY = data.width-10*10*2*2+10*2+10*10/2+10*10/2,10*10
    #decrease speed
    if leftRectX-10<=event.x<=leftRectX+10 and leftRectY-10<=event.y<= \
    leftRectY+10:
        data.multiply -= 1
        for circle in data.circleDir: circle.speedX /=2; circle.speedY /=2
    #increase speed
    elif rightRectX-10<=event.x<=rightRectX+10 and rightRectY-10<=event.y<=\
         rightRectY+10:
        data.multiply += 1
        for circle in data.circleDir: circle.speedX *=2; circle.speedY *=2

#general mouse pressed
def leftMousePressed(event,data):
    #different screens
    if data.screen== "splashScreen":
        hit = hitSplashButton(event,data)
        #splash screen buttons
        if hit: return
    elif data.screen == "solveScreen":
        #solve screen buttons
        hit = hitSolveButton(event,data)
        if hit: return
        solveLeftMousePressed(event,data)
        return
    elif data.screen == "instructionScreen":
        cx,cy, text = data.instructionButton
        width,height = 80,52
        x0,y0,x1,y1 = cx-width/2,cy-height/2,cx+width/2,cy+height/2
        #instruction screen buttons
        if x0<=event.x<=x1 and y0<=event.y<=y1:
            data.screen = "splashScreen"; data.selected = None; return
    elif data.screen == "helpScreen":
        cx,cy, text = data.instructionButton; width,height = 80,52
        x0,y0,x1,y1 = cx-width/2,cy-height/2,cx+width/2,cy+height/2
        #help screen buttons
        if x0<=event.x<=x1 and y0<=event.y<=y1:
            data.screen = "solveScreen"; return         

#get bound for each element        
def getBound(element):
    size = 28; length= 30; width= 15
    #check the boundary of each element
    if type(element) == Source:
        cx = element.x; cy = element.y
        return cx-size,cy-size,cx+size,cy+size
    #resistor
    elif type(element) == Resistor:
        cx = element.x; cy = element.y
        if element.input.col == element.output.col:
            return cx-width,cy-length,cx+width,cy+length
        else:
            return cx-length,cy-width,cx+length,cy+width
    #ground
    elif type(element) == Ground:
        cx = element.x; cy= element.y
        return cx-10*2,cy,cx+10*2,cy+10*2+10
        
#mouse pressed in solve screen
def solveLeftMousePressed(event,data):
    global canvas; canvas = event.widget.canvas
    #check if user selects a existing element
    for element in data.resistor+data.source+data.ground:
        x0,y0,x1,y1 = getBound(element)
        if x0<=event.x<=x1 and y0<=event.y<=y1: data.selected = element;return
    #check if user selects a wire
    for wire in data.wire:
        if wire.endY<=wire.startY: y1=wire.startY; y0=wire.endY
        else: y1 =wire.endY; y0=wire.startY
        if wire.endX<=wire.startX: x1=wire.startX; x0=wire.endX
        else: x1=wire.endX; x0=wire.startX
        if (wire.startX-10/2<=event.x<=wire.startX+10/2 and y0<=event.y<=y1) \
    or (wire.endY-10/2<=event.y<=wire.endY+10/2 and x0<=event.x<=x1):
            data.selected = wire; return
    #check if users selects a new element
    if pickElement(event,data): return
    checkStartWire(event,data)

#check if user wants to connect a wire
def checkStartWire(event,data):
    cols = 35; rows = 30
    if 10*10/2-10<=event.x<=10*10/2+cols*10*2+10 and \
       10*10+10*10/2-10<=event.y<=10*10+10*10/2+10*2*rows+10:
        #set current type
        data.currentType = "Wire"; closest = None; setX,setY = None,None
        for position in data.grid:
            (x,y) = position
            if closest == None or \
                    ((event.x-x)**2+(event.y-y)**2)**0.5<=closest:
                setX=x;setY=y; closest = ((event.x-x)**2+(event.y-y)**2)**0.5
        #set start position
        data.startX = setX; data.startY = setY; return
    
#check if user picks any new element
def pickElement(event,data):
    width = 45
    #loop through choices
    for choice in data.choices:
        (cx,cy,elemType) = choice
        if cx-width<=event.x<=cx+width and cy-width<=event.y<=2*cy+10*2:
            #stop demoing
            data.demo = False; data.circleCreated = False
            while len(data.circleDir)>0: data.circleDir.pop()
            data.currentType = elemType
            if data.currentType == "Wire": return
            else: data.currentX,data.currentY = event.x,event.y
            return True
    return False

#check if user drags the element
def leftMouseMoved(event,data):
    if data.screen == "splashScreen": return
    global canvas
    if data.currentType == None: return
    #record current position
    canvas = event.widget.canvas
    data.currentX,data.currentY = event.x,event.y

#get the closest point on the grid
def getPoint(event,data):
    closest = None; setX,setY = None,None
    #loop through the nodes on the grid
    for position in data.grid:
        (x,y) = position
        if closest == None or ((event.x-x)**2+(event.y-y)**2)**0.5<=closest:
            setX = x; setY = y; closest = ((event.x-x)**2+(event.y-y)**2)**0.5
    return setX,setY

#if user wants to change value
def changeValue(data,value):
    for element in data.source+data.resistor:
        #change the value of the selected element
        if element == data.selected:
            element.value = value
            #determine type
            if element.elemType == "Voltage Source":
                element.voltage = value
            elif element.elemType == "Current Source":
                element.current = value
            return

#get the value user input
def getValue(data):
    if (data.currentType==None and data.selected != None):
        #show a dialog
        value = showDialog(canvas,data.selected.elemType)
        if value == None: return
        else: changeValue(data,value); return
    if (data.currentType== "Voltage Source" or \
       data.currentType=="Current Source" or data.currentType == "Resistor"):
        value = showDialog(canvas,data.currentType)
        #if user does not input value
        if value == None:
            data.currentType=None;data.currentX,data.currentY=None,None
            return False
    #return value
        else: return value
    return None

#drop an element
def leftMouseReleased(event,data):
    if data.screen== "splashScreen": return
    global canvas
    #no element selected
    if data.currentType == None: return 
    canvas = event.widget.canvas; setX,setY = getPoint(event,data)
    value = getValue(data)
    #if no value, dont create it
    if value==False: return
    #create different type of elements
    if data.currentType=="Voltage Source":
        createVoltageSource(data,setX,setY,value)
    elif data.currentType == "Current Source":
        createCurrentSource(data,setX,setY,value)
    elif data.currentType =="Resistor": createResistor(data,setX,setY,value)
    elif data.currentType == "Wire" and data.startX != None:
        if data.startX!=setX or data.startY != setY:
            data.wire.append(Wire(data.startX,data.startY,setX,setY))
    elif data.currentType == "Ground": data.ground.append(Ground(setX,setY))
    #reset data
    data.startX = None; data.startY = None
    data.currentType = None; data.currentX,data.currentY = None,None

#check if user moves an element
def rightMousePressed(event,data):
    width = 45
    global canvas
    canvas = event.widget.canvas
    #check the element user moves
    for element in data.resistor+data.source+data.ground:
        x0,y0,x1,y1 = getBound(element)
        if x0<=event.x<=x1 and y0<=event.y<=y1:
            #if user moves something, stop demoing
            data.demo = False
            while len(data.circleDir)>0: data.circleDir.pop()
            data.storeX= element.x; data.storeY = element.y
            data.changed = element; data.selected = element
            data.currentX=event.x; data.currentY=event.y; return

#record current element move
def rightMouseMoved(event,data):
    global canvas
    canvas = event.widget.canvas
    if data.changed!= None:
        #record
        data.changed.x,data.changed.y = event.x, event.y
        data.currentX,data.currentY = event.x,event.y; return

#check where the user drops it
def rightMouseReleased(event,data):
    global canvas
    canvas = event.widget.canvas
    if data.changed != None:
        setX,setY = getPoint(event,data)
        #update the nodes and the dropped element
        if type(data.selected) == Source:
            if data.changed.elemType == "Voltage Source":
                data.selected=updateMoveElement(data,setX,setY)
            else:
                data.selected = updateMoveElement(data,setX,setY)
        elif type(data.changed) == Resistor or type(data.changed)==Ground:
            data.selected=updateMoveElement(data,setX,setY)
        #reset the changing element
        data.currentX,data.currentY = None,None; data.changed = None
        data.storeX, data.storeY = None,None; return

#determine the node position after moving the object
def determineNewNode(data,nodeRow,nodeCol,inputRow,inputCol,outRow,outCol):
    #horizon object
    if inputRow == outRow:
        if nodeRow<0 or nodeRow>=data.rows or nodeCol-2-1<0 or \
        nodeCol+2+1>=data.cols: return False
        #input is on the left
        if inputCol < outCol:
            inputNode=data.node[data.node.index(Node(nodeRow,nodeCol-2-1))]
            outputNode=data.node[data.node.index(Node(nodeRow,nodeCol+2+1))]
            #input on the right
        else:
            inputNode=data.node[data.node.index(Node(nodeRow,nodeCol+2+1))]
            outputNode=data.node[data.node.index(Node(nodeRow,nodeCol-2-1))]
    #vertical object
    else:
        if nodeCol<0 or nodeCol>=data.cols or nodeRow-2-1<0 or \
           nodeRow+2+1>=data.rows: return False
        #input is on the top
        if inputRow< outRow:
            inputNode = data.node[data.node.index(Node(nodeRow-2-1,nodeCol))]
            outputNode = data.node[data.node.index(Node(nodeRow+2+1,nodeCol))]
        #input is on the bottom
        else:
            inputNode = data.node[data.node.index(Node(nodeRow+2+1,nodeCol))]
            outputNode = data.node[data.node.index(Node(nodeRow-2-1,nodeCol))]
    return inputNode,outputNode

#clear previous nodes of the moved element
def clearCurrentNode(data,element):
    for node in data.node:
        node.elem=copy.copy(node.elem-{element})
        node.inputElem = copy.copy(node.inputElem-{element})
        node.outputElem = copy.copy(node.outputElem-{element})
    #remove connected nodes
    data.forwardConnected[element.input].remove(element.output)
    data.reverseConnected[element.output].remove(element.input)

#user moves the ground
def moveGround(data,nodeRow,nodeCol):
    #off the grid
    if nodeRow<0 or nodeRow>=data.rows or nodeCol<0 or nodeCol>=data.cols:
        displayWarning(); data.changed.x=data.storeX;data.changed.y=data.storeY
        return data.changed
    #find original position, reset them to be not zero
    for node in data.node:
        if node.voltageValue ==0: node.voltageValue= "V%d"%(data.unknown)
    data.unknown += 1
    data.changed.row = nodeRow; data.changed.col = nodeCol
    #reset new ground to zero
    setNodeValue(data,nodeRow,nodeCol,0)
    return data.changed

#update the info of the moved element
def updateMoveElement(data,x,y):
    nodeRow,nodeCol=(y-(10*10+10*10/2))/(10*2),(x-10*10/2)/(10*2)
    #update the position and nodes
    data.changed.x = x; data.changed.y = y
    if type(data.changed) == Ground: return moveGround(data,nodeRow,nodeCol)
    inputRow,inputCol = data.changed.input.row,data.changed.input.col
    outputRow,outputCol = data.changed.output.row,data.changed.output.col
    #fall out of grid
    if determineNewNode(data,nodeRow,nodeCol,inputRow,inputCol,
        outputRow,outputCol)==False: displayWarning();data.changed.x=\
        data.storeX;data.changed.y=data.storeY; return data.changed
    #update the node information
    inputNode,outputNode =determineNewNode(data,nodeRow,nodeCol,inputRow,
                            inputCol,outputRow,outputCol)
    clearCurrentNode(data,data.changed)
    inputNode.elem.add(data.changed); inputNode.outputElem.add(data.changed)
    outputNode.elem.add(data.changed); outputNode.inputElem.add(data.changed)
    data.changed.input = inputNode; data.changed.output = outputNode
    #determine the positives and negatives
    if data.changed.elemType == "Voltage Source":
        data.changed.input.direction = "-"; data.changed.output.direction="+"
    else: data.changed.input.direction="+"; data.changed.output.direction="-"
    #update connected
    updateConnected(inputNode,outputNode,data)
    return data.changed

#update the connection between nodes
def updateConnected(node1,node2,data):
    #update dictionary 1
    if node1 not in data.forwardConnected:
        data.forwardConnected[node1] = {node2}
    else:
        if node2 not in data.forwardConnected[node1]:
            data.forwardConnected[node1].add(node2)
    #update reverse dictionary
    if node2 not in data.reverseConnected:
        data.reverseConnected[node2] = {node1}
    else:
        if node1 not in data.reverseConnected[node2]:
            data.reverseConnected[node2].add(node1)

#user didn't put the element in the grid
def displayWarning():
    #show warning
    tkMessageBox.showwarning("Warning!",
            "Put the element in the grid system!")

#create a voltage source
def createVoltageSource(data,setX,setY,value):
    nodeRow,nodeCol=(setY-(10*10+10*10/2))/(10*2),(setX-10*10/2)/(10*2)
    if nodeRow-1-2<0 or nodeCol<0 or \
nodeRow+1+2>=data.rows or nodeCol>=data.cols: displayWarning(); return
    index1 = data.node.index(Node(nodeRow-1-2,nodeCol)) #output
    index2 = data.node.index(Node(nodeRow+1+2,nodeCol)) #input
    #input node and output node
    data.node[index1].elem.add(Source(setX,setY,"Voltage Source",
    "V","A",value))
    data.node[index2].elem.add(Source(setX,setY,"Voltage Source",
    "V","A",value))
    data.node[index1].voltageValue = "V%d" %(data.unknown)
    #add the elements 
    data.node[index1].inputElem.add(Source(setX,setY,"Voltage Source",
    "V","A",value)); data.node[index1].direction = "+"
    data.node[index2].voltageValue= "V%d" %(data.unknown+1)
    data.node[index2].outputElem.add(Source(setX,setY,"Voltage Source",
    "V","A",value)); data.unknown += 2; data.node[index2].direction ="-"
    #add the source
    data.source.append(Source(setX,setY,"Voltage Source",data.node[index2],
                              data.node[index1],value))
    updateConnected(data.node[index2],data.node[index1],data)
    return data.source[-1]

#create a current source
def createCurrentSource(data,setX,setY,value):
    nodeRow,nodeCol=(setY-(10*10+10*10/2))/(10*2),(setX-10*10/2)/(10*2)
    if nodeRow-1-2<0 or nodeCol<0 or \
nodeRow+1+2>=data.rows or nodeCol>=data.cols: displayWarning(); return
    index1 = data.node.index(Node(nodeRow-1-2,nodeCol)) #output
    index2 = data.node.index(Node(nodeRow+1+2,nodeCol)) #input
    #input and output nodes
    data.node[index1].elem.add(Source(setX,setY,"Current Source",
    "V","A",value))
    data.node[index2].elem.add(Source(setX,setY,"Current Source",
    "V","A",value))
    #add the elements into nodes
    data.node[index1].voltageValue = "V%d" %(data.unknown)
    data.node[index1].inputElem.add(Source(setX,setY,"Current Source",
    "V","A",value)); data.node[index1].direction = "-"
    data.node[index2].voltageValue= "V%d" %(data.unknown+1)
    data.node[index2].outputElem.add(Source(setX,setY,"Current Source",
    "V","A",value)); data.unknown += 2; data.node[index2].direction ="+"
    #add the source
    data.source.append(Source(setX,setY,"Current Source",data.node[index2],
                              data.node[index1],value))
    updateConnected(data.node[index2],data.node[index1],data)
    return data.source[-1]

#create a resistor
def createResistor(data,setX,setY,value):
    nodeRow,nodeCol=(setY-(10*10+10*10/2))/(10*2),(setX-10*10/2)/(10*2)
    if nodeRow<0 or nodeCol-1-2<0 or \
nodeRow>=data.rows or nodeCol+1+2>=data.cols: displayWarning(); return
    index1 = data.node.index(Node(nodeRow,nodeCol-2-1)) #input
    index2 = data.node.index(Node(nodeRow,nodeCol+2+1)) #output
    #update inputnode and outputNode
    data.node[index1].elem.add(Resistor(setX,setY,"Resistor","V","A",value))
    data.node[index2].elem.add(Resistor(setX,setY,"Resistor",
    "V","A",value))
    #add the elements into the nodes
    data.node[index1].voltageValue = "V%d" %(data.unknown)
    data.node[index1].outputElem.add(Resistor(setX,setY,"Resistor",
    "V","A",value)); data.node[index1].direction = "+"
    data.node[index2].voltageValue= "V%d" %(data.unknown+1)
    data.node[index2].inputElem.add(Resistor(setX,setY,"Resistor",
    "V","A",value)); data.unknown += 2; data.node[index2].direction ="-"
    #add the resistor 
    data.resistor.append(Resistor(setX,setY,"Resistor",data.node[index1],
                              data.node[index2],value))
    updateConnected(data.node[index1],data.node[index2],data)
    return data.resistor[-1]

#connect two nodes
def connect(data,wire):
    startCol,startRow = wire.startCol,wire.startRow
    endRow,endCol= wire.endRow,wire.endCol
    startNode = data.node[data.node.index(Node(startRow,startCol))]
    endNode = data.node[data.node.index(Node(endRow,endCol))]
    #determine start node and end Node
    if startNode not in data.forwardConnected:
        data.forwardConnected[startNode] = {endNode}
    else:
        if endNode not in data.forwardConnected[startNode]:
            data.forwardConnected[startNode].add(endNode)
        #update both dictionaries
    if endNode not in data.reverseConnected:
        data.reverseConnected[endNode] = {startNode}
    else:
        if startNode not in data.reverseConnected[endNode]:
            data.reverseConnected[endNode].add(startNode)

#for ground nodes
def setNodeValue(data,nodeRow,nodeCol,value):
    #detect the position of the ground on the wire
    for wire in data.wire:
        startCol,startRow= wire.startCol,wire.startRow
        endCol,endRow = wire.endCol,wire.endRow
        if (nodeRow==endRow and min(endCol,startCol)<=nodeCol<= \
max(endCol,startCol)) or (nodeCol==startCol and \
min(endRow,startRow)<=nodeRow<=max(endRow,startRow)):
            #set the corresponding nodes to zero
            node1 = data.node[data.node.index(Node(endRow,endCol))]
            node2 = data.node[data.node.index(Node(startRow,startCol))]
            node1.voltageValue = value
            node2.voltageValue = value

#rotates, determine the new row and new col
def determineHorizontal(data,element):
    change =3
    #input on the left
    if element.input.col< element.output.col:
        newStartRow = element.input.row - change
        newStartCol = element.input.col + change
        newEndRow = element.output.row + change
        newEndCol = element.output.col - change
    #input on the right
    else:
        newStartRow = element.input.row + change
        newStartCol = element.input.col - change
        newEndRow = element.output.row - change
        newEndCol = element.output.col + change
    return newStartRow,newStartCol,newEndRow,newEndCol

#if rotates, determine the newRow  and newCol
def determineVertical(data,element):
    change=3
    #input is on the top
    if element.input.row< element.output.row:
        newStartRow = element.input.row + change
        newStartCol = element.input.col + change
        newEndRow = element.output.row - change
        newEndCol = element.output.col - change
    #input is on the bottom
    else:
        newStartRow = element.input.row - change
        newStartCol = element.input.col - change
        newEndRow = element.output.row + change
        newEndCol = element.output.col + change
    return newStartRow,newStartCol,newEndRow,newEndCol

#when user rotates the element                       
def determineNode(data,element):
    change = 3
    if element.elemType == "Resistor":
        #resistor update
        if element.input.row == element.output.row:
            return determineHorizontal(data,element)
        else: return determineVertical(data,element)
            
    elif element.elemType == "Current Source" or \
         element.elemType=="Voltage Source":
        #source update
        if element.input.col == element.output.col:
            return determineVertical(data,element)
        else: return determineHorizontal(data,element)

#update node when user rotates the element
def updateNode(data):
    startRow,startCol = data.selected.input.row,data.selected.input.col
    endRow,endCol = data.selected.output.row,data.selected.output.col
    startNode= data.node[data.node.index(Node(startRow,startCol))]
    endNode = data.node[data.node.index(Node(endRow,endCol))]
    #remove the elements in the nodes
    startNode.outputElem.remove(data.selected)
    endNode.inputElem.remove(data.selected)
    startNode.elem.remove(data.selected); endNode.elem.remove(data.selected)
    #update the connected dictionary
    data.forwardConnected[startNode]=\
                        copy.copy(data.forwardConnected[startNode]-{endNode})
    data.reverseConnected[endNode]=\
                        copy.copy(data.reverseConnected[endNode]-{startNode})

#user rotates
def rotate(data):
    #stop demo
    data.demo = False; data.circleCreated = False; rows = 30; cols = 35
    while len(data.circleDir)>0: data.circleDir.pop()
    #determine new rows and cols
    newStartRow,newStartCol,newEndRow,newEndCol= \
                    determineNode(data,data.selected)
    if newEndRow<0 or newEndRow>=rows or newEndCol<0 or newEndCol>=cols or\
newStartRow<0 or newStartRow>=rows or newStartCol<0 or newStartCol>cols:return
    #update the nodes
    updateNode(data)
    #add the elements to the new node
    newStartNode = data.node[data.node.index(Node(newStartRow,newStartCol))]
    newEndNode = data.node[data.node.index(Node(newEndRow,newEndCol))]
    newStartNode.elem.add(data.selected);
    #determine the positives and negatives
    if data.selected.elemType=="Voltage Source":
        newStartNode.direction = "-"; newEndNode.direction="+"
    else: newStartNode.direction="+"; newEndNode.direction="-"
    newStartNode.outputElem.add(data.selected)
    #give them new values
    newStartNode.voltageValue = "V%d" %(data.unknown)
    newEndNode.elem.add(data.selected); newEndNode.inputElem.add(data.selected)
    newEndNode.voltageValue = "V%d" %(data.unknown+1); data.unknown += 2
    data.selected.input = newStartNode; data.selected.output = newEndNode
    updateConnected(newStartNode,newEndNode,data)

#when an element is removed
def updateSourceResistor(data):
    #update nodes
    for node in data.node:
        node.elem -= {data.selected}
        node.inputElem -= {data.selected}
        node.outputElem -= {data.selected}
    #two nodes are no longer connected
    data.forwardConnected[data.selected.input]=\
copy.copy(data.forwardConnected[data.selected.input] - {data.selected.output})
    data.reverseConnected[data.selected.output]=\
copy.copy(data.reverseConnected[data.selected.output] - {data.selected.input})
    #remove the elements
    if type(data.selected) == Source:
        data.source.remove(data.selected)
    elif type(data.selected) == Resistor:
        data.resistor.remove(data.selected)

#if user deletes a wire, reset nodes
def resetNode(data):
    for node in data.node:
        if node.voltageValue != "V":
            #give them new values
            node.voltageValue = "V%d" %(data.unknown); data.unknown += 1
            node.inputElem = copy.copy(node.inputElem & node.elem)
            node.outputElem = copy.copy(node.outputElem & node.elem)

#when user deletes something     
def delete(data):
    #stop demo
    data.demo = False; data.circleCreated = False
    while len(data.circleDir) >0: data.circleDir.pop()
    #delete sources and elements 
    if type(data.selected) != Wire and type(data.selected)!= Ground:
        updateSourceResistor(data)
    elif type(data.selected) == Wire:
        #determine start positions and end positions for the wire
        startRow,startCol = data.selected.startRow,data.selected.startCol
        endRow,endCol = data.selected.endRow,data.selected.endCol
        node1 = data.node[data.node.index(Node(startRow,startCol))]
        node2 = data.node[data.node.index(Node(endRow,endCol))]
        #update dictionary
        data.forwardConnected[node1].remove(node2)
        data.reverseConnected[node2].remove(node1)
        #reset nodes
        data.unknown = 0; resetNode(data)
        data.wire.remove(data.selected)
        #reset the value of the nodes that are at the ground
    elif type(data.selected) == Ground:
        setNodeValue(data,data.selected.row,data.selected.col,
"V%d" %(data.unknown)); data.ground.remove(data.selected); data.unknown += 1
    data.selected = None

def keyPressed(event,data):
    if data.selected != None:
        #features of modifying elements
        if event.keysym == "r": rotate(data)
        elif event.keysym =="d": delete(data)
        elif event.keysym=="c": getValue(data)

#instruction screen
def drawInstruction(canvas,data):
    image = canvas.data["exit"]
    cx,cy,text = data.instructionButton
    #exit button
    canvas.create_image(cx,cy,image = image)
    #instructions
    canvas.create_text(data.width/2,data.height/2,
            text = """
In this program, you can build a simple electric circuit with voltage sources,
current sources, and resistors. You can view the current and voltage drop at
each component. You can also explore the behavior of current flow in the
circuit. Hope you enjoy!""", font = "Arial 20")

#help screen
def drawHelpScreen(canvas,data):
    exitX = data.width-10*10; exitY = 10*10/2
    image = canvas.data["exit"]
    #exit button
    canvas.create_image(exitX,exitY,image = image)
    #instructions
    canvas.create_text(data.width/2,data.height/2,
                       text= """
1. Drag an element and drop it on the grid system.
2. Press 'r' to rotate the component. Right click the component and move it to
   somewhere else if you want to. 
3. Click on a start node and drag a wire to the end node.
4. Don't forget to ground the circuit! Usually, the ground should be put at the
   negative node of the voltage source. After you are done building the circuit,
   Click on Solve! to view the current and voltage at each component.
5. Click 'Demo!' to view the direction of current flow!
""", font = "Arial 20")

#draw miscellaneous objects
def drawSideObject(canvas,data):
    drawButton(canvas,data)
    drawGrid(canvas,data)
    drawChoices(canvas,data)
    drawMoveObject(canvas,data)
    drawNode(canvas,data)
    #draw information for the selected element
    if data.selected != None: drawInformation(canvas,data.selected,data)

#update dictionary
def update(connected):
    for key in connected:
        key.sync(connected[key])
        # ground
        if type(key.voltageValue) != str:
            for element in connected[key]:
                if len(element.elem&key.elem)>0: continue
                element.voltageValue = key.voltageValue
        else:
            #sync the values
            syncValue = key.voltageValue
            for element in connected[key]:
                #check if there is a ground
                if len(element.elem&key.elem)>0: continue
                if type(element.voltageValue) != str:
                    syncValue = element.voltageValue; break
                elif len(element.voltageValue)>1:syncValue=element.voltageValue
            if type(syncValue) == str and len(syncValue)==1:
                syncValue="V%d" %(data.unknown); data.unknown+= 1
            #sync values
            key.voltageValue = syncValue
            for element in connected[key]:
                if len(element.elem & key.elem)>0: continue
                element.voltageValue = syncValue

#draw change speed option
def drawChangeSpeed(canvas,data):
    speed = canvas.data["speed"]
    canvas.create_image(data.width-10*10*2*2+10*2,10*10,image=speed)
    leftRectX,leftRectY = data.width-10*10*2*2+10*2-10*10/2,10*10
    rightRectX,rightRectY = data.width-10*10*2*2+10*2+10*10/2,10*10
    #decrease and increase
    canvas.create_text(leftRectX-10*10/2,leftRectY,text="-",font="Arial 20")
    canvas.create_text(rightRectX+10*10/2,rightRectY,text="+",font="Arial 20")
                            
def redrawAll(canvas,data):
    if data.screen == "splashScreen": drawSplashScreen(canvas,data); return
    elif data.screen== "instructionScreen":drawInstruction(canvas,data);return
    elif data.screen == "helpScreen": drawHelpScreen(canvas,data); return
    #draw change speed
    if data.demo: drawChangeSpeed(canvas,data)
    drawSideObject(canvas,data)
    #draw each element
    for element in (data.source+data.resistor+data.wire+data.ground):
        if type(element) == Ground:setNodeValue(data,element.row,element.col,0)
        if type(element) == Wire: connect(data,element)
        element.draw(canvas)
    for circle in data.circleDir: circle.draw(canvas)
    #update dictionary constantly
    update(data.forwardConnected)
    update(data.reverseConnected)
    #mouse motion element
    if data.hover != None: drawHover(canvas,data)

#draw mouse motion on voltage source
def drawHoverVolt(canvas,data):
    length = 50
    #draw voltage
    canvas.create_oval(data.hoverX-10*(2+1)-10/2,
data.hoverY-10*(2+1)-10/2,data.hoverX+10*(2+1)+10/2,data.hoverY+10*(2+1)+10/2,
                               fill="red")
    canvas.create_text(data.hoverX,data.hoverY-10*2,
                       text="+",font="Arial 15")
    canvas.create_text(data.hoverX,data.hoverY+10*2,
                       text="-",font = "Arial 15")
    canvas.create_text(data.hoverX,data.hoverY,
        text = "DC %sV" %(str(data.hover.value)),font = "Arial 12")

#draw mouse motion on current source
def drawHoverCurrent(canvas,data):
    length = 50
    #draw the current source
    canvas.create_oval(data.hoverX-10*(2+1)-10/2,
data.hoverY-10*(2+1)-10/2,data.hoverX+10*(2+1)+10/2,data.hoverY+10*(2+1)+10/2,
                               fill="light slate blue")
    canvas.create_text(data.hoverX,data.hoverY,
                       text = "|", font= "Arial 25")
    canvas.create_text(data.hoverX,data.hoverY-10,
                       text = "/\\", font = "Arial 30")
    canvas.create_text(data.hoverX,data.hoverY+10*2,
            text = "DC %sA" %(str(data.hover.value)),font="Arial 10")

#draw mouse motion on resistor
def drawHoverResistor(canvas,data):
    length = 50
    #draw the resistor
    canvas.create_rectangle(data.hoverX-length+10,data.hoverY-10*2,
                                data.hoverX+length-10,data.hoverY+10*2)
    interval = 12; distance = 6.4; colorList = data.hover.getColorList()
    canvas.create_rectangle(data.hoverX-length+10+distance,
data.hoverY-10*2,data.hoverX-length+10+distance+interval,data.hoverY+10*2,
                            fill = colorList[0])
    #get colorcodes
    canvas.create_rectangle(data.hoverX-length+10+2*distance+interval,
data.hoverY-10*2,data.hoverX-length+10+2*distance+2*interval,
data.hoverY+10*2,fill = colorList[1])
    canvas.create_rectangle(data.hoverX-length+10+(2+1)*distance+2*interval,
data.hoverY-10*2,data.hoverX-length+10+(2+1)*distance+(2+1)*interval,
data.hoverY+10*2,fill = colorList[2])
    canvas.create_rectangle(data.hoverX-length+10+2*2*distance+
(2+1)*interval,data.hoverY-10*2,data.hoverX-length+10+2*2*distance+
2*2*interval,data.hoverY+10*2,fill = "gold")

#draw mouse motion
def drawHover(canvas,data):
    length =50
    canvas.create_rectangle(data.hoverX-length,data.hoverY-length,
            data.hoverX+length,data.hoverY+length,fill="light gray")
    #determine type
    if type(data.hover) == Source:
        if data.hover.elemType == "Voltage Source":
            drawHoverVolt(canvas,data)
        else: drawHoverCurrent(canvas,data)
    else:
        drawHoverResistor(canvas,data)

#draw an object that is being moved
def drawMoveObject(canvas,data):
    if data.changed!= None:
        data.changed.x = data.currentX; data.changed.y = data.currentY
        data.changed.draw(canvas)
    #determine type
    if data.currentType == "Voltage Source": drawMoveVoltage(canvas,data)
    elif data.currentType == "Current Source": drawMoveCurrent(canvas,data)
    elif data.currentType == "Resistor": drawMoveResistor(canvas,data)
    elif data.currentType == "Ground": drawMoveGround(canvas,data)
    elif data.currentType== "Wire" and data.startX != None:
        drawMoveWire(canvas,data)

#super class
class Element(object):
    def __init__(self,x,y,elemType,value):
        #position, value and type
        self.x=x
        self.y=y
        self.value = value
        self.elemType = elemType
        self.current= None; self.voltage = None

    #using sets, so use hash 
    def __hash__(self):
        #hash it
        return hash(self.getHashables())

    def getHashables(self):
        #get hash tuple
        return (self.x,self.y)

#sources, subclass
class Source(Element):
    def __init__(self,x,y,elemType,inputNode,outputNode,value):
        super().__init__(x, y, elemType, value)
        #inherit and record nodes
        self.input = inputNode
        self.output = outputNode
        if elemType == "Voltage Source": self.voltage = -value
        else: self.current = value

    #draw vertical voltage
    def drawVertVolt(self,canvas,length,size):
        canvas.create_oval(self.x-2,self.y-length-2,
                           self.x+2,self.y-length+2,fill="black")
        canvas.create_oval(self.x-2,self.y+length-2,
                   self.x+2,self.y+length+2,fill="black")
        canvas.create_line(self.x,self.y-length,self.x,self.y-size)
        canvas.create_line(self.x,self.y+size,self.x,self.y+length)
        #normal 
        if self.input.row> self.output.row:
            canvas.create_text(self.x,self.y-10-10/2,text="+",font= "Arial 15")
            canvas.create_text(self.x,self.y+10+10/2,text="-",font= "Arial 15")
            canvas.create_text(self.x,self.y,
                    text= "%s V" %(str(self.value)),font = "Arial 10")
        #reversed
        else:
            canvas.create_text(self.x,self.y-10-10/2,text="-",font= "Arial 15")
            canvas.create_text(self.x,self.y+10+10/2,text="+",font= "Arial 15")
            canvas.create_text(self.x,self.y,
                    text= "%s V" %(str(self.value)),font = "Arial 10")

    #draw a horizontal voltage
    def drawHorizonVolt(self,canvas,length,size):
        canvas.create_line(self.x-length,self.y,self.x-size,self.y)
        canvas.create_line(self.x+size,self.y,self.x+length,self.y)
        canvas.create_oval(self.x-length-2,self.y-2,
                   self.x-length+2,self.y+2,fill="black")
        canvas.create_oval(self.x+length-2,self.y-2,
                   self.x+length+2,self.y+2,fill="black")
        #normal horizon with the input on the left
        if self.input.col< self.output.col:
            canvas.create_text(self.x-10-10/2,self.y,text="-",font= "Arial 15")
            canvas.create_text(self.x+10+10/2,self.y,text="+",font= "Arial 15")
            canvas.create_text(self.x,self.y,
                    text= "%s V" %(str(self.value)),font = "Arial 10")
        #reversed with input on the right
        else:
            canvas.create_text(self.x-10-10/2,self.y,text="+",font= "Arial 15")
            canvas.create_text(self.x+10+10/2,self.y,text="-",font= "Arial 15")
            canvas.create_text(self.x,self.y+10,
                    text= "%s V" %(str(self.value)),font = "Arial 10")

    #draw vertical current source
    def drawVertCurrent(self,canvas,length,size):
        canvas.create_line(self.x,self.y-length,self.x,self.y-size)
        canvas.create_line(self.x,self.y+size,self.x,self.y+length)
        canvas.create_oval(self.x-2,self.y-length-2,
                   self.x+2,self.y-length+2,fill="black")
        canvas.create_oval(self.x-2,self.y+length-2,
                   self.x+2,self.y+length+2,fill="black")
        #draw input on the right
        if self.input.row> self.output.row:
            canvas.create_text(self.x,self.y-10/2,text = "|",font = "Arial 15")
            canvas.create_text(self.x,self.y,text = "|",font="Arial 15")
            canvas.create_text(self.x-2,self.y-10,text = "/",font="Arial 15")
            canvas.create_text(self.x+2,self.y-10,text = "\\",font="Arial 15")
        #input on the left
        else:
            canvas.create_text(self.x,self.y-10/2,text = "|",font = "Arial 15")
            canvas.create_text(self.x,self.y,text = "|",font="Arial 15")
            canvas.create_text(self.x+2,self.y+10,text = "/",font="Arial 15")
            canvas.create_text(self.x-2,self.y+10,text = "\\",font="Arial 15")

        #draw horizontal current source
    def drawHorizonCurrent(self,canvas,length,size):
        canvas.create_line(self.x-length,self.y,self.x-size,self.y)
        canvas.create_line(self.x+size,self.y,self.x+length,self.y)
        canvas.create_oval(self.x-length-2,self.y-2,
                   self.x-length+2,self.y+2,fill="black")
        canvas.create_oval(self.x+length-2,self.y-2,
                   self.x+length+2,self.y+2,fill="black")
    #draw input on the left
        if self.input.col <self.output.col:
            canvas.create_text(self.x-10/2,self.y,text="--",font = "Arial 15")
            canvas.create_text(self.x,self.y,text="--",font="Arial 15")
            canvas.create_text(self.x+10,self.y+2,text=">",font = "Arial 15")
        #draw input on the right
        else:
            canvas.create_text(self.x-10/2,self.y,text = "--",font="Arial 15")
            canvas.create_text(self.x,self.y,text = "--",font="Arial 15")
            canvas.create_text(self.x-10,self.y+2,text = "<",font="Arial 15")

    #draw a source
    def draw(self,canvas):
        size = 28; length = 60
        #draw voltage source
        if self.elemType == "Voltage Source":
            canvas.create_oval(self.x-size,self.y-size,self.x+size,self.y+size,
                           fill = "red")
            if self.input.col == self.output.col:
                self.drawVertVolt(canvas,length,size)
            else: self.drawHorizonVolt(canvas,length,size)
        #draw current source
        elif self.elemType == "Current Source":
            canvas.create_oval(self.x-size,self.y-size,self.x+size,self.y+size,
                           fill = "light slate blue")
            canvas.create_text(self.x,self.y+10+10/2+2,
                            text ="%s A" %(str(self.value)),font = "Arial 10")
            #draw different direction of the source
            if self.input.col==self.output.col:
                self.drawVertCurrent(canvas,length,size) 
            else: self.drawHorizonCurrent(canvas,length,size)

    #check if two sources are the same
    def __eq__(self,other):
        return isinstance(self,Source) and isinstance(other,Source) and \
               self.x==other.x and self.y==other.y
    #human readable representation
    def __repr__(self):
        return "%s centered at \nrow %d, column %d" \
%(self.elemType,int((self.y-(10*10+10*10/2))/(10*2)),
  int((self.x-10*10/2)/(10*2)))

    #hash value of the source
    def __hash__(self):
        return hash(self.getHashables())

    def getHashables(self):
        #hash tuple
        return (self.x,self.y)

#wire   
class Wire(object):
    def __init__(self,startX,startY,endX,endY):
        #record start node and end node
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY
        self.startCol,self.startRow=\
            (self.startX-10*10/2)/(10*2),(self.startY-(10*10+10*10/2))/(10*2)
        self.endCol,self.endRow= \
            (self.endX-10*10/2)/(10*2),(self.endY-(10*10+10*10/2))/(10*2)

    #draw the wire
    def draw(self,canvas):
        # draw nodes
        canvas.create_oval(self.startX-2,self.startY-2,
                           self.startX+2,self.startY+2,fill="black")
        canvas.create_oval(self.endX-2,self.endY-2,
                           self.endX+2,self.endY+2,fill="black")
        #draw lines
        canvas.create_line(self.startX,self.endY,self.startX,self.startY,
                           width=2)
        canvas.create_line(self.startX,self.endY,self.endX,self.endY,width=2)

    def __repr__(self):
        #represent the wire
        return "Wire from row=%s,col=%s, \nto row=%s,col=%s" \
            %(self.startRow,self.startCol,self.endRow,self.endCol)

 #ground   
class Ground(object):
    def __init__(self,x,y):
        #record position
        self.x = x; self.y = y
        nodeRow,nodeCol=(y-(10*10+10*10/2))/(10*2),(x-10*10/2)/(10*2)
        self.row = nodeRow; self.col = nodeCol

    def draw(self,canvas):
        #draw the ground
        canvas.create_line(self.x,self.y,self.x,self.y+10*2)
        canvas.create_line(self.x-10*2,self.y+10*2,self.x+10*2,self.y+10*2)
        canvas.create_line(self.x-10,self.y+10*2+10/2,
                           self.x+10,self.y+10*2+10/2)
        canvas.create_line(self.x-10/2,self.y+10*2+10,
                           self.x+10/2,self.y+10*2+10)

    def __repr__(self):
        #human readable info
        return "Ground at \nrow=%s,col=%s" %(self.row,self.col)

#resistor
class Resistor(Element):
    def __init__(self,x,y,elemType,inputNode,outputNode,value):
        super().__init__(x, y, elemType, value)
        #inherit and record nodes
        self.input = inputNode
        self.output = outputNode

    #draw resistor
    def draw(self,canvas):
        #get colorlist
        colorList = self.getColorList()
        length = 30; width = 15; interval=8; distance =5.6
        #different position of the resistor
        if self.input.row==self.output.row:
            if self.input.col < self.output.col:
                self.drawHorizontal(canvas,colorList)
            else: self.drawRevHorizontal(canvas,colorList)
        else:
            if self.input.row < self.output.row:
                self.drawVertical(canvas,colorList)
            else: self.drawRevVertical(canvas,colorList)

    #draw a vertical resistor
    def drawVertical(self,canvas,colorList):
        length = 30; width = 15; interval=8; distance =5.6
        #draw the colorlist
        canvas.create_rectangle(self.x-width,self.y-length,
                                    self.x+width,self.y+length)
        canvas.create_rectangle(self.x-width,self.y-length+distance,
            self.x+width,self.y-length+distance+interval,fill=colorList[0])
        canvas.create_rectangle(self.x-width,self.y-length+2*distance+ \
interval,self.x+width,self.y-length+2*distance+2*interval,fill=colorList[1])
        canvas.create_rectangle(self.x-width,self.y-length+(2+1)*distance+\
2*interval,self.x+width,self.y-length+(2+1)*distance+(2+1)*interval,
                                fill=colorList[2])
        canvas.create_rectangle(self.x-width,self.y-length+(2+2)*distance+\
(2+1)*interval,self.x+width,self.y-length+(2+2)*distance+(2+2)*interval,
                                fill = "gold")
        #draw nodes
        canvas.create_line(self.x,self.y-length*2,self.x,self.y-length)
        canvas.create_line(self.x,self.y+length,self.x,self.y+2*length)
        canvas.create_oval(self.x-2,self.y-length*2-2,
                           self.x+2,self.y-length*2+2,fill="black")
        canvas.create_oval(self.x-2,self.y+length*2-2,self.x+2,
                           self.y+2*length+2,fill="black")

    #draw reverse resistor vertically
    def drawRevVertical(self,canvas,colorList):
        length = 30; width = 15; interval=8; distance =5.6
        #create rectangle
        canvas.create_rectangle(self.x-width,self.y-length,
                                    self.x+width,self.y+length)
        canvas.create_rectangle(self.x-width,self.y-length+distance,
            self.x+width,self.y-length+distance+interval,fill="gold")
        canvas.create_rectangle(self.x-width,self.y-length+2*distance+ \
interval,self.x+width,self.y-length+2*distance+2*interval,fill=colorList[2])
        canvas.create_rectangle(self.x-width,self.y-length+(2+1)*distance+\
2*interval,self.x+width,self.y-length+(2+1)*distance+(2+1)*interval,
                                fill=colorList[1])
        #draw colorlist
        canvas.create_rectangle(self.x-width,self.y-length+(2+2)*distance+\
(2+1)*interval,self.x+width,self.y-length+(2+2)*distance+(2+2)*interval,
                                fill = colorList[0])
        canvas.create_line(self.x,self.y-length*2,self.x,self.y-length)
        canvas.create_line(self.x,self.y+length,self.x,self.y+2*length)
        canvas.create_oval(self.x-2,self.y-length*2-2,
                           self.x+2,self.y-length*2+2,fill="black")
        canvas.create_oval(self.x-2,self.y+length*2-2,self.x+2,
                           self.y+2*length+2,fill="black")

    #horizontal resistor
    def drawHorizontal(self,canvas,colorList):
        length = 30; width = 15; interval=8; distance =5.6
        #draw colorlist
        canvas.create_rectangle(self.x-length,self.y-width,
                                self.x+length,self.y+width)
        canvas.create_rectangle(self.x-length+distance,self.y-width,
        self.x-length+distance+interval,self.y+width,fill = colorList[0])
        canvas.create_rectangle(self.x-length+2*distance+interval,
self.y-width,self.x-length+2*distance+2*interval,self.y+width,fill=colorList[1])
        canvas.create_rectangle(self.x-length+(2+1)*distance+2*interval,
                self.y-width,self.x-length+(2+1)*distance+(2+1)*interval,
                self.y+width,fill=colorList[2])
        canvas.create_rectangle(self.x-length+(2+2)*distance+(2+1)*interval,
                self.y-width,self.x-length+(2+2)*distance+(2+2)*interval,
                                self.y+width,fill = "gold")
        #draw nodes
        canvas.create_line(self.x-length*2,self.y,self.x-length,self.y)
        canvas.create_line(self.x+length,self.y,self.x+2*length,self.y)
        canvas.create_oval(self.x-length*2-2,self.y-2,
                           self.x-length*2+2,self.y+2,fill="black")
        canvas.create_oval(self.x+length*2-2,self.y-2,
                           self.x+2*length+2,self.y+2,fill="black")

    #draw reverse resistor
    def drawRevHorizontal(self,canvas,colorList):
        length = 30; width = 15; interval=8; distance =5.6
        #draw colorlist
        canvas.create_rectangle(self.x-length,self.y-width,
                                self.x+length,self.y+width)
        canvas.create_rectangle(self.x-length+distance,self.y-width,
        self.x-length+distance+interval,self.y+width,fill ="gold")
        canvas.create_rectangle(self.x-length+2*distance+interval,
self.y-width,self.x-length+2*distance+2*interval,self.y+width,fill=colorList[2])
        canvas.create_rectangle(self.x-length+(2+1)*distance+2*interval,
                self.y-width,self.x-length+(2+1)*distance+(2+1)*interval,
                self.y+width,fill=colorList[1])
        canvas.create_rectangle(self.x-length+(2+2)*distance+(2+1)*interval,
                self.y-width,self.x-length+(2+2)*distance+(2+2)*interval,
                                self.y+width,fill =colorList[0])
        #draw nodes
        canvas.create_line(self.x-length*2,self.y,self.x-length,self.y)
        canvas.create_line(self.x+length,self.y,self.x+2*length,self.y)
        canvas.create_oval(self.x-length*2-2,self.y-2,
                           self.x-length*2+2,self.y+2,fill="black")
        canvas.create_oval(self.x+length*2-2,self.y-2,
                           self.x+2*length+2,self.y+2,fill="black")
        
    #determine the colorlist of the resistor
    def getColorList(self):
        #different inputs
        colorCode = ["black","brown","red","orange","yellow",
        "green","blue","violet","grey","white"]
        if len(str(int(self.value)))==1:
            colorList=["black",colorCode[int(self.value)],"black"]
        elif len(str(int(self.value)))==2: colorList =\
             [colorCode[int(str(int(self.value))[0])],
              colorCode[int(str(int(self.value))[1])],"black"]
        #get colors
        else:
            firstTwo = round(int(str(int(self.value))[0:3])/10)
            colorList = [colorCode[int(firstTwo//10)],
    colorCode[int(firstTwo%10)],colorCode[len(str(int(self.value)))-2]]
        return colorList

    def __hash__(self):
        return hash((self.x, self.y));
    
    def __eq__(self,other):
        #check if two resistors are equal
        return isinstance(self,Resistor) and isinstance(other,Resistor) and \
               self.x==other.x and self.y==other.y

    def __repr__(self):
        #human readable info
        return "Resistor centered at \nrow %d, column %d" \
    %(int((self.y-(10*10+10*10/2))/(10*2)),int((self.x-10*10/2)/(10*2)))

#node
class Node(object):
    def __init__(self,row,col,value="V",inputElem=set(),
                 outputElem=set(),direction="+"):
        #record row, col
        self.row = row
        self.col = col
        self.voltageValue = value
        self.elem = set()
        #record elements that are connected
        self.inputElem = copy.deepcopy(inputElem)
        self.outputElem = copy.deepcopy(outputElem)
        self.direction = direction

    def __eq__(self,other):
        #check if two nodes are the same
        return (isinstance(self,Node) and isinstance(other,Node)) and \
               ((self.row == other.row and self.col == other.col) or\
(self.voltageValue == other.voltageValue and \
    ((type(self.voltageValue)!=str and type(other.voltageValue) != str) or \
     (len(self.voltageValue)>1 and len(other.voltageValue)>1))))
    
    def __repr__(self):
        #human readable info
        return "Node(row=%s,col=%s),value=%s,elem=%s"\
    %(str(self.row),str(self.col),str(self.voltageValue),str(self.elem))

    def __hash__(self):
        #hash it
        return hash(self.getHashables())

    def getHashables(self):
        #hash the tuple
        return (self.row,self.col)

    #sync connecting nodes
    def sync(self,connectedNode):
        #share the elements
        inputElem = copy.copy(self.inputElem)
        outputElem = copy.copy(self.outputElem)
        for node in connectedNode:
            if len(node.elem & self.elem) >0: continue
            inputElem = copy.copy(inputElem|node.inputElem)
            outputElem = copy.copy(outputElem|node.outputElem)
        #update it
        self.inputElem = copy.copy(inputElem)
        self.outputElem = copy.copy(outputElem)
        for node in connectedNode:
            if len(node.elem & self.elem)>0: continue
            node.inputElem = copy.copy(inputElem)
            node.outputElem = copy.copy(outputElem)

#show a dialog asking for user input, adapted from kosbie's notes
def showDialog(canvas,elemType):
    #pop up dialog
    MyDialog(canvas,elemType)
    return canvas.data["modalResult"]

#draw resistor info
def drawResistorInfo(canvas,element,data):
    startX = 750; startY = 150
    #draw resistance
    canvas.create_text(startX,startY+10*2*2*2,
text = "Resistance: %.1f ohms" %(element.value),anchor=NW,font ="Arial 15")
    #draw voltage and current
    if element.current!= None and element.voltage!= None:
        canvas.create_text(startX,startY+10*10,
text= "Voltage Drop: %.4f Volts" %(element.voltage),anchor=NW,font="Arial 15")
        canvas.create_text(startX,startY+10*2+10*10,
text = "Current: %.4f Amps" %(element.current),anchor=NW,font="Arial 15")
    else:
        canvas.create_text(startX,startY+10*10,
text= "Voltage Drop: Unknown",anchor=NW,font="Arial 15")
        canvas.create_text(startX,startY+10*10+10*2,
text = "Current: Unknown",anchor=NW,font="Arial 15")

#draw current source info
def drawCurrentInfo(canvas,element,data):
    startX = 750; startY = 150
    #draw current
    canvas.create_text(startX,startY+10*2*2*2,
text="Current: %.1f Amps" %(element.value),anchor=NW,font="Arial 15")
    #draw voltage
    if element.voltage != None:
        canvas.create_text(startX,startY+10*10,
text = "Voltage Drop: %.4f Volts" %(element.voltage),anchor=NW,font= "Arial 15")
    else: canvas.create_text(startX,startY+10*10,
text = "Voltage Drop: Unknown", anchor=NW,font = "Arial 15")

#draw voltage info
def drawVoltageInfo(canvas,element,data):
    startX = 750; startY = 150
    #draw voltage drop across it
    canvas.create_text(startX,startY+10*2*2*2,
text= "Voltage Drop: %.4f Volts" %(element.voltage),anchor=NW,font="Arial 15")
    #draw current through it
    if element.current != None: canvas.create_text(startX,startY+10*10,
text = "Current: %.4f Amps" %(element.current),anchor=NW,font="Arial 15")
    else: canvas.create_text(startX,startY+10*10,
                text = "Current: Unknown",anchor= NW,font="Arial 15")

#draw info for the selected element  
def drawInformation(canvas,element,data):
    startX = 750; startY = 150
    canvas.create_text(startX,startY,text = "Selected:",font = "Arial 15",
                       anchor = NW)
    canvas.create_text(startX,startY+10*2,text="%s" %(data.selected),
        anchor = NW,font = "Arial 15")
    #check type
    if type(element) == Wire: pass
    elif type(element) == Ground: pass
    #draw resistors and sources selected
    elif type(element) == Resistor:
        drawResistorInfo(canvas,element,data)
    elif element.elemType == "Voltage Source":
        drawVoltageInfo(canvas,element,data)
    elif element.elemType == "Current Source":
        drawCurrentInfo(canvas,element,data)
    #draw insturctions for users telling them how to use it
    canvas.create_text(startX,startY+10*10+10*2*(2+1),
text="Press 'r' to rotate",font = "Arial 15", anchor = NW)
    canvas.create_text(startX,startY+10*10+10*2*2*2,
text="Press 'd' to delete",font = "Arial 15", anchor = NW)
    canvas.create_text(startX,startY+10*10*2,
    text="Press 'c' to change value",font = "Arial 15",anchor = NW)
    canvas.create_text(startX,startY+10*10*2+10*2,
    text="Right click the element and \ndrag it to a new position",
                       font="Arial 15",anchor= NW)

#draw voltage source at the side
def drawVoltageSource(canvas,cx,cy,data):
    marginY = 45; marginX = 100; size = 35
    #draw the oval
    canvas.create_oval(marginX-size,marginY-size,marginX+size,marginY+size,
                                fill = "red")
    canvas.create_rectangle(cx-marginY,0,cx+marginY,2*cy+10*2)
    canvas.create_text(cx,2*cy+10,
                       text = "Voltage Source",font = "Arial 10")
    #draw directions
    canvas.create_text(cx,cy,text= "DC Voltage",font = "Arial 10")
    canvas.create_text(cx,cy-10-10/2,text = "+",font= "Arial 15")
    canvas.create_text(cx,cy+10+10/2,text = "-",font= "Arial 15")

#draw current source
def drawCurrentSource(canvas,cx,cy,data):
    marginY = 45; size = 35
    #draw oval
    canvas.create_oval(cx-size,cy-size,cx+size,cy+size,
                       fill = "light slate blue")
    canvas.create_rectangle(cx-marginY,0,cx+marginY,2*cy+10*2)
    canvas.create_text(cx,2*cy+10,
                       text = "Current Source",font = "Arial 10")
    #draw direction
    canvas.create_text(cx,cy,text = "|",font = "Arial 15")
    canvas.create_text(cx,cy+10/2,text = "|",font="Arial 15")
    canvas.create_text(cx-2,cy-10/2,text = "/",font="Arial 15")
    canvas.create_text(cx+2,cy-10/2,
                       text = "\\",font="Arial 15")

#draw resistor at teh side
def drawResistor(canvas,cx,cy,data):
    colorCode = ["black","brown","red","orange","yellow",
            "green","blue","violet","grey","white"]
    #draw colorcodes
    length = 40; width = 20; marginY = 45; marginX = 100
    canvas.create_rectangle(cx-length,cy-width,cx+length,cy+width)
    canvas.create_rectangle(cx-marginY,0,cx+marginY,2*cy+10*2)
    canvas.create_text(cx,2*cy+10,text = "Resistor",font = "Arial 10")
    canvas.create_rectangle(cx-width+10/2,cy-width,cx-10+10/2,cy+10*2,
                                fill = colorCode[1])
    #draw colorlists
    canvas.create_rectangle(cx-length+10/2,cy-width,cx-length+10+10/2,cy+width,
                                fill = colorCode[0])
    canvas.create_rectangle(cx+10-10/2,cy-width,cx+width-10/2,cy+width,
                                fill = colorCode[2])
    canvas.create_rectangle(cx+length-10-10/2,cy-width,cx+length-10/2,cy+width,
                                fill = "gold")

#draw the ground at the side
def drawGround(canvas,cx,cy,data):
    marginY = 45; marginX = 100
    canvas.create_rectangle(cx-marginY,cy-marginY,cx+marginY,cy+marginY+10*2)
    #draw the lines for ground
    canvas.create_line(cx,cy-10*2,cx,cy+10*2)
    canvas.create_line(cx-10*2,cy+10*2,cx+10*2,cy+10*2)
    canvas.create_line(cx-10,cy+10*2+10/2,cx+10,cy+10*2+10/2)
    canvas.create_line(cx-10/2,cy+10*2+10,cx+10/2,cy+10*2+10)
    canvas.create_text(cx,cy+marginY+10,text= "Ground", font = "Arial 10")

#draw vertical element
def drawVertical(canvas,inputX,inputY,outputX,outputY,inputNode,outputNode,
                 element,data):
    #input on the top
    if inputNode.row < outputNode.row:
        if element == data.changed:
            inputY= element.y-10*2*(2+1); inputX = element.x
            outputY = element.y+10*2*(2+1); outputX = element.x
            #draw direction
        canvas.create_text(inputX,inputY,text = "%s"
        %(inputNode.direction),anchor = SE,font = "Arial 15")
        canvas.create_text(outputX,outputY,text="%s"
            %(outputNode.direction),anchor = NE,font = "Arial 15")
    #input on the bottom
    else:
        if element== data.changed:
            inputY= element.y+10*2*(2+1); inputX = element.x
            outputY = element.y-10*2*(2+1); outputX = element.x
        #draw direction
        canvas.create_text(inputX,inputY,text = "%s"
        %(inputNode.direction),anchor = NE,font = "Arial 15")
        canvas.create_text(outputX,outputY,text="%s"
            %(outputNode.direction),anchor = SE,font = "Arial 15")

#draw moving horizon elements
def drawHorizon(canvas,inputX,inputY,outputX,outputY,inputNode,outputNode,
                element,data):
    #input on the right
    if inputNode.col > outputNode.col:
        if element == data.changed:
            inputX = element.x+10*2*(2+1); inputY = element.y
            outputX = element.x-10*2*(2+1); outputY = element.y
            #draw direction
        canvas.create_text(inputX,inputY,text = "%s"%
        (inputNode.direction),anchor = SW,font = "Arial 15")
        canvas.create_text(outputX,outputY,text="%s"%
        (outputNode.direction),anchor = SE,font = "Arial 15")
    #input on the left
    else:
        if element == data.changed:
            inputX = element.x-10*2*(2+1); inputY = element.y
            outputX = element.x+10*2*(2+1); outputY = element.y
        #draw direction
        canvas.create_text(inputX,inputY,text = "%s"%
        (inputNode.direction),anchor = SE,font = "Arial 15")
        canvas.create_text(outputX,outputY,text="%s"%
        (outputNode.direction),anchor = SW,font = "Arial 15")
        
#draw the direction at the node
def drawNode(canvas,data):
    for element in data.source+data.resistor:
        #get input node and outputnode
        inputNode = element.input; outputNode = element.output
        inputY,inputX = \
            inputNode.row*10*2+10*10+10*10/2,inputNode.col*10*2+10*10/2
        outputY,outputX = \
            outputNode.row*10*2+10*10+10*10/2,outputNode.col*10*2+10*10/2
        #draw vertical element
        if inputNode.col == outputNode.col:
            drawVertical(canvas,inputX,inputY,outputX,outputY,
                         inputNode,outputNode,element,data)
        #draw horizontal element
        else:
            drawHorizon(canvas,inputX,inputY,outputX,outputY,inputNode,
                        outputNode,element,data)

#draw splash screen  
def drawSplashScreen(canvas,data):
    background = canvas.data["bg"]
    title = canvas.data["title"]
    name= canvas.data["name"]
    solve = canvas.data["solveCircuit"]
    instructions = canvas.data["instructions"]
    #load all the images
    canvas.create_image(data.width/2,data.height/2,image = background)
    canvas.create_image(data.width/2,data.height/2-10*10*(2+1),image = title)
    canvas.create_image(data.width/2,data.height/2,image = name)
    canvas.create_image(data.width/2,data.height/2+10*10*2,image = solve)
    canvas.create_image(data.width/2,data.height/2+10*10*2+10*10,
                        image =instructions)

#draw all the buttons
def drawButton(canvas,data):
    #loop through all the buttons
    for button in data.solveButton:
        (cx,cy,text) = button
        #new circuit
        if text == "New Circuit":
            image = canvas.data["new"]
            canvas.create_image(cx,cy,image = image)
        #exit
        elif text == "Exit":
            image = canvas.data["exit"]
            canvas.create_image(cx,cy,image = image)
        #solve it
        elif text == "Solve":
            image = canvas.data["solve"]
            canvas.create_image(cx,cy,image = image)
        #help screen
        elif text == "Help":
            image = canvas.data["help"]
            canvas.create_image(cx,cy,image=image)
        #demo button
        elif text == "Demo":
            image = canvas.data["demo"]
            canvas.create_image(cx,cy,image=image)

#draw the grid system
def drawGrid(canvas,data):
    startX,startY = 50,150; marginX, marginY = 100,45
    length = 20; rows = 30; cols = 35
    for row in range(rows):
        for col in range(cols):
            #set all the nodes
            if data.created==False: 
                node = Node(row,col)
                if node in data.node: pass
                else: data.node.append(node)
            #draw the grid
            canvas.create_rectangle(startX+col*length,startY+row*length,
            startX+(col+1)*length,startY+(row+1)*length,outline = "gray")
            if (startX+col*length,startY+row*length) not in data.grid:
                data.grid.append((startX+col*length,startY+row*length))
            if (startX+(col+1)*length,startY+(row+1)*length) not in data.grid:
                data.grid.append((startX+(col+1)*length,startY+(row+1)*length))
            if row ==0: canvas.create_text(startX+col*length,startY-10,
                                           text = str(col))
            if col ==0: canvas.create_text(startX-10,startY+row*length,
                                           text = str(row))
    data.created= True

#draw the choices at the top
def drawChoices(canvas,data):
    startX,startY = 50,150; marginX, marginY = 100,45
    length = 40; rows = 15; cols = 20
    #voltage source
    cx0,cy0 = marginX,marginY; cx1,cy1 = marginX+2*marginY,marginY
    if (cx0,cy0,"Voltage Source") not in data.choices:
        data.choices.append((cx0,cy0,"Voltage Source"))
    #current source
    if (cx1,cy1,"Current Source") not in data.choices:
        data.choices.append((cx1,cy1,"Current Source"))
    cx2 = marginX + (2+2)*marginY; cy2 = marginY
    #resistor
    if (cx2,cy2,"Resistor") not in data.choices:
        data.choices.append((cx2,cy2,"Resistor"))
    x0 = marginX + (2+2+2)*marginY; y0 = marginY
    #ground
    if (x0,y0,"Ground") not in data.choices:
        data.choices.append((x0,y0,"Ground"))
    drawVoltageSource(canvas,cx0,cy0,data)
    drawCurrentSource(canvas,cx1,cy1,data); drawResistor(canvas,cx2,cy2,data)
    drawGround(canvas,x0,y0,data)

#draw the wire that user is connecting
def drawMoveWire(canvas,data):
    if data.startX == None or data.currentX == None: return
    canvas.create_line(data.startX,data.currentY,data.startX,data.startY)
    canvas.create_line(data.startX,data.currentY,data.currentX,data.currentY)

#draw the voltage that user is dragging
def drawMoveVoltage(canvas,data):
    if data.changed!= None and data.currentX == None: return
    size = 28; length = 60
    cx = data.currentX; cy = data.currentY
    #draw the shape
    canvas.create_oval(cx-size,cy-size,cx+size,cy+size,fill = "red")
    canvas.create_text(cx,cy-10-10/2,text = "+",font= "Arial 15")
    canvas.create_text(cx,cy+10+10/2,text = "-",font= "Arial 15")
    if data.changed== None:
        canvas.create_text(cx,cy,text= "DC V",font = "Arial 10")
    else: canvas.create_text(cx,cy,text="%s V" %(str(data.changed.value)),
                        font = "Arial 10")
    #draw the nodes
    canvas.create_line(cx,cy-length,cx,cy-size)
    canvas.create_line(cx,cy+size,cx,cy+length)
    canvas.create_oval(cx-2,cy-length-2,cx+2,cy-length+2,fill="black")
    canvas.create_oval(cx-2,cy+length-2,cx+2,cy+length+2,fill="black")

#draw the current source user is dragging
def drawMoveCurrent(canvas,data):
    if data.changed!= None and data.currentX == None: return
    size = 28; length = 60
    cx = data.currentX; cy = data.currentY
    #draw the shape
    canvas.create_oval(cx-size,cy-size,cx+size,cy+size,
                       fill = "light slate blue")
    canvas.create_line(cx,cy-length,cx,cy-size)
    canvas.create_line(cx,cy+size,cx,cy+length)
    canvas.create_oval(cx-2,cy-length-2,cx+2,cy-length+2,fill="black")
    canvas.create_oval(cx-2,cy+length-2,cx+2,cy+length+2,fill="black")
    if data.changed!= None:
        #draw changing element
        canvas.create_text(cx,cy-10/2,text = "|",font = "Arial 15")
        canvas.create_text(cx,cy,text = "|",font="Arial 15")
        canvas.create_text(cx-2,cy-10,text = "/",font="Arial 15")
        canvas.create_text(cx+2,cy-10,text = "\\",font="Arial 15")
        canvas.create_text(cx,cy+10+10/2+2,
        text ="%s A" %(str(data.changed.value)),font = "Arial 10")
    else:
        #draw regular element
        canvas.create_text(cx,cy,text = "|",font = "Arial 15")
        canvas.create_text(cx,cy+10/2,text = "|",font="Arial 15")
        canvas.create_text(cx-2,cy-10/2,text = "/",font="Arial 15")
        canvas.create_text(cx+2,cy-10/2,text = "\\",font="Arial 15")

#draw the resistor user is dragging
def drawMoveResistor(canvas,data):
    colorCode = ["black","brown","red","orange","yellow","green",
    "blue","violet","grey","white"]
    if data.selected != None and data.currentX == None: return
    cx = data.currentX; cy = data.currentY
    if data.changed != None: colorList = data.changed.getColorList()
    else: colorList =[colorCode[0],colorCode[1],colorCode[2]]
    length = 30; width = 15; marginY = 45; interval =8; distance =5.6
    #draw the colorcodes
    canvas.create_rectangle(cx-length,cy-width,cx+length,cy+width)
    canvas.create_rectangle(cx-length+distance,cy-width,
    cx-length+distance+interval,cy+width,fill = colorList[0])
    canvas.create_rectangle(cx-length+2*distance+interval,cy-width,
    cx-length+2*distance+2*interval,cy+width,fill = colorList[1])
    canvas.create_rectangle(cx-length+(2+1)*distance+2*interval,
            cy-width,cx-length+(2+1)*distance+(2+1)*interval,
            cy+width,fill=colorList[2])
    canvas.create_rectangle(cx-length+(2+2)*distance+(2+1)*interval,
            cy-width,cx-length+(2+2)*distance+(2+2)*interval,
                            cy+width,fill = "gold")
    #draw nodes
    canvas.create_line(cx-length*2,cy,cx-length,cy)
    canvas.create_line(cx+length,cy,cx+2*length,cy)
    canvas.create_oval(cx-length*2-2,cy-2,cx-length*2+2,cy+2,fill="black")
    canvas.create_oval(cx+length*2-2,cy-2,cx+2*length+2,cy+2,fill="black")

#draw the ground user is dragging
def drawMoveGround(canvas,data):
    cx=data.currentX; cy = data.currentY
    canvas.create_line(cx,cy,cx,cy+10*2)
    canvas.create_line(cx-10*2,cy+10*2,cx+10*2,cy+10*2)
    canvas.create_line(cx-10,cy+10*2+10/2,cx+10,cy+10*2+10/2)
    canvas.create_line(cx-10/2,cy+10*2+10,cx+10/2,cy+10*2+10)

#find the nodes that we need to solve for
def findUnknownNode(data):
    data.connected.update(data.forwardConnected)
    data.connected.update(data.reverseConnected)
    update(data.connected)
    for node in data.connected:
        #if a node has no elem connected, discard it
        if len(node.inputElem|node.outputElem)<=1: continue
        if node not in data.unknownNode and type(node.voltageValue)== str \
    and len(node.voltageValue)!=1: data.unknownNode.append(node)
        for connectTo in data.connected[node]:
            if len(connectTo.inputElem|connectTo.outputElem)<=1: continue
            if connectTo not in data.unknownNode and \
    type(connectTo.voltageValue) == str and len(connectTo.voltageValue)!=1:
                #found an unknown Node
                data.unknownNode.append(connectTo)

#prepare for the solving process
def prepareForSolve(data):
    unknownSource=[]
    #clear all the previous data
    while len(data.unknownNode)>0: data.unknownNode.pop()
    while len(data.currEq)>0: data.currEq.pop()
    while len(data.currConstant)>0: data.currConstant.pop()
    for source in data.source:
        if source.elemType=="Voltage Source":
            # find the current through the voltage source
            if len(source.input.inputElem|source.input.outputElem)>1 and \
               len(source.output.inputElem|source.output.outputElem)>1:
                unknownSource.append(source)
    #find unknown nodes
    findUnknownNode(data)
    return unknownSource+data.unknownNode

#voltage source is connected to the current unknown Node
def sourceUpdate(data,elem,needToSolve,tempCurrEq,tempConstant,index):
    if elem.elemType=="Voltage Source":
        #locate the source
        index1= needToSolve.index(elem)
        if elem.input == data.unknownNode[index]:
            tempCurrEq[index1]=-1
        else: tempCurrEq[index1] = 1
    elif elem.elemType=="Current Source":
        #find the node that is connected
        if elem.input == data.unknownNode[index]:
            tempConstant += elem.value
        else: tempConstant -= elem.value
    #return the updated equation
    return tempCurrEq,tempConstant

#resistor is connected to the current unknown node
def resistorUpdate(data,elem,needToSolve,tempCurrEq,tempConstant,index):
    if elem.input == data.unknownNode[index]:
        #input is the same node at the unknown node
        index1 = needToSolve.index(data.unknownNode[index])
        tempCurrEq[index1] -= 1/elem.value
        if type(elem.output.voltageValue) != str:
            #need to solve this node
            tempConstant-=elem.output.voltageValue/elem.value
        else:
            index2= needToSolve.index(elem.output)
            tempCurrEq[index2] += 1/elem.value
    else:
        #output is the same node
        index1 = needToSolve.index(data.unknownNode[index])
        tempCurrEq[index1] -= 1/elem.value
        if type(elem.input.voltageValue) != str:
            #solve this node
            tempConstant+=elem.input.voltageValue/elem.value
        else:
            index2= needToSolve.index(elem.input)
            tempCurrEq[index2] += 1/elem.value
    #return the updated equation
    return tempCurrEq,tempConstant

#update equation
def updateCurrEq(data,elemAssociated,needToSolve,tempCurrEq,tempConstant,
                 index):
    for element in elemAssociated:
        #find the element
        elem = findElement(element,data)
        #element is not in the circuit, discard it
        if len(elem.input.outputElem|elem.input.inputElem)<=1 or \
           len(elem.output.inputElem|elem.output.outputElem)<=1: continue
        if type(elem) == Source:
            #update curreq, constant
            tempCurrEq,tempConstant = sourceUpdate(data,elem,
                            needToSolve,tempCurrEq,tempConstant,index)
        else: tempCurrEq,tempConstant =resistorUpdate(data,elem,
                            needToSolve,tempCurrEq,tempConstant,index)
    return tempCurrEq,tempConstant

#volt equations
def addVoltEq(data,needToSolve):
    for source in data.source:
        #check if the source is connected
        if source.elemType == "Voltage Source" and \
    len(source.input.inputElem|source.input.outputElem)>1 and \
    len(source.output.inputElem|source.output.outputElem)>1:
            #create a new equation
            voltEq = [0]*len(needToSolve)
            constant = source.value
            #check which node is connected
            try: index = needToSolve.index(source.output); voltEq[index] = 1
            except: constant += source.output.voltageValue
            try: index1 = needToSolve.index(source.input); voltEq[index1]=-1
            except: constant -= source.input.voltageValue
            data.currEq.append(voltEq)
            data.currConstant.append(constant)
            
#solve the circuit
def solve(data):
    #create need to solve nodes
    needToSolve = prepareForSolve(data)
    for index in range(len(data.unknownNode)):
        tempCurrEq = [0]*len(needToSolve); tempCurrEq1=[]; tempConstant= 0
        elemAssociated=\
        data.unknownNode[index].inputElem|data.unknownNode[index].outputElem
        #update the equations based on elements connected
        tempCurrEq,tempConstant= updateCurrEq(data,elemAssociated,
                                needToSolve,tempCurrEq,tempConstant,index)
        for number in tempCurrEq: tempCurrEq1.append(-number)
        if tempCurrEq in data.currEq or tempCurrEq1 in data.currEq: continue
        #append the equations
        data.currEq.append(tempCurrEq)
        data.currConstant.append(tempConstant)
    addVoltEq(data,needToSolve); data.needToSolve = needToSolve
    coeff=np.array(data.currEq); constant=np.array(data.currConstant)
    #record the solution
    try: data.solution = np.linalg.solve(coeff,constant); storeValue(data)
    except: displayError()

#display error in the circuit
def displayError():
    #display message
    tkMessageBox.showwarning("Warning!",
            """
TroubleShoot the circuit:
1. You did not ground the circuit.
2. You haven't finished building your circuit.
3. There is somewhere not connected in the circuit.""")

#record resistor info
def recordResistor(elem,data):
    if elem.input in data.needToSolve or \
       elem.output in data.needToSolve:
        if type(elem.input.voltageValue)==str:
            #record input voltage
            voltage1=data.solution[data.needToSolve.index(elem.input)]
        else: voltage1= elem.input.voltageValue
        if type(elem.output.voltageValue) ==str:
            #record output voltage
            voltage2=data.solution[data.needToSolve.index(elem.output)]
        else: voltage2 =elem.output.voltageValue
        #record voltage and current
        elem.voltage = voltage1-voltage2
        elem.current = (voltage1-voltage2)/elem.value
    else: elem.voltage = None; elem.current = None

#record current source info
def recordCurrent(elem,data):
    if elem.input in data.needToSolve or \
       elem.output in data.needToSolve:
        if type(elem.input.voltageValue)==str:
            #find the input voltage
            voltage1=data.solution[data.needToSolve.index(elem.input)]
        else: voltage1= elem.input.voltageValue
        if type(elem.output.voltageValue) ==str:
            #find output voltage
            voltage2=data.solution[data.needToSolve.index(elem.output)]
        else: voltage2 =elem.output.voltageValue
        #record it
        elem.voltage = voltage1-voltage2
    else: elem.voltage = None

#store the info
def storeValue(data):
    for elem in data.source+data.resistor:
        #not connected 
        if len(elem.input.outputElem|elem.input.inputElem)<=1 or\
           len(elem.output.inputElem|elem.output.outputElem)<=1:
            if elem.elemType=="Resistor": elem.current=elem.voltage=None
            elif elem.elemType == "Voltage Source": elem.current = None
            elif elem.elemType=="Current Source": elem.voltage = None
            continue
        #record resistor info
        if elem.elemType == "Resistor":
            recordResistor(elem,data)
        #record voltage source info
        elif elem.elemType == "Voltage Source":
            if elem in data.needToSolve:
                elem.current = data.solution[data.needToSolve.index(elem)]
            else: elem.current = None
        #record current source info
        else:
            recordCurrent(elem,data)

#find the elements in the element list
def findElement(element,data):
    for elem in data.source + data.resistor:
        if elem == element:
            #found it and return it
            return elem

#create circle for the demo
def createCircle(data,current,inputNode,outputNode):
    #create the circles in the demo
    if outputNode.row<inputNode.row:
        for row in range(inputNode.row-1,outputNode.row,-1):
            #create node by node
            data.circleDir.append(
    Circle(inputNode,outputNode,row,inputNode.col,current*2**data.multiply))
    else:
        for row in range(inputNode.row+1,outputNode.row):
            #loop and create
            data.circleDir.append(
    Circle(inputNode,outputNode,row,inputNode.col,current*2**data.multiply))
    if outputNode.col<inputNode.col:
        #loop and create
        for col in range(inputNode.col-1,outputNode.col,-1):
            data.circleDir.append(
    Circle(inputNode,outputNode,outputNode.row,col,current*2**data.multiply))
    else:
        for col in range(inputNode.col+1,outputNode.col):
            data.circleDir.append(
    Circle(inputNode,outputNode,outputNode.row,col,current*2**data.multiply))

#demo circles    
class Circle(object):
    def __init__(self,inputNode,outputNode,row,col,current):
        #record current
        self.current = current
        self.startX = col*10*2+10*10/2; self.col = col
        self.startY = row*10*2+10*10+10*10/2; self.row = row
        self.dx =0; self.dy =0
        #decide current
        if current>0: self.positiveInit(col,row,inputNode,outputNode)
        else: self.negativeInit(col,row,inputNode,outputNode) 
        self.x = self.startX; self.y = self.startY

    #positive current
    def positiveInit(self,col,row,inputNode,outputNode):
        #determine horizon and vertical movement of the circle
        if col==inputNode.col and row == outputNode.row:
            if col<outputNode.col:
                self.speedX = self.current; self.speedY =0
            else: self.speedX = -self.current; self.speedY =0
        #case 1
        elif col== inputNode.col:
            if row<outputNode.row:
                self.speedY = self.current; self.speedX=0
            else:
                self.speedY = -self.current; self.speedX =0
        #case 2
        elif row == outputNode.row:
            if col < outputNode.col:
                self.speedX = self.current; self.speedY =0
            else:
                self.speedX = -self.current; self.speedY =0

    #negative current
    def negativeInit(self,col,row,inputNode,outputNode):
        #case 1
        if row== outputNode.row and col == inputNode.col:
            if row <inputNode.row:
                self.speedY = self.current; self.speedX = 0
            else: self.speedY = -self.current; self.speedX= 0
        #case 2
        elif row == outputNode.row:
            if col <inputNode.col: self.speedX = -self.current; self.speedY=0
            else: self.speedX = self.current; self.speedY =0
        #determine horizontal and vertical motion
        elif col == inputNode.col:
            if row<inputNode.row: self.speedY = -self.current; self.speedX =0
            else: self.speedY =self.current; self.speedX =0
            
    def draw(self,canvas):
        #draw the circles 
        canvas.create_oval(self.x-2,self.y-2,self.x+2,self.y+2,fill="blue",
                           outline= "blue")

    def move(self):
        if self.speedX!=0:
            #move horizontally
            if self.speedX>0:
                self.dx = (self.dx+self.speedX) %(10*2)
                self.x = self.startX+self.dx
            else:
                #record increment
                self.dx = (self.dx+abs(self.speedX))%(10*2)
                self.x = self.startX - self.dx
        elif self.speedY!=0:
            #move vertically
            if self.speedY <0:
                self.dy = (self.dy-self.speedY) %(10*2)
                self.y = self.startY- self.dy
            else:
                #record increment
                self.dy = (self.dy+abs(self.speedY))%(10*2)
                self.y = self.startY + self.dy
                
    def __repr__(self):
        #human readable info
        return "%s,%s" %(self.row,self.col)

#for each elem, update the current
def updateCurrent(elem,gatherCurrent,connectedNode):
    if elem.current == None: return gatherCurrent
    if type(elem) == Resistor:
        #gather current updated
        if elem.input == connectedNode: gatherCurrent += elem.current
        else: gatherCurrent -= elem.current
    elif elem.elemType == "Voltage Source":
        #voltage source connected
        if elem.input==connectedNode: gatherCurrent += elem.current
        else: gatherCurrent -= elem.current
    else:
        #current source connected
        if elem.input == connectedNode: gatherCurrent += elem.current
        else: gatherCurrent -= elem.current
    return gatherCurrent

#determine current from one node to the other
def determineCurrent(data,node,connectedNode):
    if len(connectedNode.elem & node.elem) >0:
        #if two nodes share the same element
        for element in connectedNode.elem & node.elem:
            elem = findElement(element,data)
        if elem.current ==None: return None
        inputNode=elem.input;outputNode=elem.output;gatherCurrent=elem.current
    else:
        # two nodes connected by wire
        union=connectedNode.inputElem|connectedNode.outputElem
        elemAssoc=union - node.elem; gatherCurrent =0
        for element in elemAssoc:
            elem = findElement(element,data)
            gatherCurrent = updateCurrent(elem,gatherCurrent,connectedNode)
    return gatherCurrent
    
def timerFired(data):
    if data.demo== True and data.solution != None:
        if data.circleCreated== False:
            for node in data.forwardConnected:
                for connectedNode in data.forwardConnected[node]:
                    #determine current
                    gatherCurrent = determineCurrent(data,node,connectedNode)
                    if gatherCurrent == None: continue
                    createCircle(data,gatherCurrent,node,connectedNode)
            #finished creating demo circle
            data.circleCreated = True
        #move the circles
        for circle in data.circleDir:
            circle.move()
                         
class MyDialog(tkinter.simpledialog.Dialog): #adapted from Kosbie's notes
    def __init__(self, parent, elemType,title = None):
        #record elemType
        self.elemType = elemType
        Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        #create button
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    #ask for input
    def body(self, master):
        canvas.data["modalResult"] = None
        #determine elemType
        if self.elemType =="Voltage Source":            
            Label(master, text="Create a voltage source (V):").grid(row=0)
        elif self.elemType == "Current Source":
            Label(master, text="Create a current source (A):").grid(row=0)
        elif self.elemType == "Resistor":
            Label(master, text="Create a resistor (Ohms):").grid(row=0)
        #get value
        self.e1 = Entry(master)
        self.e1.grid(row=0, column=1)
        return self.e1 # initial focus

    #check if a value is valid
    def ok(self, event=None):
        #if the value is valid
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        #apply
        self.apply()
        self.cancel()

    #if user doesn't want to input
    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #check if the input is valid
    def validate(self):
        try:
            #good input
            first = float(self.e1.get())
            global canvas
            canvas.data["modalResult"] = first
            return True
        except:
            #failed
            tkMessageBox.showwarning("Warning!","Please enter a valid value")
            return False

    #apply user input
    def apply(self):
        return float(self.e1.get())

##test function
def testFindElem(data):
    element0 = Resistor(10*10,10*10,"Resistor",None,None,None)
    element1 = Resistor(10*10*2,10*10*2,"Resistor",None,None,None)
    element = Resistor(10*10*(2+1),10*10*(2+1),"Resistor",None,None,None)
    data.resistor.extend([element0,element1,element])
    assert(findElement(Resistor(10*10,10*10,"Resistor",Node(1,2),
        None,None),data)==element0)
    assert(findElement(Resistor(10*10*2,10*10*2,"Resistor",None,
            Node(2,2+1),None),data)==element1)
    assert(findElement(Resistor(10*10*(2+1),10*10*(2+1),"Resistor",None,
                Node(2+1,2+2),None),data)==element)
    
##run function

def run(width = 1000, height = 800): #parts adapted from kosbie's notes
    #draw
    def redrawAllWrapper(canvas,data):
        canvas.delete(ALL)
        redrawAll(canvas,data)
        canvas.update()
    #mouse events
    def mouseMotionWrapper(event,canvas,data):
        mouseMotion(event,data)
        redrawAllWrapper(canvas,data)
    
    def leftMousePressedWrapper(event,canvas,data):
        leftMousePressed(event,data)
        redrawAllWrapper(canvas,data)

    def leftMouseMovedWrapper(event,canvas,data):
        leftMouseMoved(event,data)
        redrawAllWrapper(canvas,data)
        
    def leftMouseReleasedWrapper(event,canvas,data):
        leftMouseReleased(event,data)
        redrawAllWrapper(canvas,data)

    def rightMousePressedWrapper(event,canvas,data):
        rightMousePressed(event,data)
        redrawAllWrapper(canvas,data)

    def rightMouseMovedWrapper(event,canvas,data):
        rightMouseMoved(event,data)
        redrawAllWrapper(canvas,data)
        
    def rightMouseReleasedWrapper(event,canvas,data):
        rightMouseReleased(event,data)
        redrawAllWrapper(canvas,data)
    #key events
    def keyPressedWrapper(event, canvas,data):
        keyPressed(event, data)
        redrawAllWrapper(canvas,data)
    #timer fired 
    def timerFiredWrapper(canvas,data):
        timerFired(data)
        redrawAllWrapper(canvas,data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas,data)
        
    # create the root and the canvas
    class Struct(object): pass
    data = Struct()
    global data
    #global data
    data.width = width; data.height = height
    data.timerDelay = 100
    init(data)
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    canvas = Canvas(root, width=data.width, height=data.height)
    global canvas
    # Store canvas in root and in canvas itself for callbacks
    root.canvas = canvas.canvas = canvas
    canvas.data = {}
    canvas.pack(fill= BOTH,expand=YES)
    #load all the images
    background = PhotoImage(file = "PCB.gif")
    title =PhotoImage(file = "title.gif"); name = PhotoImage(file = "name.gif")
    solveCircuit = PhotoImage(file ="solve a circuit.gif")
    instruction = PhotoImage(file = "instructions.gif")
    new = PhotoImage(file = "new.gif"); exit = PhotoImage(file = "exit.gif")
    solve = PhotoImage(file = "solve.gif"); help = PhotoImage(file = "help.gif")
    demo = PhotoImage(file = "demo.gif")
    speed =PhotoImage(file="currentspeed.gif")
    canvas.data["bg"] = background.zoom(2+2,2+2)
    canvas.data["title"] = title.zoom(2,2)
    canvas.data["name"] = name; canvas.data["solveCircuit"] = solveCircuit
    canvas.data["instructions"] = instruction; canvas.data["new"]= new
    canvas.data["exit"] = exit; canvas.data["demo"] = demo
    canvas.data["solve"] = solve; canvas.data["help"] = help
    canvas.data["speed"] = speed
    #testFindElem(data)
    #set up events
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event,canvas, data))
    root.bind("<Button-1>", lambda event:
                            leftMousePressedWrapper(event,canvas,data))
    canvas.bind("<Motion>", lambda event:
                            mouseMotionWrapper(event,canvas,data))
    canvas.bind("<B1-Motion>", lambda event:
                leftMouseMovedWrapper(event,canvas,data))
    root.bind("<Button-3>", lambda event:
                      rightMousePressedWrapper(event,canvas,data))
    root.bind("<B1-ButtonRelease>", lambda event:
              leftMouseReleasedWrapper(event,canvas,data))
    canvas.bind("<B3-Motion>", lambda event:
                rightMouseMovedWrapper(event,canvas,data))
    root.bind("<B3-ButtonRelease>", lambda event:
              rightMouseReleasedWrapper(event,canvas,data))
    timerFiredWrapper(canvas,data)
    # and launch the app
    root.mainloop()
run(1000,800)
