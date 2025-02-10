from flask import Flask, render_template, request, send_file
from music21 import *
import os
from random import choice
from midi2audio import FluidSynth
import uuid
from makeprog import makeprog

app = Flask(__name__)
fluidsynth = FluidSynth('upright.sf2')


us = environment.UserSettings()
us['musicxmlPath'] = './mscore'
us['musescoreDirectPNGPath'] = './mscore'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        randchords = request.form.get('randchords') == 'on'
        numbars = int(request.form['numbars'])
        if(randchords):
                strtest = ''
                strtest += makeprog(numbars*2) + ' '
        else:
            strtest = request.form['strtest']
            strtest = strtest if strtest else 'C A7 Dm7 G7'
        
        twelvetone = request.form.get('twelvetone') == 'on'
        usescale = request.form.get('usescale') == 'on'
        quarteronly = request.form.get('quarteronly') == 'on'
        repeat = int(request.form['repeat'])
        
        try:
            resname = save_scale_image(strtest, usescale=usescale, twelvetone=twelvetone, quarteronly=quarteronly, repeat=repeat)
        except Exception as e:
            return render_template('index.html', image=None, strtest=strtest, usescale=usescale, repeat=repeat, err=str(e))
        
        #resname = save_scale_image(strtest, usescale=usescale, twelvetone=twelvetone, quarteronly=quarteronly, repeat=repeat)
        return render_template('index.html', image='result-1.png', audio=resname, strtest=strtest, usescale=usescale, repeat=repeat)
    return render_template('index.html', image=None, audio='out.wav')

def build_scale(strs, i, k):
    pitchListStrs = strs.split()
    pitchList = [pitch.Pitch(p) for p in pitchListStrs]
    NewScale = scale.AbstractScale()
    
    p12 = scale.AbstractScale.fixDefaultOctaveForPitchList(pitchList)
    
    NewScale.buildNetworkFromPitches(pitchList)
    return NewScale._net.realizePitch(i.replace(k, ''))

def save_scale_image(chr, usescale=True, twelvetone=False, quarteronly=False, repeat=1):
    scale_stream = stream.Stream()
    scale_stream.insert(0, clef.TrebleClef())

    if not quarteronly:
        vals = [1, 2, 4]
    else:
        vals = [4]

    for _ in range(repeat):
        if not twelvetone:
            lastchr = ''
            for i in chart_translate(chr):
                if(usescale):
                    print(i)
                    if('m' in i or 'm7' in i or '-' in i):
                        scale_notes = scale.MinorScale(i.replace('m7', '').replace('7', '').replace('m', '').replace('-', ''))
                    elif('M7' in i):
                        scale_notes = scale.MajorScale(i.replace('M7', '').replace('M', ''))
                    elif('7' in i):
                        AltScale = build_scale('C C# D D# E F# G G# A A#', i, '7')
                  
                        scale_notes = choice([scale.MixolydianScale(i.replace('7', '')),  AltScale])
                    elif('o' in i):
                        scale_notes = build_scale('C D D# F F# G# A B', i, 'o')
                    #elif('ø' in i):
                    else:
                        scale_notes = build_scale('C D D# F F# G# A A#', i, 'ø')
                   
                        
                else:
                    cpitches = harmony.ChordSymbol(i.replace('-', 'm').replace('b', '-').replace('o', 'dim').replace('ø', 'dim7')).pitches
                   
                    scale_notes = []
                    
                    for _, p in enumerate(cpitches):
                        newp = p.transpose('P8')
                        scale_notes.append(newp)
                        scale_notes.append(newp.transpose('P8'))

                    
                if(usescale):
                    try:
                        scale_notes = scale_notes.getPitches()
                    except:
                        pass
                chosen = choice(vals)
                for j in range(chosen):
                    newnote = note.Note(choice(scale_notes), quarterLength=2/chosen)
                    if(j == 0):
                        if(i != lastchr):
                            newnote.addLyric(i)
                    scale_stream.append(newnote)
                lastchr = i
        else:
            scale_notes = scale.ChromaticScale().getPitches()
            chosen = choice(vals)
            for _ in range(chosen):
                newnote = note.Note(choice(scale_notes), quarterLength=2/chosen)
                scale_stream.append(newnote)
    scale_stream.write('musicxml.png', fp='result')
    scale_stream.write('midi', fp='resultmidi.mid')
    fluidsynth.midi_to_audio("resultmidi.mid", "out.wav")
    clearstatic()
    wavfilename = str(uuid.uuid4())[:8] + '.wav'
    os.rename('out.wav', 'static/'+wavfilename)
    os.rename('result-1.png', 'static/result-1.png')
    return wavfilename

def clearstatic():
    path = 'static'
    files = os.listdir(path)
    
    # Iterate over each file and delete it
    for file_name in files:
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

def chart_translate(chr):
    allchr = chr.split('|')
    res = []
    for i in allchr:
        if(len([k for k in i.split(' ') if k]) == 1):
            if i:
                res += [i, i]
        else:
            for j in i.split(' '):
                if j:
                    res += [j]
    return res

if __name__ == '__main__':
    app.run(debug=True)
