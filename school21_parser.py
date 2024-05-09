import asyncio
import time
from config import URL, TOKEN, LOGIN, PASSWORD, TG_USER_ID, TG_GROUP_ID
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiogram import Bot
from bs4 import BeautifulSoup


def make_authorization(driver: object, URL: str, LOGIN:str, PASSWORD: str) -> bool:
    try:
        driver.get(URL)

        wait = WebDriverWait(driver, 120)
        wait.until(EC.presence_of_element_located((By.NAME, 'username')))

        username_input = driver.find_element(By.NAME, 'username')
        password_input = driver.find_element(By.NAME, 'password')
        username_input.send_keys(LOGIN)
        password_input.send_keys(PASSWORD)

        login_button = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "rcx-button--primary")]'))
        )
        login_button.click()
        print("Авторизация прошла успешно!")
        return True

    except Exception as error:
        print(f"Ошибка: {error}")
        return False


def check_changes(post_id: str, last_post_html:str) -> str | None:
    with open("log.txt", "r", encoding="utf-8") as file_data:
        if file_data.read() != post_id:
            with open("log.txt", "w", encoding="utf-8") as file:
                try:
                    file.write(post_id)
                    header = last_post_html.find("div", class_="rcx-box rcx-box--full rcx-message-header")
                    message = last_post_html.find("div", class_="rcx-message-body").find("div", class_="rcx-css-9nv4z9")

                    data = f"{message.text.strip()}" if header is None else f"{header.text}\n{message.text.strip()}"

                    return data
                except Exception as error:
                    print(f"Ошибка: {error}")
                    return None
        return None


def find_last_post(HTML_CODE: str) -> tuple[str, str] | None:
    try:
        soup = BeautifulSoup(HTML_CODE, 'html.parser')

        last_rcx_message = soup.find_all("div", class_="rcx-message")[-1]
        post_id = last_rcx_message.get("id")

        if post_id is None: #отработка если у последнего поста есть тред
            last_rcx_message = soup.find_all("div", class_="rcx-message")[-2]
            post_id = last_rcx_message.get("id")

        last_post = last_rcx_message.find("div", "rcx-box rcx-box--full rcx-message-container")
        if last_post is None:
            print("Последний пост не найден!")
        return (last_post, post_id)
    except Exception as error:
        print(f"Ошибка: {error}")
        return None


async def main() -> bool:
    bot = Bot(token=TOKEN)
    await bot.send_message(text="Бот запущен!", chat_id=TG_USER_ID)

    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(options=options)

    if not make_authorization(driver, URL, LOGIN, PASSWORD):
        print("Ошибка авторизации!")
        await bot.send_message(text="Ошибка авторизации!", chat_id=TG_USER_ID)
        await bot.session.close()
        return 0

    while (True):
        try:
            time.sleep(10)
            driver.refresh()
            wait = WebDriverWait(driver, 360)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rcx-message")))

            HTML_CODE = driver.page_source

            last_post, post_id = find_last_post(HTML_CODE)

            if not last_post or not post_id:
                print("Ошибка парсера!")
                await bot.session.close()
                return 0

            data = check_changes(post_id, last_post)
            if data:
                await bot.send_message(text=data, chat_id=TG_USER_ID)
                if TG_GROUP_ID:
                    await bot.send_message(text=data, chat_id=TG_GROUP_ID)
        except Exception as error:
            print(f"Ошибка: {error}")
            await bot.send_message(text = "Ошибка парсера!", chat_id=TG_USER_ID)
            driver.close()
            driver.quit()
            await bot.session.close()
            return 0


if __name__ == "__main__":
    asyncio.run(main())


