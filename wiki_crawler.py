
# coding: utf-8

# # set Threshold here for key word variation

# In[1]:


global Threshold
Threshold = 0.3


# In[8]:


import time
import re
import urllib.request
import urllib
from collections import deque
import requests 
import json
from itertools import product
from nltk.corpus import wordnet
from itertools import product
#import pyenchant
#This will not run on online IDE 
from bs4 import BeautifulSoup 
""" 
def write_to_file(filename,content_list):
    f= open(filename,"a+",encoding="utf-8")
    for line in content_list:
        if "\r\n" not in line:
            f.write(line+"\r\n")
        else:
            f.write(line)
    f.close()
    
    def write_to_file(filename,content_list,flag):
    f= open(filename,"a+",encoding="utf-8")
    if flag == True:
        f.write(line+"\r\n")
    else:
        f.write(line)      
    for line in content_list:
        if "\r\n" not in line:
            f.write(line+"\r\n")
        else:
            f.write(line)
    f.close()

"""
def write_to_file(filename,content_list,flag):
    
    f= open(filename,"a+",encoding="utf-8")
    if flag == True:
        url = content_list.popleft()
        #print(url)
        f.write(json.dumps(url))
        #f.write('\n'.join('%s %s' % x for x in content_list))
        """
        for line in content_list:
            if "\r\n" not in line:
                f.write(line)
                f.write("\r\n")
            else:
                f.write(line)
        """    
    else:
        if "\r\n" not in content_list:
            f.write(content_list+"\r\n")
        else:
            f.write(content_list) 
    f.close()


#write_to_file("timezone.txt","This is line content\r\n")    


# In[3]:


"""
scrap all the links on the current page, 
extract anchor text into global variable -- "anchor_text"
return the url_set for the next depth
by filterring admin page, 
non-English page, avoiding outside link, 
ignoring navigations and marginal/side links; 
avoiding main Wikipedia page,disambiguation
"""

def get_current_pageurl_set(url,dom,en_keyword):
    #url_set=set() 
    url_set = deque()
    # ignore navigations and marginal/side links; ignore Non‐English articles
    inner_contents = dom.find("div", {"id":"mw-content-text","lang":"en"})
    #print(inner_contents)
    try:
        if len(inner_contents) > 0:
            #ignore external links
            external_links = inner_contents.findAll("a",{"class":"external"})
            for match in external_links:
                match.decompose()
            #links = inner_contents.findAll("a", href=True)
            #find_all <a href=/wiki..., avoid outside link
            links = inner_contents.findAll('a', attrs={'href': re.compile("^/wiki")})
            #linkre = re.compile('href=\"https://en.wikipedia.org/wiki(.+?)\"')
            #linkre.findall(inner_contents):
            #print(links)
            for link in links:
                wiki_url = link["href"].strip()
                archor_text = link.text
                # just Follow the links with the prefix /wiki, ignore # in current page,
                #linkre_wiki = re.compile("/wiki(.+?)").match(link_url).group(0)
                #print("linkre_wiki pattern match: " + wiki_url + "\r\n")
                #if linkre_wiki != None:
                #print("get inner url from /wiki/... pattern <--- " + wiki_url)
                message = "get inner url from /wiki/... pattern <--- " + wiki_url
                write_to_file('execute.log',message,False)
                ignore_filter = False
                # ignore administrative links, main Wikipedia page,disambiguation
                ignore_pattern_list = ["\D+:\D+","/wiki/Main_Page$","disambiguation"]
                for ignor in ignore_pattern_list:
                    try:
                        linkre_ignor = re.compile(ignor).search(wiki_url).group()
                        if linkre_ignor != None:
                            ignore_filter = True
                            filter_pattern = ignor
                            break
                    except AttributeError:
                        #print("Don't match pattern-- >"+ignor+ "\r\n")
                        message = "Don't match pattern-- >"+ignor+ "\r\n"
                        write_to_file('execute.log',message,False)
                        continue
                if ignore_filter == True:
                    #print("Ignore the current url --->"+wiki_url + ". Pattern---> "+filter_pattern+ "\r\n")
                    f= open("ignore.log","a+",encoding="utf-8")
                    f.write("Ignore the current url:"+wiki_url+". Pattern: "+filter_pattern + "\r\n")
                    f.close()
                else:
                    url_set.append(wiki_url)
                    if en_keyword == True:
                        anchor_text.append(archor_text)
                    #print('Add URL to the queue --->  ' + wiki_url + "\r\n")
                    message = 'Add URL to the queue --->  ' + wiki_url + "\r\n"
                    write_to_file('execute.log',message,False)
    except TypeError:
        message = url+" can't find the content block \r\n" + "pattern is: {id:mw-content-text,lang:en}\r\n" 
        log_name = "lostContentBlock.txt"
        write_to_file(log_name,message,False)
         
    return url_set
    


