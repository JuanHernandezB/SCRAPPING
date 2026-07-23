import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SELECTORS = {
    "id": By.ID,
    "class": By.CLASS_NAME,
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
}


def create_driver(headless=False):
    options = uc.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    options.add_argument(
        "--user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    )

    return uc.Chrome(
        options=options,
        use_subprocess=True,
        version_main=150,
    )


def get_by(selector_type):
    try:
        return SELECTORS[selector_type.lower()]

    except KeyError:
        raise ValueError("selector_type debe ser: id, class, css o xpath")


def click_when_clickable(
    driver,
    selector,
    selector_type="css",
    timeout=10,
):
    by = get_by(selector_type)

    element = WebDriverWait(
        driver,
        timeout,
    ).until(EC.element_to_be_clickable((by, selector)))

    element.click()

    return element


def find_elements(
    driver,
    selector,
    selector_type="css",
    timeout=10,
):
    by = get_by(selector_type)

    WebDriverWait(
        driver,
        timeout,
    ).until(EC.presence_of_element_located((by, selector)))

    return driver.find_elements(
        by,
        selector,
    )


def find_in_shadow_dom(
    driver,
    selector,
):
    return driver.execute_script(
        """
        const selector = arguments[0];
        const elements = document.querySelectorAll("*");

        for (const element of elements) {
            if (!element.shadowRoot) {
                continue;
            }

            const target =
                element.shadowRoot.querySelector(selector);

            if (target) {
                return target;
            }
        }

        return null;
        """,
        selector,
    )


def click_shadow(
    driver,
    selector,
    timeout=10,
):
    def find_shadow_element(current_driver):
        return find_in_shadow_dom(
            current_driver,
            selector,
        )

    element = WebDriverWait(
        driver,
        timeout,
    ).until(find_shadow_element)

    driver.execute_script(
        "arguments[0].click();",
        element,
    )

    return element
