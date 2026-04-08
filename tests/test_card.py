import pytest
from poker.card import Card, Deck, RANKS, SUITS


# ---- Card Tests ----

class TestCard:

    def test_valid_card_creation(self):
        card = Card('A', 'spades')
        assert card.rank == 'A'
        assert card.suit == 'spades'
        assert card.rank_val == 14
        assert card.suit_val == 0

    def test_rank_values(self):
        assert Card('2', 'hearts').rank_val == 2
        assert Card('10', 'hearts').rank_val == 10
        assert Card('J', 'hearts').rank_val == 11
        assert Card('Q', 'hearts').rank_val == 12
        assert Card('K', 'hearts').rank_val == 13
        assert Card('A', 'hearts').rank_val == 14

    def test_invalid_rank(self):
        with pytest.raises(ValueError):
            Card('1', 'spades')

    def test_invalid_suit(self):
        with pytest.raises(ValueError):
            Card('A', 'swords')

    def test_repr(self):
        card = Card('K', 'diamonds')
        assert repr(card) == 'K of diamonds'

    def test_equality(self):
        assert Card('A', 'spades') == Card('A', 'spades')
        assert Card('A', 'spades') != Card('A', 'hearts')
        assert Card('A', 'spades') != Card('K', 'spades')

    def test_equality_non_card(self):
        card = Card('A', 'spades')
        assert card.__eq__(None) is NotImplemented
        assert card.__eq__(42) is NotImplemented

    def test_comparison(self):
        two = Card('2', 'spades')
        ten = Card('10', 'hearts')
        ace = Card('A', 'diamonds')

        assert two < ten
        assert ten < ace
        assert ace > two
        assert two <= two
        assert ace >= ten

    def test_comparison_non_card(self):
        card = Card('A', 'spades')
        assert card.__lt__(42) is NotImplemented
        assert card.__le__(42) is NotImplemented
        assert card.__gt__(42) is NotImplemented
        assert card.__ge__(42) is NotImplemented

    def test_hash(self):
        # Same cards should have same hash, can be used in sets/dicts
        card1 = Card('A', 'spades')
        card2 = Card('A', 'spades')
        assert hash(card1) == hash(card2)
        assert len({card1, card2}) == 1

    def test_to_int_range(self):
        # All 52 cards should map to unique ints 0-51
        all_ints = set()
        for suit in SUITS:
            for rank in RANKS:
                card = Card(rank, suit)
                val = card.to_int()
                assert 0 <= val <= 51
                all_ints.add(val)
        assert len(all_ints) == 52

    def test_to_int_specific(self):
        assert Card('2', 'spades').to_int() == 0
        assert Card('A', 'diamonds').to_int() == 51


# ---- Deck Tests ----

class TestDeck:

    def test_deck_size(self):
        deck = Deck(shuffle=False)
        assert len(deck) == 52

    def test_deck_unique_cards(self):
        deck = Deck(shuffle=False)
        cards = deck.deal_many(52)
        assert len(set(cards)) == 52

    def test_deck_no_shuffle(self):
        # Two unshuffled decks should have same order
        deck1 = Deck(shuffle=False)
        deck2 = Deck(shuffle=False)
        cards1 = deck1.deal_many(52)
        cards2 = deck2.deal_many(52)
        assert cards1 == cards2

    def test_deck_shuffle(self):
        # Shuffled deck should (almost certainly) differ from unshuffled
        deck_ordered = Deck(shuffle=False)
        deck_shuffled = Deck(shuffle=True)
        ordered = deck_ordered.deal_many(52)
        shuffled = deck_shuffled.deal_many(52)
        assert ordered != shuffled

    def test_deal_removes_card(self):
        deck = Deck(shuffle=False)
        deck.deal()
        assert len(deck) == 51

    def test_deal_many(self):
        deck = Deck(shuffle=False)
        cards = deck.deal_many(5)
        assert len(cards) == 5
        assert len(deck) == 47

    def test_deal_empty_deck(self):
        deck = Deck(shuffle=False)
        deck.deal_many(52)
        with pytest.raises(ValueError):
            deck.deal()

    def test_deal_many_too_many(self):
        deck = Deck(shuffle=False)
        with pytest.raises(ValueError):
            deck.deal_many(53)

    def test_reset(self):
        deck = Deck()
        deck.deal_many(10)
        assert len(deck) == 42
        deck.reset()
        assert len(deck) == 52

    def test_repr(self):
        deck = Deck()
        assert repr(deck) == 'Deck (52 cards remaining)'
        deck.deal()
        assert repr(deck) == 'Deck (51 cards remaining)'
