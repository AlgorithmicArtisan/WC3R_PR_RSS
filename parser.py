import os
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from selenium import webdriver

def parser(url:str):
    #Инициализация экземпляра RSS ленты
    fg = FeedGenerator()
    #Заполнение общей информации о ленте RSS
    fg.id("HERE_WILL_BE_GIT_HUB_LINK")
    fg.title('WarCraft 3 Reforged')
    fg.author( {'name':'Артём Евсеев ','email':'magnaflamma@icloud.com'} )
    fg.link( href='https://us.forums.blizzard.com/', rel='alternate' )
    fg.logo('https://avatars.githubusercontent.com/u/10351618?v=4&size=64')
    fg.subtitle('Моя кастомная генерация RSS ленты на основе парсинга интересных страниц')
    fg.link( href='https://nan', rel='self' )
    fg.language('en')
    #Среда запуска
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'

    #Инициализация опций запуска эмуляции браузерной активности в Selenium
    options = Options()
    #options.binary_location = "/usr/bin/chromium-browser"

    # Установка пути к исполнительному ChromDriver v146.0.7680.165, изменить при размещении на Github Actions
    is_github = os.getenv('GITHUB_ACTIONS') == 'true'

    if is_github:
        service = Service("/usr/bin/chromedriver")
    else:
        service = Service("C:\\Users\\Administrator\\PyCharmMiscProject\\chromedriver-win64\\chromedriver.exe")

    '''
    Параметры запуска браузерной сессии:
    headless - Без рендера окна
    no-sandbox - Отключает изоляцию процессов Chrome (Нужно для Github Actions)
    disable-dev-shm-usage - Перенаправляет временные файлы из памяти на диск (Нужно для Github Actions)
    '''
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    #Применение переменой пути к экзешнику и опций выше
    driver = webdriver.Chrome(service=service, options=options)

    #Защита от краша
    html = ""

    #Простая конструкция: Попытка спарсить, нет - дать ошибку, финал - закрыть браузерную сессию
    try:
        driver.get(url)
        time.sleep(2)
        html = driver.page_source
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

    #Инициализация инстанса BeautifulSoup, передача результатов парсинга, тип парсингового алгоритма
    soup = BeautifulSoup(html, 'lxml')

    #Перебор элементов страницы, заполнение полей экземпляра RSS генератора
    items = soup.find_all(class_='title raw-link raw-topic-link')
    base_url = "https://us.forums.blizzard.com"
    #Переворачивает список
    items.reverse()
    #Цикл перебора элементов страницы
    for item in items:
        link = item.get('href')
        entry = fg.add_entry()
        entry.id(item.get('data-topic-id'))
        entry.title(item.text)
        entry.link(href=f"{base_url}{link}", rel='alternate')

    #Генерация RSS
    fg.atom_file("WarCraft_III_REFORGED.xml")

     #Сохраняем в HTML файл отладка
    #with open('output.html', 'w', encoding='utf-8') as file:
        #file.write(str(soup))


if __name__ == "__main__":
    parser("https://us.forums.blizzard.com/en/warcraft3/u/Kaivax/activity/topics")