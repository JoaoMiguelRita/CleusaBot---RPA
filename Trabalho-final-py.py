import time
import os
import getpass
from cryptography.fernet import Fernet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configurações do ChromeDriver
chrome_options = Options()
chrome_options.add_argument('--ignore-ssl-errors=true')  # Ignorar verificação SSL (NÃO RECOMENDADO)

# Definir diretório de download
download_dir = os.path.abspath("downloads")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Configurar o Chrome para fazer download de PDFs automaticamente
chrome_prefs = {
    "download.default_directory": download_dir,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option("prefs", chrome_prefs)

d = {}
chave = Fernet.generate_key()
cipher_suite = Fernet(chave)

resp = 'S'
count = 0
while resp.upper() == 'S':
    # Cadastro de usuários
    count += 1
    matricula = count
    nome = input('Nome: ').capitalize()
    usuario = input('Informe o usuário: ')
    senhaCrua = getpass.getpass(prompt='Informe a senha: ', stream=None).encode()
    senhaCrypt = cipher_suite.encrypt(senhaCrua)
    descr = []
    descr.append(nome)
    descr.append(usuario)
    descr.append(senhaCrypt)

    d.update({matricula: descr})

    print("\nFuncionários atuais:")
    for matricula, descr in d.items():
        print(f"ID: {matricula}, Nome: {descr[0]}, Usuario: {descr[1]}, Senha: {descr[2]}")

    resp = input('\nDeseja cadastrar mais usuários (S/N)? ')

print('\nAguarde, preparando ambiente.')
time.sleep(1)
print('\nAguarde, preparando ambiente..')
time.sleep(1.8)
print('\nAguarde, preparando ambiente...')
time.sleep(1)

# Iterar sobre cada usuário cadastrado
for matricula, descr in d.items():
    nome = descr[0]
    usuario = descr[1]
    senhaCrypt = descr[2]
    senhaDecrypt = cipher_suite.decrypt(senhaCrypt)
    senhaDecodada = senhaDecrypt.decode('utf-8')

    print(f'\nAbrindo o portal de {nome}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Abrir o URL diretamente no Chrome
    url = "https://unisatc.com.br/pagina-inicial/?utm_source=pagina-inicial-satc-educacao"
    driver.get(url)

    # Esperar um pouco para a página carregar completamente
    time.sleep(2)

    # XPath do botão que você quer clicar
    caminhoPortal = "/html/body/div[1]/header/div/div[4]/div/div[4]/div/div/div[1]/a"

    try:
        # Localizar o botão pelo XPath
        botaoPortal = driver.find_element(By.XPATH, caminhoPortal)
        
        # Rolar até o botão
        driver.execute_script("arguments[0].scrollIntoView();", botaoPortal)
        time.sleep(2)  # Aguardar um pouco para garantir que a rolagem foi concluída
        
        # Usar JavaScript para clicar no botão
        driver.execute_script("arguments[0].click();", botaoPortal)
        print("Botão clicado com sucesso.")
        
        # Esperar a nova aba/janela abrir
        time.sleep(5)
        
        # Mudar para a nova aba/janela
        driver.switch_to.window(driver.window_handles[1])
    except Exception as e:
        print(f"Erro ao tentar clicar no botão: {e}")
        driver.quit()
        continue

    # Esperar até que o campo de entrada esteja visível
    wait = WebDriverWait(driver, 5)

    # A partir daqui é para fazer o login 
    login = usuario
    senha = senhaDecodada

    try:
        # Usando XPath para encontrar o campo de login
        campo_login_xpath = '//*[@id="user1"]'
        campo_login = wait.until(EC.visibility_of_element_located((By.XPATH, campo_login_xpath)))
        campo_login.clear()
        time.sleep(1)
        campo_login.send_keys(login)

        # Usando XPath para encontrar o campo de senha
        campo_senha_xpath = '//*[@id="content_desktop"]/section/div/div[1]/form/fieldset[1]/div[3]/div[2]/div/div/input'
        campo_senha = driver.find_element(By.XPATH, campo_senha_xpath)
        campo_senha.clear()
        time.sleep(1)
        campo_senha.send_keys(senha)

        # XPath do botão de login
        botaoAcessar_xpath = '//*[@id="content_desktop"]/section/div/div[1]/form/fieldset[1]/div[3]/div[3]/div[1]/div/button'
        botaoAcessar = driver.find_element(By.XPATH, botaoAcessar_xpath)
        driver.execute_script("arguments[0].click();", botaoAcessar)

        print("Realizando Login...")
        
        # Aguardar um tempo para garantir que o login seja concluído
        time.sleep(5)
        
        # Verificar se o login foi efetuado corretamente
        if "login" in driver.current_url.lower():
            print("Falha ao realizar o login.")
            driver.quit()
            continue
        else:
            print("Login realizado com sucesso.")
    except Exception as e:
        print(f"Erro ao tentar realizar o login: {e}")
        driver.quit()
        continue

    # XPath do próximo botão a ser clicado após o login
    caminhoServicosExtras = '/html/body/main/div/div/aside/div[1]/ul/li[2]/a'

    try:
        # Esperar até que o botão esteja visível e, em seguida, clicar nele
        btServicosExtras = wait.until(EC.visibility_of_element_located((By.XPATH, caminhoServicosExtras)))
        driver.execute_script("arguments[0].click();", btServicosExtras)
        print("Serviços Extras clicado com sucesso.")
    except Exception as e:
        print(f"Erro ao tentar clicar nos Serviços Extras: {e}")
        driver.quit()
        continue

    # XPath do botão de atestado de matrícula
    caminhoAtestadoMatricula = '/html/body/main/div/div/section/div[2]/ul[2]/li[3]/a'

    try:
        # Esperar até que o botão esteja visível e, em seguida, clicar nele
        btAtestadoMatricula = wait.until(EC.visibility_of_element_located((By.XPATH, caminhoAtestadoMatricula)))
        driver.execute_script("arguments[0].click();", btAtestadoMatricula)
        print("Atestado de matrícula clicado com sucesso.")
    except Exception as e:
        print(f"Erro ao tentar clicar no botão Atestado de matrícula: {e}")
        driver.quit()
        continue

    # XPath do botão do semestre
    caminhoSemestre = '/html/body/main/div/div/section/ul/li'

    try:
        # Esperar até que o botão esteja visível e, em seguida, clicar nele
        btSemestre = wait.until(EC.visibility_of_element_located((By.XPATH, caminhoSemestre)))
        driver.execute_script("arguments[0].click();", btSemestre)
        print("Semestre clicado com sucesso.")
    except Exception as e:
        print(f"Erro ao tentar clicar no botão Semestre: {e}")
        driver.quit()
        continue

    # Esperar um tempo para garantir que a página pós-clique carregue completamente
    time.sleep(5)

    # Verificar se o PDF foi baixado corretamente
    pdf_downloaded = False
    pdf_file = None
    for _ in range(10):  # Tentar verificar até 10 vezes
        for filename in os.listdir(download_dir):
            if filename.endswith('.pdf'):
                pdf_downloaded = True
                pdf_file = os.path.join(download_dir, filename)
                break
        if pdf_downloaded:
            break
        time.sleep(1)

    if pdf_downloaded:
        print(f"Download do PDF concluído com sucesso. Arquivo salvo em '{pdf_file}'.")
    else:
        print("Falha ao baixar o PDF.")

    # Aguardar um tempo para visualizar a ação
    time.sleep(10)

    # Fechar o navegador após o uso
    driver.quit()

print('Trabalho apresentado com sucesso!')