"""
DFA Builder — Converts regex patterns into Deterministic Finite Automata.

Pipeline:
  1. Regex string → parsed AST (recursive descent parser)
  2. AST → NFA (Thompson's construction)
  3. NFA → DFA (subset construction / powerset algorithm)

Output: JSON-serializable DFA with states, alphabet, transitions,
start_state, and accept_states.

DESIGN NOTE: Character classes like [0-9०-९] are treated as ATOMIC
symbols in the DFA alphabet. They are NOT expanded to individual
characters, keeping the DFA compact and readable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ======================================================================
# AST Nodes
# ======================================================================

@dataclass
class ASTNode:
    pass

@dataclass
class LiteralNode(ASTNode):
    char: str

@dataclass
class CharClassNode(ASTNode):
    """Treated as an atomic symbol identified by its label."""
    label: str  # e.g., "[0-9०-९]"

@dataclass
class ConcatNode(ASTNode):
    left: ASTNode
    right: ASTNode

@dataclass
class AlternationNode(ASTNode):
    left: ASTNode
    right: ASTNode

@dataclass
class StarNode(ASTNode):
    child: ASTNode

@dataclass
class PlusNode(ASTNode):
    child: ASTNode

@dataclass
class OptionalNode(ASTNode):
    child: ASTNode

@dataclass
class GroupNode(ASTNode):
    child: ASTNode
    group_id: int = 0


# ======================================================================
# NFA representation
# ======================================================================

@dataclass
class NFAState:
    id: int
    transitions: dict[str, list[int]] = field(default_factory=dict)
    epsilon_transitions: list[int] = field(default_factory=list)

    def add_transition(self, symbol: str, target: int):
        self.transitions.setdefault(symbol, []).append(target)

    def add_epsilon(self, target: int):
        self.epsilon_transitions.append(target)


@dataclass
class NFA:
    states: dict[int, NFAState]
    start: int
    accept: int
    alphabet: set[str]


# ======================================================================
# Regex Parser
# ======================================================================

class RegexParser:
    """
    Parses a regex string into an AST.

    Character classes [abc], [0-9], etc. are kept as atomic labels.
    No character expansion — keeps the DFA compact.
    """

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.pos = 0
        self.group_counter = 0

    def parse(self) -> ASTNode:
        node = self._parse_alternation()
        return node

    def _peek(self) -> str | None:
        return self.pattern[self.pos] if self.pos < len(self.pattern) else None

    def _advance(self) -> str:
        ch = self.pattern[self.pos]
        self.pos += 1
        return ch

    def _parse_alternation(self) -> ASTNode:
        left = self._parse_concat()
        while self._peek() == "|":
            self._advance()
            right = self._parse_concat()
            left = AlternationNode(left, right)
        return left

    def _parse_concat(self) -> ASTNode:
        nodes: list[ASTNode] = []
        while self._peek() is not None and self._peek() not in (")", "|"):
            nodes.append(self._parse_quantifier())
        if not nodes:
            return LiteralNode("")
        result = nodes[0]
        for n in nodes[1:]:
            result = ConcatNode(result, n)
        return result

    def _parse_quantifier(self) -> ASTNode:
        node = self._parse_atom()
        p = self._peek()
        if p == "*":
            self._advance()
            return StarNode(node)
        elif p == "+":
            self._advance()
            return PlusNode(node)
        elif p == "?":
            self._advance()
            return OptionalNode(node)
        elif p == "{":
            return self._parse_repetition(node)
        return node

    def _parse_repetition(self, node: ASTNode) -> ASTNode:
        self._advance()  # {
        min_r = self._parse_int()
        max_r = min_r
        if self._peek() == ",":
            self._advance()
            max_r = self._parse_int() if self._peek() != "}" else min_r + 3
        if self._peek() == "}":
            self._advance()

        result = None
        for _ in range(min_r):
            result = ConcatNode(result, node) if result else node
        for _ in range(max_r - min_r):
            opt = OptionalNode(node)
            result = ConcatNode(result, opt) if result else opt
        return result if result else LiteralNode("")

    def _parse_int(self) -> int:
        digits = []
        while self._peek() and self._peek().isdigit():
            digits.append(self._advance())
        return int("".join(digits)) if digits else 0

    def _parse_atom(self) -> ASTNode:
        ch = self._peek()
        if ch == "(":
            return self._parse_group()
        elif ch == "[":
            return self._parse_char_class()
        elif ch == "\\":
            return self._parse_escape()
        elif ch == ".":
            self._advance()
            return CharClassNode(".")
        elif ch is not None and ch not in (")", "|", "*", "+", "?", "{", "}"):
            self._advance()
            return LiteralNode(ch)
        return LiteralNode("")

    def _parse_group(self) -> ASTNode:
        self._advance()  # (
        non_capturing = False
        if self._peek() == "?" and self.pos + 1 < len(self.pattern) and self.pattern[self.pos + 1] == ":":
            self._advance()  # ?
            self._advance()  # :
            non_capturing = True
        child = self._parse_alternation()
        if self._peek() == ")":
            self._advance()
        if non_capturing:
            return child
        self.group_counter += 1
        return GroupNode(child, self.group_counter)

    def _parse_char_class(self) -> ASTNode:
        """Read the entire [...] as an atomic label string."""
        start = self.pos
        self._advance()  # [
        # Read until matching ]
        depth = 1
        while self.pos < len(self.pattern) and depth > 0:
            ch = self.pattern[self.pos]
            if ch == "\\":
                self.pos += 2  # skip escaped char
                continue
            if ch == "]":
                depth -= 1
                if depth == 0:
                    self.pos += 1
                    break
            self.pos += 1

        label = self.pattern[start:self.pos]
        return CharClassNode(label)

    def _parse_escape(self) -> ASTNode:
        self._advance()  # backslash
        if self._peek() is None:
            return LiteralNode("\\")
        ch = self._advance()
        if ch == "s":
            return CharClassNode("\\s")
        elif ch == "d":
            return CharClassNode("\\d")
        elif ch == "S":
            return CharClassNode("\\S")
        elif ch == "D":
            return CharClassNode("\\D")
        elif ch == "w":
            return CharClassNode("\\w")
        else:
            return LiteralNode(ch)


# ======================================================================
# Thompson's Construction (AST → NFA)
# ======================================================================

class ThompsonBuilder:
    def __init__(self):
        self.state_counter = 0
        self.alphabet: set[str] = set()

    def _new_state(self) -> NFAState:
        s = NFAState(id=self.state_counter)
        self.state_counter += 1
        return s

    def build(self, ast: ASTNode) -> NFA:
        states: dict[int, NFAState] = {}
        start_id, accept_id = self._build_node(ast, states)
        return NFA(states=states, start=start_id, accept=accept_id, alphabet=self.alphabet)

    def _build_node(self, node: ASTNode, states: dict) -> tuple[int, int]:
        if isinstance(node, LiteralNode):
            return self._build_literal(node, states)
        elif isinstance(node, CharClassNode):
            return self._build_symbol(node.label, states)
        elif isinstance(node, ConcatNode):
            return self._build_concat(node, states)
        elif isinstance(node, AlternationNode):
            return self._build_alt(node, states)
        elif isinstance(node, StarNode):
            return self._build_star(node, states)
        elif isinstance(node, PlusNode):
            return self._build_plus(node, states)
        elif isinstance(node, OptionalNode):
            return self._build_optional(node, states)
        elif isinstance(node, GroupNode):
            return self._build_node(node.child, states)
        else:
            return self._build_epsilon(states)

    def _build_epsilon(self, states: dict) -> tuple[int, int]:
        s, a = self._new_state(), self._new_state()
        s.add_epsilon(a.id)
        states[s.id] = s
        states[a.id] = a
        return s.id, a.id

    def _build_literal(self, node: LiteralNode, states: dict) -> tuple[int, int]:
        s, a = self._new_state(), self._new_state()
        if node.char:
            self.alphabet.add(node.char)
            s.add_transition(node.char, a.id)
        else:
            s.add_epsilon(a.id)
        states[s.id] = s
        states[a.id] = a
        return s.id, a.id

    def _build_symbol(self, symbol: str, states: dict) -> tuple[int, int]:
        """Build an NFA fragment for an atomic symbol (char class label)."""
        s, a = self._new_state(), self._new_state()
        self.alphabet.add(symbol)
        s.add_transition(symbol, a.id)
        states[s.id] = s
        states[a.id] = a
        return s.id, a.id

    def _build_concat(self, node: ConcatNode, states: dict) -> tuple[int, int]:
        s1, a1 = self._build_node(node.left, states)
        s2, a2 = self._build_node(node.right, states)
        states[a1].add_epsilon(s2)
        return s1, a2

    def _build_alt(self, node: AlternationNode, states: dict) -> tuple[int, int]:
        s, a = self._new_state(), self._new_state()
        s1, a1 = self._build_node(node.left, states)
        s2, a2 = self._build_node(node.right, states)
        s.add_epsilon(s1)
        s.add_epsilon(s2)
        states[a1].add_epsilon(a.id)
        states[a2].add_epsilon(a.id)
        states[s.id] = s
        states[a.id] = a
        return s.id, a.id

    def _build_star(self, node: StarNode, states: dict) -> tuple[int, int]:
        s, a = self._new_state(), self._new_state()
        cs, ca = self._build_node(node.child, states)
        s.add_epsilon(cs)
        s.add_epsilon(a.id)
        states[ca].add_epsilon(cs)
        states[ca].add_epsilon(a.id)
        states[s.id] = s
        states[a.id] = a
        return s.id, a.id

    def _build_plus(self, node: PlusNode, states: dict) -> tuple[int, int]:
        s, a = self._new_state(), self._new_state()
        cs, ca = self._build_node(node.child, states)
        s.add_epsilon(cs)
        states[ca].add_epsilon(cs)
        states[ca].add_epsilon(a.id)
        states[s.id] = s
        states[a.id] = a
        return s.id, a.id

    def _build_optional(self, node: OptionalNode, states: dict) -> tuple[int, int]:
        s, a = self._new_state(), self._new_state()
        cs, ca = self._build_node(node.child, states)
        s.add_epsilon(cs)
        s.add_epsilon(a.id)
        states[ca].add_epsilon(a.id)
        states[s.id] = s
        states[a.id] = a
        return s.id, a.id


# ======================================================================
# Subset Construction (NFA → DFA)
# ======================================================================

class SubsetConstructor:
    def construct(self, nfa: NFA) -> dict[str, Any]:
        start_closure = self._epsilon_closure(nfa, frozenset({nfa.start}))
        start_key = self._state_key(start_closure)

        dfa_states: dict[str, frozenset[int]] = {start_key: start_closure}
        dfa_transitions: dict[str, dict[str, str]] = {}
        worklist = [start_key]
        processed: set[str] = set()

        while worklist:
            current_key = worklist.pop()
            if current_key in processed:
                continue
            processed.add(current_key)
            current_nfa_states = dfa_states[current_key]
            dfa_transitions[current_key] = {}

            for symbol in nfa.alphabet:
                move_states: set[int] = set()
                for sid in current_nfa_states:
                    s = nfa.states.get(sid)
                    if s and symbol in s.transitions:
                        move_states.update(s.transitions[symbol])
                if not move_states:
                    continue
                closure = self._epsilon_closure(nfa, frozenset(move_states))
                next_key = self._state_key(closure)
                if next_key not in dfa_states:
                    dfa_states[next_key] = closure
                    worklist.append(next_key)
                dfa_transitions[current_key][symbol] = next_key

        # Accept states
        accept_states = [k for k, v in dfa_states.items() if nfa.accept in v]

        # Rename to human-friendly names
        sorted_keys = sorted(dfa_states.keys())
        name_map = {k: f"q{i}" for i, k in enumerate(sorted_keys)}

        renamed_transitions: dict[str, dict[str, str]] = {}
        for src, edges in dfa_transitions.items():
            renamed_transitions[name_map[src]] = {
                sym: name_map[dst] for sym, dst in edges.items()
            }

        return {
            "states": [name_map[k] for k in sorted_keys],
            "alphabet": sorted(nfa.alphabet),
            "transitions": renamed_transitions,
            "start_state": name_map[start_key],
            "accept_states": [name_map[k] for k in accept_states],
            "state_count": len(dfa_states),
        }

    def _epsilon_closure(self, nfa: NFA, state_ids: frozenset[int]) -> frozenset[int]:
        stack = list(state_ids)
        closure = set(state_ids)
        while stack:
            sid = stack.pop()
            s = nfa.states.get(sid)
            if not s:
                continue
            for t in s.epsilon_transitions:
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
        return frozenset(closure)

    @staticmethod
    def _state_key(state_set: frozenset[int]) -> str:
        return str(sorted(state_set))


# ======================================================================
# DFA Builder (public interface)
# ======================================================================

class DfaBuilder:
    """
    Public API for building DFA from regex patterns.

    Character classes are treated as atomic alphabet symbols,
    producing compact, readable DFAs.
    """

    def build(self, regex_pattern: str) -> dict[str, Any]:
        parser = RegexParser(regex_pattern)
        ast = parser.parse()

        builder = ThompsonBuilder()
        nfa = builder.build(ast)

        constructor = SubsetConstructor()
        dfa = constructor.construct(nfa)
        dfa["regex_source"] = regex_pattern
        return dfa

    def simulate(self, dfa: dict[str, Any], input_string: str) -> dict[str, Any]:
        """
        Simulate DFA on input. For each character, tries to match
        against DFA alphabet symbols (exact chars or character class labels).
        """
        transitions = dfa.get("transitions", {})
        current = dfa.get("start_state", "q0")
        accept_states = set(dfa.get("accept_states", []))
        steps = []

        for char in input_string:
            state_trans = transitions.get(current, {})
            next_state = None

            # Exact match first
            if char in state_trans:
                next_state = state_trans[char]
            else:
                # Try character class labels
                for symbol, target in state_trans.items():
                    if self._char_matches(char, symbol):
                        next_state = target
                        break

            if next_state is None:
                steps.append({"state": current, "input": char, "next_state": None, "status": "rejected"})
                return {
                    "accepted": False,
                    "steps": steps,
                    "final_state": current,
                    "rejection_point": len(steps) - 1,
                }

            steps.append({"state": current, "input": char, "next_state": next_state, "status": "ok"})
            current = next_state

        return {
            "accepted": current in accept_states,
            "steps": steps,
            "final_state": current,
        }

    @staticmethod
    def _char_matches(char: str, symbol: str) -> bool:
        if symbol == char:
            return True
        if symbol == ".":
            return True
        if symbol == "\\s":
            return char in (" ", "\t", "\n", "\r")
        if symbol == "\\d":
            return char.isdigit()
        if symbol == "\\w":
            return char.isalnum() or char == "_"
        # Character class label like [0-9०-९]
        if symbol.startswith("[") and symbol.endswith("]"):
            try:
                return bool(re.match(symbol, char, re.UNICODE))
            except re.error:
                return False
        return False
