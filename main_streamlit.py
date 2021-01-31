import io

import streamlit as st

from Recap.PDFManager import PDFExtractor
from Recap.TextAnalysis import TextStatistics, TextResume
from Recap.TextAnalysis import TextOutputFormatter

import matplotlib.pyplot as plt
from PIL import Image
from util.refresh_state import _get_state

def work_on_text(t,output,algorhitm="td_idf",overmean=1.25):
    ts = TextStatistics(t)
    tokens = ts.tokenizeWords(extra_stop=["et", "al"])
    freq,fig=ts.bigramFrequence(extra_stop=["et","al"])
    #st.write(fig)
    outputdir_wordcloud = output + ".png"
    wordcloud=ts.wordCloud(outputDir=outputdir_wordcloud, extra_stop=["et", "al"])
    #st.write(wordcloud)

    if algorhitm == "td_idf":
        tr_td_idf = TextResume(t, method="td_idf")
        resume = tr_td_idf.make_resume(over_mean=overmean, extra_stop=["et", "al"])
        #tr_td_idf.save("resume_TD.txt")

    if algorhitm == "abstractive":
        tr_abstractive = TextResume(t, method="abstractive")
        resume = tr_abstractive.make_resume(over_mean=overmean, extra_stop=["et", "al"])
        #tr_abstractive.save("resume_abstractive.txt")

    return resume,fig,wordcloud



def extract_and_save(file,state):
    p = PDFExtractor(file)

    [t, d] = p.extract_fine()
    img_dir = "images"
    state.t = t
    state.d = d

    s,fig,wordcloud = work_on_text(t, img_dir)
    state.s = s
    state.p = p
    state.freq=fig
    state.wordcloud=wordcloud
    state.last_run=last_run+1

def prepare_img(p,slider):
    img, data = p.raw2img(slider)
    image = Image.frombytes(mode='1', size=p.images[slider].srcsize, data=data, decoder_name='raw')

    image = Image.open(io.BytesIO(data))
    return image


file=st.file_uploader("Upload your file")
run_btn=st.button("RUN")
slider=None

state = _get_state()
last_run=state.last_run

#init last run
if last_run is None:
    last_run=0

if file is not None:

    if run_btn:
        extract_and_save(file,state)
    if state.last_run>0:
        p=state.p
        t=state.t
        d=state.d
        s=state.s
        freq=state.freq
        wordcloud=state.wordcloud

    st.info(f"[INFO] original text length: {len(t)} \t\t summary length:{len(s)}")
    st.write(freq)
    st.write(wordcloud)

    to=TextOutputFormatter.TextOutputFormatter(s)
    s=to.prettify()
    st.markdown(f"<p align='justify'>{s}</p>", unsafe_allow_html=True)
    st.info(f"{len(p.images)} images found with {len(d)} captions")
    # p = PDFExtractor(file)
    #
    # [t, d] = p.extract_fine()
    # img_dir = "images"
    # state.t = t
    # state.d = d
    #
    # s = work_on_text(t, img_dir)
    # state.s = s
    # state.p = p
    # st.info(f"[LAST RUN] {last_run}")
    # st.info(f"[INFO] original text length: {len(t)} \t\t summary length:{len(s)}")
    # st.markdown(f"<p align='justify'>{s}</p>", unsafe_allow_html=True)
    # st.info(f"{len(p.images)} images found")

    #
    # state.last_run=last_run+1


    slider = st.slider("Figura", max_value=(len(p.images) - 1))
    st.image(prepare_img(p,slider))


