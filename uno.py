from itertools import cycle
import numpy as np
import random
import sys
import pickle

LEARNING_RATE = 0.2
DECAY_GAMMA = 0.9
EXPLORATION_RATE = 0.3

# TODO: Refactor
class Card:
    def __init__(self, color, symbol, used=None):
        self.color = color
        self.symbol = symbol
        self.used = used # only for special cards

class Game:
    def __init__(self, players):
        self.players = players
        self.number_of_players = len(players)
        self.cards = []
        self.player_order = list(range(1, len(players)+1))
        self.discarded = []

    def init_cards(self):
        colors = ['blue', 'green', 'yellow', 'red']
        for i in colors:
            for j in range(10):
                if j == 0:
                    self.cards.append(Card(i, str(j)))
                else:
                    self.cards.append(Card(i, str(j)))
                    self.cards.append(Card(i, str(j)))
            for k in ['+2', 'Skip', 'Reverse']:
                self.cards.append(Card(i, k))
                self.cards.append(Card(i, k))
        for i in range(4):
            self.cards.append(Card('joker', '+4'))
            self.cards.append(Card('joker', 'Change Color'))

    def create_deck(self):
        # Initialize deck
        dealer = self.player_order.pop(0)
        print("{} is the dealer!".format(self.players[dealer-1].name))
        self.player_order.append(dealer)
        random.shuffle(self.cards)
        for _ in range(7):
            for player in self.player_order:
                    card = self.cards.pop(0)
                    self.players[player-1].deck.append(card)
        first_discarded_card = self.cards.pop(0)
        self.discarded.append(first_discarded_card)

    def play_game(self, rounds=10):
        # In the first round, Player 1 is the first to deal and then player 2 starts (depending on which card is the first discarded)
        # In next rounds, Player N deals and Player N+1 starts, it's a circle.
        for uno_round in range(rounds):
            self.init_cards()
            self.create_deck()
            self.game_order = self.player_order.copy()
            self.game_finished = False
            self.already_played = []
            print("=" * 50)
            print("=" * 50)
            print("NEW GAME - Round {}".format(uno_round+1))
            print("=" * 50)
            print("Current standings: ")
            for player in self.players:
                print("{} wins: {}".format(player.name, player.wins))
            print("=" * 50)
            print("=" * 50)
            while self.game_finished is False:
                current_player = self.players[self.check_turn()-1]
                # current_player.show_deck()
                print("{}'s turn!".format(current_player.name))
                if len(self.cards) == 0:
                    self.init_cards()
                    self.discarded = [self.cards.pop(0)]
                state = self.get_state()
                current_player.add_state(str(state))
                current_player.take_action(self.discarded, self.cards, state)
                if len(current_player.deck) == 1: print("{} says UNO!".format(current_player.name)) 
                self.game_finished = self.check_winner(current_player)
            self.cards = []
        for player in self.players:
            player.save_policy()

    def skip_turn(self):
        if len(self.game_order) <= 1:
            if len(self.game_order) == 1:
                self.game_order += self.already_played
            else:
                self.game_order = self.already_played
            self.already_played = []
        skipped_turn = self.game_order.pop(0)
        turn = self.game_order.pop(0)
        self.already_played.append(skipped_turn)
        self.already_played.append(turn)
        return turn

    def check_turn(self):
        top_card = self.discarded[-1]
        if top_card.symbol == 'Reverse' and not top_card.used:
            top_card.used = True
            if len(self.players) == 2:
                return self.skip_turn()
            self.already_played.reverse()
            self.game_order.reverse()
            self.game_order = self.already_played + self.game_order
            self.already_played = []
            last_played = self.game_order.pop(0)
            self.game_order.append(last_played)
        elif top_card.symbol == 'Skip' and not top_card.used:
            top_card.used = True
            return self.skip_turn()
        else:
            if len(self.game_order) == 0:
                self.game_order = self.already_played
                self.already_played = []
        turn = self.game_order.pop(0)
        self.already_played.append(turn)
        return turn

    def get_state(self):
        ''' This function generates a unique hash that identifies the state for the decks and the cards '''
        current_state = {}
        for player in self.players:
            current_state[player.player_id] = []
            for card in player.deck:
                current_state[player.player_id].append((card.color, card.symbol))
        current_state["D"] = (self.discarded[-1].color, self.discarded[-1].symbol)
        return current_state

    def check_winner(self, player):
        if len(player.deck) == 0:
            print("{} won the game!".format(player.name))
            player.feed_reward(1)
            player.reset_states()
            for other_players in self.players:
                if other_players != player:
                    other_players.feed_reward(0)
                    other_players.reset_states()
            player.wins += 1
            return True
        return False

