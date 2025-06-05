import discord
import time
from collections import defaultdict
from enum import Enum
from abc import ABC
from typing import Dict, List, Optional, Any, Callable
from .events import Event, EventType


class RoleTypes(Enum):
    EVERYONE = "@everyone"
    NEW_MEMBER = "New Player"
    ACTIVE_MEMBER = "Active Player"
    ELIMINATED = "Eliminated"

ROLES_TYPE_NAMES = [role.value for role in RoleTypes.__members__.values()]


class PlayerState(Enum):
    DEFAULT = "Default"
    NEW_MEMBER = "New Member"
    ACTIVE_MEMBER = "Active Member"
    ELIMINATED = "Eliminated"



class RoleState(ABC):
    """Base abstract class for role states in an event-driven state machine."""

    def __init__(self, name: PlayerState, role_ids: Dict[RoleTypes, int] = None):
        self.name = name
        self.roles: List[int] = [role_ids[RoleTypes.EVERYONE]]  # List of role IDs associated with this state
        self.transitions: Dict[EventType, List[Callable[[Event], Optional[str]], PlayerState]] = defaultdict(list)

    def add_transition(self, event_type: EventType, handler: Callable[[Event], bool], next_state: Optional[PlayerState]=None) -> None:
        """
        Add a transition handler for a specific event type.

        Args:
            event_type: The type of event that triggers this transition
            handler: Function that takes an Event and returns the next state name or None if no transition
            next_state: The state to transition to if the handler returns True, None if the transition handler supplies
            the target_state in the event data
        """
        if next_state and not isinstance(next_state, PlayerState):
            raise ValueError("next_state must be of PlayerState type")
        self.transitions[event_type].append((handler, next_state))

    def handle_event(self, event: Event) -> Optional[PlayerState]:
        """
        Handle an event and determine if a transition should occur.

        Args:
            event: The event to handle

        Returns:
            Optional[str]: The name of the next state if a transition should occur, None otherwise
        """
        # Process all handlers for this event type

        for handler, next_state in self.transitions[event.type]:
            if handler(event):
                # For manual updates, use the target_state from the event data if available
                if event.type == EventType.MANUAL_UPDATE and "target_state" in event.data:
                    # Find the PlayerState enum value that matches the target_state string
                    try:
                        return PlayerState(event.data["target_state"])
                    except ValueError:
                        print(f"Invalid target_state {event.data['target_state']} for manual update")
                        # If the target_state is not a valid PlayerState, use the configured next_state
                        return None
                return next_state
        return None

    def get_ctx(self, member_id: int) -> Dict[str, any]:
        return {}

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
        for role_id in self.roles[1:]:  # offset is to make sure we dont try to remove the default role
            role = member.guild.get_role(role_id)
            if role and role in member.roles:
                try:
                    await member.remove_roles(role, reason=f"Exiting {self.name} state")
                    print(f"Removed role {role.name} from {member.display_name}")
                except discord.Forbidden:
                    print(f"Missing permissions to remove role {role.name} from {member.display_name}")
                except discord.HTTPException as e:
                    print(f"Failed to remove role {role.name} from {member.display_name}: {e}")


class _ElapsedTimeState(RoleState):
    """State for tracking elapsed time since state was obtained.

    Implements a dict for mapping members to start times. Handles cleanup and context generation."""

    def __init__(self, player_state: PlayerState, role_ids: Dict[RoleTypes, int]):
        super().__init__(player_state, role_ids)
        self.start_times = {}  # Maps member IDs to elimination timestamps

    def get_ctx(self, member_id: int) -> Dict[str, any]:
        return {'start_time': self.start_times[member_id]}

    async def exit(self, member: discord.Member) -> None:
        """
        Make sure to remove member's start timestamp and removes the role.
        Args:
            member: The Discord member to remove roles from
        """
        self.start_times.pop(member.id)
        await super().exit(member)

    async def enter(self, member: discord.Member) -> None:
        """
        Actions to perform when entering this state.
        Records the time when member transitioned to state and adds the role.

        Args:
            member: The Discord member to apply roles to
        """
        # Record the time player transitioned to this state
        self.start_times[member.id] = time.time()
        print(f"Recorded start_time of state {self.name.value} for {member.display_name}")

        # Call the parent class's enter method to handle role assignment
        await super().enter(member)


class DefaultState(RoleState):
    """Represents the default role of 'everyone'"""

    def __init__(self, role_ids: Dict[RoleTypes, int]):
        super().__init__(PlayerState.DEFAULT, role_ids)


class NewMemberState(_ElapsedTimeState):
    """State for new members who have just joined the server."""

    def __init__(self, role_ids: Dict[RoleTypes, int]):
        super().__init__(PlayerState.NEW_MEMBER, role_ids)
        self.roles.append(role_ids[RoleTypes.NEW_MEMBER])


class ActiveMemberState(RoleState):
    """State for members who are active in the server."""

    def __init__(self, role_ids: Dict[RoleTypes, int]):
        super().__init__(PlayerState.ACTIVE_MEMBER, role_ids)
        self.roles.append(role_ids[RoleTypes.ACTIVE_MEMBER])


class EliminatedState(_ElapsedTimeState):
    """State for members who have been eliminated in the game."""

    def __init__(self, role_ids: Dict[RoleTypes, int]):
        super().__init__(PlayerState.ELIMINATED, role_ids)
        self.roles.append(role_ids[RoleTypes.ELIMINATED])
