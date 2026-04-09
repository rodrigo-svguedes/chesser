from dataclasses import dataclass, field
from typing import Optional
from decimal import Decimal


@dataclass
class GameData:
    white_player: str
    black_player: str 
    white_elo: int
    black_elo: int
    move_analyse_list: list = field(default_factory=list)


@dataclass
class MoveAnalyse:
    move: str
    from_square: int
    to_square: int
    promotion_to: str
    is_check: bool
    is_castling: bool
    is_en_passant: bool
    fen: Optional[str] = None
    mate_in: Optional[int] = None
    best_move: Optional[str] = None
    move_class: Optional[str] = None
    win_advantage: Optional[Decimal] = None
    evaluation: Optional[Decimal] = None
    engine_moves: list = field(default_factory=dict)
