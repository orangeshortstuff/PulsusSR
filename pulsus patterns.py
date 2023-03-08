map_file = input("map? ")
with open(f"examples/{map_file}.txt", "r") as f:
    notes = f.read()
notes = notes.split("\n")
notes = [x for x in notes if x != ""] # remove trailing newline
rate = float(input("rate? "))
rate = min(max(rate, 0.5), 2)
for i in range(len(notes)): # get note data - position, time, hold, hold time (if a hold)
    temp = notes[i][1:-1].split(",")
    notes[i] = [int(temp[0]),int(float(temp[1])*(1000/rate)),(temp[2] == "1"),int(float(temp[3])*(1000/rate))]

strain_notes = []
hand = True
hold_stack = []
strain_exp = [1,1]
current_strain = [0,0]
last_notes = [0,0]
note_strain = 0
map_length = 0
max_holds = 0
streak = 0
streak_multipliers = [0,0.9,0.8,1.05,1.2,0.9]
meta_streaks = [0,0]
last_streaks = [0,0]

for i in range(len(notes)): # handing / strain / pattern pass
    note = notes[i]

    # check and remove holds that have been released
    hold_stack = [x for x in hold_stack if x > note[1]]

    if (note[0]%3 == 0 and hand) or (note[0]%3 == 2 and not hand):
        
        if streak == last_streaks[hand]:
            meta_streaks[hand] += 1
            strain_notes, this_streak = strain_notes[:(streak * -1)], strain_notes[(streak * -1):]
            this_streak = [x * (0.92 ** meta_streaks[hand]) for x in this_streak]
            strain_notes += this_streak
            current_strain[hand] *= 0.92 ** meta_streaks[hand]
        else:
            meta_streaks[hand] = 0
        last_streaks[hand] = streak
        
        hand = not hand
        streak = 0

    streak += 1
    if streak > 4 and streak%2 == 1: # flip hands for 5th, 7th, etc
        hand = not hand

    if i != 0:
        if notes[i-1][1] + 20 > note[1]: # chord detection, with a small chording window
            current_strain[hand] = (0.15 + current_strain[hand] / 1.2)
        else: # do strain right
            vert_notes = [note[0]//3,notes[last_notes[hand]][0]//3]
            strain_exp[hand] = (note[1] - notes[last_notes[hand]][1]) / 1000
            current_strain[hand] += (4 + (len(hold_stack) * 2)) * (streak_multipliers[min(streak,4)]) / ((15+strain_notes[-1]) - abs(vert_notes[0] - vert_notes[1]))
            current_strain[hand] *= (0.66 ** strain_exp[hand])
            last_notes[hand] = i
    note_strain = current_strain[hand]

    if streak > 4 and streak%2 == 1:
        hand = not hand
 
    if note[2] == True: # hold
        hold_stack.append(note[1] + note[3])
        map_length = max(hold_stack[-1], map_length)
    else:
        map_length = max(note[1], map_length)

    strain_notes.append(note_strain)

note_times = [note[1] for note in notes]
start = min(note_times)
section_strains = []
section = []

while start <= map_length: # section pass
    section = [x for x in note_times if (start <= x < start + 400)]
    current_strain = 0
    for note in section:
        note_id = note_times.index(note)
        current_strain += strain_notes[note_id]
    section_strains.append(current_strain)
    start += 400

section_strains.sort(reverse=True)
section_strains = [x for x in section_strains if x > 0]
for i in range(len(section_strains)):
    section_strains[i] *= (0.92**i) # old method - may end up replacing with some form of line below
    #section_strains[i] /= (4+i)

#print(max(section_strains))
#print(sum(section_strains))
print(((sum(section_strains)/5.8)**0.52))
input()
