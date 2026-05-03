from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import base64
import pathlib as Path
import datetime
import time

'''
url = "https://web02.uab.es:31501/pds/consultaPublica/look%5Bconpub%5DInicioPubHora?entradaPublica=true&idiomaPais=ca.ES" #Consulta publica horarios uab
f=103 #Facultad de ciencias
g=1281 #Fisica
c=3 #3r Curso
'''

def esperar_carga_pagina(driver, timeout=20):
    wait = WebDriverWait(driver, timeout)

    # Esperar a que el calendario esté presente
    wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "fc-view"))
    )

    # Esperar a botón imprimir
    wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".fc-printButton-button.fc-button.fc-button-primary")
        )
    )
    time.sleep(1)

def imp_horario(url,f,g,c):
    # Personalizacion de archivo final
    nombre_archivo = f"hp_facultad{f}_grado{g}_curso{c}.png"

    # Carpeta donde se descargará el PDF
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DOWNLOAD_DIR = os.path.join(BASE_DIR, "horarios")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Configurar opciones de Chrome
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    #options.add_argument("--window-size=2560,1440")
    # Si el sitio usa certificado no válido (https interno como el tuyo)
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    #options.binary_location = "/usr/bin/chromium-browser"
    #options.binary_location = "/usr/bin/google-chrome"

    # Crear driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    try:
        # Abrir página
        driver.get(url)

        # Espera explícita
        wait = WebDriverWait(driver, 20)

        # Elegir centro
        print("Seleccionando centro...")
        centro = wait.until(
            EC.element_to_be_clickable((By.ID, "centro"))
        )
        Select(centro).select_by_value(f"{f}")
        print("Centro seleccionado correctamente")
        

        # Elegir grado
        print("Seleccionando grado...")
        grado = wait.until(
            EC.element_to_be_clickable((By.ID, "planEstudio"))
        )
        Select(grado).select_by_value(f"{g}")
        print("Grado seleccionado correctamente")
        

        # Elegir curso
        print("Seleccionando curso...")
        curso = wait.until(
            EC.element_to_be_clickable((By.ID, "curso"))
        )
        Select(curso).select_by_value(f"{c}")
        print("Curso seleccionado correctamente")
        

        # Pulsar boton 'Veure Calendari'
        print("Pulsando boton -Veure Calendari-...")
        boton_cal = wait.until(EC.element_to_be_clickable((By.ID, "buscarCalendario")))
        boton_cal.click()
        print('Boton -Veure Calendari- pulsado correctamente')
        esperar_carga_pagina(driver)


        #Miramos que dia es hoy
        hoy = datetime.datetime.now()
        dia_semana = hoy.weekday()  # 0 = lunes, 6 = domingo

        if dia_semana >= 5:
            print("Es fin de semana (pulsamos boton -Seguent-)")

            # Esperamos a aque cargue la pagina
            wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            #Pulsar boton 'Seguent'
            print("Pulsando boton -Seguent-...")
            boton_seg = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="SegÃ¼ent"]')))
            driver.execute_script("arguments[0].click();", boton_seg)

            print('Boton -Seguent- pulsado correctamente')
            esperar_carga_pagina(driver)

        else:
            print("Es entre semana (NO pulsamos boton -Seguent-)")
            esperar_carga_pagina(driver)


        # Esperamos a aque cargue la pagina
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )


        # Descargar PDF
        #Scroll abajo
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            new_height = driver.execute_script("return document.body.scrollHeight")
            esperar_carga_pagina(driver)

            if new_height == last_height:
                break
            last_height = new_height
        

        # Obtener tamaño total de la página
        total_width = driver.execute_script("""
            return Math.max(
                document.body.scrollWidth,
                document.documentElement.scrollWidth,
                document.body.offsetWidth,
                document.documentElement.offsetWidth,
                document.body.clientWidth,
                document.documentElement.clientWidth
            );
        """)

        total_height = driver.execute_script("""
            return Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.offsetHeight,
                document.body.clientHeight,
                document.documentElement.clientHeight
            );
        """)

        # Ajustar tamaño de la ventana al tamaño completo de la página
        driver.set_window_size(total_width, total_height)

        # Definir ruta de guardado
        ruta_completa = os.path.join(DOWNLOAD_DIR, nombre_archivo)

        # Guardar screenshot
        driver.save_screenshot(ruta_completa)

        return print(f"Screenshot guardado correctamente en:\n{ruta_completa}")


    except Exception as e:
        return print(f"Error: {e}")
    finally:
        driver.quit()

web="https://web02.uab.es:31501/pds/consultaPublica/look%5Bconpub%5DInicioPubHora?entradaPublica=true&idiomaPais=ca.ES"

for i in range(1,5):
    imp_horario(web,103,1281,i) #Fisica
    imp_horario(web,103,1286,i) #Fisica + Mates
    imp_horario(web,103,1434,i) #Fisica + Quimica

print('Programa finalizado')
