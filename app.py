from flask import Flask, render_template, request, send_file, send_from_directory
from music21 import *
import os
from random import choice
from midi2audio import FluidSynth
import re
import uuid
from makeprog import makeprog

app = Flask(__name__)
fluidsynth = FluidSynth()


us = environment.UserSettings()
us['musicxmlPath'] = '/usr/bin/mscore'
us['musescoreDirectPNGPath'] = '/usr/bin/mscore'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        randchords = request.form.get('randchords') == 'on'
        numbars = int(request.form['numbars'])
        if(randchords):
                strtest = ''
                strtest += makeprog(numbars*2) + ' '
        else:
            strtest = ''
            for i in request.form['strtest'].replace('-', 'm').split('|'):
                for j in i.split():
                    strtest+=j[0].capitalize()+j[1:]
                    strtest+= ' '
                strtest+= '| '
        
        twelvetone = request.form.get('twelvetone') == 'on'
        usescale = request.form.get('usescale') != 'on'
        quarteronly = request.form.get('quarteronly') == 'on'
        repeat = int(request.form['repeat'])
        
        try:
            resname = save_scale_image(strtest, usescale=usescale, twelvetone=twelvetone, quarteronly=quarteronly, repeat=repeat)
        except Exception as e:
            return render_template('index.html', image=None, strtest=strtest, usescale=usescale, repeat=repeat, err=str(e))
        return render_template('index.html', image='result-1.png', audio=resname, strtest=strtest, usescale=usescale, repeat=repeat)
    return render_template('index.html', image=None, audio='out.wav')

UPLOAD_FOLDER = os.path.join(os.getcwd()) 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
                i = i.strip()
                if(usescale): #use scales
                    print("use scale: ", i)

                    scale_notes = get_scale(i)
                    print(scale_notes)
                else: #use chord tones
                    cpitches = harmony.ChordSymbol(i.replace('maj7', '').replace('-', 'm').replace('b', '-').replace('o', 'dim').replace('ø', 'dim7')).pitches
                    print(i, cpitches)

                    scale_notes = []

                    for _, p in enumerate(cpitches):
                        newp = p.transpose('P8')
                        scale_notes.append(newp)
                        scale_notes.append(newp.transpose('P8'))
                    print(scale_notes)

                chosen = choice(vals)
                for j in range(chosen):
                    newnote = note.Note(choice(scale_notes), quarterLength=2/chosen)
                    if(j == 0):
                        if(i != lastchr):
                            newnote.addLyric(i)
                    scale_stream.append(newnote)
                lastchr = i
        else: #if twelvetone
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

def get_scale(chord):
    basematch = r'^[A-G][#b]?'
    print("get scale", chord)
    root_note = re.match(basematch, chord).group(0) if re.match(basematch, chord) else ''
    print("get root", root_note)
    
    major_pattern = r'^[A-G][#b]?(maj|M)+(7|9|#11|13)?$'
    minor_pattern = r'^[A-G][#b]?(m|-)(7|6|9|11|13)?$'
    dominant_pattern = r'^[A-G][#b]?7$'
    sus_pattern = r'^[A-G][#b]?7sus(2|4)?$'
    diminished_pattern = r'^[A-G][#b]?(dim|diminished|o)$'
    half_diminished_pattern = r'^[A-G][#b]?(halfdim|half-diminished|half-dim|m7b5|ø)$'
    altered_pattern = r'^[A-G][#b]?7?((#|b|)(5|9|11|13|\+|aug)){1,}$'
    
    if(root_note):
        if re.match(sus_pattern, chord):
            return build_scale('C D E G A A#', root_note, 'sus')
        
        if re.match(dominant_pattern, chord):
            return scale.MixolydianScale(root_note).getPitches()

        if re.match(half_diminished_pattern, chord):
            return build_scale('C D D# F F# G# A A#', root_note, 'ø')

        if re.match(minor_pattern, chord):
            return scale.DorianScale(root_note).getPitches()

        if re.match(diminished_pattern, chord):
            return build_scale('C D D# F F# G# A B', root_note, 'o')

        if re.match(altered_pattern, chord):
            return build_scale('C C# D D# E F# G G# A A#', root_note, '7')
        
        if re.match(major_pattern, chord):
            return scale.MajorScale(root_note).getPitches()
        
        return scale.MajorScale(root_note).getPitches()
    else:
        return scale.ChromaticScale(root_note).getPitches()

def clearstatic():
    path = 'static'
    files = os.listdir(path)
    
    for file_name in files:
        if not(file_name == "styles.css"):
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

class LengthExceededError(Exception):
    def __init__(self, message="Error: maximum length exceeded (256 chords)"):
        self.message = message
        super().__init__(self.message)

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
    
    if len(res) > 256:
        raise LengthExceededError(f"Result length is {len(res)}, which exceeds the allowed limit of 256.")
    
    return res


if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
