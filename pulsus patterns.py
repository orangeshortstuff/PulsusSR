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


first_hand = (notes[0][0] != 0)
hand = bool(first_hand)
hands = []
streak = 0
streaks = []
streak_total = [0]

for note in notes: # handing pass
    if (note[0]%3 == 0 and hand) or (note[0]%3 == 2 and not hand):
        hand = not hand
        streak_total += [streak+streak_total[-1]]
        streaks.append(streak)
        streak = 0
    hands.append(hand)
    streak += 1
if streak >= 1:
    hand = not hand
    streak_total += [streak+streak_total[-1]]
    streaks.append(streak)

for i in range(len(streaks)):
    if streaks[i] > 4: # convert to full alt
        for j in range(streak_total[i]+1,streak_total[i]+streaks[i],2):
            hands[j] = not hands[j]

streak = 0
streaks = []
streak_total = [0]

for i in range(len(hands)): # get the new streaks
    if (hands[i] != hands[i-1]) and i > 0:
        streak_total += [streak+streak_total[-1]]
        streaks.append(streak)
        streak = 0
    streak += 1
if streak >= 1:
    streak_total += [streak+streak_total[-1]]
    streaks.append(streak)


streak_multipliers = [0,1,0.85,1.15,1.3,1]
note_multipliers = []
hand = bool(first_hand)
meta_streaks = [[0 for i in range(5)],[0 for i in range(5)]]
hands = []

for streak in streaks: # pattern multipliers 
    multiplier = 0
    current_streak = 0
    for i in range(5):
        if streak == i + 1:
            current_streak = meta_streaks[hand][i] 
            meta_streaks[hand][i] += 1
        else:
            meta_streaks[hand][i] = max(0,meta_streaks[hand][i]-(2+(meta_streaks[hand][i]//3)))
    hands += [hand] * streak
    hand = not hand
    multiplier = (((0.9**(current_streak))+5)/6)**1 # crank the exponent up for lulz
    note_multipliers += [multiplier*streak_multipliers[streak]]*streak

#print(sum(note_multipliers)/len(note_multipliers))
hold_stack = []
strain_exp = [1,1]
current_strain = [0,0]
last_notes = [0,0]
note_strain = 0
section_start = 0
section_strains = []
section = []

for i in range(len(notes)): # strain pass
    note = notes[i]
    hand = hands[i]
    
    # check and remove holds that have been released
    hold_stack = [x for x in hold_stack if x > note[1]]
    
    if note[1] >= section_start + 400:
        section_strains.append(sum(section))
        section = []
        section_start = note[1]
    
    if i != 0:
        if notes[i-1][1] + 20 > note[1]: # chord detection, with a small chording window
            note_strain = (0.15 + current_strain[hand] / 1.2)
            last_notes[hand] = i
        else: # do strain right
            note_strain = current_strain[hand]
            vert_notes = [note[0]//3,notes[last_notes[hand]][0]//3]
            strain_exp[hand] = (note[1] - notes[last_notes[hand]][1]) / 1000
            current_strain[hand] += note_multipliers[i] * (4 + (5*len(hold_stack)) + (2*note[2])) \
                                    / ((15 + current_strain[hand]) - abs(vert_notes[0] - vert_notes[1]))
            current_strain[hand] *= (0.66 ** strain_exp[hand])
            last_notes[hand] = i
    else:
        note_strain = current_strain[hand] 
 
    if note[2] == True: # hold
        hold_stack.append(note[1] + note[3])

    section.append(note_strain)

section_strains.append(sum(section))

section_strains.sort(reverse=True)
section_strains = [x for x in section_strains if x > 0]

for i in range(len(section_strains)):
    section_strains[i] /= (4+i)

#print(sum(section_strains))
#"""
star_rating = (sum(section_strains)/2.4)**0.49
diff_pulse = (star_rating**2.1)*7/2
acc_pulse = (star_rating**2.5)*2
max_pulse = ( (diff_pulse**(1/1.1)) + (acc_pulse**(1/1.1)) ) ** 1.1
max_pulse *= 0.8+(( (len(notes) / (1+(star_rating**(1/3))) )**0.5)/100)
print(star_rating)
print(max_pulse)
#"""
input()
