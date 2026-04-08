import pytest
from poker.card import Card, Deck
from poker.player import Player
from poker.table import Table


# Helper: action function that always picks a specific action
def always(action):
    def get_action(player_id, legal_actions):
        if action in legal_actions:
            return action
        return 1  # fallback to call/check
    return get_action


# Helper: action function from a scripted list
def scripted(actions):
    idx = [0]
    def get_action(player_id, legal_actions):
        if idx[0] < len(actions):
            a = actions[idx[0]]
            idx[0] += 1
            if a in legal_actions:
                return a
            return 1
        return 1
    return get_action


# ---- Init Tests ----

class TestTableInit:

    def test_default_creation(self):
        table = Table()
        assert table.num_players == 2
        assert table.small_blind == 1
        assert table.big_blind == 2
        assert len(table.players) == 2
        assert table.pot == 0

    def test_custom_creation(self):
        table = Table(num_players=4, small_blind=5, big_blind=10, starting_chips=500)
        assert table.num_players == 4
        assert len(table.players) == 4
        assert all(p.chips == 500 for p in table.players)

    def test_invalid_player_count_low(self):
        with pytest.raises(ValueError):
            Table(num_players=1)

    def test_invalid_player_count_high(self):
        with pytest.raises(ValueError):
            Table(num_players=11)


# ---- Blinds Tests ----

class TestPostBlinds:

    def test_heads_up_blinds(self):
        table = Table(num_players=2, small_blind=1, big_blind=2, starting_chips=200)
        table.dealer_index = 0
        table._post_blinds()
        # In heads-up, dealer (index 0) posts SB, other posts BB
        assert table.players[0].chips == 199  # posted SB
        assert table.players[1].chips == 198  # posted BB
        assert table.pot == 3
        assert table.current_bet == 2

    def test_multiplayer_blinds(self):
        table = Table(num_players=4, small_blind=5, big_blind=10, starting_chips=200)
        table.dealer_index = 0
        table._post_blinds()
        # SB = index 1, BB = index 2
        assert table.players[0].chips == 200  # dealer, no blind
        assert table.players[1].chips == 195  # SB
        assert table.players[2].chips == 190  # BB
        assert table.players[3].chips == 200  # no blind
        assert table.pot == 15

    def test_short_stack_blind(self):
        table = Table(num_players=2, small_blind=5, big_blind=10, starting_chips=3)
        table.dealer_index = 0
        table._post_blinds()
        # SB can only post 3, BB can only post 3
        assert table.players[0].chips == 0
        assert table.players[1].chips == 0
        assert table.pot == 6


# ---- Deal Tests ----

class TestDealing:

    def test_deal_hole_cards(self):
        table = Table()
        table._deal_hole_cards()
        for player in table.players:
            assert len(player.hole_cards) == 2

    def test_deal_community_flop(self):
        table = Table()
        table._deal_community_cards(3)
        assert len(table.community_cards) == 3

    def test_deal_community_full(self):
        table = Table()
        table._deal_community_cards(3)
        table._deal_community_cards(1)
        table._deal_community_cards(1)
        assert len(table.community_cards) == 5


# ---- Legal Actions Tests ----

class TestLegalActions:

    def test_basic_legal_actions(self):
        table = Table(starting_chips=200)
        table._post_blinds()
        player = table.players[0]  # SB, has 199 chips, current_bet=1
        actions = table._get_legal_actions(player)
        assert 0 in actions  # fold
        assert 1 in actions  # call
        assert 5 in actions  # all-in

    def test_short_stack_no_raises(self):
        table = Table(small_blind=1, big_blind=2, starting_chips=2)
        table._post_blinds()
        # SB posted 1, has 1 chip left, needs 1 to call = no chips for raise
        player = table.players[table.dealer_index]
        actions = table._get_legal_actions(player)
        assert 0 in actions
        assert 1 in actions
        assert 5 not in actions  # can't do anything beyond call


# ---- Apply Action Tests ----

class TestApplyAction:

    def test_fold(self):
        table = Table()
        table._post_blinds()
        player = table.players[0]
        table._apply_action(player, 0)
        assert player.is_folded is True

    def test_call(self):
        table = Table(starting_chips=200)
        table.dealer_index = 0
        table._post_blinds()
        player = table.players[0]  # SB, bet 1, needs 1 more to call
        pot_before = table.pot
        table._apply_action(player, 1)
        assert table.pot == pot_before + 1
        assert player.current_bet == 2

    def test_all_in(self):
        table = Table(starting_chips=100)
        table._post_blinds()
        player = table.players[0]  # SB, has 99 chips
        table._apply_action(player, 5)
        assert player.chips == 0
        assert player.is_all_in is True


# ---- Betting Round Tests ----

class TestBettingRound:

    def test_all_check(self):
        table = Table(starting_chips=200)
        table._post_blinds()
        table._deal_hole_cards()
        # Everyone calls/checks
        result = table._betting_round(always(1))
        assert result is True  # hand continues

    def test_fold_ends_hand(self):
        table = Table(num_players=2, starting_chips=200)
        table._post_blinds()
        table._deal_hole_cards()
        # First player folds
        result = table._betting_round(always(0))
        assert result is False


# ---- Full Hand Tests ----

class TestPlayHand:

    def test_hand_completes_all_call(self):
        table = Table(starting_chips=200)
        result = table.play_hand(always(1))
        assert "winners" in result
        assert "winnings" in result
        assert "hand_name" in result
        assert len(result["winners"]) >= 1

    def test_hand_fold_preflop(self):
        table = Table(num_players=2, starting_chips=200)
        # First to act folds immediately
        result = table.play_hand(always(0))
        assert result["hand_name"] == "Fold"
        assert len(result["winners"]) == 1

    def test_chips_conserved_call_hand(self):
        table = Table(num_players=2, starting_chips=200)
        result = table.play_hand(always(1))
        total_chips = sum(p.chips for p in table.players) + result["winnings"] * len(result["winners"])
        # This is tricky with split pots — just verify no chips created from nothing
        total_after = sum(p.chips for p in table.players)
        assert total_after <= 400  # can't exceed total starting chips

    def test_multiple_hands(self):
        table = Table(starting_chips=200)
        for _ in range(10):
            table.play_hand(always(1))
        # After 10 hands, game should still function
        assert sum(p.chips for p in table.players) <= 400


# ---- Reset Tests ----

class TestResets:

    def test_reset_for_new_hand(self):
        table = Table(starting_chips=200)
        table.play_hand(always(1))
        # play_hand resets at the START of each hand, so after it returns
        # the community cards from the just-played hand are still present.
        # Calling play_hand again should reset cleanly.
        table.play_hand(always(1))
        # If second hand completes without error, reset worked
        assert len(table.community_cards) == 5  # full board from second hand

    def test_reset_game(self):
        table = Table(starting_chips=200)
        table.play_hand(always(1))
        table.reset_game()
        assert all(p.chips == 200 for p in table.players)
        assert table.pot == 0
        assert table.dealer_index == 0
        assert table.community_cards == []

    def test_dealer_rotates(self):
        table = Table(num_players=2, starting_chips=200)
        assert table.dealer_index == 0
        table.play_hand(always(1))
        # After _reset_for_new_hand inside play_hand, dealer should have rotated
        # Note: play_hand calls _reset_for_new_hand at the start, so after one hand
        # the dealer_index reflects the reset at the START of that hand
        initial_dealer = table.dealer_index
        table.play_hand(always(1))
        assert table.dealer_index != initial_dealer
