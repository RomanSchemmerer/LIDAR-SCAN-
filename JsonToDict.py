import json 
from pprint import pprint 

ASYS = 0
OFEN = 0
SMD1 = 0
SMD2 = 0
Aufsteller = 0
Boden = 0
Decke = 0
FL = 0
ME = 0
Palette = 0
Person = 0
PS = 0
Rohr = 0
RW = 0
Sg = 0
Glas = 0
SO = 0
SW = 0
SS = 0
TB = 0
Tuer = 0
Wand = 0

for x in range(100, 110, 5):
    try:
        with open('Color_%d.json'%x) as f:
            dict = json.load(f)
            text = str(dict.get('shapes'))

            ASYS = ASYS + text.count('Anlage ASYS')
            OFEN = OFEN + text.count('Anlage Ofen')
            SMD1 = SMD1 + text.count('Anlage SMD 1')
            SMD2 = SMD2 + text.count('Anlage SMD 2')
            Aufsteller = Aufsteller + text.count('Aufsteller')
            Boden = Boden + text.count('Boden')
            Decke = Decke + text.count('Decke')
            FL = FL + text.count('Feuerloescher')
            ME = ME + text.count('Muelleimer')
            Palette = Palette + text.count('Palette')
            Person = Person + text.count('Person')
            PS = PS + text.count('Platinen Store')
            Rohr = Rohr + text.count('Rohr')
            RW = RW + text.count('Rollwagen')
            Sg = Sg+ text.count('Schrank geschlossen')
            Glas = Glas + text.count('Schrank Glas')
            SO = SO + text.count('Schrank offen')
            SW = SW + text.count('Servicewagen')
            SS = SS + text.count('SMD Store')
            TB = TB + text.count('Transportbox')
            Tuer = Tuer + text.count('Tuer')
            Wand = Wand + text.count('Wand')
            
            text = 'Zeroooooo'
            f.close()
    except:
        print("Number %d is not available" %x)

print("Anlage ASYS: %d\nAnlage Ofen: %d\nAnlage SMD 1: %d\nAnlage SMD 2: %d\nAufsteller: %d\nBoden: %d\nDecke: %d\nFeuerloescher: %d\nMuelleimer%d\nPalette: %d\nPerson: %d\nPlatinen Store: %d\nRohr: %d\nRollwagen: %d\nSchrank geschlossen: %d\nSchrank Glas: %d\nSchrank offen: %d\nServicewagen: %d\nSMD Store: %d\nTransportbox: %d\nTuer: %d\nWand: %d\n" %(ASYS, OFEN, SMD1, SMD2, Aufsteller, Boden, Decke, FL, ME, Palette, Person, PS, Rohr, RW, Sg, Glas, SO, SW, SS, TB, Tuer, Wand ))


