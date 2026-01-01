

import random


# ==================== CARD CLASS ====================
class Card:
    def __init__(self, color, value):
        self.color = color  # "Red", "Green", "Blue", "Yellow", "Wild"
        self.value = value  # "0"-"9", "Skip", "Reverse", "Draw 2", "Wild", "Wild Draw 4"

    def __str__(self):
        return f"{self.color} {self.value}"

    def __repr__(self):
        return f"Card('{self.color}', '{self.value}')"

    # NEW: Convert card to dictionary for sending over network
    def to_dict(self):
        """
        Converts card to a dictionary that can be sent over network
        Example: Card("Red", "5") → {"color": "Red", "value": "5"}
        """
        return {
            "color": self.color,
            "value": self.value
        }

    # NEW: Recreate card from dictionary received over network
    @staticmethod
    def from_dict(data):

        return Card(data["color"], data["value"])



class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        """Create all 108 UNO cards"""
        colors = ["Red", "Green", "Blue", "Yellow"]
        self.cards = []

        for color in colors:
            # One 0 card per color
            self.cards.append(Card(color, "0"))
            # Two of each 1-9
            for i in range(1, 10):
                self.cards.extend([Card(color, str(i))] * 2)
            # Two of each action card
            for action in ["Skip", "Reverse", "Draw 2"]:
                self.cards.extend([Card(color, action)] * 2)

        # Add Wild cards
        self.cards.extend([Card("Wild", "Wild")] * 4)
        self.cards.extend([Card("Wild", "Wild Draw 4")] * 4)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):

        if not self.cards:
            return None
        return self.cards.pop()

    def reshuffle_from_discard(self, discard_pile):

        if len(discard_pile) > 1:
            top_card = discard_pile[-1]  # Keep top card
            self.cards = discard_pile[:-1]  # Everything else goes to deck
            self.shuffle()
            return [top_card]  # New discard pile with just top card
        return discard_pile



class Player:
    def __init__(self, name, player_id):
        self.name = name
        self.player_id = player_id  # NEW: Each player has an ID (0, 1, 2, 3)
        self.hand = []
        self.called_uno = False

    def draw(self, deck):
        """Draw a card and add to hand"""
        card = deck.draw_card()
        if card:
            self.hand.append(card)
        return card


    def to_dict(self):

        return {
            "name": self.name,
            "player_id": self.player_id,
            "card_count": len(self.hand),
            "called_uno": self.called_uno
        }


