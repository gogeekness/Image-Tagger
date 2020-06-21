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
from TagMasterList import TaggerList
import os
import io

#### Global Var Lists
menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']],
            ['&Help', '&About...'], ]

TaggerList.sort()
TaggerList.append("<end>")

#### Global Vars
TaggerListLen = len(TaggerList)
Tags1 = TaggerList[:int(TaggerListLen/3)]
Tags2 = TaggerList[int(TaggerListLen/3):int(TaggerListLen/3*2)]
Tags3 = TaggerList[int(TaggerListLen/3*2):-1]
BaseTag = Filenames = []
ImageSize = (1440, 920)
KeyValue = 40094  # ExIF key for KeyWords in Windows
Nullth = '0th'
KeyStr = "XPKeywords"
exifDataRaw = {}

#### Get the folder containin:g the images from the user
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
                TagOutput = str(bytes(exifDataRaw[Nullth][KeyValue]).decode('utf_16_le'))[:-1]
                return str(TagOutput)
    except ValueError:
        print("Error no", Nullth, "Data:", exifDataRaw)
        return ""
    return ""


def PushTags(pathname, filename):
    InsertString = ""
    global exifDataRaw
    for Tag in TaggerList[:-1]:
        if values[Tag]:
            InsertString = InsertString + Tag + ";"
    #Get whole dataset
    print("Missing ", Nullth, "Data:", exifDataRaw)
    if exifDataRaw:
        if exifDataRaw[Nullth]:
            exifDataRaw[Nullth][KeyValue] = tuple(InsertString[:-1].encode('utf_16_le'))
            ByteExif = piexif.dump(exifDataRaw)
            piexif.insert(ByteExif, pathname + '\\' + filename)
        else:
            print("Missing ", Nullth, "Data:", exifDataRaw)
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
ImageNameText = sg.Text(filename, size=(80, 1), justification='center', auto_size_text=True)

col_files = [[sg.Listbox(values=Filenames, change_submits=True, size=(40, 40), key='listbox')], [file_num_display_elem],
             [sg.Button(('Save Image'), size=(10, 2)), sg.Button(('Clear Boxes'), size=(10, 2)),
             sg.Button(('Hold Boxes'), size=(10, 2))]
             ]

TagButtons = [sg.Button(('Save Image'), size=(10, 2)), sg.Button(('Clear Boxes'), size= (10, 2)), sg.Button(('Hold Boxes'), size= (10, 2))]

Col_Frame1 = [ [ sg.Column([[sg.Text('Tag Lists:')], [sg.Column(column1)]]) ] ]
Col_Frame2 = [ [ sg.Column([[sg.Text('Tag Lists:')], [sg.Column(column2)]]) ] ]
Col_Frame3 = [ [ sg.Column([[sg.Text('Tag Lists:')], [sg.Column(column3)]]) ] ]

layout = [
    [sg.Text('Image Tagger', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE),
     sg.Text('Your Folder', size=(15, 1), justification='right'), sg.InputText(ImagePath), sg.FolderBrowse(),
     sg.Button(('Go'), size=(4,1)), ImageNameText, sg.Button(('Exit'), size=(10,2)) ],
    [sg.Button(('<'), size=(3, 50)), (sg.Column(col_image, size=ImageSize)),
     sg.Button(('>'), size=(3, 50)), sg.Column(Col_Frame1), sg.Column(Col_Frame2), sg.Column(Col_Frame3),
     sg.Column(col_files)],
    ]

#### Main ===============================================
##
def main():
    Running = True
    Hold = False
    image_idx = 0
    ImageName = ""
    HoldList = []

    global ImagePath, Filenames, window, values

    window = sg.Window('Image Tagger', layout, return_keyboard_events=True,
                       location=(0, 0), use_default_focus=False)

#### Main update loop for tagger
##
    while Running == True:
        Interlist = []
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
        #### Browse Dir chang46428e
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
                    #print("Hold Vaules: ", HoldList)
        elif event == 'Clear Boxes':
            Hold = False
            HoldList = []
            ImageTagsClear()
        elif event == 'Save Image':
            # Read checkboxes
            PushTags(ImagePath, Filenames[image_idx])
        elif event == 'Exit':
            Running = False
        else:
            pass
        print("Image index:", image_idx, Filenames[image_idx])

        ShowImageTags(PullTags(ImagePath, Filenames[image_idx]))
        ImageName = os.path.join(ImagePath, Filenames[image_idx])

        image_elem.Update(data=get_img_data(ImageName))
        # image_elem.Update(ImageName)
        ImageNameText.Update(ImageName)
        file_num_display_elem.Update('File {} of {}'.format(image_idx+1, num_files ))


#### This is the main_init
if __name__=='__main__':
    main()

### Ende