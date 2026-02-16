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

def imp_horario(url,f,g,c):
    # Personalizacion de archivo final
    nombre_archivo = f"horario_personalizado_facultad{f}_grado{g}_curso{c}.pdf"

    # Carpeta donde se descargará el PDF
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DOWNLOAD_DIR = os.path.join(BASE_DIR, "horarios_pdf")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Configurar opciones de Chrome
    options = Options()
    options.add_argument("--start-maximized")
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

        else:
            print("Es entre semana (NO pulsamos boton -Seguent-)")


        # Esperamos a aque cargue la pagina
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".fc-printButton-button.fc-button.fc-button-primary")
            ))
        time.sleep(1)


        # Descargar PDF
        # Obtener altura total de la página en píxeles
        total_height_px = driver.execute_script("""
            return Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.offsetHeight,
                document.body.clientHeight,
                document.documentElement.clientHeight
            );
        """)
        # Convertir px → pulgadas
        dpi = 96 # Chrome usa 96 DPI por defecto
        total_height_inches = total_height_px / dpi

        # Generar PDF usando CDP
        pdf = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True,
            "landscape": False,
            "paperWidth": 8.27,               # A4 ancho en pulgadas
            "paperHeight": total_height_inches,
            "marginTop": 0,
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0,
            "preferCSSPageSize": False
        })

        # Guardar archivo
        ruta_completa = os.path.join(DOWNLOAD_DIR, nombre_archivo)

        with open(ruta_completa, "wb") as f:
            f.write(base64.b64decode(pdf['data']))
        
        return print(f"PDF guardado correctamente en:\n{ruta_completa}")


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
