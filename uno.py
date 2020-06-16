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
            for j in range(0, 10):
                self.cards.append(Card(i, str(j)))
                self.cards.append(Card(i, str(j)))
            self.cards.append(Card(i, "+2"))
            self.cards.append(Card(i, "+2"))
            self.cards.append(Card(i, "Skip"))
            self.cards.append(Card(i, "Skip"))
            self.cards.append(Card(i, "Reverse"))
            self.cards.append(Card(i, "Reverse"))
        for i in range(4):
            self.cards.append(Card('joker', '+4'))
            self.cards.append(Card('joker', 'Change Color'))

    def create_deck(self):
        # Initialize deck
        dealer = self.player_order.pop(0)
        print("{} is the dealer!".format(self.players[dealer-1].name))
        self.player_order.append(dealer)
        for _ in range(7):
            for player in self.player_order:
                    choice = np.random.choice(len(self.cards))
                    players[player-1].deck.append(self.cards[choice])
                    self.cards.pop(choice)
        random.shuffle(self.cards)
        first_discarded_card = self.cards.pop(0)
        self.discarded.append(first_discarded_card)

    def play_game(self, rounds=10):
        # In the first round, Player 1 is the first to deal and then player 2 starts (depending on which card is the first discarded)
        # In next rounds, Player N deals and Player N+1 starts, it's a circle.
        for _ in range(rounds):
            self.init_cards()
            self.create_deck()
            self.game_finished = False
            while self.game_finished is False:
                for player in self.player_order:
                    current_player = players[player-1]
                    current_player.show_deck()
                    print("{}'s turn!".format(current_player.name))
                    if len(self.cards) == 0:
                        random.shuffle(self.discarded)
                        self.cards = self.discarded
                        self.discarded = []
                        self.discarded.append(self.cards.pop(0))
                    current_player.take_action(self.discarded, self.cards)
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

    def take_action(self, discarded_cards, cards):
        # TODO: Joker's and special cards actions
        matched_cards = []
        top_discarded_card = discarded_cards[-1]
        print("Discarded card at top is {} {}".format(top_discarded_card.color, top_discarded_card.symbol))
        for card in self.deck:
            if card.color in [top_discarded_card.color, 'joker'] or card.symbol == top_discarded_card.symbol:
                print("{} {} matches discarded card at top!".format(card.color, card.symbol))
                matched_cards.append(card)
        # print("Length of matched cards is {}".format(len(matched_cards)))
        if len(matched_cards) > 0:
            card_choice_idx = np.random.choice(len(matched_cards))
            card_chosen = matched_cards.pop(card_choice_idx)
            self.deck.pop(self.deck.index(card_chosen))
            print("The card chosen by {} is {} {}".format(self.name, card_chosen.color, card_chosen.symbol))
            discarded_cards.append(card_chosen)
        else:
            print("{} needs to buy a card!".format(self.name))
            new_card_idx = np.random.choice(len(cards))
            new_card = cards.pop(new_card_idx)
            print("Card bought is {} {}".format(new_card.color, new_card.symbol))
            if new_card.color in [top_discarded_card.color, 'joker'] or new_card.symbol == top_discarded_card.symbol:
                print("Card bought {} {} matches with discarded card {} {}".format(new_card.color, new_card.symbol, top_discarded_card.color, top_discarded_card.symbol))
                discarded_cards.append(new_card)
            else:
                self.deck.append(new_card)
        # print("Player 1 does not have matched cards!")


if __name__ == "__main__":
    players = []
    players.append(Player("Victor", 1))
    players.append(Player("Angélica", 2))
    game = Game(players)
    game.play_game(rounds=1)