# In[12]:


"""
Main body of our crawller
start from seed,
if enable check_keyword, 
we will also estimate the correlation of the currrent anchor text with key word
For polite crawlling, set timesleep = 10 seconds
'frontier_queue' used for the list of url we will crawl one by one
'visited' handled all the url we have visited
'url_depth' used for store the url and its depth information
Every request, ignore image, no-english-html,non-‐textual media, table
find all the canonical link, put them in visited
"""
def Walk_wiki(seed,check_keyword):
    """
    crawlling from the seed, until 6 depth or 1000 url
    """
    #my frontier
    frontier_queue = deque()
    depth = 1;
    
    frontier_queue.append({depth:seed})
    cnt = 1
    
    #avoid crwalling duplicated url
    visited = set();
   
    
    # restore pairs of depth and url 
    url_depth = deque();
    
    #visited = set(visited_path)
    while frontier_queue:
        
        url_depth_pair = frontier_queue.popleft()  # get url from the frontier top 
        depth,url = list(url_depth_pair.items())[0]
        
        if int(depth) > 6:
            print("We are already at the 6th depth. Stop crawlling now! \r\n")
            break
        if int(cnt) > 1000:
            print("We are already get 1000 urls. Stop crawlling now! \r\n")
            break
        
        if url not in visited:
            print('All ready got the: ' + str(cnt) + ' URL.  Currently crawling at:  <---  ' + url)
            message = "All ready got the: " + str(cnt) + "URL.  Currently crawling at:  <--- "  + url
            write_to_file('execute.log',message,False)
            
            try:
                #headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
                headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
