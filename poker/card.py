import random
from typing import List

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['spades', 'clubs', 'hearts', 'diamonds']

class Card:
    # Represents a single card in the deck

    def __init__(self, rank: str, suit: str):
        if rank not in RANKS:
            raise ValueError(f'Invalid rank {rank}, must be one of {RANKS}')
        if suit not in SUITS:
            raise ValueError(f'Invalid suit {suit}, must be one of {SUITS}')
        
        self.rank = rank
        self.suit = suit
        self.rank_val = RANKS.index(rank) + 2
        self.suit_val = SUITS.index(suit)
    
    def __repr__(self) -> str:
        return f'{self.rank} of {self.suit}'
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank_val < other.rank_val

    def __le__(self, other) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank_val <= other.rank_val

    def __gt__(self, other) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank_val > other.rank_val

    def __ge__(self, other) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank_val >= other.rank_val
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))
    
    def to_int(self) -> int:
        # encodes card as int in range [0, 51] for model
        return (self.rank_val - 2) * 4 + self.suit_val
    
class Deck:
    # Represents a standard 52 card deck

    def __init__(self, shuffle=True):
        self.cards: List[Card] = []
        self._build()
        if shuffle:
            self.shuffle()

    def _build(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self) -> Card:
        if not self.cards:
            raise ValueError('Cannot deal from empty deck')
        return self.cards.pop()

    def deal_many(self, n: int) -> List[Card]:
        if n > len(self.cards):
            raise ValueError(f'Cannot deal {n} cards, only {len(self.cards)} remaining')
        return [self.deal() for _ in range(n)]
    
    def reset(self):
        self._build()
        self.shuffle()

    def __len__(self):
        return len(self.cards)
    
    def __repr__(self):
        return f'Deck ({len(self.cards)} cards remaining)'