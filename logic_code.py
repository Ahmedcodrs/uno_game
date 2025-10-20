import random
import sys

class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value
    def __str__(self): return f"{self.color} {self.value}"
    def __repr__(self): return f"Card('{self.color}', '{self.value}')"

class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        colors = ["Red", "Green", "Blue", "Yellow"]
        self.cards = []
        for color in colors:
            self.cards.append(Card(color, "0"))
            for i in range(1, 10): self.cards.extend([Card(color, str(i))] * 2)
            for action in ["Skip", "Reverse", "Draw 2"]: self.cards.extend([Card(color, action)] * 2)

        self.cards.extend([Card("Wild", "Wild")] * 4)
        self.cards.extend([Card("Wild", "Wild Draw 4")] * 4)

    def shuffle(self): random.shuffle(self.cards)

    def draw_card(self):
        if not self.cards:
            print("Deck empty!")
            return None
        return self.cards.pop()

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw(self, deck):
        card = deck.draw_card()
        if card: self.hand.append(card)
        return card

    def show_hand(self):
        print(f"\n--- {self.name}'s Hand ---")
        for i, card in enumerate(self.hand): print(f"  {i}: {card}")
        print("-" * (len(self.name) + 14))

class Game:
    def __init__(self, player_names):
        self.deck = Deck()
        self.deck.shuffle()
        self.discard_pile = []
        self.players = [Player(name) for name in player_names]
        self.current_player_index = 0
        self.game_direction = 1
        self.current_color = ""

        self.deal_initial_cards()
        self.start_game()

    def deal_initial_cards(self, num_cards=7):
        for player in self.players:
            for _ in range(num_cards): player.draw(self.deck)

    def start_game(self):
        first_card = self.deck.draw_card()
        while first_card and first_card.value == "Wild Draw 4":
            self.deck.cards.append(first_card)
            self.deck.shuffle()
            first_card = self.deck.draw_card()

        if first_card:
            self.discard_pile.append(first_card)
            self.current_color = first_card.color
            print(f"Game started! Top: {first_card}")
            self.apply_card_effect(first_card, is_first_card=True)

    def get_current_player(self): return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + self.game_direction) % len(self.players)

    def is_valid_play(self, card):
        top_card = self.discard_pile[-1]
        return card.color == "Wild" or card.color == self.current_color or card.value == top_card.value

    def play_card(self, player, card_index, chosen_color=None):
        if not (0 <= card_index < len(player.hand)): 
            return False
        card_to_play = player.hand[card_index]

        if self.is_valid_play(card_to_play):
            player.hand.pop(card_index)
            self.discard_pile.append(card_to_play)
            
            self.current_color = chosen_color if card_to_play.color == "Wild" else card_to_play.color
            if card_to_play.color == "Wild" and not chosen_color: 
                print("Defaulting to Red.")

            print(f"{player.name} played {card_to_play}.")

            if not player.hand:
                self.end_game(player)
                return True

            self.apply_card_effect(card_to_play)
            self.next_turn()

            return True
        else:
            print(f"Invalid play.")
            return False

    def apply_card_effect(self, card, is_first_card=False):
        if card.value == "Skip":
            print("Skipped!")
            self.next_turn()
        elif card.value == "Reverse":
            print("Reversed!")
            self.game_direction *= -1
            if len(self.players) == 2 and not is_first_card: self.next_turn()
        elif card.value == "Draw 2":
            target = self.players[(self.current_player_index + self.game_direction) % len(self.players)]
            print(f"{target.name} draws 2 and is skipped!")
            for _ in range(2): target.draw(self.deck)
            self.next_turn()
        elif card.value == "Wild Draw 4":
            target = self.players[(self.current_player_index + self.game_direction) % len(self.players)]
            print(f"{target.name} draws 4 and is skipped!")
            for _ in range(4): target.draw(self.deck)
            self.next_turn()
    
    def end_game(self, winner):
        print("\n" + "="*30)
        print(f"GAME OVER! Winner: {winner.name}!")
        print("="*30 + "\n")
        sys.exit()

if __name__ == "__main__":
    player_names = ["Kittu omega", "Kittu supreme","rohan"]
    game = Game(player_names)

    while True:
        current_player = game.get_current_player()
        top_card = game.discard_pile[-1]
        print(f"\n{'*'*40}\nTop card: {top_card} ({game.current_color})")
        current_player.show_hand()

        playable = [i for i, card in enumerate(current_player.hand) if game.is_valid_play(card)]

        if not playable:
            drawn_card = current_player.draw(game.deck)
            print(f"{current_player.name} drew {drawn_card}.")
            
            if game.is_valid_play(drawn_card):
                idx = len(current_player.hand) - 1
                color = random.choice(["Red", "Green", "Blue", "Yellow"]) if drawn_card.color == "Wild" else None
                game.play_card(current_player, idx, color)
            else:
                print("Cannot play drawn card. Skipped.")
                game.next_turn()
            continue

        try:
            choice = input(f"{current_player.name}, card (0-{len(current_player.hand)-1}) or 'draw': ")
            
            if choice.lower() == 'draw':
                current_player.draw(game.deck)
                game.next_turn()
                continue

            card_index = int(choice)
            card_to_play = current_player.hand[card_index]
            
            chosen_color = None
            if card_to_play.color == "Wild":
                while chosen_color not in ["Red", "Green", "Blue", "Yellow"]:
                    chosen_color = input("Choose color (Red, Green, Blue, Yellow): ").capitalize()

            game.play_card(current_player, card_index, chosen_color)

        except (ValueError, IndexError):
            print("Invalid input.")
        except KeyboardInterrupt:
            sys.exit()
