# Import Splinter, BeautifulSoup, Pandas and datetime
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Set news title and paragraph variables
    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
    
    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for erro handling
    try:
        # Scrape
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
   
    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url


def mars_facts():
    
    try:
        # Use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
        
    except BaseException:
        return None
    
    # Assign columns to the new DataFrame for additional clarity.
    df.columns=['Description', 'Mars', 'Earth']
    # Turn the Description column into the DataFrame's index.
    df.set_index('Description', inplace=True)

    # Convert our DataFrame back into HTML-ready code
    return df.to_html(classes="table table-striped")


def hemispheres(browser):
    # Visit URL
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    
    # Create a list to hold the images and titles.
    hemisphere_image_urls = [] 
    
    # Parse the resulting html with soup
    html = browser.html
    hemi_soup = soup(html, 'html.parser')
    
    try:
        # Find the number of images to scan
        pics = len(hemi_soup.select("div.item"))
                 
        # Using a for loop, iterate through the tags
        for i in range(pics):
            # Create an empty dictionary
            hemispheres = {}
            # Loop through the full-resolution image URL, click the link, find the Sample 
            #image anchor tag, and get the href.
            image_link = hemi_soup.select("div.description a")[i].get('href')
            browser.visit(f'https://marshemispheres.com/{image_link}')
            sample_soup = soup(browser.html, 'html.parser')
            img_url = sample_soup.select_one("div.downloads ul li a").get('href')
            # Retrieve the full-resolution image URL string and title for the hemisphere image
            title = sample_soup.select_one("h2.title").get_text()
            hemispheres = {
                'img_url': url + img_url,
                'title': title}
            # Add the dictionary with the image URL string and the hemisphere image title to the list
            hemisphere_image_urls.append(hemispheres)
            # Navigate back to the beginning to get the next hemisphere image
            browser.back()
        
    except BaseException:
        return None
    
    # Return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

# Tells Flask our script is complete and ready for action.
if __name__ == "__main__":
    
    # If running as script, print scraped data
    print(scrape_all())