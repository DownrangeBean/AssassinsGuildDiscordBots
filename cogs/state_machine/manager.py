import discord
from typing import Dict, Optional
from .states import RoleState, RoleTypes, ROLES_TYPE_NAMES as SUPPORTED_ROLES, DefaultState, PlayerState
from .events import Event, EventType


class StateNotFoundError(BaseException):
    """Exception raised when a state is not found for a member."""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message


class RoleManager:
    """Manages role states and transitions for members in an event-driven manner."""

    def __init__(self):
        self.states: Dict[PlayerState, RoleState] = {}
        self.member_states: Dict[int, str] = {}  # Maps member IDs to current state names

    def add_state(self, state: RoleState) -> None:
        """Add a state to the manager."""
        self.states[state.name] = state

    def get_member_state(self, member_id: int) -> Optional[RoleState]:
        """Get the current state of a member."""
        state_name = self.member_states.get(member_id)
        if state_name:
            return self.states.get(state_name)
        return None

    def find_best_matching_state(self, member_roles: list[discord.Role]) -> RoleState:

        """Find the state that most closely represents the roles that the member has currently."""
        min_difference = None
        best_state = None
        member_roles = set(role.id for role in member_roles)

        for state in self.states.values():
            if not member_roles.issuperset(state.roles):
                # If the member doesn't have all the roles that the state requires, skip it.
                continue

            difference = member_roles.difference(state.roles)
            if len(difference) == 0:
                # If the member has all the roles that the state requires, return it.
                best_state = state
                min_difference = None
                break
            if not min_difference or len(difference) < len(min_difference):
                # if this state represents more of the roles that the member has, update the best state.
                min_difference = difference
                best_state = state

        if best_state:
            print(f"matched {best_state.name} as best fitting state with unrepresented roles {min_difference}")
        return best_state


    async def set_member_state(self, member: discord.Member, state: PlayerState) -> None:
        """Set a member to a new state."""
        if state not in self.states:
            raise ValueError(f"State {state.value} does not exist")

        # Exit current state if exists
        current_state = self.get_member_state(member.id)
        if current_state:
            await current_state.exit(member)

        # Enter new state
        new_state = self.states[state]
        await new_state.enter(member)

        # Update member state
        self.member_states[member.id] = state
        print(f"Member {member.display_name} transitioned to {state} state")

    async def process_event(self, event: Event) -> None:
        """
        Process an event and trigger state transitions if needed.

        Args:
            event: The event to process
        """
        if event is None:
            return
        # Get current state
        current_state_name = self.member_states.get(event.member.id)

        # If no current state try to resolve the state using event context or member context
        if not current_state_name:
            await self._resolve_unknown_state(event)
            current_state_name = self.member_states.get(event.member.id)

        # Get current state object
        current_state = self.states[current_state_name]

        # Handle event and check for transition
        next_state = current_state.handle_event(event)

        # If transition is needed, change state
        if next_state and next_state in self.states:
            await self.set_member_state(event.member, next_state)

    async def _resolve_unknown_state(self, event: Event) -> RoleState:
        """Attempts to find a state for the current member, given known context"""
        print(f"State not known for member {event.member.display_name} attempting to resolve...")
        state = None
        if self.states and event.type == EventType.MEMBER_JOIN:
            state = self.states.get("@everyone")
            print(f"Member {event.member.display_name} is a new member, using default state")
            await self.set_member_state(event.member, state.name)
            return state

        # use members current roles to match a state.
        roles = [role for role in event.member.roles if role.name in SUPPORTED_ROLES]
        if not len(roles):
            state = self.states.get("@everyone")
            print(f"No roles found for member {event.member.display_name}, using default state")
        else:
            state = self.find_best_matching_state(roles)

        if state is None:
            raise StateNotFoundError(f"No state found for member {event.member.display_name}")

        await self.set_member_state(event.member, state.name)
        return state