# ==================== MAIN GAME CLASS ====================
class UNOGame:

    def __init__(self, player_names):

        self.deck = Deck()
        self.deck.shuffle()
        self.discard_pile = []

        # Create players with IDs
        self.players = [Player(name, i) for i, name in enumerate(player_names)]

        self.current_player_index = 0  # Whose turn (0, 1, 2, 3)
        self.game_direction = 1  # 1 = clockwise, -1 = counter-clockwise
        self.current_color = ""  # Current color in play

        # NEW: Game state flags
        self.game_over = False
        self.winner = None
        self.last_action = ""  # Description of last thing that happened

        # Setup game
        self.deal_initial_cards()
        self.start_game()

    def deal_initial_cards(self, num_cards=7):

        for player in self.players:
            for _ in range(num_cards):
                player.draw(self.deck)

    def start_game(self):

        first_card = self.deck.draw_card()

        # Keep drawing until we don't get Wild Draw 4
        while first_card and first_card.value == "Wild Draw 4":
            self.deck.cards.append(first_card)
            self.deck.shuffle()
            first_card = self.deck.draw_card()

        if first_card:
            self.discard_pile.append(first_card)
            self.current_color = first_card.color
            self.last_action = f"Game started! Top card: {first_card}"

            # Apply effect of first card (if it's Skip, Reverse, etc.)
            self.apply_card_effect(first_card, is_first_card=True)

    def get_current_player(self):

        return self.players[self.current_player_index]

    def next_turn(self):

        self.current_player_index = (self.current_player_index + self.game_direction) % len(self.players)

    def is_valid_play(self, card):

        if not self.discard_pile:
            return False

        top_card = self.discard_pile[-1]

        return (
                card.color == "Wild" or  # Wild cards can always be played
                card.color == self.current_color or  # Match color
                card.value == top_card.value  # Match number/action
        )

    def call_uno(self, player_id):
        """
        Player calls UNO when they have 1 card left
        Returns result dict
        """
        player = self.players[player_id]

        # Check if player has exactly 1 card
        if len(player.hand) == 1:
            player.called_uno = True
            self.last_action = f"{player.name} called UNO!"
            return {
                "success": True,
                "message": f"{player.name} called UNO!",
                "called_uno": True
            }
        else:
            return {
                "success": False,
                "error": "Can only call UNO with 1 card",
                "message": f"{player.name} has {len(player.hand)} cards"
            }

    def check_uno_penalty(self, player_id):
        """
        Check if player should be penalized for not calling UNO
        Called after a player plays a card
        """
        player = self.players[player_id]

        # If player has 1 card but didn't call UNO
        if len(player.hand) == 1 and not player.called_uno:
            # Penalty: draw 2 cards
            for _ in range(2):
                player.draw(self.deck)
            self.last_action = f"{player.name} forgot to call UNO! Drew 2 cards as penalty."
            return {
                "penalty": True,
                "message": f"{player.name} penalized for not calling UNO"
            }

        return {"penalty": False}

    def play_card(self, player_id, card_index, chosen_color=None):
        player = self.players[player_id]

        # VALIDATION 1: Check if valid card index
        if not (0 <= card_index < len(player.hand)):
            return {
                "success": False,
                "error": "Invalid card index",
                "message": f"Card index {card_index} out of range"
            }

        # VALIDATION 2: Check if it's this player's turn
        if self.current_player_index != player_id:
            return {
                "success": False,
                "error": "Not your turn",
                "message": f"It's {self.get_current_player().name}'s turn"
            }

        card_to_play = player.hand[card_index]

        # VALIDATION 3: Check if card can be played
        if not self.is_valid_play(card_to_play):
            return {
                "success": False,
                "error": "Invalid card",
                "message": f"Cannot play {card_to_play} on {self.discard_pile[-1]}"
            }



        # Remove from hand
        player.hand.pop(card_index)

        # Add to discard pile
        self.discard_pile.append(card_to_play)

        # Handle Wild card color choice
        if card_to_play.color == "Wild":
            if chosen_color and chosen_color in ["Red", "Green", "Blue", "Yellow"]:
                self.current_color = chosen_color
            else:
                self.current_color = "Red"  # Default
        else:
            self.current_color = card_to_play.color

        self.last_action = f"{player.name} played {card_to_play}"

        # Check for win (player has no cards left)
        if not player.hand:
            self.game_over = True
            self.winner = player
            return {
                "success": True,
                "card_played": card_to_play.to_dict(),
                "current_color": self.current_color,
                "game_over": True,
                "winner": player.name,
                "message": f"{player.name} wins!"
            }

        # Apply card effects (Skip, Reverse, Draw 2, etc.)
        effect_msg = self.apply_card_effect(card_to_play)
        if len(player.hand) != 1:
            player.called_uno = False
        # Move to next turn
        self.next_turn()

        # Return result
        return {
            "success": True,
            "card_played": card_to_play.to_dict(),
            "current_color": self.current_color,
            "next_player": self.current_player_index,
            "effect": effect_msg,
            "game_over": False,
            "message": f"{player.name} played {card_to_play}"
        }

    def draw_card_action(self, player_id):


        if self.current_player_index != player_id:
            return {
                "success": False,
                "error": "Not your turn"
            }

        player = self.players[player_id]

        # Check if deck is empty
        if not self.deck.cards:
            self.discard_pile = self.deck.reshuffle_from_discard(self.discard_pile)

        drawn_card = player.draw(self.deck)

        if not drawn_card:
            # Deck still empty even after reshuffle
            self.last_action = f"{player.name} tried to draw but deck empty"
            self.next_turn()
            return {
                "success": True,
                "drew_card": False,
                "next_player": self.current_player_index,
                "message": "Deck empty, turn skipped"
            }

        self.last_action = f"{player.name} drew a card"

        # Check if drawn card can be played
        can_play = self.is_valid_play(drawn_card)

        if can_play:
            # Automatically play it if possible
            card_index = len(player.hand) - 1
            chosen_color = None
            if drawn_card.color == "Wild":
                chosen_color = random.choice(["Red", "Green", "Blue", "Yellow"])

            # Play the drawn card
            return self.play_card(player_id, card_index, chosen_color)
        else:
            # Can't play, skip turn
            self.next_turn()
            return {
                "success": True,
                "drew_card": True,
                "can_play": False,
                "next_player": self.current_player_index,
                "message": f"{player.name} drew a card but cannot play"
            }

    def apply_card_effect(self, card, is_first_card=False):

        effect = ""

        if card.value == "Skip":
            skipped_player = self.players[(self.current_player_index + self.game_direction) % len(self.players)]
            effect = f"{skipped_player.name} is skipped!"
            self.next_turn()

        elif card.value == "Reverse":
            self.game_direction *= -1
            effect = "Direction reversed!"
            # In 2-player game, Reverse acts like Skip
            if len(self.players) == 2 and not is_first_card:
                self.next_turn()

        elif card.value == "Draw 2":
            target = self.players[(self.current_player_index + self.game_direction) % len(self.players)]
            for _ in range(2):
                target.draw(self.deck)
            effect = f"{target.name} draws 2 cards and is skipped!"
            self.next_turn()

        elif card.value == "Wild Draw 4":
            target = self.players[(self.current_player_index + self.game_direction) % len(self.players)]
            for _ in range(4):
                target.draw(self.deck)
            effect = f"{target.name} draws 4 cards and is skipped!"
            self.next_turn()

        if effect:
            self.last_action += f" - {effect}"

        return effect

    # ==================== GET GAME STATE ====================
    def get_game_state(self, for_player_id=None):


        state = {
            "top_card": self.discard_pile[-1].to_dict() if self.discard_pile else None,
            "current_color": self.current_color,
            "current_player": self.current_player_index,
            "direction": self.game_direction,
            "players": [p.to_dict() for p in self.players],
            "last_action": self.last_action,
            "game_over": self.game_over,
            "winner": self.winner.name if self.winner else None
        }

        # Include specific player's hand
        if for_player_id is not None and 0 <= for_player_id < len(self.players):
            player = self.players[for_player_id]
            state["your_hand"] = [card.to_dict() for card in player.hand]

        return state

    # ==================== HELPER METHODS ====================
    def get_playable_cards(self, player_id):
        """
        Get indices of cards that can be played
        Returns: [0, 2, 5] ← These card positions are playable
        """
        player = self.players[player_id]
        return [i for i, card in enumerate(player.hand) if self.is_valid_play(card)]



