import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import base64

@st.cache_data
def get_image_as_base64(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

@st.cache_data
def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        films = []
        for film_div in soup.find_all('li', class_='mdl'):
            title_div = film_div.find('a', class_='meta-title-link')
            if title_div:
                title = title_div.text.strip()
            else:
                continue
            
            user_rating_div = film_div.find('div', class_='rating-item').find_next('div', class_='rating-item')
            if user_rating_div:
                user_rating = user_rating_div.find('span', class_='stareval-note').text.strip()
            else:
                user_rating = "N/A"
            
            image_div = film_div.find('figure', class_='thumbnail')
            if image_div:
                image = image_div.find('img', class_='thumbnail-img')
                if 'data-src' in image.attrs:
                    image_url = image['data-src']
                else:
                    image_url = image['src']
            else:
                image_url = "N/A"
            
            films.append((title, image_url, user_rating))
        
        return films
    except requests.RequestException as e:
            st.error(f"Erreur lors de la récupération des données : {e}")
            return []
    
def generate_table(films):
    # Début du tableau HTML
    table_html = "<table style='width:100%; border-collapse: collapse;'>"
    table_html += "<tr><th>Position</th><th>Titre</th><th>Affiche</th><th>Note Utilisateur</th></tr>"
    
    for position, (title, image_url, user_rating) in enumerate(films, start=1):
        image_base64 = get_image_as_base64(image_url) if image_url != "N/A" else ""
        img_html = f'<img src="data:image/jpeg;base64,{image_base64}" width="100px">' if image_base64 else "Pas d'image"
        # Ajout des lignes au tableau
        table_html += f"<tr><td>{position}</td><td>{title}</td><td>{img_html}</td><td>{user_rating}</td></tr>"
    
    table_html += "</table>"
    return table_html

def display_films(films):
    # Affichage des 20 premiers films
    top_films = films[:20]
    table_html = generate_table(top_films)
    st.markdown(table_html, unsafe_allow_html=True)

def main():
    url = "https://www.allocine.fr/film/meilleurs/"
    films = scrape_page(url)
    if len(films) < 20:
        next_page_url = url + "?page=2"
        films += scrape_page(next_page_url)
        display_films(films)

if __name__ == "__main__":
    st.title('Top 20 des films sur Allociné')
    main()