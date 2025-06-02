from typing import Optional
import time
from .events import Event, EventType


def check_message_count(event: Event) -> Optional[str]:
    """Check if member has sent enough messages to transition to active state."""
    if "message_count" in event.data and event.data["message_count"] >= 5:
        return "Active Member"
    return None


def handle_manual_update(event: Event) -> Optional[str]:
    """Handle manual state update requests."""
    if "target_state" in event.data:
        return event.data["target_state"]
    return None


def check_inactivity(event: Event) -> Optional[str]:
    """Check if member has been inactive for too long."""
    if "days_since_last_message" in event.data and event.data["days_since_last_message"] > 30:
        return "New Member"  # Demote to new member if inactive
    return None


def handle_reaction(event: Event) -> Optional[str]:
    """Example of handling reaction events."""
    # This is just an example - you would implement your own logic
    # For example, transitioning based on reactions to specific messages
    if "emoji" in event.data:
        # Example: if user reacts with a specific emoji, change their state
        if event.data["emoji"] == "📊":  # Example: chart emoji
            return "New Member"  # Just an example transition
    return None


def check_hit_confirmation(event: Event) -> Optional[str]:
    """
    Check if a player has been eliminated based on a hit confirmation.

    Conditions:
    1. The reaction is a tick emoji (✅)
    2. The message is in the "hit-confirmed" channel
    3. The message has a photo
    4. The message mentions the player
    """
    if event.type != EventType.REACTION_ADD:
        return None

    # Check if the emoji is a tick
    if "emoji" not in event.data or event.data["emoji"] != "✅":
        return None

    # Check if the channel is "hit-confirmed"
    if "channel_name" not in event.data or event.data["channel_name"] != "hit-confirmed":
        return None

    # Check if the message has attachments (photos)
    if "has_attachments" not in event.data or not event.data["has_attachments"]:
        return None

    # Check if the player is mentioned in the message
    if "mentions" not in event.data or event.member.id not in event.data["mentions"]:
        return None

    # All conditions met, transition to Eliminated state
    return "Eliminated"


def check_elimination_time(event: Event) -> Optional[str]:
    """
    Check if a player has been eliminated for 2 hours and should return to Active Player state.
    """
    if event.type != EventType.TIME_ELAPSED:
        return None

    # Check if the elimination time is available
    if "elimination_time" not in event.data:
        return None

    # Check if 2 hours have passed since elimination
    elimination_time = event.data["elimination_time"]
    current_time = time.time()

    # 2 hours = 7200 seconds
    if current_time - elimination_time >= 7200:
        return "Active Member"

    return None
