import math

matplot = True #True for on, False for off. Obviously. You don't need me telling you this wtf am I doing

map_file = input("map? ")
with open(f"examples/{map_file}.txt", "r") as f:
    notes = f.read()
notes = notes.split("\n")
notes = [x for x in notes if x != ""]
rate = float(input("rate? "))
rate = min(max(rate, 0.5), 2)
for i in range(len(notes)):
    temp = notes[i][1:-1].split(",")
    notes[i] = [int(temp[0]),int(float(temp[1])*(1000/rate)),(temp[2] == "1"),int(float(temp[3])*(1000/rate))]

finPos = [[4,4],[4,4]]
rolled = [True,True]
finStrain = [[0,0],[0,0]]
chordStrain = [[0,0],[0,0]]
currentHand = True
currentFin = True
sectionInterval = notes[0][1]
section = []
sectionStrains = []
prevUse = [[-1,-1],[-1,-1]] #The times in which the finger was last used
prevMove = [[False,0,0],[False,0,0]] #If the nerf was just triggered, horiz, vert movement
lastFin = [-1,-1]
averageStrain = [0,0,0,0,0,0,0,0,0,0] #Gives a VERY slight bonus based on the general difficulty of previous sections. Used to buff long, difficult parts.
strainBonus = 0
decayFactor = 1.5
holdInd = []
finMap = []
holdStack = [[],[]]
graphSection = []
graphFins = []
graphFinStrains = []
graphAverageStrain = []
notesC = [0] #Chord detection
cos = math.cos
pi = math.pi
e = math.e

for i in range(len(notes)):
    notes[i].append(1)
    notes[i].append(i)
    if notes[i][2] == True:
        notes.append([notes[i][0], notes[i][1] + notes[i][3], False, 0, 0.6, i])
notes.sort(key=lambda elem: elem[1])
holdInd = [ind[5] for ind in notes]

for i in range(len(notes)): #Chord detection / add releases
    if i > 0:
        if notes[i-1][1] + 10 > notes[i][1]:
            notesC.append(1)
        else:
            notesC.append(0)

def Resection(a):
    global sectionInterval, section, finStrain, currentFin, graphFins, strainBonus

    if notes[a][1] >= sectionInterval + 400:
        graphSection.append(sectionInterval)
        sectionInterval += 400
        if len(section) == 0:
            section.append(0)
            graphFins.append([0,0,0,0])
        sectionStrains.append(sum(section) / len(section))
        graphFinStrains.append([sum([x[0] for x in graphFins]) / len(graphFins),
                                sum([x[1] for x in graphFins]) / len(graphFins),
                                sum([x[2] for x in graphFins]) / len(graphFins),
                                sum([x[3] for x in graphFins]) / len(graphFins)])
        del averageStrain[0]
        averageStrain.append(sum(section) / len(section))
        graphAverageStrain.append(sum(averageStrain) / len(averageStrain))
        strainBonus = (1 + ((sum(averageStrain) / len(averageStrain)) ** 0.5 * 0.02))
        section = []
        graphFins = []
        Resection(a)

def DivZero(n, d):
    return n / d if d else 0

