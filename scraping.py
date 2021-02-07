# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt


def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispeheres": hemispheres(browser),        
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):

    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
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

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    return img_url


def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Values']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


#pull in images of the hemispheres of mars
def hemispheres(browser):
    # A way to break up long strings
    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
        #"https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul li", wait_time=1)

    # Click the link, find the sample anchor, return the href
    hemisphere_image_urls = []

    # Parse the HTML
    html = browser.html
    mhemi_list = soup(html, 'html.parser')
    # find the list of results
    items = mhemi_list.find_all('div', class_='item')

    base_part_url = 'https://astrogeology.usgs.gov'

    # for i in range(4):
    #     # Find the elements on each loop to avoid a stale element exception
    #     browser.find_by_css("a.product-item")[i].click()
    #     hemi_data = scrape_hemisphere(browser.html)
    #     # Append hemisphere object to list
    #     hemisphere_image_urls.append(hemi_data)
    #     # Finally, we navigate backwards
    #     browser.back()

    # #print('*' * 100, hemisphere_image_urls)

    # return hemisphere_image_urls

    for item in items:
        url = item.find("a")['href']
        browser.visit(base_part_url+url)
        # Parse individual hemi page
        hemi_item_html = browser.html
        hemi_soup = soup(hemi_item_html, 'html.parser')
        # Scrape title of hemi
        title = hemi_soup.find('h2', class_ = 'title').text
        # Scrape URL of JPG image
        downloads = hemi_soup.find('div', class_ = 'downloads')
        image_url = downloads.find('a')['href']
        # append dict to empty list
        hemisphere_image_urls.append({"title": title, "img_url": image_url})

    return hemisphere_image_urls


def scrape_hemisphere(html_text):
    hempi_soup = soup(html_text, "html.parser")
    try:
        title = hemi_soup.find("h2", class_="title").get_text()
        sample = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:
        title = None
        sampe = None

    hemisphere = {"title": title, "img_url": sample}
    return hemisphere

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())