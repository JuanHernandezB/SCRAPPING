from explorer import interactive_explorer
from selenium_utils import create_driver
from wallapop import Wallapop


def main():
    driver = create_driver(
        headless=False
    )

    wallapop = Wallapop(driver)

    try:
        wallapop.open_search(
            keywords="SEAT Leon",
            min_price=1000,
            max_price=5000,
            min_year=2013,
        )

        wallapop.wait_page_loaded()

        wallapop.reject_cookies()

        articles = wallapop.print_extracted_items(
            limit=10
        )

        interactive_explorer(driver)

        input(
            "\nPulsa ENTER para cerrar..."
        )

    finally:
        driver.quit()

        print("\n✓ Navegador cerrado")


if __name__ == "__main__":
    main()