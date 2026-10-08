from logic import SteamTrustCheсker, API_KEY, FILE_PATH
from rich.console import Console
from rich.panel import Panel

console = Console()

if __name__ == "__main__":

    console.print(
        Panel.fit(
            "[bold cyan]SteamTrustFactor v2.0[/bold cyan]\n[dim]Automated Risk Assessment Tool[/dim]",
            title="[bold yellow]SYSTEM ENGINE[/bold yellow]",
            border_style="cyan"
        )
    )

    checker = SteamTrustCheсker(api_key=API_KEY, scam_words_file=FILE_PATH)

    while True:
        steam_id = checker.extract_steam_id()

        if steam_id is None:
            console.print("[bold yellow]Выход из системы...[/bold yellow]")
            break

        if steam_id:
            # 1. ПРОВЕРКА КЭША
            cached_result = checker._check_cache(steam_id)

            if cached_result:
                # Рисуем красивую карточку для данных из кэша!
                console.print(
                    Panel(
                        f"[bold]Вердикт:[/bold] {cached_result['verdict']}\n"
                        f"[bold]Оценка риска:[/bold] {cached_result['risk']}/100",
                        title="[bold yellow]⚡ CACHED RESULT (24h TTL)[/bold yellow]",
                        border_style="yellow"
                    )
                )

            else:
                # 2. ЕСЛИ В КЭШЕ НЕТ — ИДЁМ В API
                player_data = checker.get_data_player(steam_id)
                games_count = checker.get_steam_games(steam_id)
                friends_count = checker.get_steam_friend(steam_id)
                bans_data = checker.get_player_bans(steam_id)

                if player_data:
                    risk = checker.calc_risk(player_data, friends_count, games_count, bans_data)
                    player_name = player_data.get('personaname', 'Unknown')

                    # Настраиваем текст и цвет рамки в зависимости от риска!
                    if risk <= 30:
                        verdict = "🟢 БЕЗОПАСНЫЙ ПРОФИЛЬ"
                        card_color = "green"
                    elif 30 < risk < 60:
                        verdict = "🟡 ПОДОЗРИТЕЛЬНЫЙ ПРОФИЛЬ"
                        card_color = "yellow"
                    else:
                        verdict = "🔴 ВЫСОКИЙ РИСК СКАМА"
                        card_color = "red"

                    # ВЫВОДИМ КРАСИВЫЙ HUD ИЗ RICH!
                    console.print(
                        Panel(
                            f"[bold white]Игрок:[/bold white] {player_name}\n"
                            f"[bold white]Вердикт:[/bold white] {verdict}\n"
                            f"[bold white]Оценка риска:[/bold white] [bold {card_color}]{risk}/100[/bold {card_color}]",
                            title=f"[bold {card_color}]ANALYSIS COMPLETE[/bold {card_color}]",
                            border_style=card_color
                        )
                    )

                    # СОХРАНЯЕМ В CSV!
                    checker._save_to_csv(steam_id, player_name, risk, verdict)

                else:
                    console.print("[bold red]❌ Игрок не найден![/bold red]")
        else:
            console.print("[bold red]⚠️ Неверный формат ссылки![/bold red]")
