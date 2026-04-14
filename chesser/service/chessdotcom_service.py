from client import chessdotcom_api as chessapi
from repository import chessdotcom_repository as chessrepo


def import_and_save_archives_from_chessdotcom(user_name):
    archives = chessapi.get_player_months_archive(user_name)
    chessrepo.persist_user_archives(archives)


def import_and_save_games_from_chessdotcom(user_name, date_game):
    archive = chessrepo.select_archive_by_username_and_month(user_name, date_game)
    games = chessapi.get_games_from_monthly_archive(user_name, date_game)

    for game in games:
        game.user_arch_id = archive[0].id

    chessrepo.persist_games_pgn(games)


def get_archives_of_user(user_name):
    archives = chessrepo.select_archives_by_username(user_name)

    return [{'id': arc[0].id, 
             'user_name': arc[0].user_name, 
             'date_month': arc[0].date_month.strftime('%Y/%m')
            } for arc in archives]


def get_games_by_month_and_user(user_name, date_game):
    games = chessrepo.select_games_by_username_and_month(user_name, date_game)
    games_d = [{'register': game[0].register, 'pgn': game[0].pgn} for game in games]

    return {'user_archive_id': games[0][0].user_arch_id, 'games': games_d}