def Patterning(a):
    global finPos, currentHand, currentFin, rolled, lastFin, patternBonus, holdStack, finMap, finStrain

    testStrain = [[],[],[],[]]
    currentStrains = [[],[],[],[]]
    savedValues = []
    notePos = notes[a][0]

    holdStack = [[x for x in holdStack[0] if x[1] > (notes[a][1] + 10)],[x for x in holdStack[1] if x[1] > (notes[a][1] + 10)]]
    holdStackApp = [[x for x in holdStack[0] if x[0] < (notes[a][1] - 10)],[x for x in holdStack[1] if x[0] < (notes[a][1] - 10)]] #Applicable holdStack, takes out notes too close to the starting point of the hold.

    if a > 0:
        dt = (notes[a][1] - notes[a - 1][1]) / 1000
        for b in range(4): # per finger decay
            if finStrain[(b % 2)][math.floor(b / 2)] > 0:
                finStrain[(b % 2)][math.floor(b / 2)] = (decayFactor / ((dt) + (decayFactor / finStrain[(b % 2)][math.floor(b / 2)])))

    if a > 1: #Rhythm bonus
        rratio = DivZero((notes[a-1][1] - notes[a-2][1]), (notes[a][1] - notes[a-1][1]))
        rbonus = (cos(1*pi*rratio)**8)-(cos(2*pi*rratio)**8)-(cos(3*pi*rratio)**8)-(cos(4*pi*rratio)**8)
        nerf = 1 + ((e**(e*-((rratio-1)**2)/(0.5**2))) - (2*e**(e*-((rratio-1)**2)/(0.125**2))))
        rhythmBonus = ((rbonus+(0.5*nerf))/16+1.125)**1.3
    else:
        rhythmBonus = 1

    if (notes[a][4] < 1) and (a < (len(notes) - 1)): #Nerf hold ends if close to another note. Funnily enough also affects tap holds (how convenient!). Eventually it should probably get changed to a ratio, though.
        if ((notes[a][1] - notes[a-1][1]) < 10) or ((notes[a+1][1] - notes[a][1]) < 10):
            notes[a][4] /= 3

    if holdInd.index(holdInd[a]) != a: #Uses the correct finger if it's a release.
        appliedFin = finMap[holdInd.index(holdInd[a])]
        currentHand = math.floor(appliedFin / 2)
        currentFin = (appliedFin % 2)
        holdBonus = 1 + ((len(holdStackApp[currentHand]) ** 1.5) * 2.5)
        patternBonus = holdBonus
    else:
        for b in range(4): #Beginning of individual finger checks
            currentStrains[b] = [finStrain[0][0], finStrain[0][1], finStrain[1][0], finStrain[1][1]]
            currentHand = math.floor(b / 2)
            currentFin = (b % 2)
            cFinPos = finPos[currentHand][currentFin]
            if (currentFin != lastFin[currentHand]) and (not prevMove[currentHand][0]):
                finHoriz = ((cFinPos % 3) - prevMove[currentHand][1]) - (notePos % 3)
                finVert = (math.floor(cFinPos / 3) - prevMove[currentHand][2]) - math.floor(notePos / 3)
            else:
                finHoriz = (cFinPos % 3) - (notePos % 3)
                finVert = math.floor(cFinPos / 3) - math.floor(notePos / 3)
            finDistance = (((abs(finHoriz) ** 2) + (abs(finVert) ** 2)) ** 0.5)
            #print(str(finVert) + "   " + str(finHoriz) + "   " + str(finDistance))

            movementBonus = 1
            patternBonus = 1
            holdBonus = 1 + ((len(holdStackApp[currentHand]) ** 1.5) * 2.5)

            if (currentFin != lastFin[currentHand]) and (not rolled[currentHand]):
                rollNerf = 0.85*(1-(0.1**dt))+0.15
            else:
                rollNerf = 1

            if prevUse[currentHand][currentFin] > 0: #Movement bonus
                timeDiff = (notes[a][1] - prevUse[currentHand][currentFin])
                movementBonus = 1 + (finDistance/(1 + ((timeDiff / 100) ** 1.5)))

            patternBonus = rollNerf * movementBonus * holdBonus

            #print(str(patternBonus) + "     " + str(rollNerf) + "   " + str(movementBonus) + "   " + str(rhythmBonus) + "   " + str(holdBonus))
            currentStrains[b][b] += (0.5 * patternBonus)
            testStrain[b] = (((((currentStrains[b][0] ** exp) + (currentStrains[b][1] ** exp)) ** exp2) + (((currentStrains[b][2] ** exp) + (currentStrains[b][3] ** exp)) ** exp2)) ** (1/(exp * exp2))) #Strain bonus not necessary here.
            savedValues.append([patternBonus, finHoriz, finVert])

        appliedFin = testStrain.index(min(testStrain))
        currentHand = math.floor(appliedFin / 2)
        currentFin = (appliedFin % 2)
        patternBonus = savedValues[appliedFin][0] * rhythmBonus

        if lastFin[currentHand] != currentFin:
            rolled[currentHand] = not rolled[currentHand]
        else:
            rolled[currentHand] = False

        if prevMove[currentHand][1] != currentFin:
            prevMove[currentHand] = [not prevMove[currentHand][0], savedValues[appliedFin][1], savedValues[appliedFin][2]]
        else:
            prevMove[currentHand] = [False, savedValues[appliedFin][1], savedValues[appliedFin][2]]

    finMap.append(appliedFin)

    if notes[a][2] == True:
        holdStack[currentHand].append([notes[a][1], notes[a][1] + notes[a][3]])

    finPos[currentHand][currentFin] = notePos
    prevUse[currentHand][currentFin] = notes[a][1]
    lastFin[currentHand] = currentFin

exp = 2
exp2 = 1.2
for i in range(len(notes)):
    Patterning(i)
    Resection(i)
    graphFins.append([chordStrain[0][0], chordStrain[0][1], chordStrain[1][0], chordStrain[1][1]])
    section.append(((((chordStrain[0][0] ** exp) + (chordStrain[0][1] ** exp)) ** exp2) + (((chordStrain[1][0] ** exp) + (chordStrain[1][1] ** exp)) ** exp2)) ** (1/(exp * exp2)) * strainBonus)
    if notesC[i] == 0:
        chordStrain = [[finStrain[0][0], finStrain[0][1]], [finStrain[1][0], finStrain[1][1]]]
    finStrain[currentHand][currentFin] += 0.5 * patternBonus * notes[i][4]

graphSection = [x/1000 for x in graphSection]
graphCombStrain = [x for x in sectionStrains]

sectionStrains.sort(reverse=True)
sectionStrains = [x for x in sectionStrains if x > 0]

for i in range(len(sectionStrains)):
    sectionStrains[i] /= (2 + (i ** 1.4))

starRating = (sum(sectionStrains) ** 1.36) * 0.38

print(starRating)
print(sum(sectionStrains))

if matplot:
    import matplotlib.pyplot as plt
    plt.figure()
    plt.title("Strain over time for {} ({}x rate)".format(map_file, rate))
    plt.xlabel("Section start (seconds)")
    plt.ylabel("Strain")
    plt.plot(graphSection, graphCombStrain, ':', c="#D9D9D9", label="Raw strain")
    plt.plot(graphSection, graphAverageStrain, '-.', c="#666666", label="Average Strain")
    plt.plot(graphSection, [x[0] for x in graphFinStrains], color="blue", label="L1")
    plt.plot(graphSection, [x[1] for x in graphFinStrains], color="green", label="L2")
    plt.plot(graphSection, [x[2] for x in graphFinStrains], color="red", label="R1")
    plt.plot(graphSection, [x[3] for x in graphFinStrains], color="orange", label="R2")
    plt.legend()
    plt.show()
else:
    input()
