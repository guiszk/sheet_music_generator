from random import choice, randint

def makeprog(numbars):
    c = 'A A# B C C# D D# E F F# G G#'.split()
    c1 = ['7', 'maj7', 'o', 'ø', '']

    res = ''
    first_chord = ''
    first_mod = ''

    i = 0
    while i < numbars:
        if i == 0:
            first_chord = choice(c)
            first_mod = choice(['7', 'M7', 'm7', 'm', ''])
            res += first_chord + first_mod + ' ' 
            i += 1
        else:
            ch = choice(c)
            modch = choice(c1)

            if (randint(1, 100) < 70 and numbars - i > 2):  # 70% chanve de 251 se tiver 2+ compassos
                if numbars - i == 3:
                    ch = first_chord  
                if randint(1, 100) < 70:
                    res += c[(c.index(ch) + 2) % 12] + 'ø '  # 251 maior
                    res += c[(c.index(ch) + 7) % 12] + '7 '
                    res += ch + 'm '
                else:
                    res += c[(c.index(ch) + 2) % 12] + 'm '  # 251 menor
                    res += c[(c.index(ch) + 7) % 12] + '7 '
                    res += ch + ' '
                i += 3  
            elif numbars - i > 1 and i != 0:  # V - I se tiver 1+ compassos
                if numbars - i == 2:
                    ch = first_chord  
                res += c[(c.index(ch) + 7) % 12] + '7 '
                res += ch + choice(['m ', ' '])
                i += 2  
            else:  
                if i == numbars - 1: # se último
                    res += first_chord + first_mod  
                else: #aleatório
                    res += ch + choice(['m ', ' '])  
                i += 1  #

    newres = ''
    
    for i in range(len(res.strip().split())):
        if i%2 == 0 and i != 0:
            newres += '| ' + res.split()[i] + ' '
        else:
            newres += res.split()[i] + ' '

    return newres  