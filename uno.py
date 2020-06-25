import argparse
import random
import sys
import pickle
import numpy as np

LEARNING_RATE = 0.2
DECAY_GAMMA = 0.9
EXPLORATION_RATE = 0.1
ROUNDS = int(sys.argv[1])

class Card:
    '''
    This class models a UNO game card.

    Args:
        color (str):
        Card color, ranges from red, blue, yellow or green.
        Special action cards can be used on any color, so they are joker cards.

        symbol (str):
        Card symbol, it can be a number from 0 to 9 or an action card symbol,
        such as +2, Skip, Reverse or jokers +4 and Change Color.

        Used (boolean, optional):
        Indicates whether the card effect has already passed. Used only for action cards.
    '''
    def __init__(self, color, symbol, used=None):
        self.color = color
        self.symbol = symbol
        self.used = used

class Game:
    def __init__(self, players):
        self.players = players
        self.number_of_players = len(self.players)
        self.cards = []
        self.player_order = list(range(1, self.number_of_players+1))
        self.progressive_amount = 0

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
        for _ in range(4):
            self.cards.append(Card('joker', '+4'))
            self.cards.append(Card('joker', 'Change Color'))

    def create_deck(self):
        # Initialize deck
        dealer = self.player_order.pop(0)
        if INTERACTIVE: print("{} is the dealer!".format(self.players[dealer-1].name))
        self.player_order.append(dealer)
        random.shuffle(self.cards)
        for _ in range(7):
            for player in self.player_order:
                card = self.cards.pop(0)
                self.players[player-1].deck.append(card)
        while self.cards[-1].symbol == '+4':
            random.shuffle(self.cards)

    def play_game(self, rounds=10):
        # In the first round, Player 1 is the first to deal and then player 2 starts
        # (depending on which card is the first discarded)
        # In next rounds, Player N deals and Player N+1 starts, it's a circle.
        for uno_round in range(rounds):
            game_finished = False
            self.init_cards()
            self.create_deck()
            self.game_order = self.player_order.copy()
            self.already_played = []
            self.progressive_amount = 0
            if INTERACTIVE:
                print("=" * 50)
                print("=" * 50)
                print("NEW GAME - Round {}".format(uno_round+1))
                print("=" * 50)
                print("Current standings: ")
                for player in self.players:
                    print("{} wins: {}".format(player.name, player.wins))
                print("=" * 50)
                print("=" * 50)
            while game_finished is False:
                current_player = self.players[self.check_turn()-1]
                if INTERACTIVE: 
                    print("{}'s turn!".format(current_player.name))
                state = self.get_state()
                current_player.add_state(str(state))
                if self.cards[-1].symbol in ['+2', '+4'] and not self.cards[-1].used:
                    partial_amount = self.cards[-1].symbol[1:]
                    self.progressive_amount += int(partial_amount)
                current_player.take_action(self, state)
                if len(current_player.deck) == 1:
                    if INTERACTIVE: 
                        print("{} says UNO!".format(current_player.name))
                game_finished = self.check_winner(current_player)
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
        top_card = self.cards[-1]
        if top_card.symbol == 'Reverse' and not top_card.used:
            top_card.used = True
            if self.number_of_players == 2:
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
        ''' This function generates a unique hash that 
        identifies the state for the decks and the cards '''
        current_state = {}
        for player in self.players:
            current_state[player.player_id] = []
            for card in player.deck:
                current_state[player.player_id].append((card.color, card.symbol))
        current_state["D"] = (self.cards[-1].color, self.cards[-1].symbol)
        return current_state

    def check_winner(self, player):
        if len(player.deck) == 0:
            if INTERACTIVE: 
                print("{} won the game!".format(player.name))
            player.feed_reward(1)
            player.reset_states()
            player.deck = []
            for other_players in self.players:
                if other_players != player:
                    other_players.feed_reward(0)
                    other_players.reset_states()
                    other_players.deck = []
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

    # IA Part

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
            self.states_value[state] += self.learning_rate * \
            (self.decay_gamma * reward - self.states_value[state])
            reward = self.states_value[state]

    # Actual game part

    def show_deck(self):
        print("==============================================")
        print("{} has {} cards: ".format(self.name, len(self.deck)))
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

    def play_card(self, matched_cards, current_state):
        if np.random.uniform(0, 1) <= self.exp_rate:
            random.shuffle(matched_cards)
            card = matched_cards.pop(0)
        else:
            value_max = -9999999
            for potential_card in matched_cards:
                next_state = current_state.copy()
                next_state[self.player_id].append((potential_card.color, potential_card.symbol))
                next_state_str = self.get_state_str(next_state)
                if self.states_value.get(next_state_str) is None:
                    value = 0
                else:
                    value = self.states_value.get(next_state_str)
                if value >= value_max:
                    value_max = value
                    card = potential_card
        self.deck.pop(self.deck.index(card))
        if card.symbol in ['Change Color', '+4']:
            card.color = self.choose_color()
            if INTERACTIVE: print("{} chose {}".format(self.name, card.color))
            if card.symbol == 'Change Color':
                card.used = True
        return card

    def human_choose_color(self):
        colors = ['blue', 'green', 'yellow', 'red']
        print("Choose from: \n")
        for color in colors:
            print("{} - {}".format(colors.index(color)+1, color))
        chosen_color = colors[int(input("Choice : "))-1]
        return chosen_color

    def human_play_card(self, matched_cards):
        self.show_deck()
        self.show_matched_deck(matched_cards)
        card_idx = int(input("Which card do you want to play? "))
        card = matched_cards.pop(card_idx-1)
        self.deck.pop(self.deck.index(card))
        if card.symbol in ['Change Color', '+4']:
            card.color = self.human_choose_color()
            print("{} chose {}".format(self.name, card.color))
            if card.symbol == 'Change Color':
                card.used = True
        return card

    def choose_color(self):
        colors_dict = {'red': 0, 'yellow': 0, 'blue': 0, 'green': 0}
        for card in self.deck:
            if card.color != 'joker':
                colors_dict[card.color] += 1
        sorted_colors_dict = {k: v for k, v in \
            sorted(colors_dict.items(), key=lambda item: item[1], reverse=True)}
        color = next(iter(sorted_colors_dict))
        return color

    def compare_cards(self, deck_card, discarded_card):
        if deck_card.color == 'joker' or deck_card.color == discarded_card.color \
        or deck_card.symbol == discarded_card.symbol:
            return True
        return False

    def buy_cards(self, cards, amount):
        for _ in range(amount):
            new_card = cards.pop(0)
            self.deck.append(new_card)

    def take_action(self, game, current_state):
        buy_extra = True
        matched_cards = []
        discarded = game.cards[-1]
        has_card = False
        if INTERACTIVE: 
            print("Discarded card at top is {} {}".format(discarded.color, discarded.symbol))
        if discarded.symbol == 'Change Color' and not discarded.used:
            discarded.color = self.choose_color()
            if INTERACTIVE: 
                print("{} chose {}".format(self.name, discarded.color))
        elif discarded.symbol in ['+2', '+4'] and not discarded.used:
            for card in self.deck:
                if card.symbol == discarded.symbol:
                    has_card = True
                    break
            if not has_card:
                if INTERACTIVE: 
                    print("{} will need to buy {} cards!".format(self.name, game.progressive_amount))
                self.buy_cards(game.cards, game.progressive_amount)
                if INTERACTIVE and self.human:
                    self.show_deck()
                buy_extra = False
                discarded.used = True
                game.progressive_amount = 0
        for card in self.deck:
            if self.compare_cards(card, discarded):
                matched_cards.append(card)
        if len(matched_cards) > 0:
            if self.human:
                card_chosen = self.human_play_card(matched_cards)
            else:
                card_chosen = self.play_card(matched_cards, current_state)
            if INTERACTIVE:
                print("The card played by {} is {} {}" \
                .format(self.name, card_chosen.color, card_chosen.symbol))
            if has_card and card_chosen.symbol not in ['+2', '+4']:
                self.buy_cards(game.cards, game.progressive_amount)
                if INTERACTIVE:
                    print("Since {} did not make a progressive play, he needs to buy {} cards!" \
                        .format(self.name, game.progressive_amount))
                    self.show_deck()
                discarded.used = True
                game.progressive_amount = 0
            game.cards.append(card_chosen)
        else:
            if buy_extra:
                if INTERACTIVE: 
                    print("{} needs to buy a card!".format(self.name))
                new_card = game.cards.pop(0)
                if self.compare_cards(new_card, discarded):
                    if INTERACTIVE: 
                        print("Card bought {} {} matches with discarded card {} {}" \
                        .format(new_card.color, new_card.symbol, discarded.color, discarded.symbol))
                    if new_card.symbol in ['Change Color', '+4']:
                        new_card.color = self.choose_color()
                        if new_card.symbol == 'Change Color':
                            new_card.used = True
                    if INTERACTIVE: 
                        print("The card played by {} is {} {}" \
                        .format(self.name, new_card.color, new_card.symbol))
                    game.cards.append(new_card)
                else:
                    self.deck.append(new_card)

    def save_policy(self):
        file_to_write = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, file_to_write)
        file_to_write.close()

    def load_policy(self, file):
        file_to_read = open(file, 'rb')
        self.states_value = pickle.load(file_to_read)
        file_to_read.close()

if __name__ == "__main__":
    INTERACTIVE = bool(int(sys.argv[2]))
    GAME_PLAYERS = []
    GAME_PLAYERS.append(Player("Victor", 1))
    GAME_PLAYERS.append(Player("Angélica", 2))
    # GAME_PLAYERS.append(Player("Churros", 3))
    # GAME_PLAYERS.append(Player("Lucas", 4))
    # GAME_PLAYERS.append(Player("João", 5))
    GAME = Game(GAME_PLAYERS)
    GAME.play_game(rounds=ROUNDS)
    print("Training the players in {} rounds...".format(ROUNDS))

    INTERACTIVE = True
    NEW_PLAYERS = []
    NEW_PLAYERS.append(Player("Victor", 1, human=True))
    TRAINED_PLAYER = Player("Angélica", 2)
    TRAINED_PLAYER.load_policy("policy_Angélica")
    NEW_PLAYERS.append(TRAINED_PLAYER)
    GAME_WITH_HUMAN = Game(NEW_PLAYERS)
    GAME_WITH_HUMAN.play_game(rounds=2)

    # TODO: Progressive Uno
