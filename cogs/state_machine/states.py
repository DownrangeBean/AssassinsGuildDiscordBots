from collections import defaultdict
import time

import discord
from abc import ABC
from typing import Dict, List, Optional, Any, Callable
from .events import Event, EventType


class RoleState(ABC):
    """Base abstract class for role states in an event-driven state machine."""

    def __init__(self, name: str):
        self.name = name
        self.roles: List[int] = []  # List of role IDs associated with this state
        self.transitions: Dict[EventType, List[Callable[[Event], Optional[str]]]] = defaultdict(list)

    def add_transition(self, event_type: EventType, handler: Callable[[Event], Optional[str]]) -> None:
        """
        Add a transition handler for a specific event type.

        Args:
            event_type: The type of event that triggers this transition
            handler: Function that takes an Event and returns the next state name or None if no transition
        """
        self.transitions[event_type].append(handler)

    def handle_event(self, event: Event) -> Optional[str]:
        """
        Handle an event and determine if a transition should occur.

        Args:
            event: The event to handle

        Returns:
            Optional[str]: The name of the next state if a transition should occur, None otherwise
        """
        # Process all handlers for this event type
        for handler in self.transitions[event.type]:
            next_state = handler(event)
            if next_state:
                return next_state
        return None

    async def enter(self, member: discord.Member) -> None:
        """
        Actions to perform when entering this state.

        Args:
            member: The Discord member to apply roles to
        """
        for role_id in self.roles:
            role = member.guild.get_role(role_id)
            if role and role not in member.roles:
                try:
                    await member.add_roles(role, reason=f"Entering {self.name} state")
                    print(f"Added role {role.name} to {member.display_name}")
                except discord.Forbidden:
                    print(f"Missing permissions to add role {role.name} to {member.display_name}")
                except discord.HTTPException as e:
                    print(f"Failed to add role {role.name} to {member.display_name}: {e}")

    async def exit(self, member: discord.Member) -> None:
        """
        Actions to perform when exiting this state.

        Args:
            member: The Discord member to remove roles from
        """
        for role_id in self.roles:
            role = member.guild.get_role(role_id)
            if role and role in member.roles:
                try:
                    await member.remove_roles(role, reason=f"Exiting {self.name} state")
                    print(f"Removed role {role.name} from {member.display_name}")
                except discord.Forbidden:
                    print(f"Missing permissions to remove role {role.name} from {member.display_name}")
                except discord.HTTPException as e:
                    print(f"Failed to remove role {role.name} from {member.display_name}: {e}")


class NewMemberState(RoleState):
    """State for new members who have just joined the server."""

    def __init__(self, new_member_role_id: int):
        super().__init__("New Member")
        self.roles = [new_member_role_id]


class ActiveMemberState(RoleState):
    """State for members who are active in the server."""

    def __init__(self, active_member_role_id: int):
        super().__init__("Active Member")
        self.roles = [active_member_role_id]


class EliminatedState(RoleState):
    """State for members who have been eliminated in the game."""

    def __init__(self, eliminated_role_id: int):
        super().__init__("Eliminated")
        self.roles = [eliminated_role_id]
        self.elimination_times = {}  # Maps member IDs to elimination timestamps

    async def enter(self, member: discord.Member) -> None:
        """
        Actions to perform when entering this state.
        Records the elimination time and adds the role.

        Args:
            member: The Discord member to apply roles to
        """
        # Record the elimination time
        self.elimination_times[member.id] = time.time()
        print(f"Recorded elimination time for {member.display_name}")

        # Call the parent class's enter method to handle role assignment
        await super().enter(member)
