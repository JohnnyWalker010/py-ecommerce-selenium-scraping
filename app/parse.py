import csv
import time
from dataclasses import dataclass, fields, asdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from tqdm import tqdm

BASE_URL = "https://webscraper.io/"
URLS = {
    "home": "https://webscraper.io/test-sites/e-commerce/more",
    "computers": "https://webscraper.io/test-sites/"
                 "e-commerce/more/computers",
    "laptops": "https://webscraper.io/test-sites/"
               "e-commerce/more/computers/laptops",
    "tablets": "https://webscraper.io/test-sites/"
               "e-commerce/more/computers/tablets",
    "phones": "https://webscraper.io/test-sites/e-commerce/more/phones",
    "touch": "https://webscraper.io/test-sites/e-commerce/more/phones/touch",
}


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int


PRODUCT_FIELDS = [field.name for field in fields(Product)]


class WebScraper:
    def __init__(self) -> None:
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)

    def click_accept_cookies(self, url: str) -> None:
        self.driver.get(url)
        cookies_accept_button = self.driver.find_element(
            By.CLASS_NAME, "acceptCookies"
        )
        if cookies_accept_button.is_displayed():
            cookies_accept_button.click()

    def scroll_down_page_with_more_button(self, url: str) -> None:
        self.driver.get(url)

        while True:
            try:
                more_button = self.driver.find_element(
                    By.CSS_SELECTOR, "[class*=scroll-more]"
                )
                if more_button.is_displayed():
                    more_button.click()
                    time.sleep(1)
            finally:
                break

    def scrape_single_page(self, url: str) -> [Product]:
        result = []
        self.driver.get(url)
        products = self.driver.find_elements(
            By.CSS_SELECTOR, "[class*=product-wrapper]"
        )
        for product in products:
            result.append(
                Product(
                    title=product.find_element(
                        By.CSS_SELECTOR, "a.title"
                    ).get_attribute("textContent"),
                    description=product.find_element(
                        By.CSS_SELECTOR, "[class*=description]"
                    ).text,
                    price=float(
                        product.find_element(
                            By.CSS_SELECTOR, "[class*=price]"
                        ).text.replace("$", "")
                    ),
                    rating=len(
                        product.find_elements(
                            By.CSS_SELECTOR, "p > span.ws-icon-star"
                        )
                    ),
                    num_of_reviews=int(
                        product.find_element(
                            By.CSS_SELECTOR, "[class*=review-count]"
                        ).text.split()[0]
                    ),
                )
            )
        return result

    @staticmethod
    def write_to_csv(products: [Product], filename: str) -> None:
        with open(
                filename,
                "w",
                newline="",
                encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(PRODUCT_FIELDS)
            writer.writerows(
                [asdict(product).values() for product in products]
            )

    def close_driver(self) -> None:
        self.driver.quit()


def get_all_products() -> None:
    for name, url in tqdm(
        URLS.items(),
        desc="Scrapping pages",
        colour="green",
    ):
        webscraper = WebScraper()
        webscraper.click_accept_cookies(url)
        webscraper.scroll_down_page_with_more_button(url)
        products = webscraper.scrape_single_page(url)
        webscraper.write_to_csv(products, f"{name.lower()}.csv")
        webscraper.driver.quit()
        webscraper.close_driver()


if __name__ == "__main__":
    get_all_products()
