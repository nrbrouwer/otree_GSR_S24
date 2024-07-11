from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'cooperation_game'
    PLAYERS_PER_GROUP = 5 #five players in a group together
    PLAYERS_PER_GROUP_minus_one = PLAYERS_PER_GROUP - 1 #this is just to make the instructions a little simpler
    NUM_ROUNDS = 1
    payoff_agree_your_color = 5 #payoffs for different results
    payoff_agree_other_color = 3
    payoff_disagree = 0



class Subsession(BaseSubsession):
    pass

class Group(BaseGroup): #these variables are just for reporting in the results page
    count_blue = models.IntegerField(initial=0) #saves the number of blue votes
    count_red = models.IntegerField(initial=0) #saves the number of red votes
    count_sum = models.IntegerField(initial=0) #counts the sum of votes to check for unanimity


class Player(BasePlayer):
    prefer_blue = models.BooleanField() #saves the player's preference
    color_choice = models.BooleanField( #saves their choice in the game
                choices=[
            [True, 'Blue'], #easier to just treat the colors as booleans rather than strings
            [False, 'Red'],
        ]
    )

def creating_session(subsession):
    pref_list = [1,1,0,0,0] #Instead of random assignment, we have the first two players prefer blue, the others prefer red
    for i, player in enumerate(subsession.get_players()): #for each player in the subsession, we iterate
        player.prefer_blue = bool(pref_list[i]) #using their index in the group, grabs that spot in pref_list and transforms to T/F
# PAGES
class Instructions(Page):
    pass

class Decision(Page):
    form_model = 'player'
    form_fields = ['color_choice']

class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        player_list = group.get_players() #get all the players
        choices = [player.color_choice for player in player_list] #get a vector containing the choices of all the players
        group.count_blue = choices.count(1) #count each vote choice to show in the results page later
        group.count_red = choices.count(0)
        group.count_sum = sum(choices)
        if all(choice == 1 for choice in choices): #if everyone chooses Blue
            for player in player_list:
                if player.prefer_blue == True:
                    player.payoff = C.payoff_agree_your_color #players who were assigned blue get max points
                else:
                    player.payoff = C.payoff_agree_other_color #players assigned red get reduced points
        elif all(choice == 0 for choice in choices): #when everyone chooses Red, we flip the payout logic
            for player in player_list:
                if player.prefer_blue == True:
                    player.payoff = C.payoff_agree_other_color
                else:
                    player.payoff = C.payoff_agree_your_color
        else:                                #any other result (not unanimous voting) results in no points given
            for player in player_list:
                player.payoff = C.payoff_disagree


class Results(Page):
    pass




page_sequence = [Instructions ,Decision, ResultsWaitPage, Results]
