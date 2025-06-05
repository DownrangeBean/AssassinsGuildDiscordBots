from typing import Optional, Callable
import time
from .events import Event, EventType


def check_message_count(event: Event) -> bool:
    """Check if member has sent enough messages to transition to active state."""
    if "message_count" in event.data and event.data["message_count"] >= 5:
        return True
    return False


def handle_manual_update(event: Event) -> bool:
    """Handle manual state update requests."""
    if "target_state" in event.data:
        return True
    return False


def check_inactivity(event: Event) -> bool:
    """Check if member has been inactive for too long."""
    if "days_since_last_message" in event.data and event.data["days_since_last_message"] > 30:
        return True  # Demote to new member if inactive
    return False


def handle_reaction(event: Event) -> bool:
    """Example of handling reaction events."""
    # This is just an example - you would implement your own logic
    # For example, transitioning based on reactions to specific messages
    if "emoji" in event.data:
        # Example: if user reacts with a specific emoji, change their state
        if event.data["emoji"] == "📊":  # Example: chart emoji
            return True  # Just an example transition
    return False


def check_pledge(event: Event) -> bool:
    """
    Check if a player has been eliminated based on a hit confirmation.

    Conditions:
    1. The message is in the "pledge-and-surety" channel
    2. The message has a photo
    """
    if event.type != EventType.MESSAGE:
        return False

    # Check if the channel is "pledge-and-surety"
    if "channel_name" not in event.data or event.data["channel_name"] != "pledge-and-surety":
        return False

    # Check if the message has attachments (photos)
    if "has_attachments" not in event.data or not event.data["has_attachments"]:
        return False

    # All conditions met, transition to New Player state
    return True


def check_hit_confirmation(event: Event) -> bool:
    """
    Check if a player has been eliminated based on a hit confirmation.

    Conditions:
    1. The reaction is a tick emoji (✅)
    2. The message is in the "hit-confirmed" channel
    3. The message has a photo
    4. The message mentions the player
    """
    if event.type != EventType.REACTION_ADD:
        return False

    # Check if the emoji is a tick
    if "emoji" not in event.data or event.data["emoji"] != "✅":
        return False

    # Check if the channel is "hit-confirmed"
    if "channel_name" not in event.data or event.data["channel_name"] != "hit-confirmed":
        return False

    # Check if the message has attachments (photos)
    if "has_attachments" not in event.data or not event.data["has_attachments"]:
        return False

    # Check if the player is mentioned in the message
    if "mentions" not in event.data or event.member.id not in event.data["mentions"]:
        return False

    # All conditions met, transition to Eliminated state
    return True


def time_elapsed(delta: int) -> Callable[[Event], bool]:
    """
    Check if a certain delta of time has elapsed.
    """

    def func(event: Event) -> bool:
        if event.type != EventType.TIME_ELAPSED:
            return False

        # Check if the elimination time is available
        if "start_time" not in event.data:
            print('[time_elapsed] start_time attribute could not be found in event.data')
            return False

        # Check if 2 hours have passed since elimination
        start_time = event.data["start_time"]
        current_time = time.time()

        # has the elapsed time exceeded the delta?
        if current_time - start_time >= delta:
            print(f'[time_elapsed] time elapsed exceeded the delta {delta}')
            return True
        return False

    return func
