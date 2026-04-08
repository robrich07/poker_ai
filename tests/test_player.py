import pytest
from poker.card import Card
from poker.player import Player


class TestPlayer:

    def test_creation(self):
        player = Player(player_id=0, chips=100)
        assert player.player_id == 0
        assert player.chips == 100
        assert player.hole_cards == []
        assert player.current_bet == 0
        assert player.is_folded is False
        assert player.is_all_in is False

    def test_place_bet(self):
        player = Player(0, 100)
        actual = player.place_bet(30)
        assert actual == 30
        assert player.chips == 70
        assert player.current_bet == 30
        assert player.is_all_in is False

    def test_place_bet_all_in(self):
        player = Player(0, 50)
        actual = player.place_bet(50)
        assert actual == 50
        assert player.chips == 0
        assert player.is_all_in is True

    def test_place_bet_more_than_chips(self):
        player = Player(0, 30)
        actual = player.place_bet(100)
        assert actual == 30  # can only bet what you have
        assert player.chips == 0
        assert player.is_all_in is True

    def test_place_bet_accumulates(self):
        player = Player(0, 100)
        player.place_bet(20)
        player.place_bet(30)
        assert player.current_bet == 50
        assert player.chips == 50

    def test_fold(self):
        player = Player(0, 100)
        player.fold()
        assert player.is_folded is True

    def test_receive_cards(self):
        player = Player(0, 100)
        cards = [Card('A', 'spades'), Card('K', 'hearts')]
        player.receive_cards(cards)
        assert player.hole_cards == cards

    def test_reset_for_new_hand(self):
        player = Player(0, 100)
        player.place_bet(30)
        player.fold()
        player.receive_cards([Card('A', 'spades'), Card('K', 'hearts')])
        player.reset_for_new_hand()
        assert player.chips == 70  # chips stay
        assert player.hole_cards == []
        assert player.current_bet == 0
        assert player.is_folded is False
        assert player.is_all_in is False

    def test_reset_bet(self):
        player = Player(0, 100)
        player.place_bet(25)
        player.reset_bet()
        assert player.current_bet == 0
        assert player.chips == 75  # chips don't come back

    def test_is_active(self):
        player = Player(0, 100)
        assert player.is_active is True

        player.fold()
        assert player.is_active is False

    def test_is_active_all_in(self):
        player = Player(0, 100)
        player.place_bet(100)
        assert player.is_active is False  # all-in players can't act

    def test_repr(self):
        player = Player(0, 100)
        assert repr(player) == 'Player 0 (chips=100)'
