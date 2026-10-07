import os
import time
import csv

import requests
from dotenv import load_dotenv
from datetime import datetime

current_time = time.time()
load_dotenv()
API_KEY = os.getenv("STEAM_API_KEY")

class SteamTrustCheсker:
    """
    Нижнее подчеркивание _ — это знак для других программистов:
    «Слышь, это мой внутренний инструмент! Не вызывай его снаружи, я сам им пользуюсь внутри завода для подготовки ресурсов. Это служебная функция».
    """

    def __init__(self, api_key: str, scam_words_file: str):
        self.api_key = api_key
        self.scam_words = self._load_scam_words(scam_words_file)
        self.history_file = os.path.join(BASE_DIR, "history.csv")

    def _save_to_csv(self, steam_id: str, name: str, risk: int, verdict: str) -> None:
        """
        Записывает результаты проверки профиля в историю (CSV-файл).
        Не возвращает ничего (-> None), просто производит запись на диск.
        """

        now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_exists = os.path.exists(self.history_file)

        with open(self.history_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(["Timestamp", "SteamID", "RiskScore", "Verdict"])

            writer.writerow([now_date, steam_id, risk, verdict])


    def _check_cache(self, steam_id: str) -> dict | None:
        """
        Ищет steam_id в CSV-файле истории.
        Возвращает словарь с сохранёнными данными ИЛИ None, если записи нет или она устарела.
        """

        if not os.path.exists(self.history_file):
            return None

        with open(self.history_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row["SteamID"] == steam_id:
                    saved_time = datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S")

                    if (datetime.now() - saved_time).total_seconds() < 86400:
                        return {"risk": int(row["RiskScore"]), "verdict": row["Verdict"]}



        return None

    def _load_scam_words(self, file_path: str) -> set:
        words = set()
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                clean_word = line.strip().lower()
                if clean_word:
                    words.add(clean_word)
                else:
                    print("Ошибка")

            return words


    def get_player_bans(self, steam_id: str) -> dict | None:
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={self.api_key}&steamids={steam_id}"
        responce = requests.get(url)

        """
        200 (OK): «Бро, всё четко, вот твои данные». 403 (Forbidden): «Твой API-ключ неверный или забанен». 500 (Server Error): «У Steam что-то упало, попробуй позже».
        """

        if responce.status_code == 200:
            data = responce.json()
            players = data.get("players", [])
            if players:
                return players[0]
        return None



    def extract_steam_id(self) -> str | None:

        """
        В этой функции мы принимает ссылку, распаковываем её до id.
        """

        print("Введите q, чтобы выйти")
        user_input = input("Введите ссылку: ").strip()

        if user_input.endswith("/"):
            user_input = user_input[:-1]

        if user_input in ["q", "Q", "й", "Й"]:
            return None

        parts = user_input.split("/")
        potencial_id = parts[-1]

        if len(potencial_id) == 17 and potencial_id.isdigit():
            return potencial_id
        else:
            zapros = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={self.api_key}&vanityurl={potencial_id}"
            polush = requests.get(zapros)
            beidj = polush.json()

            user_id = beidj.get("response", {}).get("steamid")
            if user_id:
                return user_id
            else:
                print("Ошибка")
        return ""

    def get_steam_friend(self, steam_id: str) -> int:

        friendurl = "https://api.steampowered.com/ISteamUser/GetFriendList/v1/"

        params = {
            "key": self.api_key,
            "steamid": steam_id,
            "relationship": "friends",
            "format": "json"
        }

        peredacha = requests.get(friendurl, params=params)
        data1 = peredacha.json()

        if "friendlist" in data1:
            friends_list = data1["friendlist"].get("friends", [])
            friends_count = len(friends_list)
        else:
            friends_count = -1

        return friends_count

    def get_steam_games(self, steam_id: str) -> int:

        gameurl = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={self.api_key}&steamid={steam_id}&format=json"

        givegames = requests.get(gameurl)
        datagames = givegames.json()

        player_games = datagames.get("response", {}).get("games", [])

        if player_games:
            games_count = len(player_games)
        else:
            games_count = -1

        return games_count


    def get_player_level(self, steam_id: str) -> int | None:

        """
        Тут мы получаем url - переводим в json ( включая get data )
        :param self: - передаем метод из класса
        :param steam_id: - 17-ти значный уникальный код профиля steam
        :return: целое число ( кол-во игр, друзей ) или -1, None, если профиль скрыт там и т.д
        """

        url = f"https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={self.api_key}&steamid={steam_id}"
        responce = requests.get(url)
        data = responce.json()

        player_level = data.get("response", {}).get("player_level")

        if player_level:
            return player_level
        return None

    def get_data_player(self, steam_id: str) -> dict:

        """
        Формируем ссылку для запроса

        А метод .get() делаем безотказный возврат даже при падении тоесть :
        .get("что мы хотим взять", {что вернется если ключ не найден})
        """

        # Формируем правильную ссылку для запроса
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={self.api_key}&steamids={steam_id}"
        response = requests.get(url)
        data = response.json()

        player_data = data.get("response", {}).get("players", [])

        if player_data:
            return player_data[0]
        return None


    def calc_risk(self, player: dict, friends_count: int, games_count: int,  bans_data: dict | None = None) -> int:

        """
        Это наша основная функция которая считает уровень подозрительности
        """


        score = 0
        name = (player.get("personaname") or "").lower()

        if games_count < 3:
            score += 30

        if player.get("communityvisibilitystate") != 3:
            score += 25

        if any(w in name for w in self.scam_words):
            score += 30

        if friends_count >= 0 and friends_count < 5:
            score += 15

        if bans_data and bans_data.get("EconomyBan") != "none":
            score += 40

        if bans_data and bans_data.get("CommunityBanned"):
            score += 25

        if bans_data and bans_data.get("VACBanned"):
            days = bans_data.get("DaysSinceLastBan", 0)
            if days < 365:
                score += 20

        acc_created = (player.get("timecreated") or "")

        if acc_created:
            age_in_seconds = current_time - acc_created
            age_in_years = age_in_seconds / 31536000

            if age_in_years < 2:
                score += 20

        return min(score, 100)

# 1. Находим абсолютный путь к папке, где лежит текущий скрипт (logic.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Склеиваем путь к папке с именем нашего файла
FILE_PATH = os.path.join(BASE_DIR, "scam_words")

# Дебагинг ( мало-ли ошибки )
print("--- ОТЛАДКА ПУТИ ---")
print("Python ищет файл тут:", FILE_PATH)
print("Файл реально существует?", os.path.exists(FILE_PATH))
print("--------------------")

# Простое лобби которое крутит пока есть айди стима и показывает что делается
if __name__ == "__main__":

    checker = SteamTrustCheсker(api_key=API_KEY, scam_words_file=FILE_PATH)

    """
    ОБЯЗАТЕЛЬНО if name потому, что эта функция показывает что запускать.
    А так тут у нас "финиш" где показывает уровень угрозы.
    """
    while True:

        steam_id = checker.extract_steam_id()

        if steam_id is None:
            print("Выход...")
            break

        if steam_id:

            # 1. СНАЧАЛА ПРОВЕРЯЕМ КЭШ (history.csv)
            cached_result = checker._check_cache(steam_id)


            if cached_result:
                print(f"⚡ [КЭШ] Данные из истории (без запросов к Steam API):")
                print(f"Вердикт: {cached_result['verdict']}")
                print(f"Оценка риска: {cached_result['risk']}/100")

            else:
                player_data = checker.get_data_player(steam_id)
                games_count = checker.get_steam_games(steam_id)
                friends_count = checker.get_steam_friend(steam_id)
                bans_data = checker.get_player_bans(steam_id)

                print(f"Найден ID: {steam_id}")

            if player_data:
                risk = checker.calc_risk(player_data, friends_count, games_count, bans_data)
                player_name = player_data.get('personaname', 'Unknown')

                print(f"Игрок: {player_data.get('personaname')}")

                if risk <= 30:
                    verdict = "🟢 БЕЗОПАСНЫЙ"
                elif 30 < risk < 60:
                    verdict = "🟡 ПОДОЗРИТЕЛЬНЫЙ"
                else:
                    verdict = "🔴 ВЫСОКИЙ РИСК СКАМА"

                checker._save_to_csv(steam_id, player_name, risk, verdict)
                print(f"Оценка риска: {risk}/100")
            else:
                print("Игрок не найден")
        else:
            print("Неверный формат. Нужна ссылка вида: https://steamcommunity.com/profiles/11111111111111111")




