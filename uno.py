from itertools import cycle
import numpy as np
import random
import sys

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
        self.discarded = []
        self.player_order = list(range(1, len(players)+1))

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
                    players[player-1].deck.append(card)
        first_discarded_card = self.cards.pop(0)
        self.discarded.append(first_discarded_card)

    def play_game(self, rounds=10):
        # In the first round, Player 1 is the first to deal and then player 2 starts (depending on which card is the first discarded)
        # In next rounds, Player N deals and Player N+1 starts, it's a circle.
        for _ in range(rounds):
            self.init_cards()
            self.create_deck()
            self.game_order = self.player_order
            self.game_finished = False
            self.already_played = []
            while self.game_finished is False:
                current_player = players[self.check_turn()-1]
                # current_player.show_deck()
                print("{}'s turn!".format(current_player.name))
                if len(self.cards) == 0:
                    self.init_cards()
                    self.discarded = [self.cards.pop(0)]
                current_player.take_action(self.discarded, self.cards)
                self.game_finished = self.check_winner(current_player)
            self.cards = []

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


    def check_winner(self, player):
        if len(player.deck) == 0:
            return True
        return False

class Player:
    def __init__(self, name, player_id, human=False):
        self.name = name
        self.player_id = player_id
        self.deck = []
        self.human = human

    def show_deck(self, deck=None):
        i = 1
        if not deck:
            deck = self.deck
        print("==============================================")
        print("{}'s cards are: ".format(self.name))
        for card in deck:
            print("{} - {} {}".format(i, card.color, card.symbol))
            i += 1
        print("==============================================")

    def play_card(self, matched_cards, discarded_cards):
        random.shuffle(matched_cards)
        card = matched_cards.pop(0)
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
        print("{}'s matched cards are: ".format(self.name))
        self.show_deck(matched_cards)
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

    def take_action(self, discarded_cards, cards):
        buy_extra = True
        matched_cards = []
        top_discarded_card = discarded_cards[-1]
        print("Discarded card at top is {} {}".format(top_discarded_card.color, top_discarded_card.symbol))
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
                card_chosen = self.play_card(matched_cards, discarded_cards)
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
        # print("Player 1 does not have matched cards!")


if __name__ == "__main__":
    players = []
    players.append(Player("Victor", 1, human=True))
    players.append(Player("Angélica", 2))
    # players.append(Player("Churros", 3))
    # players.append(Player("Lucas", 4))
    # players.append(Player("João", 5))
    game = Game(players)
    game.play_game(rounds=1)

    # TODO: For a perfect game, introduce missing rules for first discards
    # TODO: Progressive Uno