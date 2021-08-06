#!/usr/bin/env python3
# This is to help with German vocabulary
# From CSV data-set
# Richard Eseke 2021

import os, sys, time
import os.path
import csv, random
import gtts
from playsound import playsound

if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

MasterList = []
WertType = ["fragenwört", "adjektiv", "verb", "nomen", "adverb", "präposition", "konjunktion", "phrase"]
VerbeType = ["Nominativ", "Akkusativ", "Dativ", "Genitiv", "Akk-Dat"]
LangType = ['DE_LAG', 'KED_LAG', 'EN_LAG']

random.seed()

def get_data(Filename):
    global MasterList
    if os.path.isfile(Filename):
        try:
            with open(Filename, newline='', encoding='utf-8') as csvfile:
                GermanReader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in GermanReader:
                    MasterList.append(row)
            # Snip off the title and column names from the MasterList
            return MasterList
        except csv.Error as error:
            print("Error with CSV file", error)
            quit(3)
    else:
        print("Error missing file", Filename)
        quit(1)


def filter_list(Filter, ListSize):
    global MasterList
    ResultList = []
    for wertnum in range(len(MasterList)):
        if MasterList[wertnum][0] in Filter:
            ResultList.append(wertnum)
            print("wert : ", wertnum, MasterList[wertnum][0], Filter)
    print("List len : ", len(ResultList), len(MasterList), "List  ", ResultList)

    random.shuffle(ResultList)
    return ResultList[:ListSize]


sg.theme('Dark Red')

#CSVPath = sg.PopupGetFolder('CSV file folder to open', default_path=str(os.getcwd()))
CSVPath = sg.PopupGetFolder('CSV file folder to open', default_path=str('C:\\Users\\rdese\\Documents\\German Language Notes'))
# C:\Users\rdese\Documents\German Language Notes

if not CSVPath:
    sg.PopupCancel('Cancelling')
    raise SystemExit()

#### PIL supported image types
img_types = (".csv")
flist0 = os.listdir(CSVPath)
DirFilenames = [f for f in flist0 if os.path.isfile(os.path.join(CSVPath, f)) and f.lower().endswith(img_types)]
Filename = os.path.join(CSVPath, DirFilenames[0])  # name of first file in list

FilterWert = [sg.Combo(WertType, key='Wert', enable_events=True)]

Col_verbclass = [[sg.Text('Verb Klass')], [sg.Radio('Akkusitiv', "Verblich", size=(10, 1), key='Verb_Akk')],
                              [sg.Radio('Nomativ', "Verblich", size=(10, 1), key='Verb_Nom')],
                              [sg.Radio('Dativ', "Verblich", size=(10, 1), key='Verb_Dat')],
                              [sg.Radio('Gentiv', "Verblich", size=(10, 1), key='Verb_Gen')]]

Col_gender = [[sg.Text('Noun Gender')], [sg.Radio('Der', "Nounlich", size=(5, 1), key='Noun_Der')],
                              [sg.Radio('Das', "Nounlich", size=(5, 1), key='Noun_Das')],
                              [sg.Radio('Die', "Nounlich", size=(5, 1), key='Noun_Die')]]

FilterVerbe = [sg.Listbox(values=VerbeType, size=(20, 4), key='VerbeSel', select_mode="LISTBOX_SELECT_MODE_SINGLE", enable_events=True)]