'Accept':'text/html;q=0.9,/;q=0.8',
'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'en-US,en',
'Connection':'close',
'Referer':'https://www.google.com/'}
                #polite restriction
                t0 = time.time()
                r = requests.get(url,headers=headers, timeout=10)
                #response_delay = 10*(time.time() - t0)
                response_delay = 5
                respose_message = str(r.status_code) +'\r\n Our crawller is politely Waiting for<---  ' + str(response_delay) +"seconds. Current URL is: "+ url+ "\r\n"
                #print(respose_message)
                message = respose_message
                write_to_file('execute.log',message,False)
                time.sleep(response_delay)
                
                if "blocked" in r.text:
                    #print (str(cnt) + url + " Request Error: we've been blocked\r\n")
                    message = str(cnt) + url + " Request Error: we've been blocked\r\n"
                    write_to_file('execute.log',message,False)
                    f = open("blocked.log","a+",encoding="utf-8")
                    f.write(str(cnt) + url + " Request Error: we've been blocked\r\n")
                    f.close()
                else:
                    content_type = r.headers.get('content-type')
                    content_language = r.headers.get('content-language')
                    # ignore image, no-english-html,non-‐textual media.
                    if 'html' in content_type and 'en' in content_language:
                        #print("Request: "+ str(cnt) +"URL--> "+url+" ---> content-type: "+ content_type + " content-language: " + content_language +"\r\n")
                        message = "Request: "+ str(cnt) +"URL--> "+url+" ---> content-type: "+ content_type + " content-language: " + content_language +"\r\n"
                        write_to_file('execute.log',message,False)
                        #soup = BeautifulSoup(r.content, 'html5lib')
                        soup = BeautifulSoup(r.text, "html.parser")
                        
                        #ignore table
                        try:
                            soup.table.decompose();

                            # get all the url we desired in current page
                            if(check_keyword == True):
                                next_depth_url = match_against_keywords(url,soup)
                            else:
                                next_depth_url = get_current_pageurl_set(url,soup,False)
                                
                            #next_depth_url = fetch_url
                            for scrap_url in next_depth_url:
                                next_depth = depth + 1
                                fetch_url = "https://en.wikipedia.org" + scrap_url
                                frontier_queue.append({next_depth:fetch_url})
                            #url_depth |= {(fetch_url,next_depth)}
                        
                        #depth += 1
                            visited |= {url}       # after crawling, put it in visited set
                            url_depth.append({next_depth:url})
                            #test
                            f = open("Frontier.log","a+",encoding="utf-8")
                            f.write(url + " "+ str(depth) + "\n")
                            f.close()
                            #find canonical link and put in the visited set
                            canonical_links = soup.find("link",{"rel":"canonical"})["href"]
                            if (canonical_links != url):
                                visited |= {canonical_links}
                            #visited_dom_name = url +".txt";
                            visited_dom_name = str(cnt) +".txt";
                            cnt += 1
                            #f = open(visited_dom_name,"a+",encoding="utf-8")
                            #f.write(r.content)
                            #f.close()
                            message = str(url) + "\r\n" + r.text
                            #write_to_file(visited_dom_name,r.text,False)
                            write_to_file(visited_dom_name,message,False)
                        except AttributeError:
                            #message = "we didn't get page!!! url-->"+url+". The times:"+ str(cnt) + "\r\n"
                            #print("Didn't get soup. Please check log")
                            message = "Didn't get soup. Please check log"
                            write_to_file('execute.log',message,False)
                            block_message = url + str(soup)
                            write_to_file("souperror.log",block_message,False)
                            """
                            else:
                            message = "we didn't get page!!! url-->"+url+". The times:"+ str(cnt) + "\r\n"
                            print(message)
                            write_to_file("emptypage.log",message,False)
                            """        
                    else:
                        message = "we've been on weird page!!! url-->"+url+". Content-Type:"+ content_type + " Content-Language: "+ content_language + "\r\n"
                        #print(message)
                        #message = "Didn't get soup. Please check log"
                        write_to_file('execute.log',message,False)
                        write_to_file("ignorepage.log",message,False)
                        #f = open("blocked.log","a+")
                        #f.write(url + " Request Error: we've been blocked\r\n")
                        #f.close() 
                        
            except requests.exceptions.RequestException:
                #print("Request Error ---->"+ requests.exceptions.RequestException + "\r\n")
                message = "Request Error ---->"+ requests.exceptions.RequestException + "\r\n"
                write_to_file('execute.log',message,False)
                f = open("RequerstError.log","a+",encoding="utf-8")
                f.write(url + " Request Error "+ requests.exceptions.RequestException + "\r\n")
                f.close()
                continue  
    return url_depth
    


# In[5]:


"""

"""
def keywords_importance(archor_text,keywords):
    weights = []
    
    #Thanks to @alexis' note from https://stackoverflow.com/questions/30829382/check-the-similarity-between-two-words-with-nltk-with-python
    for word1 in archor_text:
        for word2 in keywords:
            wordFromList1 = wordnet.synsets(word1)
            wordFromList2 = wordnet.synsets(word2)
            if wordFromList1 and wordFromList2: 
                s = wordFromList1[0].wup_similarity(wordFromList2[0])
                if s == None:
                    s = 0.0
                pair = {'weight':s,'key_word':word1}
                weights.append(pair)
                #print("SSSSSS")
                #print(s)
    seq = [x['weight'] for x in weights]
    if len(seq) == 0:
        max_weight = 0.0
    else:
        max_weight = max(seq)
    #print("max_weight")
    #print(max_weight)
    #max_weight = (max(weights["weight"]))
    find = False
    for item in weights:
        if item["weight"] == max_weight:
            find_keywords = item["key_word"]
            find = True
            break
    if find == False:
        find_keywords = "green"
    
    return {'weight':max_weight,'key_word':find_keywords}


# In[7]:


# for keywords set, avoid duplicate
def remove_duplicate(duplicate): # thanks to https://www.geeksforgeeks.org/python-remove-duplicates-list/
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num) 
    return final_list 


# In[6]:


