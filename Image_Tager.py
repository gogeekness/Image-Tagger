#!/usr/bin/env python3
# This is to help speed up image tagging in creating a push button
# tagger for my images
# Richard Eseke 2020

import sys
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg
from PIL import Image, ImageTk
import piexif
from TagMasterList import TaggerList, SpecialList

import os
import io

#### Global Var Lists
menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']],
            ['&Help', '&About...'], ]
radio_list = ['RAD0', 'RAD1', 'RAD2', 'RAD3', 'RAD4', 'RAD5']

### Sorting Tag list alphebetacaly
TaggerList.sort()
TaggerList.append("<end>")
SpecialList.sort()


#### Global Vars
TaggerListLen = len(TaggerList)
Tags1 = TaggerList[:int(TaggerListLen/3)]
Tags2 = TaggerList[int(TaggerListLen/3):int(TaggerListLen/3*2)]
Tags3 = TaggerList[int(TaggerListLen/3*2):-1]
BaseTag = Filenames = []
ImageSize = (800,600) #(1440, 920)
KeyValue = 40094  # ExIF key for KeyWords in Windows
KeyRating = 18246  # ExIF key for rating in Windows
PerRating = 18249  # ExIF Percentage rating
Nullth = '0th'
KeyStr = "XPKeywords"
exifDataRaw = {}
ExtRating = 0  # temporary value
BlankTag = {'0th': {18246: 0, 18249: 0, 40094: (65, 0)}, 'Exif': {}, 'GPS': {}, 'Interop': {}, '1st': {}, 'thumbnail': None}


### Get the folder containin:g the images from the user
sg.theme('Dark Red')

ImagePath = sg.PopupGetFolder('Image folder to open', default_path='')
if not ImagePath:
    sg.PopupCancel('Cancelling')
    raise SystemExit()

#### PIL supported image types
img_types = (".jpg", ".jpeg")

#### get list of files in folder
flist0 = os.listdir(ImagePath)


#### create sub list of image files (no sub folders, no wrong file types)
Filenames = [f for f in flist0 if os.path.isfile(os.path.join(ImagePath, f)) and f.lower().endswith(img_types)]

num_files = len(Filenames)                # number of iamges found
if num_files == 0:
    sg.Popup('No files in folder')
    raise SystemExit()

del flist0   # no longer needed


#### Functions =================================================
##
def get_file_list(ImagePath):
    FileList = os.listdir(ImagePath)
    LocFilenames = [f for f in FileList if os.path.isfile(os.path.join(ImagePath, f)) and f.lower().endswith(img_types)]
    return LocFilenames


def get_img_data(f, maxsize = ImageSize, first = False):
    try:
        img = Image.open(f)
    except OSError:
        print("OS Error", OSError, "  First ", first)
        return None
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format = "PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


def PullTags(pathname, filename):
    global exifDataRaw
    exifDataRaw = piexif.load(pathname + '\\' + filename)
    try:
        if exifDataRaw[Nullth]:
            if KeyValue in exifDataRaw[Nullth]:
                TagOutput = str(bytes(exifDataRaw[Nullth][KeyValue]).decode('utf_16_le'))#[:-1]
                return str(TagOutput)
    except ValueError:
        print("Error no", Nullth, "Data:", exifDataRaw)
        print("Dump 0th:", piexif.dump(BlankTag))
        piexif.insert(piexif.dump(BlankTag), pathname + '\\' + filename)
        return ""
    return ""


def PullRating(pathname, filename):
    global exifDataRaw
    exifDataRaw = piexif.load(pathname + '\\' + filename)
    try:
        if exifDataRaw[Nullth]:
            try:
                if exifDataRaw[Nullth][KeyRating]:
                    RatingOut = exifDataRaw[Nullth][KeyRating]
                else:
                    RatingOut = 0
            except KeyError:
                print("Key error with: ", KeyRating)
                RatingOut = 0
            return RatingOut
    except ValueError:
        print("Error no", Nullth, "Data:", exifDataRaw)
        return 0
    return 0


