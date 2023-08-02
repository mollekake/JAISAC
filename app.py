import threading
import tkinter as tk
from tkinter import ttk
import requests
import bs4 
import json
import time
import re

#Setting up tkinter
root = tk.Tk()
root.title('JAISAC')
root.geometry("900x900")
root.resizable(False, False)

file = "JAISAC_export.txt"
text_to_file = ""

#Function to start a second thread, so the app won't freeze up while processing
def button_thread():
    button.config(text="Checking, please wait...",state="disable")
    
    progressbar.pack(fill="x")
    progressbar['value'] = 0
    x = threading.Thread(target=check_shows)
    x.start()

#export func
def save_to_file(file, text):
    with open(file, 'w') as f:
        json.dump(text, f, indent=4)

#Main function
#Very sloppy. Could be better.
def check_shows():
    c = str({country.get()}).removeprefix("{'").removesuffix("'}")
    user_id = str({username.get()}).removeprefix("{'").removesuffix("'}")

    justwatch = "https://www.justwatch.com/"
    url = justwatch+c

    u = []

    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, "html.parser") 

    for div in soup.find_all('div', attrs={'class':'filter-bar-content-type__item'}):
        for a in div.find_all('a'):
            u.append(str(a['href']).removeprefix("/"))
    del u[0]
    movie_url = u[0]
    show_url = u[1]

    time.sleep(1)
    res = requests.get(justwatch+movie_url)
    soup = bs4.BeautifulSoup(res.text, "html.parser") 
    for div in soup.find_all('div', attrs={'class':'title-list-grid__item'})[0]:
        movie_url = re.findall(".*\/",str(div.find_next('a')['href']))[0]
        movie_url = justwatch+str(movie_url).removeprefix("/")
        break

    time.sleep(1)
    res = requests.get(justwatch+show_url)
    soup = bs4.BeautifulSoup(res.text, "html.parser") 
    for div in soup.find_all('div', attrs={'class':'title-list-grid__item'})[0]:
        show_url = re.findall(".*\/",str(div.find_next('a')['href']))[0]
        show_url=justwatch+str(show_url).removeprefix("/")
        break

    url = 'https://www.imdb.com/user/'+user_id+'/watchlist?sort=alpha%2Casc&view=detail' 

    res = requests.get(url,headers={'Accept-Language':'en','User-Agent': 'python-requests/2.31.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}) 
    soup = bs4.BeautifulSoup(res.text, "html.parser") 
    js_elements = soup.find_all('script')
    js_text = None
    search_str = 'IMDbReactInitialState.push('

    for element in js_elements:
        text = element.text
        if search_str in text:
            js_text = text.strip()
            break

    json_start = js_text.index(search_str) + len(search_str)
    json_text = js_text[json_start:-2]
    json_obj = json.loads(js_text[json_start:-2])
    titles = []
    for title in json_obj['titles']:
        json_title = json_obj['titles'][title]
        list.append(titles,json_title['primary']['title'])

    #Running the same thing again because imdb only show 100 titles at once.
    if len(titles) == 100:
        url = 'https://www.imdb.com/user/'+user_id+'/watchlist?sort=alpha%2Cdesc&view=detail'
        #This header should fetch the titles in english, and not the language of the country
        res = requests.get(url,headers={'Accept-Language':'en','User-Agent': 'python-requests/2.31.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}) 
        soup = bs4.BeautifulSoup(res.text, "html.parser") 
        js_elements = soup.find_all('script')
        js_text = None
        search_str = 'IMDbReactInitialState.push('

        for element in js_elements:
            text = element.text
            if search_str in text:
                js_text = text.strip()
                break

        json_start = js_text.index(search_str) + len(search_str)
        json_text = js_text[json_start:-2]
        json_obj = json.loads(js_text[json_start:-2])

        for title in json_obj['titles']:
            json_title = json_obj['titles'][title]
            list.append(titles,json_title['primary']['title'])

    #Ran the thing at least once, maybe twice. If the watchlist has more than 200 titles, no more than 200 will show up currently.
    titles = list(dict.fromkeys(titles))
    
    #JustWatch part--------------------------------------------------------------------------
    just = ""
    found = {}
    not_found = []
    no_streams = []

    
    l = 99.999/len(titles)
    mins = (len(titles)/60)*2
    if len(titles) >= 200:
        time_label.config(text="Found "+str(len(titles))+" titles in watchlist.\nWARNING! The app can not handle more than 200 titles at this point.\nTime to complete:\nRoughly "+str(mins)+" minutes.")    
    time_label.config(text="Found "+str(len(titles))+" titles in watchlist.\nTime to complete:\nRoughly "+str(mins)+" minutes.")
    
    #Going through each title in the list. Adding in pauses so JustWatch won't deny the requests
    for title in titles:
        if l >= 5:
            exit()
        progressbar.step(l) 
        n_title = str((str(str(title.replace(" ","-")).lower()).replace("'","")).replace(".","")).replace(":","")
        shows = requests.get(show_url+n_title)
        time.sleep(1)
        movies = requests.get(movie_url+n_title)
        just = 'Not Found'
        if movies.status_code != 404:
            just = movie_url+n_title
        if shows.status_code != 404 and just == "Not Found":
            just = show_url+n_title
        time.sleep(1)

        #Title was found on JustWatch. Gathering which streaming platforms each title can be viewed on.
        if just != 'Not Found':
            url=just
            
            try:
                res = requests.get(url) 
            except Exception as e:
                print(e)
            soup = bs4.BeautifulSoup(res.text, "html.parser") 
            sc = soup.find_all('div', attrs={'class':'buybox-row'})
            streams = 0
            platforms = []
            for div in sc:
                for label in div.find_all('label'):
                    if "stream" in str(label):
                        streams = div
                        break
            
            if streams != 0:
                for a in streams:
                    for img in a.find_all("img"):
                        platforms.append(img['alt'])
                found[title]=platforms
            else:
                no_streams.append(title)
        else:
            not_found.append(title)
    
    view_text_1 = ""
    view_text_2 = ""
    view_text_3 = ""
    for entry in found:
        view_text_1 = view_text_1 + entry + "\n" +str(found[entry]) + "\n" + "---" + "\n"
    for entry in no_streams:
        view_text_2 = view_text_2 + entry  + "\n" + "---" + "\n"
    for entry in not_found:
        view_text_3 = view_text_3 + entry  + "\n" + "---" + "\n"

    #Automatically exports a text file
    save_to_file(file,found)

    #Setting tkinter stuff. enabling the button.
    view_1.insert(tk.INSERT,view_text_1)
    view_2.insert(tk.INSERT,view_text_2)
    view_3.insert(tk.INSERT,view_text_3)
    progressbar['value'] = 100
    button.config(text="Check movies and shows",state="enable")
    time_label.config(text="")


#The tkinter window
country = tk.StringVar()
username = tk.StringVar()
button_frame = ttk.Frame(root)

#Box for country code, username and confirm button
country_label = ttk.Label(button_frame, text="Enter your country code below:\n Examples: \n NO = Norway \n US = USA \n SE = Sweden")
country_label.pack(fill='x', expand=True)
country_entry = ttk.Entry(button_frame, textvariable=country)
country_entry.pack(fill='x', expand=True)
country_entry.focus()
user_label = ttk.Label(button_frame, text="Enter your IMDB username:\n(Usually begins with 'ur')")
user_label.pack(fill='x', expand=True)
user_entry = ttk.Entry(button_frame, textvariable=username)
user_entry.pack(fill='x', expand=True)
button = ttk.Button(button_frame, text="Check movies and shows", command=button_thread)
button.pack(fill='x', expand=True, pady=10)

#label used for telling how long the checkings will take
time_label = ttk.Label(button_frame,text="")
time_label.pack(fill='x', expand=True)


progressbar = ttk.Progressbar(button_frame, maximum=100)
button_frame.pack(padx=10, pady=0)

#The 3 text boxes that will be populated with movies etc.
frame = ttk.Frame(root)
text= ttk.Label(frame, text= "Movies and shows with streaming options:\n(This list is automatically exportet to a text file)")
text.pack(pady=10)

scroll_1=ttk.Scrollbar(frame,orient="vertical")
scroll_1.pack(side="right",fill="y")
view_1 = tk.Text(frame,yscrollcommand=scroll_1.set, height=7)
view_1.pack(pady=10)

#button_export = ttk.Button(frame, text="Export list to text file", command=lambda:save_to_file(file,text_to_file))
#button_export.pack(fill='x', expand=True, pady=10)

frame.pack()

frame_2 = ttk.Frame(root)
text= ttk.Label(frame_2, text= "Movies and shows not found on any streaming platforms:\n(The app doesn't catch all. Double check if you belive it should be)\n(It does not catch movies that has the same title as already released movies)")
text.pack(pady=10)
scroll_2=ttk.Scrollbar(frame_2,orient="vertical")
scroll_2.pack(side="right",fill="y")
view_2 = tk.Text(frame_2,yscrollcommand=scroll_2.set, height=7)
view_2.pack(pady=10)
frame_2.pack()

frame_3 = ttk.Frame(root)
text= ttk.Label(frame_3, text= "Movies and shows not found on JustWatch:\n(Foreign title names might cause issues.)")
text.pack(pady=10)
scroll_3=ttk.Scrollbar(frame_3,orient="vertical")
scroll_3.pack(side="right",fill="y")
view_3 = tk.Text(frame_3,yscrollcommand=scroll_3.set, height=7)
view_3.pack(pady=10)
frame_3.pack()

root.mainloop()
