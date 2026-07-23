from pathlib import Path
from urllib.parse import urlencode

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_utils import click_shadow


class Wallapop:
    BASE_URL = "https://es.wallapop.com/search"

    COOKIE_REJECT_SELECTOR = ".cmpboxbtnno"

    ITEMS_CONTAINER_SELECTOR = (
        "div.item-card-grid_ItemCardGrid__Rd15w"
        ".item-card-grid_ItemCardGrid--horizontal__X_Q6D"
    )

    ITEM_SELECTOR = (
        "article.retrieval-item-card-module_RetrievalItemCard__ckj4h"
    )

    TITLE_SELECTOR = (
        "h3.retrieval-item-card-module_"
        "RetrievalItemCard__title__GjAq9"
    )

    ATTRIBUTES_SELECTOR = (
        "span.retrieval-item-card-module_"
        "RetrievalItemCard__attributes__x4gQr"
    )

    PRICE_SELECTOR = (
        "div.retrieval-item-card-module_"
        "RetrievalItemCard__price__zXvlG"
    )

    DESCRIPTION_SELECTOR = (
        "p.retrieval-item-card-module_"
        "RetrievalItemCard__description__Luzcb"
    )

    LINK_SELECTOR = "a[href]"

    def __init__(self, driver):
        self.driver = driver

    def build_search_url(
        self,
        keywords,
        min_price,
        max_price,
        min_year=None,
        max_year=None,
        order_by="most_relevance",
    ):
        params = {
            "category_id": 100,
            "min_sale_price": min_price,
            "max_sale_price": max_price,
            "keywords": keywords,
            "order_by": order_by,
        }

        if min_year is not None:
            params["min_year"] = min_year

        if max_year is not None:
            params["max_year"] = max_year

        return f"{self.BASE_URL}?{urlencode(params)}"

    def open_search(
        self,
        keywords,
        min_price,
        max_price,
        min_year=None,
        max_year=None,
        order_by="most_relevance",
    ):
        url = self.build_search_url(
            keywords=keywords,
            min_price=min_price,
            max_price=max_price,
            min_year=min_year,
            max_year=max_year,
            order_by=order_by,
        )

        print(f"\n→ Abriendo búsqueda: {keywords}")

        self.driver.get(url)

        print("✓ Búsqueda abierta")

        return url

    def wait_page_loaded(
        self,
        timeout=15,
    ):
        WebDriverWait(
            self.driver,
            timeout,
        ).until(
            lambda driver: (
                driver.execute_script(
                    "return document.readyState"
                )
                == "complete"
            )
        )

        print("✓ Página cargada")

    def reject_cookies(
        self,
        timeout=15,
    ):
        print("\n→ Intentando rechazar cookies")

        try:
            click_shadow(
                self.driver,
                selector=self.COOKIE_REJECT_SELECTOR,
                timeout=timeout,
            )

            print("✓ Cookies rechazadas")

            return True

        except TimeoutException:
            print("↳ No apareció el aviso de cookies")

            return False

    def get_items_container(
        self,
        timeout=15,
    ):
        container = WebDriverWait(
            self.driver,
            timeout,
        ).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    self.ITEMS_CONTAINER_SELECTOR,
                )
            )
        )

        print("✓ Contenedor de anuncios encontrado")

        return container

    def get_items(
        self,
        timeout=15,
    ):
        container = self.get_items_container(
            timeout=timeout,
        )

        items = container.find_elements(
            By.CSS_SELECTOR,
            self.ITEM_SELECTOR,
        )

        print(
            f"✓ Anuncios encontrados: {len(items)}"
        )

        return items

    def extract_text(
        self,
        item,
        selector,
    ):
        elements = item.find_elements(
            By.CSS_SELECTOR,
            selector,
        )

        if not elements:
            return None

        text = elements[0].text.strip()

        return text or None

    def extract_url(
        self,
        item,
    ):
        links = item.find_elements(
            By.CSS_SELECTOR,
            self.LINK_SELECTOR,
        )

        if not links:
            return None

        return links[0].get_attribute("href")

    def extract_item(
        self,
        item,
    ):
        return {
            "title": self.extract_text(
                item,
                self.TITLE_SELECTOR,
            ),
            "attributes": self.extract_text(
                item,
                self.ATTRIBUTES_SELECTOR,
            ),
            "price": self.extract_text(
                item,
                self.PRICE_SELECTOR,
            ),
            "description": self.extract_text(
                item,
                self.DESCRIPTION_SELECTOR,
            ),
            "url": self.extract_url(item),
        }

    def extract_items(
        self,
        timeout=15,
    ):
        items = self.get_items(
            timeout=timeout,
        )

        results = []

        for index, item in enumerate(
            items,
            start=1,
        ):
            try:
                data = self.extract_item(item)

                results.append(data)

                print(
                    f"✓ Anuncio {index}: "
                    f"{data['title']}"
                )

            except Exception as error:
                print(
                    f"✗ Error extrayendo anuncio "
                    f"{index}: {error}"
                )

        return results

    def print_extracted_items(
        self,
        timeout=15,
        limit=5,
    ):
        items = self.extract_items(
            timeout=timeout,
        )

        for index, item in enumerate(
            items[:limit],
            start=1,
        ):
            print(
                f"\n--- ANUNCIO {index} ---"
            )

            print(
                "Título:",
                item["title"],
            )

            print(
                "Atributos:",
                item["attributes"],
            )

            print(
                "Precio:",
                item["price"],
            )

            print(
                "Descripción:",
                item["description"],
            )

            print(
                "URL:",
                item["url"],
            )

        return items

    def save_item_html(
        self,
        item,
        filename="item.html",
    ):
        output_path = Path(filename)

        output_path.write_text(
            item.get_attribute("outerHTML"),
            encoding="utf-8",
        )

        print(
            f"✓ HTML guardado en: "
            f"{output_path.resolve()}"
        )