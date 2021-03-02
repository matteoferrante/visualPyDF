# -*- coding: utf-8 -*


# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import PySimpleGUI as sg
import os.path

from Recap.PDFManager import PDFExtractor
from Recap.TextAnalysis import TextStatistics
from Recap.TextAnalysis import TextResume
import cv2
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch, cm
from Recap.TextAnalysis import TextOutputFormatter



def list_found_images(window, img_dir):
    try:
        # Get list of files in folder
        file_list = os.listdir(img_dir)
    except:
        file_list = []

    fnames = [
        f
        for f in file_list
        if os.path.isfile(os.path.join(img_dir, f))
           and f.lower().endswith((".png", ".gif"))
    ]
    window["-FILE LIST-"].update(fnames)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# Two helpful functions to resize images and cut extra information for text
def get_image(path, width=1 * cm):
    img = cv2.imread(path)
    (ih, iw, dp) = img.shape
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


def just_text(text):
    idx = text.find("Abstract")
    if idx < 0:
        idx = 0
    return text[idx:]

def visual_clean(tweet):
    char_list = [tweet[j] for j in range(len(tweet)) if ord(tweet[j]) in range(65536)]
    tweet = ''
    for j in char_list:
        tweet = tweet + j
    return tweet


def work_on_text(t,output,algorhitm="td_idf",overmean=1.25):
    ts = TextStatistics(t)
    tokens = ts.tokenizeWords(extra_stop=["et", "al"])
    # freq=ts.bigramFrequence(outputDir="test.png",extra_stop=["et","al"])
    outputdir_wordcloud = output + ".png"
    ts.wordCloud(outputDir=outputdir_wordcloud, extra_stop=["et", "al"])
    if algorhitm == "td_idf":
        tr_td_idf = TextResume(t, method="td_idf")
        resume = tr_td_idf.make_resume(over_mean=overmean, extra_stop=["et", "al"])
        #tr_td_idf.save("resume_TD.txt")

    if algorhitm == "abstractive":
        tr_abstractive = TextResume(t, method="abstractive")
        resume = tr_abstractive.make_resume(over_mean=overmean, extra_stop=["et", "al"])
        #tr_abstractive.save("resume_abstractive.txt")

    return resume

def main():
    # prepare the layout
    file_list_column = [
        [
            sg.Text("SELECT FILE"),
            sg.In(size=(25, 1), enable_events=True, key="-FILE-"),
            sg.FileBrowse(file_types=(("Text Files", "*.pdf"),)),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
            )
        ],
    ]

    # For now will only show the name of the file that was chosen
    image_viewer_column = [
        [sg.Text("Choose an image from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
    ]

    summary=[
        [sg.Text(size=(40,2000),key="-SUMMARY-")]
    ]

    # ----- Full layout -----
    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),sg.Column(summary,scrollable=True),sg.VSeperator(),
            sg.Column(image_viewer_column),
        ]
    ]

    window = sg.Window("Image Viewer", layout)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        # load the file
        if event == "-FILE-":
            file = values["-FILE-"]
            #prepare a full analysis
            p=PDFExtractor(file)




            [t, d] = p.extract_fine()           #most important function

            img_dir=file[:-4]+"_images"

            s=work_on_text(t,img_dir)
            window["-SUMMARY-"].update(s)
            print(s)
            p.extract_img()
            #to show the images

            list_found_images(window,img_dir)


        if event=="-FILE LIST-":
            try:
                filename = os.path.join(
                    img_dir, values["-FILE LIST-"][0]
                )
                window["-TOUT-"].update(filename)
                window["-IMAGE-"].update(filename=filename)
            except:
                pass




    window.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