"""
Return the url match against out keywords
get all the url, filtered by get_current_pageurl_set() and their anchor text
for each url and its anchor text: 
compared with keywords set and estimate the correlation between them
set Threshold as 0.7
if correlation > 0.7, we think they are highly correlated, 
we will put it in frontier waiting for visiting
"""
def match_against_keywords(url,soup):
    final_url_list = deque()
    
    raw_url = get_current_pageurl_set(url,soup,True)
    keywords_set = remove_duplicate(key_words_list)
    message = "Now search keywords is:"
    print("Now search keywords is:")            
    for keyword_item in keywords_set:
        print(keyword_item)
        write_to_file('execute.log',message,False)
    while anchor_text:
        current_text = anchor_text.popleft()
        current_url = raw_url.popleft()
        # find target url with keywords pattern
        #keywords_set = remove_duplicate(key_words_list)
        key_words_pattern = ""
        
        for word in keywords_set:
            if current_text.lower().find(word) != -1 and current_url.lower().find(word):
                text_list = current_text.split()
                data = keywords_importance(text_list,key_words_list)
                words_weight = data["weight"]
                relative_keyword = data["key_word"]
                #print("weight!!!")
                #words_weight,relative_keyword = keywords_importance(text_list,key_words_list)
                #Threshold = 0.7
                if words_weight == None:
                    words_weight_float = 0.0
                else:
                    words_weight_float = float(words_weight)
                if words_weight_float > Threshold:
                    print("similar word from anchor text:")
                    print(relative_keyword)
                    print("weight:")
                    print(words_weight)
                    final_url_list.append(current_url)
                    key_words_list.append(relative_keyword)
                    message = "similar word from anchor text:"+ relative_keyword + "weight:" + str(words_weight) + "\r\n" + "Add URL to the queue --->  " + current_url + "\r\n"
                    print('Add URL to the queue --->  ' + current_url + "\r\n")
                    write_to_file('execute.log',message,False)
    return final_url_list


# # Entrance of problem 3

# In[8]:



#https://en.wikipedia.org/wiki/Carbon_footprint
def problem3():
    URL = input("Please type the seed URL: ");
    key_words = input("Please type the keywords list, seperated by comma: ");
    print(URL)
    #handel the keyword variation
    global key_words_list
    
    # extract the achor text here, if it match against keywords 
    #(compared by their correlation), anchor_text would be added to keywords sets
    global anchor_text
    
    key_words_list = key_words.split()
    anchor_text = deque()   
    url_set = Walk_wiki(URL,True)
    
    write_to_file("crawlerlistwithkeywords.txt",url_set,True)
    
problem3()


# # Entrance of problem 1

# In[13]:


#%connect_info
#https://en.wikipedia.org/wiki/Time_zone

#%qtconsole
def problem1():
    URL = input("Please type the seed URL");
    print(URL)   
    url_set = Walk_wiki(URL,False)
    write_to_file("crawlerlist.txt",url_set,True)
    
problem1()
    


# In[11]:


from operator import itemgetter
def writ_in_order(filepath):

    with open(filepath,encoding="utf-8") as fp:  
        lines = fp.readlines()
        lines.sort(key=lambda l: float(l.split()[1]))

    with open('problem2result.txt', 'a+',encoding="utf-8") as outfile: 
        for line in lines:  
            outfile.write(line)
            #print(lines)

        #new_lines = sorted(lines,key=itemgetter(1))

       # cnt = 1
    """
    for line in lines:  
        url,depth = line.split()
        print("{} {}".format(depth, url))
            #print("Line {}: {}".format(cnt, line.strip()))
            #line = fp.readline()
            #cnt += 1 
    
    """
    


# # Entrance of problem 2

# In[13]:


def problem2(): 
    filenames = ['ElectricCar.txt', 'CarbonFootprint.txt','Timezon.txt']
    with open('merge.txt', 'a+',encoding="utf-8") as outfile:
        for fname in filenames:
            with open(fname,encoding="utf-8") as infile:
                content = infile.read() 
                try:
                    re.compile('\n$').search(content).group()
                    outfile.write(content)
                except AttributeError:
                    content = content +'\n'
                    outfile.write(content)
    filepath = "merge.txt"
    writ_in_order(filepath);
problem2()            


# In[ ]:



        


# In[26]:




