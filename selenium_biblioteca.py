# ─────────────────────────────────────────────────────────
# Script de Automatización — Sistema de Gestión de Biblioteca
# Autor: Samuel Florez, Stiven Coronado, Esteban Chaparro
# Tema: Automatización con Selenium
# Basado en: Tutorial de Automatización - Felipe Gómez
# ─────────────────────────────────────────────────────────

# ── 1. IMPORTACIÓN DE LIBRERÍAS ───────────────────────────
from webdriver_manager.chrome import ChromeDriverManager
# Descarga automáticamente el driver de Chrome compatible con el navegador
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
# Importa herramienta para controlar el navegador Chrome
import time
# Permite pausar la ejecución con time.sleep()
from selenium.webdriver.common.by import By
# Define la forma de localizar elementos (By.ID, By.NAME, By.XPATH, etc.)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait

# ── 2. VARIABLES GLOBALES ─────────────────────────────────
# Credenciales del bibliotecario para iniciar sesión
USER     = "admin@biblioteca.com"
PASSWORD = "admin123"

# URL de la app Flask corriendo localmente
URL = "http://127.0.0.1:5000"

# ── 3. FUNCIÓN PRINCIPAL ──────────────────────────────────
def main():

    # ── CONFIGURACIÓN DEL NAVEGADOR ───────────────────────
    # Instala y configura el chromedriver automáticamente
    service = Service(ChromeDriverManager().install())
    # Crea opciones para el navegador (tamaño de ventana)
    option = webdriver.ChromeOptions()
    option.add_argument("--window-size=1920,1080")
    # Inicia una instancia del navegador Chrome
    driver = Chrome(service=service, options=option)

    # Abre la página de inicio de sesión de la biblioteca
    driver.get(URL + "/login")
    # Espera 3 segundos para que se vea el proceso
    time.sleep(3)

    # ── AUTENTICACIÓN (LOGIN) ─────────────────────────────
    # Localiza los campos de email y contraseña por su ID
    # y envía las credenciales del bibliotecario
    driver.find_element(By.NAME, "email").send_keys(USER)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    # Hace clic en el botón de login
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    # Espera 3 segundos para que se vea el proceso
    time.sleep(3)

    # ── PASO 1: VER CATÁLOGO DE LIBROS ────────────────────
    # Navega al catálogo para ver los libros disponibles (RF-1)
    driver.get(URL + "/catalogo")
    time.sleep(3)

    # ── PASO 2: BUSCAR UN LIBRO (RF-1) ────────────────────
    # Localiza el campo de búsqueda por su nombre
    driver.find_element(By.NAME, "q").send_keys("1984")
    # Hace clic en el botón de buscar
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    # Limpia la búsqueda volviendo al catálogo completo
    driver.get(URL + "/catalogo")
    time.sleep(2)

    # ── PASO 3: SOLICITAR PRÉSTAMO (RF-2 / RF-4) ─────────
    # Hace clic en "Solicitar Préstamo" del primer libro disponible
    # Localizado por el texto del botón dentro del formulario
    botones_prestamo = driver.find_elements(
        By.CSS_SELECTOR, "button[type='submit']"
    )
    # Hace clic en el primer botón de préstamo disponible
    if botones_prestamo:
        botones_prestamo[0].click()
    time.sleep(3)

    # ── PASO 4: VER HISTORIAL DE PRÉSTAMOS (RF-3) ────────
    # Navega al historial personal del usuario
    driver.get(URL + "/historial")
    time.sleep(3)

    # ── PASO 5: AGREGAR UN LIBRO NUEVO (RF-6) ────────────
    # Solo el bibliotecario puede agregar libros
    driver.get(URL + "/admin/libros")
    time.sleep(2)

    # Localiza el campo de título del libro por su nombre
    driver.find_element(By.NAME, "titulo").send_keys("Automatización con Selenium")
    # Localiza el campo de autor
    driver.find_element(By.NAME, "autor").send_keys("Felipe Gómez")
    # Hace clic en el botón de agregar
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    # ── PASO 6: GESTIONAR PRÉSTAMOS ACTIVOS ──────────────
    # El bibliotecario ve los préstamos activos (RF-5)
    driver.get(URL + "/prestamos")
    time.sleep(3)

    # ── PASO 7: CERRAR SESIÓN ─────────────────────────────
    driver.get(URL + "/logout")
    time.sleep(2)

    # Cierra el navegador
    driver.quit()
    print("\n✅ Automatización completada exitosamente.")

# ── EJECUTAR EL SCRIPT ────────────────────────────────────
if __name__ == "__main__":
    main()