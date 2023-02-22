from flask import Flask, request, render_template,redirect,url_for,session,flash,Markup
from bs4 import BeautifulSoup
import requests
from jinja2 import Template 
from Model import BoxOfficePredticion
import validators


app = Flask(__name__)

data = {}
predictor = BoxOfficePredticion()

@app.route('/')
def my_form():
    return render_template('index.html')



def scrape_data(url,tconst):
    response = requests.get(url)
    soup = BeautifulSoup(response.content,'html.parser')
    title = soup.find('div', attrs = {'class':'sc-80d4314-1 fbQftq'}).find('h1').text
    date  = soup.find('a', attrs = {'class':"ipc-link ipc-link--baseAlt ipc-link--inherit-color sc-8c396aa2-1 WIUyh"}).text                      # Hossam Galal
    genres = soup.find('div',attrs={'class':'ipc-chip-list__scroller'})
    new_genres = []
    if(genres != None):
        for genre in genres:
            print(genre.find('span').text)
            new_genres.append('<div class="genre">{}</div>\n'.format(genre.find('span').text))
        
        
    director  = soup.find('a', attrs = {'class':"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}).text    
    writers  = soup.find('a', attrs = {'class':"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}).text    
    
    description = soup.find('span',attrs={'class':"sc-16ede01-1 kgphFu"}).text                    # Hossam Galal
    img_src = soup.find('img', attrs = {'class':'ipc-image'})['src']
    status = soup.find('div',attrs={'class':'sc-5766672e-1 fsIZKM'})
    if status == None:
        status = 'Launched'
    else:
        status = status.text
    expected_date = soup.find('div',attrs={'class':'sc-5766672e-2 bweBzH'})
    if expected_date == None:
        expected_date = date
    else:
        expected_date = expected_date.text
    global data
    data = {'tconst':tconst,"title":title,"year":date,'genres':new_genres,'description':description,'img_src':img_src,'status':status,'expected_date':expected_date,'director':director,'writers':writers}


def validate_url(url):
    global predictor
    valid=validators.url(url)
    tconst = ""
    if valid==True:
        first_slash = url.find('/', url.find("title")) + 1
        tconst = url[first_slash:url.find('/',first_slash)]
    else:
        tconst = predictor.get_tconst(url)
        if(tconst == ""):
            return "",""
        else:
            url = "https://www.imdb.com/title/{}/".format(tconst)
    return tconst,url


@app.route('/done',methods=['POST'])
def search_post():
    text = request.form['text']
    url = text.lower()
    tconst, url = validate_url(url)
    if url == "":
        return redirect("done")
    scrape_data(url, tconst)
    return redirect("done")
    

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    url = text.lower()
    tconst, url = validate_url(url)
    if url == "":
        return render_template('index.html')
    scrape_data(url, tconst)
    return redirect("done")

@app.route('/done')
def done():
    global predictor
    global data
    revenue = int(predictor.get_movie(data['tconst']))
    revenue = "{:,} $".format(revenue)
    new_genres = ' '.join(data['genres'])
    return render_template("/expRev.html", title = data['title'],year=data['year'],genres= new_genres, description=data['description'],
                           img_src=data['img_src'],status=data['status'],expected_date=data['expected_date'],director=data['director'],writers=data['writers'],world_revenue=revenue)
    

