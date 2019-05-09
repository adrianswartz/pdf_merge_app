#Import Libraries
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
import shutil
import logging
import numpy as np

def initialize_and_retrieve(temp_dir, input_dir):
    pdf_list=[]
    
    for item in os.listdir(input_dir):
        if item.endswith('.pdf'):
            pdf_list.append(input_dir+item)

    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)
    else:
        os.mkdir(temp_dir)

    return pdf_list

def retrieve_files(input_dir):
    pdf_list=[]
    
    for item in os.listdir(input_dir):
        if item.endswith('.pdf'):
            pdf_list.append(input_dir+item)

    return pdf_list


def attach_page_numbers(pdf, output, current_page_num):
    logging.info("Processing {0} file".format(pdf))

    # open the pdf and get the total page numbers
    existing_pdf = PdfFileReader(open(pdf, "rb"), strict=False)
    page_count_for_pdf = existing_pdf.getNumPages()

    # for each page in the pdf, attach a overall page number
    for i in range(0, page_count_for_pdf):
        page = existing_pdf.getPage(i)
        size = page.mediaBox
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        # we print a four digit page number on the bottom left of the page
        can.drawString(int(size[2]) - 40, 15, str(current_page_num).zfill(4))
        can.save()
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        current_page_num += 1

        # add the "watermark" (which is the new pdf) on the existing page
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)

    logging.info("process success")

    return (output, current_page_num)


def generate_content_page(temp_dir, index_list):
    logging.info("generating content page canvas")

    height = 700
    content_canvas = canvas.Canvas(os.path.join(temp_dir, 'CONTENT.pdf'), pagesize=letter)
    content_canvas.setFont('Courier', 18)
    content_canvas.drawCentredString(320, 750, "CONTENTS")
    # font style needs to be monospaced so that the page numbers are aligned in the content page
    content_canvas.setFont('Courier', 12)

    for namepage in index_list:
        file_name, page = namepage
        title_name = '.'.join(file_name.split('.')[:-1])


        if len(title_name)>49:
            s_list = title_name.split(' ')
            lengths = []
            for item in s_list:
                lengths.append(len(item))

            lines = []
            while s_list != []:
                for i in range(int(np.ceil(len(title_name) / 40))):
                    line = ''
                    while len(line) < 40:
                        if s_list == []:
                            break
                        else:
                            line += s_list.pop(0) + ' '
                    if i == max(range(int(np.ceil(len(title_name) / 40)))):
                        total_len = len(line) + len(str(page))
                        spaces = 55 - total_len
                        filler = ''.join([' '] * spaces)
                        content_canvas.drawString(25, height, ' '*10 + line + filler + str(page))
                        height -= 20
                    else:
                        content_canvas.drawString(25, height, ' '*10 + line)
                        height -= 20
        else:
            total_len = len(title_name) + len(str(page))
            spaces = 55 - total_len
            filler = ''.join([' '] * spaces)
            content_canvas.drawString(25, height, ' '*10 + title_name + filler + str(page))
            height -= 20


    logging.info("content page canvas generated")

    return content_canvas


def merge_all_pdfs(temp_dir, contentCanvas, FinalPdfOutputStream):
    logging.info("creating merged pdf")
    outputStream = open(os.path.join(temp_dir, 'MERGED.pdf'), 'wb')
    FinalPdfOutputStream.write(outputStream)
    outputStream.close()
    logging.info("merged pdf created")

    logging.info("generating content pdf")
    contentCanvas.save()
    logging.info("content pdf created")

    merger = PdfFileMerger()

    for generated_pdfs in [os.path.join(temp_dir, 'CONTENT.pdf'), \
                           os.path.join(temp_dir, 'MERGED.pdf')]:
        merger.append(generated_pdfs)

    return merger

def check_file_name_extension(file_name):
    if file_name.endswith('.pdf'):
        return file_name
    else:
        return file_name+'.pdf'
    


def execute_merge(pdf_lst, temp_dir, input_dir, file_name):
    
    FinalOutputStream = PdfFileWriter()
    start_page_num = 1
    index_list = []
    
    logging.basicConfig(level=logging.DEBUG, filename=os.path.join(temp_dir, 'LogFile.txt'), filemode='w')

#    perform_pdf_validations(pdf_lst)

    for pdf in pdf_lst:

        index_list.append((pdf.split('/')[-1], start_page_num))
        intermOutputStream, ending_page_num = attach_page_numbers(pdf, FinalOutputStream, start_page_num)
        FinalOutputStream = intermOutputStream
        start_page_num = ending_page_num
        
    content_page_canvas = generate_content_page(temp_dir, index_list)

    # merge all pdfs
    final_pdf = merge_all_pdfs(temp_dir, content_page_canvas, FinalOutputStream)

    logging.info("Finishing touches.....")
    # output the final merged pdf in the temp directory
    file_name = check_file_name_extension(file_name)
    final_pdf.write(os.path.join(temp_dir, file_name))
    logging.info("Final Pdf written")

    logging.info("Hang tight..")
    # paste the file back into the input folder

    shutil.copy((os.path.join(temp_dir, file_name)), input_dir)
    logging.info("PROCESS SUCCESS")

    return None




