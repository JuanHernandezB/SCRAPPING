from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from selenium_utils import (
    SELECTORS,
    click_shadow,
    click_when_clickable,
    find_elements,
    get_by,
)


def xpath_by_text(
    text,
    tag="*",
    partial=True,
):
    if partial:
        return (
            f'//{tag}'
            f'[contains(normalize-space(.), "{text}")]'
        )

    return (
        f'//{tag}'
        f'[normalize-space(.)="{text}"]'
    )


def print_elements(
    elements,
    title="Elementos encontrados",
    limit=10,
):
    print(f"\n✓ {title}: {len(elements)}")

    for index, element in enumerate(
        elements[:limit],
        start=1,
    ):
        print(f"\n--- Elemento {index} ---")
        print("tag:", element.tag_name)
        print("text:", element.text[:300])
        print("displayed:", element.is_displayed())
        print("enabled:", element.is_enabled())

        outer_html = element.get_attribute(
            "outerHTML"
        )

        print(
            "html:",
            outer_html[:500],
        )


def find_elements_debug(
    driver,
    selector,
    selector_type="css",
    timeout=10,
):
    try:
        elements = find_elements(
            driver,
            selector,
            selector_type,
            timeout,
        )

        print_elements(elements)

        return elements

    except TimeoutException:
        print(
            "✗ No se encontró ningún elemento "
            "con ese selector."
        )

        return []


def find_by_text(
    driver,
    text,
    tag="*",
    partial=True,
    timeout=10,
):
    xpath = xpath_by_text(
        text,
        tag,
        partial,
    )

    try:
        WebDriverWait(
            driver,
            timeout,
        ).until(
            EC.presence_of_element_located(
                (By.XPATH, xpath)
            )
        )

        elements = driver.find_elements(
            By.XPATH,
            xpath,
        )

        print_elements(
            elements,
            title="Elementos encontrados por texto",
        )

        return elements

    except TimeoutException:
        print(
            "✗ No se encontró ningún elemento "
            "con ese texto."
        )

        return []


def click_by_text(
    driver,
    text,
    tag="*",
    partial=True,
    timeout=10,
):
    xpath = xpath_by_text(
        text,
        tag,
        partial,
    )

    element = WebDriverWait(
        driver,
        timeout,
    ).until(
        EC.element_to_be_clickable(
            (By.XPATH, xpath)
        )
    )

    element.click()

    print(
        f"✓ Click por texto realizado: {text}"
    )

    return element


def save_page_html(
    driver,
    filename="page.html",
):
    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            driver.page_source
        )

    print(
        f"✓ HTML completo guardado en: {filename}"
    )


def save_element_html(
    driver,
    selector,
    selector_type="css",
    filename="element.html",
    timeout=10,
):
    by = get_by(selector_type)

    element = WebDriverWait(
        driver,
        timeout,
    ).until(
        EC.presence_of_element_located(
            (by, selector)
        )
    )

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            element.get_attribute(
                "outerHTML"
            )
        )

    print(
        f"✓ HTML del elemento guardado en: "
        f"{filename}"
    )

    return element


def ask_selector():
    selector_type = input(
        "Tipo [id/class/css/xpath]: "
    ).strip().lower()

    selector = input(
        "Selector: "
    ).strip()

    return selector_type, selector


def ask_text_search():
    text = input(
        "Texto a buscar: "
    ).strip()

    tag = input(
        "Tag [* / span / button / a / div]: "
    ).strip() or "*"

    partial = (
        input(
            "¿Búsqueda parcial? [s/n]: "
        )
        .strip()
        .lower()
        != "n"
    )

    return text, tag, partial


def show_menu():
    print("\n=== MODO EXPLORADOR ===")

    print(
        "Comandos:"
    )

    print(
        "  find       Buscar elementos por selector"
    )

    print(
        "  click      Hacer click por selector"
    )

    print(
        "  text       Buscar elementos por texto"
    )

    print(
        "  clicktext  Hacer click por texto"
    )

    print(
        "  shadow     Click dentro de Shadow DOM"
    )

    print(
        "  html       Guardar HTML completo"
    )

    print(
        "  element    Guardar HTML de un elemento"
    )

    print(
        "  url        Mostrar URL actual"
    )

    print(
        "  salir      Cerrar modo explorador"
    )


def interactive_explorer(
    driver,
    timeout=10,
):
    show_menu()

    while True:
        command = input(
            "\nComando: "
        ).strip().lower()

        if command in {
            "salir",
            "exit",
            "quit",
            "q",
        }:
            print(
                "✓ Modo explorador finalizado"
            )

            break

        try:
            if command == "url":
                print(
                    driver.current_url
                )

            elif command == "find":
                selector_type, selector = (
                    ask_selector()
                )

                find_elements_debug(
                    driver,
                    selector,
                    selector_type,
                    timeout,
                )

            elif command == "click":
                selector_type, selector = (
                    ask_selector()
                )

                element = click_when_clickable(
                    driver,
                    selector,
                    selector_type,
                    timeout,
                )

                print(
                    f"✓ Click realizado sobre "
                    f"<{element.tag_name}>"
                )

                print(
                    f"URL actual: "
                    f"{driver.current_url}"
                )

            elif command == "text":
                text, tag, partial = (
                    ask_text_search()
                )

                find_by_text(
                    driver,
                    text,
                    tag,
                    partial,
                    timeout,
                )

            elif command == "clicktext":
                text, tag, partial = (
                    ask_text_search()
                )

                click_by_text(
                    driver,
                    text,
                    tag,
                    partial,
                    timeout,
                )

            elif command == "shadow":
                selector = input(
                    "Selector CSS dentro "
                    "del Shadow DOM: "
                ).strip()

                element = click_shadow(
                    driver,
                    selector,
                    timeout,
                )

                print(
                    "✓ Click realizado dentro "
                    "de Shadow DOM"
                )

                print(
                    element.get_attribute(
                        "outerHTML"
                    )[:500]
                )

            elif command == "html":
                filename = input(
                    "Nombre del archivo "
                    "[page.html]: "
                ).strip() or "page.html"

                save_page_html(
                    driver,
                    filename,
                )

            elif command == "element":
                selector_type, selector = (
                    ask_selector()
                )

                filename = input(
                    "Nombre del archivo "
                    "[element.html]: "
                ).strip() or "element.html"

                save_element_html(
                    driver,
                    selector,
                    selector_type,
                    filename,
                    timeout,
                )

            else:
                print(
                    "✗ Comando no reconocido"
                )

        except TimeoutException:
            print(
                "✗ Timeout: el elemento no apareció "
                "a tiempo."
            )

        except Exception as error:
            print(
                f"✗ Error: {error}"
            )