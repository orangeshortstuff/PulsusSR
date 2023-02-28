with open("disk 1.txt", "r") as f:
    notes = f.read()
notes = notes.split("\n")
for i in range(len(notes)): # get note data - position, time, hold, hold time (if a hold)
    temp = notes[i][1:-1].split(",")
    notes[i] = [int(temp[0]),int(float(temp[1])*1000),bool(temp[2]),int(float(temp[3])*1000)]

strain_notes = []
hand = True
hold_stack = []
strain_exp = [1,1]
current_strain = [0,0]
note_strain = 0
map_length = 0 # currently unused - think i took a different approach for the section pass
for i in range(len(notes)): # handing / strain pass - add pattern buffs later
    note = notes[i] # get current note

    # check and remove holds that have been released
    hold_stack = [x for x in hold_stack if x > note[1]]

    if note[0]%3 == 0 and hand:
        hand = False # lh
    if note[0]%3 == 2 and not hand:
        hand = True # rh
    
    if i != 0:
        if notes[i-1][1] + 20 > note[1]: # chord detection, with a small chording window
            current_strain[hand] = max(current_strain[hand] / 2, 0.5)
        else: # do strain right
            strain_exp[hand] = (note[1] - notes[i-1][1]) / 1000
            current_strain[hand] *= (0.6 ** strain_exp[hand])
            current_strain[hand] += (5 + ((len(hold_stack) / 1.5))) / 10
    note_strain = current_strain[hand]
    
    if note[2]: # hold
        hold_stack.append(note[1] + note[3])
        map_length = max((note[1] + note[3]), map_length)
    else:
        map_length = max(note[1], map_length)

    strain_notes.append([note_strain * (not hand), note_strain * hand])
    notes[i].append(hand)

note_times = [note[1] for note in notes] # only time values
note_hands = [note[4] for note in notes]
start, end = min(note_times), max(note_times)
section_strains = []
section = []

while start <= end: # section pass
    section = [x for x in note_times if (start <= x < start + 400)]
    current_strain = [0,0]
    for note in section:
        note_id = note_times.index(note)
        hand = notes[note_id][4]
        current_strain[hand] += strain[note_id][hand]
    section_strains.append((current_strain[0]**1.25)+(current_strain[1]**1.25)**0.8)
    start += 400

section_strains.sort(reverse=True)
section_strains = [x for x in section_strains if x > 0]

for i in range(len(section_strains)):
    section_strains[i] *= 0.92**i

print(sum(section_strains))
    
