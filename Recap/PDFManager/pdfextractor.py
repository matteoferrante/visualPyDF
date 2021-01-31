from __future__ import print_function
### Pdf managing
from pdfminer3.layout import LTImage, LTFigure
from pdfminer3.pdfparser import PDFParser
from pdfminer3.pdfdocument import PDFDocument
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.layout import LAParams, LTTextBox, LTTextLine
from pdfminer3.converter import TextConverter
from pdfminer3.pdfpage import PDFPage
from io import StringIO
from random import randint
#regular expression
import re
# images handling
import fitz
import os, sys, time
import fitz
import PySimpleGUI as sg
#colored terminal
from termcolor import colored


from binascii import b2a_hex




class PDFExtractor:
    def __init__(self,pdf,codec='utf-8'):

        """
        Parameters:
        --------------
        codec:      codific, default utf-8
        pdf:        path to the pdf file

        Attributes:
        ---------------
        records:        list of lines from the pdf file
        text:           string of joined records, default ""
        didascalies:    list of found didascalies with regexpr
        nimages:        int, number of found images

        """
        self.pdf=pdf
        self.text=""
        self.records= []
        self.didascalies=[]
        self.nimages=0
        self.images=[]

        parser = PDFParser(pdf)
        #parser = PDFParser(open(pdf, 'rb'))
        document = PDFDocument(parser)
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        # Create a PDF resource manager object
        # that stores shared resources.
        rsrcmgr = PDFResourceManager()
        # Create a buffer for the parsed text
        retstr = StringIO()
        # Spacing parameters for parsing
        laparams = LAParams()
        self.codec = codec
        device = TextConverter(rsrcmgr, retstr,
                               codec = codec,
                               laparams = laparams)
        # Create a PDF interpreter object
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # Process each page contained in the document.
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)

        #images

        img_device=PDFPageAggregator(rsrcmgr,laparams=laparams)
        img_interpreter = PDFPageInterpreter(rsrcmgr, img_device)
        for page in PDFPage.create_pages(document):
            img_interpreter.process_page(page)
            pdf_item = img_device.get_result()
            if pdf_item is not None:
                for thing in pdf_item:
                    if isinstance(thing, LTImage):
                        self.save_image(thing)
                    if isinstance(thing, LTFigure):
                        self.find_images_in_thing(thing)

        lines = retstr.getvalue().splitlines()
        for line in lines:
            self.records.append(line)

    def find_images_in_thing(self,outer_layout):
        for thing in outer_layout:
            if isinstance(thing, LTImage):
                self.save_image(thing)


    def save_image(self,thing):
        self.images.append(thing)

    def extract(self,remove_ref=True):
        """ Extract text from pdf
        Parameters:
        -------------
        remove_ref: boolean, chose if remove text under refernces or not

        Return:
        -------------
        text: string, join of all lines

        """


        text='\n'.join(self.records)
        text=re.sub('-\n','',text)
        if remove_ref:
            idx=text.lower().find("references")                  #trovo l'indice della bibliografia
            text=text[:idx]
        self.text=text
        return text

    def extract_fine(self,remove_ref=True,regex='\n\n+',start="Fig"):
        """
        Function to operate a fine tuning of extracted raw text, removing redudant white lines and separated didascalies"
        Return:
        ----------
        fine_text:  formatted text
        didascalies: list of didascalies
        """

        print("[INFO] Eurisitc procedure, result may be worse than standard extract method")

        if self.text=="":
            self.extract(remove_ref)
        self.check_did()

        if self.nimages:        #if self.nimages!=0
            if self.didascalies==self.nimages:
                print(f"[INFO]: Euristic procedure found all {len(self.didascalies)}/{self.nimages} didascalies")
            else:
                print(colored(f"[WARNING]: Euristic procedure found {len(self.didascalies)}/{self.nimages} didascalies","yellow"))
        else:
            print(f"[INFO]: Euristic procedure found {len(self.didascalies)} didascalies, but you do not have already extracted images. To extract them run .extract_img() method")



        #remove noisy char
        #controllare qua!!
        myrec=[]
        for (i,record) in enumerate(self.records):
            if len(record)>2:
                myrec.append(record)

        self.records=[]
        self.records=myrec[:]
        text='\n'.join(myrec)
    #    print(text)
        text=re.sub('-\n','',text)
        if remove_ref:
            idx=text.lower().find("references")                  #trovo l'indice della bibliografia
            text=text[:idx]
        self.text=self.text_cleaner(text)

        return self.text,self.didascalies

    def check_did(self,regex='\n\n+',start="Fig"):
        """
        Function to check didascalies
        self.didascalies: list of found didascalies
        """


        text=self.text
        text=re.sub(regex,'\n\n',text)
        separated = re.split('\n\n', text)
        cleaned_text=[]
        for (i,chunk) in enumerate(separated):
            if chunk.startswith(start):
                self.didascalies.append(self.text_cleaner(chunk))

            else:
                cleaned_text.append(self.text_cleaner(chunk))

        c_text='\n'.join(cleaned_text)
        self.text=""
        self.text=c_text

    def text_cleaner(self,text):
        """Function to clean out some strange character"
        """
        out_text=re.sub("ﬁ","fi",text)
        return out_text

    def save_text(self,output_name=None):
        """
        Save extracted text to a file.

        Parameters:
        ------------
        output_name: string, default same as pdf name, but extension turn to .txt

        """
        if output_name is None:
            output_name=self.pdf[:-4]+".txt"
        if self.text=="":
            self.extract()
        f=open(output_name,"w")
        prettyfied_text=self.text.encode('utf-8').decode('ascii', 'ignore')
        f.write(prettyfied_text)
        f.close()
        print(f"[INFO] Text extracted and filtered, saved as {output_name}")

    def raw2img(self,idx):
        """Try to save the image data from this LTImage object, and return the file name, if successful"""

        result = None
        lt_image=self.images[idx]
        file_name=f"{randint(0,1000)}"
        if lt_image.stream:
            file_stream = lt_image.stream.get_rawdata()
        file_ext = self.determine_image_type(file_stream[0:4])
        if file_ext:
            file_name = ''.join([str(idx), '_', lt_image.name, file_ext])
        result,img,data=self.write_file(file_name, lt_image.stream.get_rawdata(), flags='wb')

        return img,data



    def determine_image_type(self,stream_first_4_bytes):
        """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""

        file_type = None
        bytes_as_hex = b2a_hex(stream_first_4_bytes)
        if bytes_as_hex.startswith(b'ffd8'):
            file_type = '.jpeg'
        elif bytes_as_hex == '89504e47':
            file_type = ',png'
        elif bytes_as_hex == '47494638':
            file_type = '.gif'
        elif bytes_as_hex.startswith(b'424d'):
            file_type = '.bmp'
        return file_type




    def write_file (self, filename, filedata, flags='w'):
        """Write the file data to the folder and filename combination
        (flags: 'w' for write text, 'wb' for write binary, use 'a' instead of 'w' for append)"""
        result = False
        fileobj=None
        try:
            file_obj = open(filename, flags)
            file_obj.write(filedata)
            file_obj.close()
            result = True
        except IOError:
            pass
        return result,file_obj,filedata


