import discord
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Any, Optional


class EventType(Enum):
    """Types of events that can trigger state transitions."""
    MESSAGE = auto()
    MEMBER_JOIN = auto()
    REACTION_ADD = auto()
    MANUAL_UPDATE = auto()
    INACTIVITY = auto()
    TIME_ELAPSED = auto()
    # Add more event types as needed


@dataclass
class Event:
    """Base class for events in the state machine."""
    type: EventType
    member: discord.Member
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}