layout = [
    [sg.Text('Flash Cards', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE),
     sg.Text(' ' * 69), sg.Button(('Exit'), size=(12, 2))],
    [sg.Button('Sprechen', size=(8, 1), key='VoiceMe'), sg.Text('German', size=(24, 1), justification='center', font=("Helvetica", 16)),
     sg.Text('English', size=(24, 1), justification='center', font=("Helvetica", 16)),
     sg.Text('Notes', size=(24, 1), justification='center', font=("Helvetica", 16))],
    [sg.Button(('<'), size=(3, 6)), sg.Button(('>'), size=(3, 6)), sg.Multiline(default_text="Hallo", key='De', size=(30,6), font=("Helvetica", 12)),
      sg.Multiline(default_text="Hello", key='En', size=(30,6), font=("Helvetica", 12)),
      sg.Multiline(default_text="Notes", key='Nt', size=(30,6), font=("Helvetica", 12))],
    [sg.Button('Set Lang', size=(8, 1), key='Set_Mode'), sg.Radio('Deutsch', "RadStr", size=(11, 1), key='DE_LAG'),
     sg.Radio('Deutsch keine text', "RadStr", size=(18, 1), key='KED_LAG'), sg.Radio('English', "RadStr", size=(57, 1), key='EN_LAG'),
     sg.Button('  Go  ', size=(12, 2), key="Go_and_do")],
    [ sg.Button('DE Answer', size=(12, 1), key='DEAnswer'), sg.Text(' ' * 44),
     sg.Button('EN Answer', size=(12, 1), key='ENAnswer'), sg.Text(' ' * 43), sg.Button('Show Notes', size=(12, 1), key='ShowNotes')],
    [sg.Column(Col_verbclass), sg.VSeperator(), sg.Column(Col_gender),sg.Text(' ' * 8),
     sg.Column( [[sg.Text('Word Filter', size=(20, 1),  justification='center', font=("Helvetica", 14))],
    [sg.Listbox(values=WertType, select_mode='extended', key='wert', size=(20, 5), font=("Helvetica", 16))],
    [sg.Button('Set Filter', size=(15, 1))]] )]
]

def main():
    Running = True
    global ImagePath, Filenames, window, values, ProperListNames

    ## Vocab List break down
    # [0] wert type
    # [1] verb type
    # [2] noun type
    # [3] wert
    # [4] Eng. word

    VocabeList = get_data(Filename)
    VocabMax = len(VocabeList)
    IndexList = range(1, VocabMax)
    VocabIndex = 0

    window = sg.Window('Flash Cards', layout, return_keyboard_events=True,
                       location=(0, 0), use_default_focus=False)

    print("Total list  ", len(MasterList))
    for i in MasterList:
        print("Element : ", i)


    while Running == True:
        event, values = window.read()

        print("Event : ", event, "Value : ", values)
        if event == 'Exit':
            Running = False

        elif event in ('>', 'MouseWheel:Down', 'Down:40', 'Next:34') and VocabIndex < (len(IndexList)-1):
            VocabIndex += 1
            window['De'].update(VocabeList[IndexList[VocabIndex]][3])
            window['En'].update(VocabeList[IndexList[VocabIndex]][4])
        elif event in ('<', 'MouseWheel:Up',  'Up:38', 'Prior:33') and VocabIndex >= 1:
            VocabIndex -= 1
            window['De'].update(VocabeList[IndexList[VocabIndex]][3])
            window['En'].update(VocabeList[IndexList[VocabIndex]][4])
        elif event == 'VoiceMe':
            print("The sprechen wert ", str(VocabeList[IndexList[VocabIndex]][3]))
            tts = gtts.gTTS(str(VocabeList[IndexList[VocabIndex]][3]), lang='de')
            try:
                tts.save("Sprechen.mp3")
                try:
                    playsound("Sprechen.mp3")
                    print("Playing sound for", str(VocabeList[IndexList[VocabIndex]][3]))
                except IOError:
                    print("File busyn playing please wait.")
            except IOError:
                print("File busy please wait.")




            if os.path.exists("Sprechen.mp3"):
                os.remove("Sprechen.mp3")

        elif event == 'Set Filter':
            print("Filter : ", values['wert'])
            IndexList = filter_list(values['wert'], 30)
            print("wert 2 : ", IndexList)
            window['De'].update(VocabeList[IndexList[VocabIndex]][3])
            window['En'].update(VocabeList[IndexList[VocabIndex]][4])

        elif event == 'Go_and_do':
            if not any(list(values[i] for i in LangType)):
                print("There is nothing selected")
                continue
            elif values['DE_LAG'] is True:
                print("DE langage")
            elif values['KED_LAG'] is True:
                print("DE langage no screen")
            elif values['EN_LAG'] is True:
                print("EN langage")

        print("Index : ", IndexList[VocabIndex], VocabeList[IndexList[VocabIndex]][3])




#### This is the main_init
if __name__=='__main__':
    main()

### Ende