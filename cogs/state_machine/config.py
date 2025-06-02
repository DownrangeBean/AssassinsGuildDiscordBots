from .events import EventType
from .transitions import (
    check_message_count,
    handle_manual_update,
    check_inactivity,
    handle_reaction,
    check_hit_confirmation,
    check_elimination_time
)
from .states import NewMemberState, ActiveMemberState, EliminatedState


def configure_states(new_member_role_id: int, active_member_role_id: int, eliminated_role_id: int = None):
    """
    Configure states with their transitions.

    Args:
        new_member_role_id: Role ID for new members
        active_member_role_id: Role ID for active members
        eliminated_role_id: Role ID for eliminated players (optional)

    Returns:
        List of configured states
    """
    # Create states
    new_member_state = NewMemberState(new_member_role_id)
    active_member_state = ActiveMemberState(active_member_role_id)

    # If eliminated_role_id is not provided, use active_member_role_id as a fallback
    if eliminated_role_id is None:
        eliminated_role_id = active_member_role_id

    eliminated_state = EliminatedState(eliminated_role_id)

    # Configure transitions for new member state
    new_member_state.add_transition(EventType.MESSAGE, check_message_count)
    new_member_state.add_transition(EventType.MANUAL_UPDATE, handle_manual_update)

    # Configure transitions for active member state
    active_member_state.add_transition(EventType.INACTIVITY, check_inactivity)
    active_member_state.add_transition(EventType.MANUAL_UPDATE, handle_manual_update)
    active_member_state.add_transition(EventType.REACTION_ADD, handle_reaction)

    # Add the new transition for hit confirmation
    active_member_state.add_transition(EventType.REACTION_ADD, check_hit_confirmation)

    # Configure transitions for eliminated state
    eliminated_state.add_transition(EventType.TIME_ELAPSED, check_elimination_time)
    eliminated_state.add_transition(EventType.MANUAL_UPDATE, handle_manual_update)

    return [new_member_state, active_member_state, eliminated_state]
