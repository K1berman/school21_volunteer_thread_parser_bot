import asyncio
import re
import time
import sys
from config import URL, TOKEN, LOGIN, PASSWORD, TG_USER_ID, TG_GROUP_ID
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiogram import Bot
from bs4 import BeautifulSoup


def make_post_format(POST_HTML: str) -> str | None:
    try:
        message_data = []
        header = POST_HTML.find("div", class_="rcx-box rcx-box--full rcx-message-header")
        header_name = header.find("span", class_="rcx-box rcx-box--full rcx-message-header__name-container")
        header_time = header.find('span', class_='rcx-box rcx-box--full rcx-message-header__time')['title']
        message = POST_HTML.find("div", class_="rcx-message-body")
        for message_string in message.find_all("div"):
            if message_string is None:
                return None
            link = message_string.find("a")
            message_string = re.sub(r":(.+?):", "&#10071;", message_string.text)
            if link:
                link_text = link.text
                link_url = link.get('href')
                formatted_link = f'<a href="{link_url}">{link_text}</a>'
                full_text = re.sub(link_text, formatted_link, message_string)
                message_data.append(full_text)
            else:
                message_data.append(message_string)
        message = "\n".join(message_data)
        data = f"{message}" if header is None else f"<b>{header_name.text} | {header_time}</b>\n{message}"
        return data
    except Exception as error:
        print(f"Ошибка: {error}")
        return None


def make_authorization(driver: object, URL: str, LOGIN:str, PASSWORD: str) -> bool:
    try:
        driver.get(URL)

        wait = WebDriverWait(driver, 120)
        wait.until(EC.presence_of_element_located((By.NAME, 'usernameOrEmail')))

        username_input = driver.find_element(By.NAME, 'usernameOrEmail')
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


def check_changes(post_id: str, last_post_html: str) -> str | None:
    with open("log.txt", "r", encoding="utf-8") as file_data:
        if file_data.read() != post_id:
            with open("log.txt", "w", encoding="utf-8") as file:
                try:
                    file.write(post_id)
                    data = make_post_format(last_post_html)
                    if not data:
                        print("Ошибка форматирования поста!")
                        return None
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

        if post_id is None: #отработка если у последнего поста есть тред
            last_rcx_message = soup.find_all("div", class_="rcx-message")[-3]
            post_id = last_rcx_message.get("id")

        last_post = last_rcx_message.find("div", "rcx-box rcx-box--full rcx-message-container")
        if last_post is None:
            print("Последний пост не найден!")
        return (last_post, post_id)
    except Exception as error:
        print(f"Ошибка: {error}")
        return None


async def main() -> bool:

    sys.stdout.reconfigure(encoding='utf-8')

    bot = Bot(token=TOKEN)
    await bot.send_message(text="Бот запущен!", chat_id=TG_USER_ID)

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    if not make_authorization(driver, URL, LOGIN, PASSWORD):
        print("Ошибка авторизации!")
        await bot.send_message(text="Ошибка авторизации!", chat_id=TG_USER_ID)
        await bot.session.close()
        return 0

    while (True):
        try:
            time.sleep(10)
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
                await bot.send_message(text=data, chat_id=TG_USER_ID, parse_mode='HTML')
                if TG_GROUP_ID:
                    await bot.send_message(text=data, chat_id=TG_GROUP_ID, parse_mode='HTML')
        except Exception as error:
            print(f"Ошибка: {error}")
            await bot.send_message(text = "Ошибка парсера!", chat_id=TG_USER_ID)
            driver.close()
            driver.quit()
            await bot.session.close()
            return 0


if __name__ == "__main__":
    asyncio.run(main())


