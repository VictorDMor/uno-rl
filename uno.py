import numpy as np

class Card:
    def __init__(self, color, symbol):
        self.color = color
        self.symbol = symbol

class Game:
    def __init__(self, number_of_players=2):
        self.number_of_players = number_of_players
        self.cards = []

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
        deck = {}
        for i in range(self.number_of_players):
            deck["Player {}".format(i+1)] = []
            for j in range(7):
                choice = np.random.choice(len(self.cards))
                deck["Player {}".format(i+1)].append(self.cards[choice])
                self.cards.pop(choice)


if __name__ == "__main__":
    game = Game()
    game.init_cards()
    game.create_deck()