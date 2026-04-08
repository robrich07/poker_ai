import pytest
from poker.card import Card
from poker.hand_evaluator import (
    evaluate_5_cards, evaluate_7_cards, get_hand_name, get_winner,
    HIGH_CARD, ONE_PAIR, TWO_PAIR, THREE_OF_A_KIND, STRAIGHT,
    FLUSH, FULL_HOUSE, FOUR_OF_A_KIND, STRAIGHT_FLUSH,
)


# Helper to quickly create cards
def c(rank, suit):
    suit_map = {'s': 'spades', 'c': 'clubs', 'h': 'hearts', 'd': 'diamonds'}
    return Card(rank, suit_map[suit])


# ---- 5-Card Evaluation Tests ----

class TestEvaluate5Cards:

    def test_high_card(self):
        cards = [c('2', 's'), c('5', 'h'), c('9', 'd'), c('J', 'c'), c('A', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == HIGH_CARD

    def test_one_pair(self):
        cards = [c('3', 's'), c('3', 'h'), c('7', 'd'), c('J', 'c'), c('A', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == ONE_PAIR
        assert score[1] == 3  # pair of 3s

    def test_two_pair(self):
        cards = [c('4', 's'), c('4', 'h'), c('9', 'd'), c('9', 'c'), c('A', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == TWO_PAIR
        assert score[1] == 9   # high pair
        assert score[2] == 4   # low pair
        assert score[3] == 14  # kicker

    def test_three_of_a_kind(self):
        cards = [c('7', 's'), c('7', 'h'), c('7', 'd'), c('2', 'c'), c('A', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == THREE_OF_A_KIND
        assert score[1] == 7

    def test_straight(self):
        cards = [c('5', 's'), c('6', 'h'), c('7', 'd'), c('8', 'c'), c('9', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == STRAIGHT
        assert score[1] == 9  # high card of straight

    def test_straight_ace_high(self):
        cards = [c('10', 's'), c('J', 'h'), c('Q', 'd'), c('K', 'c'), c('A', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == STRAIGHT
        assert score[1] == 14

    def test_straight_ace_low(self):
        cards = [c('A', 's'), c('2', 'h'), c('3', 'd'), c('4', 'c'), c('5', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == STRAIGHT
        assert score[1] == 5  # ace-low, 5 is high card

    def test_flush(self):
        cards = [c('2', 'h'), c('5', 'h'), c('8', 'h'), c('J', 'h'), c('A', 'h')]
        score = evaluate_5_cards(cards)
        assert score[0] == FLUSH

    def test_full_house(self):
        cards = [c('10', 's'), c('10', 'h'), c('10', 'd'), c('K', 'c'), c('K', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == FULL_HOUSE
        assert score[1] == 10  # trips
        assert score[2] == 13  # pair

    def test_four_of_a_kind(self):
        cards = [c('J', 's'), c('J', 'h'), c('J', 'd'), c('J', 'c'), c('3', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == FOUR_OF_A_KIND
        assert score[1] == 11  # quads
        assert score[2] == 3   # kicker

    def test_straight_flush(self):
        cards = [c('5', 'd'), c('6', 'd'), c('7', 'd'), c('8', 'd'), c('9', 'd')]
        score = evaluate_5_cards(cards)
        assert score[0] == STRAIGHT_FLUSH
        assert score[1] == 9

    def test_royal_flush(self):
        cards = [c('10', 's'), c('J', 's'), c('Q', 's'), c('K', 's'), c('A', 's')]
        score = evaluate_5_cards(cards)
        assert score[0] == STRAIGHT_FLUSH
        assert score[1] == 14

    def test_ace_low_straight_flush(self):
        cards = [c('A', 'h'), c('2', 'h'), c('3', 'h'), c('4', 'h'), c('5', 'h')]
        score = evaluate_5_cards(cards)
        assert score[0] == STRAIGHT_FLUSH
        assert score[1] == 5

    def test_wrong_card_count(self):
        with pytest.raises(AssertionError):
            evaluate_5_cards([c('A', 's'), c('K', 's')])


# ---- Hand Ranking Comparison Tests ----

class TestHandRankings:

    def test_pair_beats_high_card(self):
        high_card = evaluate_5_cards([c('2', 's'), c('5', 'h'), c('9', 'd'), c('J', 'c'), c('A', 's')])
        pair = evaluate_5_cards([c('3', 's'), c('3', 'h'), c('7', 'd'), c('J', 'c'), c('A', 'd')])
        assert pair > high_card

    def test_flush_beats_straight(self):
        straight = evaluate_5_cards([c('5', 's'), c('6', 'h'), c('7', 'd'), c('8', 'c'), c('9', 's')])
        flush = evaluate_5_cards([c('2', 'h'), c('5', 'h'), c('8', 'h'), c('J', 'h'), c('A', 'h')])
        assert flush > straight

    def test_full_house_beats_flush(self):
        flush = evaluate_5_cards([c('2', 'h'), c('5', 'h'), c('8', 'h'), c('J', 'h'), c('A', 'h')])
        full_house = evaluate_5_cards([c('3', 's'), c('3', 'h'), c('3', 'd'), c('6', 'c'), c('6', 's')])
        assert full_house > flush

    def test_four_of_a_kind_beats_full_house(self):
        full_house = evaluate_5_cards([c('3', 's'), c('3', 'h'), c('3', 'd'), c('6', 'c'), c('6', 's')])
        quads = evaluate_5_cards([c('2', 's'), c('2', 'h'), c('2', 'd'), c('2', 'c'), c('7', 's')])
        assert quads > full_house

    def test_straight_flush_beats_four_of_a_kind(self):
        quads = evaluate_5_cards([c('A', 's'), c('A', 'h'), c('A', 'd'), c('A', 'c'), c('K', 's')])
        sf = evaluate_5_cards([c('5', 'd'), c('6', 'd'), c('7', 'd'), c('8', 'd'), c('9', 'd')])
        assert sf > quads

    def test_higher_pair_wins(self):
        pair_3 = evaluate_5_cards([c('3', 's'), c('3', 'h'), c('7', 'd'), c('J', 'c'), c('A', 's')])
        pair_k = evaluate_5_cards([c('K', 's'), c('K', 'h'), c('2', 'd'), c('5', 'c'), c('7', 's')])
        assert pair_k > pair_3

    def test_same_pair_kicker_decides(self):
        pair_a_kicker = evaluate_5_cards([c('10', 's'), c('10', 'h'), c('A', 'd'), c('3', 'c'), c('2', 's')])
        pair_k_kicker = evaluate_5_cards([c('10', 'd'), c('10', 'c'), c('K', 'd'), c('3', 's'), c('2', 'h')])
        assert pair_a_kicker > pair_k_kicker

    def test_flush_tiebreak_by_high_card(self):
        flush_a = evaluate_5_cards([c('2', 'h'), c('4', 'h'), c('6', 'h'), c('8', 'h'), c('A', 'h')])
        flush_k = evaluate_5_cards([c('2', 'd'), c('4', 'd'), c('6', 'd'), c('8', 'd'), c('K', 'd')])
        assert flush_a > flush_k

    def test_high_card_tiebreak(self):
        hand_a = evaluate_5_cards([c('2', 's'), c('4', 'h'), c('6', 'd'), c('8', 'c'), c('A', 's')])
        hand_k = evaluate_5_cards([c('2', 'd'), c('4', 'c'), c('6', 's'), c('8', 'h'), c('K', 'd')])
        assert hand_a > hand_k

    def test_identical_hands_are_equal(self):
        hand1 = evaluate_5_cards([c('2', 's'), c('5', 'h'), c('9', 'd'), c('J', 'c'), c('A', 's')])
        hand2 = evaluate_5_cards([c('2', 'd'), c('5', 'c'), c('9', 's'), c('J', 'h'), c('A', 'd')])
        assert hand1 == hand2


# ---- 7-Card Evaluation Tests ----

class TestEvaluate7Cards:

    def test_finds_best_hand(self):
        # 7 cards contain a flush in hearts
        cards = [
            c('2', 'h'), c('5', 'h'), c('8', 'h'), c('J', 'h'), c('A', 'h'),
            c('3', 's'), c('K', 'd'),
        ]
        score = evaluate_7_cards(cards)
        assert score[0] == FLUSH

    def test_straight_among_junk(self):
        cards = [
            c('4', 's'), c('5', 'h'), c('6', 'd'), c('7', 'c'), c('8', 's'),
            c('2', 'h'), c('K', 'd'),
        ]
        score = evaluate_7_cards(cards)
        assert score[0] == STRAIGHT
        assert score[1] == 8

    def test_full_house_from_7(self):
        cards = [
            c('9', 's'), c('9', 'h'), c('9', 'd'), c('K', 'c'), c('K', 's'),
            c('2', 'h'), c('3', 'd'),
        ]
        score = evaluate_7_cards(cards)
        assert score[0] == FULL_HOUSE

    def test_wrong_card_count(self):
        with pytest.raises(AssertionError):
            evaluate_7_cards([c('A', 's')])


# ---- get_hand_name Tests ----

class TestGetHandName:

    def test_all_hand_names(self):
        assert get_hand_name((HIGH_CARD, [14, 10, 8, 5, 2])) == "High Card"
        assert get_hand_name((ONE_PAIR, 10, [14, 8, 5])) == "One Pair"
        assert get_hand_name((TWO_PAIR, 10, 5, 14)) == "Two Pair"
        assert get_hand_name((THREE_OF_A_KIND, 10, [14, 8])) == "Three of a Kind"
        assert get_hand_name((STRAIGHT, 10)) == "Straight"
        assert get_hand_name((FLUSH, [14, 10, 8, 5, 2])) == "Flush"
        assert get_hand_name((FULL_HOUSE, 10, 5)) == "Full House"
        assert get_hand_name((FOUR_OF_A_KIND, 10, 14)) == "Four of a Kind"
        assert get_hand_name((STRAIGHT_FLUSH, 14)) == "Straight Flush"


# ---- get_winner Tests ----

class TestGetWinner:

    def test_single_winner(self):
        community = [c('2', 's'), c('5', 'h'), c('9', 'd'), c('J', 'c'), c('K', 'd')]
        player0 = [c('A', 's'), c('3', 'h')]  # pair of nothing, ace high
        player1 = [c('K', 's'), c('K', 'h')]  # three kings
        winners = get_winner([player0, player1], community)
        assert winners == [1]

    def test_split_pot(self):
        # Both players play the board
        community = [c('A', 's'), c('A', 'h'), c('A', 'd'), c('A', 'c'), c('K', 's')]
        player0 = [c('2', 's'), c('3', 'h')]
        player1 = [c('4', 's'), c('5', 'h')]
        winners = get_winner([player0, player1], community)
        assert winners == [0, 1]

    def test_three_players(self):
        community = [c('2', 's'), c('5', 'h'), c('9', 'd'), c('J', 'c'), c('K', 'd')]
        player0 = [c('3', 's'), c('4', 'h')]
        player1 = [c('A', 's'), c('A', 'h')]  # best hand
        player2 = [c('K', 's'), c('Q', 'h')]
        winners = get_winner([player0, player1, player2], community)
        assert winners == [1]

    def test_wrong_community_count(self):
        with pytest.raises(AssertionError):
            get_winner([[c('A', 's'), c('K', 's')]], [c('2', 's'), c('3', 's')])
