import discord

from .events import EventType
from .transitions import (
    check_message_count,
    handle_manual_update,
    check_inactivity,
    handle_reaction,
    check_hit_confirmation,
    check_pledge, time_elapsed
)
from .states import NewMemberState, ActiveMemberState, EliminatedState, DefaultState, RoleTypes, PlayerState

AVAILABLE_STATES: list


def get_role_ids(guild, roles: RoleTypes):
    """
    Get multiple role IDs by their names

    Args:
        guild (discord.Guild): The guild to search in
        role_names (list): List of role names to find

    Returns:
        dict: Dictionary mapping role names to their IDs (or None if not found)
    """
    return {role: (discord.utils.get(guild.roles, name=role.value).id
                   if discord.utils.get(guild.roles, name=role.value)
                   else None)
            for role in roles}


def configure_states(roleIds: dict):
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
    new_member_state = NewMemberState(roleIds)
    active_member_state = ActiveMemberState(roleIds)
    eliminated_state = EliminatedState(roleIds)
    default_state = DefaultState(roleIds)

    # Configure transitions for default state
    default_state.add_transition(EventType.MESSAGE, check_pledge, PlayerState.NEW_MEMBER)

    # Configure transitions for new member state
    new_member_state.add_transition(EventType.MESSAGE, check_message_count, PlayerState.ACTIVE_MEMBER)
    new_member_state.add_transition(EventType.TIME_ELAPSED, time_elapsed(1), PlayerState.ACTIVE_MEMBER)
    new_member_state.add_transition(EventType.MANUAL_UPDATE, handle_manual_update)

    # Configure transitions for active member state
    active_member_state.add_transition(EventType.INACTIVITY, check_inactivity, PlayerState.NEW_MEMBER)
    active_member_state.add_transition(EventType.MANUAL_UPDATE, handle_manual_update)
    active_member_state.add_transition(EventType.REACTION_ADD, handle_reaction, PlayerState.NEW_MEMBER)
    active_member_state.add_transition(EventType.REACTION_ADD, check_hit_confirmation, PlayerState.ELIMINATED)

    # Configure transitions for eliminated state
    eliminated_state.add_transition(EventType.TIME_ELAPSED, time_elapsed(1700), PlayerState.ACTIVE_MEMBER)
    eliminated_state.add_transition(EventType.MANUAL_UPDATE, handle_manual_update)

    global AVAILABLE_STATES
    AVAILABLE_STATES = [default_state, new_member_state, active_member_state, eliminated_state]


def init(guild: discord.Guild):
    configure_states(get_role_ids(guild, RoleTypes))
