import scraper

def get_stats(usernames, game_mode=None):
    result = None
    if game_mode is None:
        result = Bedwars(usernames)
    elif game_mode == 'eight_one':
        result = SoloBedwars(usernames)
    elif game_mode == 'eight_two':
        result = DoublesBedwars(usernames)
    elif game_mode == 'four_three':
        result = ThreesBedwars(usernames)
    elif game_mode == 'four_four':
        result = FourFourBedwars(usernames)
    elif game_mode == 'two_four':
        result = TwoFourBedwars(usernames)
    else:
        result = Bedwars(usernames)

    return result.get_table()

class Bedwars:
    rows = ['^Solo.Wins$ #Solo Wins', '^Doubles.Wins$ #Doubles Wins',
            '^3v3v3v3.Wins$ #3v3v3v3 Wins', '^4v4v4v4.Wins$ #4v4v4v4 Wins',
            '^4v4.Wins$ #4v4 Wins', '^Overall.Wins$ #Total Wins',
            '^Overall.Wins$ / (^Overall.Wins$ + ^Overall.Losses$) #Win Rate',
            '^Overall.Kills$ #Kills', '^Overall.K/D$ #K/D',
            '^Overall.Final Kills$ #Final Kills', '^Overall.Final K/D$ #Final K/D',
            '^Overall.Kills$ + ^Overall.Final Kills$ #Total Kills']

    def __init__(self, usernames):
        self.usernames = usernames

    def get_table(self):
        usernames = self.usernames
        pages = scraper.get_player_pages(usernames)
        datasets = list(zip(usernames, [scraper.get_bw_data(page) for page in pages]))

        return scraper.make_bw_table(self.rows, datasets)


class SoloBedwars(Bedwars):
    rows = ['^Solo.Wins$ #Solo Wins',
            '^Solo.Wins$ / (^Solo.Wins$ + ^Solo.Losses$) #Win Rate',
            '^Solo.Kills$ #Kills', '^Solo.K/D$ #K/D',
            '^Solo.Final Kills$ #Final Kills', '^Solo.Final K/D$ #Final K/D',
            '^Solo.Kills$ + ^Solo.Final Kills$ #Total Kills']


class DoublesBedwars(Bedwars):
    rows = ['^Doubles.Wins$ #Doubles Wins',
            '^Doubles.Wins$ / (^Doubles.Wins$ + ^Doubles.Losses$) #Win Rate',
            '^Doubles.Kills$ #Kills', '^Doubles.K/D$ #K/D',
            '^Doubles.Final Kills$ #Final Kills', '^Doubles.Final K/D$ #Final K/D',
            '^Doubles.Kills$ + ^Doubles.Final Kills$ #Total Kills']


class ThreesBedwars(Bedwars):
    rows = ['^3v3v3v3.Wins$ #3v3v3v3 Wins',
            '^3v3v3v3.Wins$ / (^3v3v3v3.Wins$ + ^3v3v3v3.Losses$) #Win Rate',
            '^3v3v3v3.Kills$ #Kills', '^3v3v3v3.K/D$ #K/D',
            '^3v3v3v3.Final Kills$ #Final Kills', '^3v3v3v3.Final K/D$ #Final K/D',
            '^3v3v3v3.Kills$ + ^3v3v3v3.Final Kills$ #Total Kills']


class FourFourBedwars(Bedwars):
    rows = ['^4v4v4v4.Wins$ #4v4v4v4 Wins',
            '^4v4v4v4.Wins$ / (^4v4v4v4.Wins$ + ^4v4v4v4.Losses$) #Win Rate',
            '^4v4v4v4.Kills$ #Kills', '^4v4v4v4.K/D$ #K/D',
            '^4v4v4v4.Final Kills$ #Final Kills', '^4v4v4v4.Final K/D$ #Final K/D',
            '^4v4v4v4.Kills$ + ^4v4v4v4.Final Kills$ #Total Kills']


class TwoFourBedwars(Bedwars):
    rows = ['^4v4.Wins$ #4v4 Wins',
            '^4v4.Wins$ / (^4v4.Wins$ + ^4v4.Losses$) #Win Rate',
            '^4v4.Kills$ #Kills', '^4v4.K/D$ #K/D',
            '^4v4.Final Kills$ #Final Kills', '^4v4.Final K/D$ #Final K/D',
            '^4v4.Kills$ + ^4v4.Final Kills$ #Total Kills']


if __name__ == '__main__':
    # paco = TwoFourBedwars(['parcerx', 'ronansfire'])
    # print(paco.get_table())
    print(get_stats(['parcerx'], game_mode='eight_one'))