def PushTags(pathname, filename, ListTag):
    InsertString = ""
    global exifDataRaw
    for Tag in TaggerList[:-1]:
        if values[Tag]:
            InsertString = InsertString + Tag + ";"
    InsertString = ListTag + InsertString
    print("Push string", InsertString)
    #Get whole dataset
    print("Missing ", Nullth, "Data:", exifDataRaw)
    if exifDataRaw:
        exifDataRaw[Nullth][KeyValue] = tuple(InsertString[:-1].encode('utf_16_le'))
        exifDataRaw[Nullth][KeyRating] = GetRadio()
        exifDataRaw[Nullth][PerRating] = 20 * GetRadio()
        ByteExif = piexif.dump(exifDataRaw)
        piexif.insert(ByteExif, pathname + '\\' + filename)
    else:
        print("No Exif Data")


def ShowImageTags(TagStr):
    InterList = []
    global window
    if TagStr != None:
            for Tag in TaggerList:
                if str(Tag) in TagStr:
                    InterList.append(str(Tag))
                    window.Element(str(Tag)).Update(value=True)

def ImageTagsClear():
    for Tag in TaggerList[:-1]:
        window.Element(str(Tag)).Update(value=False)


def CBtn(BoxText):
    return sg.Checkbox(BoxText, size=(11, 1), default=False, key=(BoxText))

def GetRadio():
    rating = 0
    for i in range(len(radio_list)):
        if window.FindElement(radio_list[i]).Get() == True:
            return rating
        rating = rating + 1
    return 0

#### Layout sets ===============================================
##   make these 2 elements outside the layout as we want to "update" them later
##   initialize to the first file in the list

filename = os.path.join(ImagePath, Filenames[0])  # name of first file in list
image_elem = sg.Image(data = get_img_data(filename, first = True))
file_num_display_elem = sg.Text('File 1 of {}'.format(num_files), size=(20,1))

#### Colunm list of tags
column1 = [[CBtn(Tags1[i])] for i in range(len(Tags1))]
column2 = [[CBtn(Tags2[i])] for i in range(len(Tags2))]
column3 = [[CBtn(Tags3[i])] for i in range(len(Tags3))]

col_image = [[image_elem]]
ImageNameText = sg.Text(filename, size=(60, 1), justification='center',  relief='sunken', auto_size_text=True)

ProperList = [sg.Listbox(values=SpecialList, size=(30, 10), key='proplist', select_mode="LISTBOX_SELECT_MODE_SINGLE",
                         enable_events=True)]

BoxListButtons = [[sg.Button(('Add Tag'), size=(8, 2)), sg.Button(('Clear Tag'), size=(8, 2)), sg.Checkbox(('Special Tag\nSelected'), key='TagSpecial', default=False, size=(12,12))]]

col_files = [[sg.Listbox(values=Filenames, change_submits=True, size=(40, 40), key='listbox')], [file_num_display_elem],
             [sg.Button(('Save Image'), size=(10, 2)), sg.Button(('Clear Boxes'), size=(10, 2)),
             sg.Button(('Hold Boxes'), size=(10, 2))], ProperList, [sg.Column(BoxListButtons)]]

col_adds = [[sg.Column(col_image, size=ImageSize)], [sg.Text(str(PullTags(ImagePath, Filenames[0])), size=(80,1), key='TextTag')]]

TagButtons = [sg.Button(('Save Image'), size=(10, 2)), sg.Button(('Clear Boxes'), size= (10, 2)), sg.Button(('Hold Boxes'), size= (10, 2))]

Col_Frame1 = [ [ sg.Column([[sg.Text('Tag Lists:')], [sg.Column(column1)]]) ] ]
Col_Frame2 = [ [ sg.Column([[sg.Text('Tag Lists:')], [sg.Column(column2)]]) ] ]
Col_Frame3 = [ [ sg.Column([[sg.Text('Tag Lists:')], [sg.Column(column3)]]) ] ]

