# encoding: utf-8

import io
import traceback
import streamlit as st

from Recap.PDFManager import PDFExtractor
from Recap.TextAnalysis import TextStatistics, TextResume
from Recap.TextAnalysis import TextOutputFormatter
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from util.refresh_state import _get_state


page_bg_img = '''
<style>
body {
background-image: url("https://www.alfagroup.it/wp-content/uploads/2019/05/Background-connection.png");
background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)


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



def extract_and_save(file,state,method,over_mean):
    p = PDFExtractor(file)

    [t, d] = p.extract_fine()
    img_dir = "images"

    #tables
    df=p.extract_tables()

    state.t = t
    state.d = d

    s,fig,wordcloud = work_on_text(t, img_dir,method,overmean=over_mean)
    st.info(f"[INFO] Parameter: {over_mean} \t Algorithm: {method}")
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
    state.last_run=0

over_mean=st.sidebar.slider("OverMean Parameter (Higher is Shorter)",min_value=0, max_value=200,value=25)
algo=st.sidebar.selectbox("Algorithm",("td_idf","abstractive"))

if file is not None:

    if run_btn:
        over=1.+over_mean/100
        extract_and_save(file,state,algo,over)
    if state.last_run>0:
        p=state.p
        t=state.t
        d=state.d
        s=state.s
        freq=state.freq
        wordcloud=state.wordcloud

    try:
        st.info(f"[INFO] original text length: {len(t)} \t\t summary length:{len(s)}")
        st.write(freq)
        st.write(wordcloud)

        to=TextOutputFormatter.TextOutputFormatter(s)
        s=to.prettify()
        st.markdown(f"<p align='justify'>{s}</p>", unsafe_allow_html=True)
        st.info(f"{len(p.images)} images found with {len(d)} captions")

    except:
        st.info("[INFO] Click on RUN to start the analysis")

    ##tables



    try:

        if len(p.tables):

            if len(p.tables)>1:
                print(f"[INFO] found {len(p.tables)} tables")
                st.info(f"[INFO] found {len(p.tables)} tables ")
                table_slider = st.slider("Table", max_value=(len(p.tables) - 1),key="table")

                #df=pd.DataFrame(p.rawtables[table_slider],columns=p.rawtables[table_slider][0])
                #st.write(f"{p.rawtables[table_slider]}")
                st.write(p.tables[table_slider])
            else:
                print(f"[INFO] found {len(p.tables)} table")
                st.info(f"[INFO] found {len(p.tables)} table")

                st.write(p.tables[0])
    except:
        traceback.print_exc()
        print(f"[INFO] No tables found")
        st.info(f"[INFO] No tables found")

    #images

    try:
        if len(p.images)>0:

            if len(p.images)>1:
                slider = st.slider("Figura", max_value=(len(p.images) - 1))
                st.image(prepare_img(p,slider),width=700)
                if len(d)>=slider:
                    st.write(f"[CAPTION] {d[slider]}")

            else:
                st.image(prepare_img(p, 0), width=700)
                if len(d):
                    st.write(f"[CAPTION] {d[0]}")
    except:
        pass


