import time

from core.environment.host import get_host_for_selenium_testing
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


@pytest.mark.slow  
def test_notepad_index():
    # Configurar Selenium para usar Google Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Iniciar el driver de Chrome usando webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        host = get_host_for_selenium_testing()

        # 1. Abrir la página de índice
        driver.get(f'{host}/notepad')

        # 2. Esperar un momento para asegurarse de que la página se haya cargado completamente
        time.sleep(4)

        # 3. Verificar que la página contenga un elemento específico
        notepad_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "notepad-list"))
        )

        assert notepad_list is not None, "La lista de notas no se encontró en la página."

    except Exception as e:
        print(f"Error durante la prueba: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("Captura de pantalla guardada como 'error_screenshot.png'")

    finally:
        # Cerrar el navegador
        driver.quit()


@pytest.mark.slow
def test_login_success():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Acceder a la página de login
        driver.get("http://localhost:5000/login")

        # Localizar el campo de email, contraseña y botón de login
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        
        # Esperar hasta que el botón de envío esté clickable
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "submit"))
        )

        # Introducir las credenciales
        email_input.send_keys("user1@example.com")
        password_input.send_keys("1234")
        login_button.click()

        # Esperar que la URL cambie y comprobar que ya no estás en la página de login
        WebDriverWait(driver, 10).until(EC.url_contains("/notepad"))
        print("Inicio de sesión exitoso.")

    except Exception as e:
        print(f"Error durante la prueba de inicio de sesión: {e}")

    finally:
        driver.quit()


@pytest.mark.slow
def test_create_notepad():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 1. Iniciar sesión (precondición)
        driver.get("http://localhost:5000/login")
        driver.find_element(By.NAME, "email").send_keys("user1@example.com")
        driver.find_element(By.NAME, "password").send_keys("1234")
        
        # Esperar hasta que el botón de inicio de sesión sea clickable
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "submit"))
        )
        login_button.click()

        # 2. Acceder a la página de crear nota
        driver.get("http://localhost:5000/notepad/new")

        # 3. Introducir datos de la nueva nota
        title_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "title"))
        )
        content_input = driver.find_element(By.NAME, "content")

        title_input.send_keys("Mi nueva nota")
        content_input.send_keys("Contenido de la nueva nota.")

        # Esperar hasta que el botón de envío de la nota sea clickable
        submit_note_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        submit_note_button.click()

        # 4. Comprobar que la nota se ha creado y que estamos de vuelta en la lista
        WebDriverWait(driver, 10).until(EC.url_contains("/notepad"))
        print("Nota creada correctamente.")

    except Exception as e:
        print(f"Error durante la prueba de creación de nota: {e}")

    finally:
        driver.quit()


@pytest.mark.slow
def test_edit_notepad():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 1. Abrir la página de inicio de sesión
        driver.get("http://localhost:5000/login")
        
        # 2. Completar el formulario de inicio de sesión
        driver.find_element(By.NAME, "email").send_keys("user1@example.com")
        driver.find_element(By.NAME, "password").send_keys("1234") 

        # 3. Hacer clic en el botón de inicio de sesión
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "submit"))
        )
        login_button.click()

        # 4. Abrir la página del Notepad
        driver.get("http://localhost:5000/notepad")
        driver.set_window_size(927, 1012)

        # 5. Hacer clic en la nota que deseas editar
        driver.find_element(By.LINK_TEXT, "Please, Please, Please").click()

        # 6. Hacer clic en el cuerpo de la nota y editar el texto
        body_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "body"))
        )
        body_input.click()
        body_input.send_keys("Heartbreak is one thing, my ego is another. I beg you don't embarrass me motherfucker.")

        # 7. Hacer clic en el botón de enviar
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        submit_button.click()

        # 8. Confirmar que la edición fue exitosa (puedes agregar una verificación aquí si lo deseas)
        print("¡Nota editada correctamente!")

    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("Captura de pantalla guardada como 'error_screenshot.png'")

    finally:
        # Cerrar el navegador
        driver.quit()


@pytest.mark.slow
def test_create_and_delete_notepad():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Iniciar el driver de Chrome usando webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 1. Abrir la página de inicio de sesión
        driver.get("http://localhost:5000/login")

        # 2. Completar el formulario de inicio de sesión
        driver.find_element(By.NAME, "email").send_keys("user1@example.com") 
        driver.find_element(By.NAME, "password").send_keys("1234")

        # 3. Hacer clic en el botón de inicio de sesión
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "submit"))
        )
        login_button.click()

        # 4. Abrir la página de creación de notas
        driver.get("http://localhost:5000/notepad/create")
        driver.set_window_size(927, 1012)

        # 5. Completar el formulario de creación de nota
        driver.find_element(By.ID, "title").click()
        driver.find_element(By.ID, "title").send_keys("Holii")
        driver.find_element(By.ID, "body").click()
        driver.find_element(By.ID, "body").send_keys("Que tal?")
        
        # 6. Hacer clic en el botón de enviar
        driver.find_element(By.ID, "submit").click()

        # 7. Regresar a la página de notas
        driver.get("http://localhost:5000/notepad")

        # 8. Hacer clic en el botón de eliminar para la nota recién creada
        driver.find_element(By.CSS_SELECTOR, "li:nth-child(3) button").click()

        # 9. Confirmar la eliminación
        confirm_delete_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirmar')]"))
        )
        confirm_delete_button.click()

        print("¡Nota creada y eliminada correctamente!")

    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("Captura de pantalla guardada como 'error_screenshot.png'")

    finally:
        # Cerrar el navegador
        driver.quit()
