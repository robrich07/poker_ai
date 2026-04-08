from typing import List, Optional
from .card import Card


class Player:
    # Represents a player at the table

    def __init__(self, player_id: int, chips: int):
        self.player_id = player_id
        self.chips = chips
        self.hole_cards: List[Card] = []
        self.current_bet = 0
        self.is_folded = False
        self.is_all_in = False

    def place_bet(self, amount: int) -> int:
        # Places a bet up to the player's remaining chips.
        # Returns the actual amount bet (may be less if all-in).
        actual = min(amount, self.chips)
        self.chips -= actual
        self.current_bet += actual
        if self.chips == 0:
            self.is_all_in = True
        return actual

    def fold(self):
        self.is_folded = True

    def receive_cards(self, cards: List[Card]):
        self.hole_cards = cards

    def reset_for_new_hand(self):
        # Resets per-hand state while keeping chips
        self.hole_cards = []
        self.current_bet = 0
        self.is_folded = False
        self.is_all_in = False

    def reset_bet(self):
        # Called at the start of each betting round
        self.current_bet = 0

    @property
    def is_active(self) -> bool:
        # A player is active if they haven't folded and aren't all-in
        return not self.is_folded and not self.is_all_in

    def __repr__(self) -> str:
        return f'Player {self.player_id} (chips={self.chips})'
