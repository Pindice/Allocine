import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import base64

def get_image_as_base64(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_table(films):
    table_html = "<table>"
    table_html += "<tr><th>Position</th><th>Title</th><th>Image</th><th>User Rating</th></tr>"
    
    for position, (title, image_url, user_rating) in enumerate(films, start=1):
        image_base64 = get_image_as_base64(image_url) if image_url != "N/A" else ""
        img_html = f'<img src="data:image/jpeg;base64,{image_base64}" width="100px">' if image_base64 else "No image"
        table_html += f"<tr><td>{position}</td><td>{title}</td><td>{img_html}</td><td>{user_rating}</td></tr>"
    
    table_html += "</table>"
    return table_html

def display_films(films):
    table_html = generate_table(films)
    st.markdown(table_html, unsafe_allow_html=True)


def scrape_page(url):
    response = requests.get(url)
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

# def display_films(films):
#     # Convertir les URLs en objets images PIL pour l'affichage
#     for i in range(len(films)):
#         if films[i][1] != "N/A":  # Assurez-vous que l'URL de l'image est valide
#             response = requests.get(films[i][1])
#             films[i] = (films[i][0], Image.open(BytesIO(response.content)), films[i][2])

#     # Créez un dataframe pour une meilleure présentation dans Streamlit
#     df = pd.DataFrame(films, columns=['Title', 'Image', 'User Rating'])

#     # Affichez le tableau avec Streamlit
#     st.dataframe(df)  # Utilisez st.dataframe au lieu de st.table pour permettre des images

def main():
    url = "https://www.allocine.fr/film/meilleurs/"
    films = scrape_page(url)
    
    # Vérifiez s'il y a une deuxième page et scrapez-la si nécessaire
    if len(films) < 20:
        next_page_url = url + "?page=2"
        films += scrape_page(next_page_url)
    
    # Affichez les 20 premiers films avec leurs images
    # for i, (title, user_rating, image_url) in enumerate(films[:20], start=1):
    #     print(f"{i}. {title} - Note des spectateurs: {user_rating}")
    #     print(f"Image: {image_url}")
    #     print("\n")

        display_films(films)

# Ceci est le point d'entrée pour l'application Streamlit
if __name__ == "__main__":
    st.title('Top 20 des films sur Allociné')
    main()