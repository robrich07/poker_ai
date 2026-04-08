from typing import List, Tuple, Optional, Callable
from .card import Card, Deck
from .player import Player
from .hand_evaluator import evaluate_7_cards, get_winner, get_hand_name


class Table:
    # Manages a heads-up No-Limit Texas Hold'em game

    def __init__(self, num_players: int = 2, small_blind: int = 1, big_blind: int = 2, starting_chips: int = 200):
        if num_players < 2 or num_players > 10:
            raise ValueError(f'Number of players must be between 2 and 10, got {num_players}')

        self.small_blind = small_blind
        self.big_blind = big_blind
        self.starting_chips = starting_chips
        self.num_players = num_players

        self.players = [Player(player_id=i, chips=starting_chips) for i in range(num_players)]
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.dealer_index = 0  # dealer button position, rotates each hand
        self.current_bet = 0   # the highest bet on the table this round
        self.hand_over = False

    def play_hand(self, get_action: Callable[[int, List[int]], int]) -> dict:
        # Plays a single hand from start to finish.
        # get_action(player_id, legal_actions) -> action
        # Returns a dict with hand results (winner, pot, etc.)
        self._reset_for_new_hand()
        self._post_blinds()
        self._deal_hole_cards()

        # Pre-flop betting
        if not self._betting_round(get_action):
            return self._resolve_hand()

        # Flop
        self._deal_community_cards(3)
        if not self._betting_round(get_action):
            return self._resolve_hand()

        # Turn
        self._deal_community_cards(1)
        if not self._betting_round(get_action):
            return self._resolve_hand()

        # River
        self._deal_community_cards(1)
        if not self._betting_round(get_action):
            return self._resolve_hand()

        # Showdown
        return self._resolve_hand()

    def _post_blinds(self):
        # Posts small and big blinds, updates pot and current_bet.
        if self.num_players == 2:
            sb_idx = self.dealer_index
            bb_idx = (self.dealer_index + 1) % 2
        else:
            sb_idx = (self.dealer_index + 1) % self.num_players
            bb_idx = (self.dealer_index + 2) % self.num_players

        small_blind_player = self.players[sb_idx]
        big_blind_player = self.players[bb_idx]

        sb_actual = small_blind_player.place_bet(self.small_blind)
        bb_actual = big_blind_player.place_bet(self.big_blind)

        self.pot += sb_actual + bb_actual
        self.current_bet = max(sb_actual, bb_actual)
        

    def _deal_hole_cards(self):
        # Deals 2 cards to each player
        for player in self.players:
            player.receive_cards(self.deck.deal_many(2))

    def _deal_community_cards(self, n: int):
        # Deals n community cards (3 for flop, 1 for turn, 1 for river).
        self.community_cards.extend(self.deck.deal_many(n))

    def _betting_round(self, get_action: Callable[[int, List[int]], int]) -> bool:
        # Runs a single betting round.
        # get_action(player_id, legal_actions) -> action
        # Returns True if 2+ players remain, False if only one left.
        self._reset_bets_for_new_round()

        # Determine starting player for this round
        if self.num_players == 2:
            start_idx = self.dealer_index  # SB acts first post-flop, dealer in heads-up
            if len(self.community_cards) == 0:
                # Pre-flop: SB (dealer) acts first in heads-up
                start_idx = self.dealer_index
        else:
            if len(self.community_cards) == 0:
                # Pre-flop: player after BB acts first
                start_idx = (self.dealer_index + 3) % self.num_players
            else:
                # Post-flop: player after dealer acts first
                start_idx = (self.dealer_index + 1) % self.num_players

        # Track who still needs to act and who last raised
        players_to_act = set()
        for i in range(self.num_players):
            p = self.players[(start_idx + i) % self.num_players]
            if p.is_active:
                players_to_act.add(p.player_id)

        current_idx = start_idx

        while players_to_act:
            player = self.players[current_idx % self.num_players]

            if player.is_active and player.player_id in players_to_act:
                legal_actions = self._get_legal_actions(player)
                action = get_action(player.player_id, legal_actions)

                if action not in legal_actions:
                    action = 1  # default to call/check if invalid action

                self._apply_action(player, action)
                players_to_act.discard(player.player_id)

                # If only one non-folded player remains, hand is over
                active_count = sum(1 for p in self.players if not p.is_folded)
                if active_count == 1:
                    return False

                # A raise means everyone else needs to act again
                if action >= 2:
                    for p in self.players:
                        if p.is_active and p.player_id != player.player_id:
                            players_to_act.add(p.player_id)

            current_idx += 1

        return True

    def _get_legal_actions(self, player: Player) -> List[int]:
        # Returns a list of legal action indices for the given player.
        # Actions: 0=fold, 1=call/check, 2=raise 25%, 3=raise 50%, 4=raise 100%, 5=all-in
        actions = [0, 1]  # fold and call/check are always legal

        amount_to_call = self.current_bet - player.current_bet

        # If calling would put the player all-in, no raise options
        if player.chips <= amount_to_call:
            return actions

        chips_after_call = player.chips - amount_to_call

        # Raise amounts based on pot size after calling
        pot_after_call = self.pot + amount_to_call
        raise_amounts = {
            2: int(pot_after_call * 0.25),  # 25% pot
            3: int(pot_after_call * 0.50),  # 50% pot
            4: int(pot_after_call * 1.00),  # 100% pot
        }

        min_raise = self.big_blind  # minimum raise is one big blind

        for action, raise_amount in raise_amounts.items():
            total_needed = amount_to_call + max(raise_amount, min_raise)
            if total_needed < player.chips:
                actions.append(action)

        # All-in is always available if player has chips beyond the call
        actions.append(5)

        return actions

    def _apply_action(self, player: Player, action: int):
        # Applies the chosen action for a player, updating bets/pot/state.
        if action == 0:
            player.fold()
            return

        amount_to_call = self.current_bet - player.current_bet

        if action == 1:
            # Call / Check
            actual = player.place_bet(amount_to_call)
            self.pot += actual
            return

        # Raise actions
        pot_after_call = self.pot + amount_to_call
        min_raise = self.big_blind

        if action == 5:
            # All-in
            actual = player.place_bet(player.chips)
            self.pot += actual
            self.current_bet = max(self.current_bet, player.current_bet)
            return

        raise_pcts = {2: 0.25, 3: 0.50, 4: 1.00}
        raise_amount = max(int(pot_after_call * raise_pcts[action]), min_raise)
        total = amount_to_call + raise_amount
        actual = player.place_bet(total)
        self.pot += actual
        self.current_bet = player.current_bet

    def _resolve_hand(self) -> dict:
        # Determines the winner and distributes the pot.
        # Returns a dict with results (winner, winnings, hand name, etc.)
        active_players = [p for p in self.players if not p.is_folded]

        if len(active_players) == 1:
            winner = active_players[0]
            return {"winners": [winner.player_id], "winnings": self.pot, "hand_name": "Fold"}

        winners_idx = get_winner([p.hole_cards for p in active_players], self.community_cards)
        winners = [active_players[i].player_id for i in winners_idx]
        winnings = self.pot // len(winners)
        hand_name = get_hand_name(evaluate_7_cards(active_players[winners_idx[0]].hole_cards + self.community_cards))
        return {
            "winners": winners,
            "winnings": winnings,
            "hand_name": hand_name
        }

    def _reset_for_new_hand(self):
        # Resets table and player state for the next hand.
        self.pot = 0
        self.current_bet = 0
        self.dealer_index = (self.dealer_index + 1) % self.num_players
        self.community_cards = []
        self.deck.reset()
        for player in self.players:
            player.reset_for_new_hand()
        self.hand_over = False

    def _reset_bets_for_new_round(self):
        # Resets per-round betting state (player current_bet, table current_bet).
        self.current_bet = 0
        for player in self.players:
            player.reset_bet()

    def reset_game(self):
        # Resets the entire game to starting state (all chips, positions, etc.)
        self.players = [Player(player_id=i, chips=self.starting_chips) for i in range(self.num_players)]
        self.community_cards = []
        self.pot = 0
        self.dealer_index = 0
        self.current_bet = 0
        self.hand_over = False
        self.deck.reset()
