from itertools import combinations
from typing import List, Tuple
from .card import Card
 
 
# Hand rank constants — higher number beats lower number
HIGH_CARD       = 0
ONE_PAIR        = 1
TWO_PAIR        = 2
THREE_OF_A_KIND = 3
STRAIGHT        = 4
FLUSH           = 5
FULL_HOUSE      = 6
FOUR_OF_A_KIND  = 7
STRAIGHT_FLUSH  = 8  # Includes Royal Flush (just a straight flush to Ace)
 
HAND_NAMES = {
    0: "High Card",
    1: "One Pair",
    2: "Two Pair",
    3: "Three of a Kind",
    4: "Straight",
    5: "Flush",
    6: "Full House",
    7: "Four of a Kind",
    8: "Straight Flush",
}

def evaluate_7_cards(cards: List[Card]) -> Tuple:

    assert len(cards) == 7, f'Expected 7 cards, got {len(cards)}'

    best_score = None
    for five_cards in combinations(cards, 5):
        score = _evaluate_5_cards(list(five_cards))
        if best_score is None or best_score < score:
            best_score = score
    return best_score

def evaluate_5_cards(cards: List[Card]) -> Tuple:
    # Public wrapper to score 5 cards
    assert len(cards) == 5, f'Expected 5 cards, got {len(cards)}'
    return _evaluate_5_cards(cards)

def get_hand_name(score: Tuple) -> str:
    return HAND_NAMES[score[0]]

def get_winner(player_cards_list: List[List[Card]], community_cards: List[Card]) -> List[int]:
    # returns winning players
    assert len(community_cards) == 5, 'Must have 5 community cards to determine winner'

    scores = []
    for player_cards in player_cards_list:
        hand = player_cards + community_cards
        score = evaluate_7_cards(hand)
        scores.append(score)
    best_score = max(scores)
    winners = [i for i, score in enumerate(scores) if score == best_score]
    return winners

# Private helpers

def _evaluate_5_cards(cards: List[Card]) -> Tuple:
    values = sorted([c.rank_val for c in cards], reverse=True)
    suits = [c.suit for c in cards]

    is_flush = _is_flush(suits)
    straight_high = _straight_high_card(values)
    counts = _count_ranks(values)

    if is_flush and straight_high:
        return (STRAIGHT_FLUSH, straight_high)
    
    if 4 in counts.values():
        quad_rank = _ranks_with_count(counts, 4)[0]
        kicker = _ranks_with_count(counts, 1)[0]
        return (FOUR_OF_A_KIND, quad_rank, kicker)
    
    if 3 in counts.values() and 2 in counts.values():
        triple_rank = _ranks_with_count(counts, 3)[0]
        pair_rank = _ranks_with_count(counts, 2)[0]
        return (FULL_HOUSE, triple_rank, pair_rank)
    
    if is_flush:
        # return all 5 values for tie break
        return (FLUSH, values)
    
    if straight_high:
        return (STRAIGHT, straight_high)
    
    if 3 in counts.values():
        triple_rank = _ranks_with_count(counts, 3)[0]
        kickers = sorted(_ranks_with_count(counts, 1), reverse=True)
        return (THREE_OF_A_KIND, triple_rank, kickers)
    
    pairs = _ranks_with_count(counts, 2)
    if len(pairs) == 2:
        high_pair = max(pairs)
        low_pair = min(pairs)
        kicker = _ranks_with_count(counts, 1)[0]
        return (TWO_PAIR, high_pair, low_pair, kicker)
    
    if len(pairs) == 1:
        pair_rank = pairs[0]
        kickers = sorted(_ranks_with_count(counts, 1), reverse=True)
        return (ONE_PAIR, pair_rank, kickers)
    
    return (HIGH_CARD, values)

def _is_flush(suits: List[str]) -> bool:
    return len(set(suits)) == 1

def _straight_high_card(values: List[int]) -> int:
    # returns high card value of straight or 0 if no straight exists
    unique = sorted(set(values), reverse=True)

    if len(unique) == 5 and unique[0] - unique[4] == 4:
        return unique[0]
    
    # Edge case for A-2-3-4-5
    if unique == [14, 5, 4, 3, 2]:
        return 5
    
    return 0

def _count_ranks(values: List[int]) -> dict:
    # count frequency of card values
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts

def _ranks_with_count(counts: dict, n: int) -> List[int]:
    # returns list of card vals that appear n times
    # sorted in descending so high card comes first
    return sorted([rank for rank, count in counts.items() if count == n], reverse=True)