class Player:
    def __init__(self, name, player_id, human=False):
        self.name = name
        self.player_id = player_id
        self.deck = []
        self.human = human
        self.wins = 0
        self.game_states = []
        self.states_value = {}
        self.learning_rate = LEARNING_RATE
        self.decay_gamma = DECAY_GAMMA
        self.exp_rate = EXPLORATION_RATE

    ''' IA Part '''

    def get_state_str(self, state):
        return str(state)

    def add_state(self, state):
        self.game_states.append(state)

    def reset_states(self):
        self.game_states = []

    def feed_reward(self, reward):
        for state in reversed(self.game_states):
            if self.states_value.get(state) is None:
                self.states_value[state] = 0
            self.states_value[state] += self.learning_rate * (self.decay_gamma * reward - self.states_value[state])
            reward = self.states_value[state]

    ''' Actual game part '''

    def show_deck(self):
        print("==============================================")
        print("{}'s cards are: ".format(self.name))
        for card in self.deck:
            print("{} {}".format(card.color, card.symbol))
        print("==============================================")

    def show_matched_deck(self, matched_deck):
        i = 1
        print("==============================================")
        print("{}'s matched cards are: ".format(self.name))
        for card in matched_deck:
            print("{} - {} {}".format(i, card.color, card.symbol))
            i += 1
        print("==============================================")

    def play_card(self, matched_cards, discarded_cards, current_state):
        if np.random.uniform(0, 1) <= self.exp_rate:
            random.shuffle(matched_cards)
            card = matched_cards.pop(0)
        else:
            value_max = -9999999
            for potential_card in matched_cards:
                next_state = current_state.copy()
                next_state[self.player_id].append((potential_card.color, potential_card.symbol))
                next_state_str = self.get_state_str(next_state)
                value = 0 if self.states_value.get(next_state_str) is None else self.states_value.get(next_state_str)
                if value >= value_max:
                    value_max = value
                    card = potential_card
        self.deck.pop(self.deck.index(card))
        if card.symbol in ['Change Color', '+4']:
            card.color = self.choose_color()
            print("{} chose {}".format(self.name, card.color))
        discarded_cards.append(card)
        return card

    def human_choose_color(self):
        colors = ['blue', 'green', 'yellow', 'red']
        print("Choose from: \n")
        for color in colors:
            print("{} - {}".format(colors.index(color)+1, color))
        chosen_color = colors[int(input("Choice : "))-1]
        return chosen_color

    def human_play_card(self, matched_cards, discarded_cards):
        self.show_deck()
        self.show_matched_deck(matched_cards)
        card_idx = int(input("Which card do you want to play?"))
        card = matched_cards.pop(card_idx-1)
        self.deck.pop(self.deck.index(card))
        if card.symbol in ['Change Color', '+4']:
            card.color = self.human_choose_color()
            print("{} chose {}".format(self.name, card.color))
        discarded_cards.append(card)
        return card

    def choose_color(self):
        colors_dict = {
            'red': 0,
            'yellow': 0,
            'blue': 0,
            'green': 0
        }
        for card in self.deck:
            if card.color != 'joker':
                colors_dict[card.color] += 1
        sorted_colors_dict = {k: v for k, v in sorted(colors_dict.items(), key=lambda item: item[1], reverse=True)}
        color = next(iter(sorted_colors_dict))
        return color

    def compare_cards(self, deck_card, discarded_card):
        if deck_card.color == 'joker':
            return True
        if deck_card.color == discarded_card.color or deck_card.symbol == discarded_card.symbol:
            return True
        return False

    def buy_cards(self, cards, amount, discarded):
        for _ in range(amount):
            if len(cards) == 0:
                for card in discarded:
                    if card.color in ['red', 'yellow', 'blue', 'green'] and card.symbol in ['+4', 'Change Color']:
                        card.color = 'joker'
                    if card.symbol in ['Skip', 'Reverse'] and card.used:
                        card.used = None
                random.shuffle(discarded)
                cards = discarded
                discarded = []
            new_card = cards.pop(0)
            self.deck.append(new_card)

    def take_action(self, discarded_cards, cards, current_state):
        buy_extra = True
        matched_cards = []
        print("Discarded card at top is {} {}".format(discarded_cards[-1].color, discarded_cards[-1].symbol))
        if len(discarded_cards) == 1:
            # First discard!
            if discarded_cards[0].symbol == 'Change Color':
                discarded_cards[0].color = self.choose_color()
                print("{} chose {}".format(self.name, discarded_cards[-1].color))
            elif discarded_cards[0].symbol == '+4':
                cards.append(discarded_cards[0])
                discarded_cards.pop(0)
                new_first_discard = cards.pop(0)
                discarded_cards.append(new_first_discard)
        top_discarded_card = discarded_cards[-1]
        if top_discarded_card.symbol in ['+2', '+4']:
            amount_to_buy = int(top_discarded_card.symbol[1:])
            print("{} will need to buy {} cards!".format(self.name, amount_to_buy))
            self.buy_cards(cards, amount_to_buy, discarded_cards)
            buy_extra = False
        for card in self.deck:
            if self.compare_cards(card, top_discarded_card):
                matched_cards.append(card)
        # print("Length of matched cards is {}".format(len(matched_cards)))
        if len(matched_cards) > 0:
            if self.human:
                card_chosen = self.human_play_card(matched_cards, discarded_cards)
            else:
                card_chosen = self.play_card(matched_cards, discarded_cards, current_state)
            print("The card played by {} is {} {}".format(self.name, card_chosen.color, card_chosen.symbol))
        else:
            if buy_extra:
                print("{} needs to buy a card!".format(self.name))
                new_card = cards.pop(0)
                if self.compare_cards(new_card, top_discarded_card):
                    print("Card bought {} {} matches with discarded card {} {}".format(new_card.color, new_card.symbol, top_discarded_card.color, top_discarded_card.symbol))
                    if new_card.symbol == 'Change Color':
                        new_card.color = self.choose_color()
                    print("The card played by {} is {} {}".format(self.name, new_card.color, new_card.symbol))
                    discarded_cards.append(new_card)
                else:
                    self.deck.append(new_card)

    def save_policy(self):
        fw = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    def load_policy(self, file):
        fr = open(file, 'rb')
        self.states_value = pickle.load(fr)
        fr.close()

if __name__ == "__main__":
    players = []
    players.append(Player("Victor", 1))
    players.append(Player("Angélica", 2))
    # players.append(Player("Churros", 3))
    # players.append(Player("Lucas", 4))
    # players.append(Player("João", 5))
    game = Game(players)
    game.play_game(rounds=10000)

    new_players = []
    new_players.append(Player("Victor", 1, human=True))
    trained_player = Player("Angélica", 2)
    trained_player.load_policy("policy_Angélica")
    new_players.append(trained_player)
    game_with_human = Game(new_players)
    game_with_human.play_game(rounds=1)

    # TODO: For a perfect game, introduce missing rules for first discards
    # TODO: Progressive Uno