layout = [
    [sg.Text('Image Tagger', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE),
     sg.Text('Your Folder', size=(15, 1), justification='right'), sg.InputText(ImagePath), sg.FolderBrowse(),
     sg.Button(('Go'), size=(4,1)), sg.Button(('Exit'), size=(16,2))],

    [sg.Button(('<'), size=(3, 50)), sg.Column(col_adds),
     sg.Button(('>'), size=(3, 50)), sg.Column(Col_Frame1), sg.Column(Col_Frame2), sg.Column(Col_Frame3),
     sg.Column(col_files)],
    [ImageNameText, sg.Radio('Star 5', "RadStr", size=(7, 1), key='RAD5'), sg.Radio('Star 4', "RadStr", size=(7, 1), key='RAD4'),
    sg.Radio('Star 3', "RadStr", size=(7, 1), key='RAD3'), sg.Radio('Star 2', "RadStr", size=(7, 1), key='RAD2'),
    sg.Radio('Star 1', "RadStr", size=(7, 1), key='RAD1'),
    sg.Radio('No Star', "RadStr", size=(7, 1), key='RAD0', default=True)]]


### Main ===============================================
##
##
def main():
    Running = True
    Hold = False
    image_idx = ExtRating = 0
    ImageName = ListTag = ""
    HoldList = []

    global ImagePath, Filenames, window, values, ProperListNames

    window = sg.Window('Image Tagger', layout, return_keyboard_events=True,
                       location=(0, 0), use_default_focus=False)

### Main update loop for tagger
##
    while Running == True:
        # Interlist = []
        event, values = window.read()
        Filenames = get_file_list(ImagePath)

        if event is None:
            break
        elif event in ('>', 'MouseWheel:Down', 'Down:40', 'Next:34') and image_idx < (num_files-1):
            image_idx += 1
            if not Hold:
                ImageTagsClear()
        elif event in ('<', 'MouseWheel:Up',  'Up:38', 'Prior:33') and image_idx >= 1:
            image_idx -= 1
            if not Hold:
                ImageTagsClear()
        elif event == 'listbox':
            imagef = values["listbox"][0]
            ImageName = os.path.join(ImagePath, imagef)
            image_idx = Filenames.index(imagef)
            if not Hold:
                ImageTagsClear()
### Browse Dir change and update
        elif event == 'Go':
            ImagePath = values[0]  # get browse str
            image_idx = 0          # set to 0 for new dir
            Filenames = get_file_list(ImagePath)
            window.Element('listbox').Update(Filenames)
            ImageTagsClear()
        elif event == 'Hold Boxes':
            Hold = True
            if len(HoldList) > len(TaggerList):
                HoldList = []
            for LookChk in (TaggerList[:-1]):
                HoldList.append(values[LookChk])
        elif event == 'Clear Boxes':
            Hold = False
            HoldList = []
            ImageTagsClear()
        elif event == 'Save Image':
            PushTags(ImagePath, Filenames[image_idx], ListTag)
        elif event == 'Add Tag':
            TupIndex = window['proplist'].get_indexes()
            try:
                ListTag = SpecialList[TupIndex[0]] + ";"
                window.Element('TagSpecial').Update(value=True)
            except IndexError:
                print("No special tag selected.")
        elif event == 'Clear Tag':
            window.Element('TagSpecial').Update(value=False)
            ListTag = ""
        elif event == 'Exit':
            Running = False
        else:
            pass

### Update image if needed
        ShowImageTags(PullTags(ImagePath, Filenames[image_idx]))
        ImageName = os.path.join(ImagePath, Filenames[image_idx])
        image_elem.Update(data=get_img_data(ImageName))
        window.FindElement('TextTag').Update(PullTags(ImagePath, Filenames[image_idx]))

### Update Rating Radio buttons
        ExtRating = PullRating(ImagePath, Filenames[image_idx])
        for i in range(len(radio_list)):
            if i == ExtRating:
                window.FindElement(radio_list[i]).Update(value=True)
                break
            else:
                window.FindElement(radio_list[i]).Update(value=False)

        ImageNameText.Update(ImageName)
        file_num_display_elem.Update('File {} of {}'.format(image_idx+1, num_files ))


#### This is the main_init
if __name__=='__main__':
    main()

### Ende