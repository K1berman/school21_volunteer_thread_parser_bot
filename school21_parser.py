from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from config import URL, TOKEN, LOGIN, PASSWORD
from aiogram import Bot
from bs4 import BeautifulSoup
import asyncio

async def main():
    bot = Bot(token=TOKEN)
    driver = webdriver.Chrome()

    driver.get(URL)
    time.sleep(10)
    username_input = driver.find_element(By.NAME,'username')
    password_input = driver.find_element(By.NAME,'password')

    username_input.send_keys(LOGIN)
    password_input.send_keys(PASSWORD)
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "rcx-button--primary")]'))
    )

    login_button.click()

    time.sleep(10)
    html = driver.page_source



    while (True):
        time.sleep(3)
        driver.refresh()
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        last_rcx_message = soup.find_all("div", class_="rcx-message")[-1]
        id = last_rcx_message.get("id")
        if id is None:
            last_rcx_message = soup.find_all("div", class_="rcx-message")[-2]
            id = last_rcx_message.get("id")
        gett = last_rcx_message.find("div", "rcx-box rcx-box--full rcx-message-container")
        with open("log.txt", "r", encoding="utf-8") as file_data:
            if file_data.read() != id:
                with open("log.txt", "w", encoding="utf-8")as file:
                    file.write(id)
                    data = gett.find("div", class_="rcx-box rcx-box--full rcx-message-header")
                    message = gett.find("div", class_="rcx-message-body")
                    data = f"{data.text}\n{message.text}"
                    await bot.send_message(text = "Find Changes!", chat_id=-4105676665)
                    await bot.send_message(text = data, chat_id="693186551",)


if __name__ == "__main__":
    asyncio.run(main())


