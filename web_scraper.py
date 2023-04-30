import logging
from typing import Dict, List

import jsonlines
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger("scraper")
logger.setLevel(logging.DEBUG)


def get_thread_links(first_url: str, prefix: str) -> List[str]:
    """Given an initial URL and a prefix, this function iterates though every page of skateboard city news threads"""
    # starting on first page
    page = requests.get(first_url)
    cont = True
    thread_links = []  # building a list of links
    while cont:
        logger.info(f"Scraping thread links from {page.url}")
        page_soup = BeautifulSoup(page.content, "html.parser")
        # getting all the links to the threads, the links are deeply nested under <id=threads...<class=title...<href=...>>>
        for thread in page_soup.find(id="threads").find_all(class_="title"):
            thread_links.append(f"{prefix}{thread.attrs['href']}")

        # are we on the last page?
        next_page_button = page_soup.find(rel="next")
        if next_page_button:
            next_page = page_soup.find(rel="next").attrs["href"]
            next_page_url = f"{prefix}{next_page}"
            page = requests.get(next_page_url)
        else:
            cont = False  # if there is no next page, we are done
            logger.info(
                f"ALL THREAD LINKS SCRAPED, BEGINNING ITERATION THROUGH {len(thread_links)} THREADS"
            )
    return thread_links


def get_thread_text_vals(thread_links: List[str]) -> List[Dict[str, List]]:
    thread_texts = []
    progress_bar = tqdm(range(len(thread_links)))
    for link in thread_links:
        thread_page = requests.get(link)
        thread_page_bs = BeautifulSoup(thread_page.content, "html.parser")
        thread_title = thread_page_bs.find("title").text
        post_texts = [
            post.text.strip()
            for post in thread_page_bs.find_all(class_="postcontent restore")
        ]
        thread_texts.append({"title": thread_title, "posts": post_texts})
        progress_bar.update(1)
    return thread_texts


if __name__ == "__main__":
    prefix = "http://www.skateboard-city.com/messageboard/"
    first_url = "http://www.skateboard-city.com/messageboard/forumdisplay.php?53-Industry-News&s=dfbb90c126cec561f2fc593627952877"
    # getting the links of every thread on every page
    thread_links = get_thread_links(first_url, prefix)

    # getting a List of Dictionaries that contain the title of each thread and the text of each post under the thread
    thread_texts = get_thread_text_vals(thread_links)

    # writing into a jsonlines file
    with jsonlines.open("data/skateboard-city-news.jsonl", mode="w") as writer:
        writer.write(thread_texts)

    logger.info("DONE")
