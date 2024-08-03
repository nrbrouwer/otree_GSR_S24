from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'coordination_game_tutorial'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    payoff_correct = 5  # payoffs for different results
    payoff_wrong = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    prefer_blue = models.BooleanField()
    blue_signal = models.BooleanField()
    result_val = models.IntegerField()
    color_choice = models.BooleanField(
        choices=[
            [True, 'Blue'],
            [False, 'Red'],
        ]
    )

def creating_session(subsession): #this sets their assigned color for the whole game, probably an easier way to do this, but this was what I got to work
    if subsession.round_number == 1: #sets the Prefer_blue value in r1, keeps it the same after
        for player in subsession.get_players():
            player.prefer_blue = random.choices([True, False], [1, 0])[0] #I have it set here to always be blue, but you can change the ratio as desired
    else:
        for player in subsession.get_players():
            player.prefer_blue = player.in_round(1).prefer_blue

# PAGES
class Instructions(Page):
    def is_displayed(player: Player): #only shows instructions on r1
        return player.round_number == 1

    def vars_for_template(player: Player):
        return {
            'correct_points': C.payoff_correct,
            'incorrect_points': C.payoff_wrong,
        }

class Decision(Page):
    form_model = 'player'
    form_fields = ['color_choice']

    def vars_for_template(player: Player): #this makes sure the signal matches assigned color 2/3rds of the time
        if player.prefer_blue == True:
            player.blue_signal = random.choices([True, False], [2/3, 1/3])[0]
        else:
            player.blue_signal = random.choices([True, False], [1/3, 2/3])[0]


        return {
            'round_number': player.round_number,
            'correct_points': C.payoff_correct,
            'incorrect_points': C.payoff_wrong,
        }

    def before_next_page(player: Player, timeout_happened): #caluclate payoff for round before going to next page
        if player.color_choice == player.prefer_blue:
            player.payoff = C.payoff_correct
        else:
            player.payoff = C.payoff_wrong


class Results(Page):
    def is_displayed(player: Player): #only shows up on final round
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):
        all_rounds = player.in_all_rounds() #pulls the data from all the rounds
        total_points = sum(round_data.payoff for round_data in all_rounds) #caluclates total points earned
        possible_points = C.NUM_ROUNDS * C.payoff_correct #calculates total possible points

        table_data = [] #this creates a list where each row has the relevant data from that round
        for round_data in all_rounds:
            table_data.append({
                'round_number': round_data.round_number,
                'prefer_blue': round_data.prefer_blue,
                'blue_signal': round_data.blue_signal,
                'color_choice': round_data.color_choice,
                'payoff': round_data.payoff,
            })

        return {
            'table_data': table_data,
            'total_points': total_points,
            'possible_points': possible_points,
        }

page_sequence = [Instructions, Decision, Results]
