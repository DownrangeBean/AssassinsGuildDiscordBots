import discord
from typing import Dict, Optional
from .states import RoleState
from .events import Event, EventType


class RoleManager:
    """Manages role states and transitions for members in an event-driven manner."""

    def __init__(self):
        self.states: Dict[str, RoleState] = {}
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

    async def set_member_state(self, member: discord.Member, state_name: str) -> None:
        """Set a member to a new state."""
        if state_name not in self.states:
            raise ValueError(f"State {state_name} does not exist")

        # Exit current state if exists
        current_state = self.get_member_state(member.id)
        if current_state:
            await current_state.exit(member)

        # Enter new state
        new_state = self.states[state_name]
        await new_state.enter(member)

        # Update member state
        self.member_states[member.id] = state_name
        print(f"Member {member.display_name} transitioned to {state_name} state")

    async def process_event(self, event: Event) -> None:
        """
        Process an event and trigger state transitions if needed.

        Args:
            event: The event to process
        """
        # Get current state
        current_state_name = self.member_states.get(event.member.id)

        # If no current state, set default state for new members
        if not current_state_name:
            if self.states and event.type == EventType.MEMBER_JOIN:
                # Find a state named "New Member" or use the first state
                default_state = self.states.get("New Member") or next(iter(self.states.values()))
                await self.set_member_state(event.member, default_state.name)
            return

        # Get current state object
        current_state = self.states[current_state_name]

        # Handle event and check for transition
        next_state_name = current_state.handle_event(event)

        # If transition is needed, change state
        if next_state_name and next_state_name in self.states:
            await self.set_member_state(event.member, next_state_name)