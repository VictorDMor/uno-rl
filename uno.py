import numpy as np
import random
import sys

# TODO: Refactor
class Card:
    def __init__(self, color, symbol):
        self.color = color
        self.symbol = symbol

class Game:
    def __init__(self, players):
        self.players = players
        self.number_of_players = len(players)
        self.cards = []
        self.discarded = []
        self.player_order = list(range(1, len(players)+1))

    def init_cards(self):
        colors = ['blue', 'green', 'yellow', 'red']
        for i in colors:
            for j in range(10):
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
                    players[player-1].deck.append(card)
        first_discarded_card = self.cards.pop(0)
        self.discarded.append(first_discarded_card)

    def play_game(self, rounds=10):
        # In the first round, Player 1 is the first to deal and then player 2 starts (depending on which card is the first discarded)
        # In next rounds, Player N deals and Player N+1 starts, it's a circle.
        for _ in range(rounds):
            self.init_cards()
            self.create_deck()
            self.game_finished = False
            self.game_order = self.player_order
            while self.game_finished is False:
                for player in self.game_order:
                    current_player = players[player-1]
                    current_player.show_deck()
                    print("Game order at the moment is: {}".format(self.game_order))
                    print("{}'s turn!".format(current_player.name))
                    if len(self.cards) == 0:
                        random.shuffle(self.discarded)
                        self.cards = self.discarded
                        self.discarded = [self.cards.pop(0)]
                    current_player.take_action(self.discarded, self.cards)
                    if self.discarded[-1].symbol == 'Reverse':
                        self.game_order.reverse()
                    print("{}'s deck length is {}".format(current_player.name, len(current_player.deck)))
                    self.game_finished = self.check_winner(current_player)
            self.cards = []

    def check_winner(self, player):
        if len(player.deck) == 0:
            return True
        return False

class Player:
    def __init__(self, name, player_id):
        self.name = name
        self.player_id = player_id
        self.deck = []

    def show_deck(self):
        print("==============================================")
        print("{}'s cards are: ".format(self.name))
        for card in self.deck:
            print("{} {}".format(card.color, card.symbol))
        print("==============================================")

    def play_card(self, matched_cards, discarded_cards):
        random.shuffle(matched_cards)
        card = matched_cards.pop(0)
        self.deck.pop(self.deck.index(card))
        if card.symbol in ['Change Color', '+4']:
            print("{} chose a {} card so he/she chooses the next color to play!".format(self.name, card.symbol))
            card.color = self.choose_color()
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
        print("The main color in {}'s deck is {} ".format(self.name, color))
        return color

    def compare_cards(self, deck_card, discarded_card):
        if deck_card.color == 'joker':
            return True
        if deck_card.color == discarded_card.color or deck_card.symbol == discarded_card.symbol:
            return True
        return False

    def buy_cards(self, cards, amount):
        # TODO: Bug that is not reshuffling cards after card pile is empty
        for _ in range(amount):
            new_card = cards.pop(0)
            self.deck.append(new_card)

    def take_action(self, discarded_cards, cards):
        # TODO: Joker's and special cards actions
        buy_extra = True
        matched_cards = []
        top_discarded_card = discarded_cards[-1]
        print("Discarded card at top is {} {}".format(top_discarded_card.color, top_discarded_card.symbol))
        if top_discarded_card.symbol in ['+2', '+4']:
            amount_to_buy = int(top_discarded_card.symbol[1:])
            print("{} will need to buy {} cards!".format(self.name, amount_to_buy))
            self.buy_cards(cards, amount_to_buy)
            buy_extra = False
        for card in self.deck:
            if self.compare_cards(card, top_discarded_card):
                print("{} {} matches discarded card at top!".format(card.color, card.symbol))
                matched_cards.append(card)
        # print("Length of matched cards is {}".format(len(matched_cards)))
        if len(matched_cards) > 0:
            card_chosen = self.play_card(matched_cards, discarded_cards)
            print("The card played by {} is {} {}".format(self.name, card_chosen.color, card_chosen.symbol))
        else:
            if buy_extra:
                print("{} needs to buy a card!".format(self.name))
                new_card = cards.pop(0)
                print("Card bought is {} {}".format(new_card.color, new_card.symbol))
                if self.compare_cards(new_card, top_discarded_card):
                    print("Card bought {} {} matches with discarded card {} {}".format(new_card.color, new_card.symbol, top_discarded_card.color, top_discarded_card.symbol))
                    if new_card.symbol == 'Change Color':
                        new_card.color = self.choose_color()
                    discarded_cards.append(new_card)
                else:
                    self.deck.append(new_card)
        # print("Player 1 does not have matched cards!")


if __name__ == "__main__":
    players = []
    players.append(Player("Victor", 1))
    players.append(Player("Angélica", 2))
    players.append(Player("Churros", 3))
    players.append(Player("Lucas", 4))
    game = Game(players)
    game.play_game(rounds=1)