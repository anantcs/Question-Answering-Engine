import urllib2
import re


def clean_para(para):
        para = re.sub(r'<[a-zA-Z0-9/\\\-%#@()!\$:\^`~&|\*\"\'\,\[\]=\+\._ ;?]+>', "", para)
        para = re.sub(r'\[[0-9]+\]', "", para)
        para = re.sub(r'\[\.\.\.\]', "", para)
        para = re.sub(r'more>', "", para)
        para = re.sub(r'>', "", para)
        para = re.sub(r'<', "", para)
        para = re.sub(r'[\.]+', ".", para)
        para = re.sub(r'\n\n', "", para)
        para = re.sub(r'#39', "", para)
        para = re.sub(r'&middot', "", para)
        para = re.sub(r'[^a-zA-Z0-9/\\\-%#@()!\$:\^`~&|\*"\'\,\[\]=\+\._ ;?<>]', "", para)
        para = ' '.join(para.split())
        return para


def write_file(text):
    write_para = clean_para(text)
    fob=open('C:\Python27\BTP\para.txt','a')
    fob.write(write_para)
    fob.write('\n\n')
    fob.close
    

def get_next_target(page):
    start_text = page.find('<span class="st">')
    end_text = page.find('</span>', start_text + 1)
    text = page[start_text + 17:end_text]
    return text, end_text
    

def ret_sourcecode(query):
        query = query.replace(' ','+')
        url = "http://www.google.com/search?q="+query
        req = urllib2.Request(url,headers={'User-Agent':'Magic Browser'})
        con = urllib2.urlopen(req)
        return con.read()




def get_all_links(query):
    source_code = ret_sourcecode(query)
    page = source_code
    for b in range(0,10):
        text,endpos = get_next_target(page)
        write_file(text)
        page = page[endpos:]



