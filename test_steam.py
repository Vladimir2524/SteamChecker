import pytest
from logic import SteamTrustCheсker, FILE_PATH, API_KEY

checker = SteamTrustCheсker(api_key=API_KEY, scam_words_file=FILE_PATH)

def test_calc_risk_high():
    # Создаем фейкового «плохого» игрока

    bad_bans = {
        "EconomyBan": "banned",
        "CommunityBanned": True,
        "DaysSinceLastBan": 50,
        "VACBanned": True
    }

    bad_player = {
        "personaname": "scam_free_skins",  # Триггерное имя (+30 баллов)
        "communityvisibilitystate": 1,  # Скрытый профиль (+25 баллов)
    }

    # Вызываем нашу функцию (передаем игрока, 0 друзей, 0 игр)
    result = checker.calc_risk(bad_player, 0, 0, bans_data=bad_bans)
    # Assert — это «утверждение». Мы утверждаем, что риск должен быть равен 100
    assert result == 100

# Проверка якобы на хорошего игрока
def test_calc_risk_low():
    bad_bans = {
        "EconomyBan": "none",
        "VACBanned": False
    }

    good_player = {
        "personaname": "vovabest",
        "communityvisibilitystate": 3,
        "EconomyBan": "none",
    }

    words = ["admin", "trade"]
    result = checker.calc_risk(good_player, 10, 10, bans_data=bad_bans)
    assert result == 0

def test1():
    bad_bans = {
        "EconomyBan": "banned",
        "VACBanned": False
    }

    normal_player = {
        "personaname": "vovchik_free_skins.csstatsFREE",
        "communityvisibilitystate": 3,

    }

    words = ["free"]
    result = checker.calc_risk(normal_player, 10, 5, bans_data=bad_bans)
    assert result == 40

# uv run pytest -vv test_steam.py  - запустить простую проверку ( их там много можно глянуть в инете )

