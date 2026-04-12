from client import chessdotcom_api as chessapi


def import_and_save_from_chessdotcom(user_name):
     
    archives = chessapi.get_player_months_archive(user_name)
    games = chessapi.get_games_from_archive(archives[-1].date_month, user_name)

    return games
    
    

