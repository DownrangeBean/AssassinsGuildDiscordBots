import discord
from discord.ext import commands, tasks
import time
from typing import Dict

# Import from state_machine package
from .state_machine.events import Event, EventType
from .state_machine.manager import RoleManager
from .state_machine.config import AVAILABLE_STATES
from .state_machine.states import _ElapsedTimeState


class RoleManagement(commands.Cog):
    """Cog for managing user roles based on their activity and state."""

    def __init__(self, bot):
        self.bot = bot
        self.role_manager = RoleManager()

        for state in AVAILABLE_STATES:
            self.role_manager.add_state(state)

        # Track message counts for context
        self.message_counts = {}

        # Schedule inactivity check task
        # self.inactivity_check.start()  # Uncomment to enable inactivity checks

        # Schedule time elapsed check task
        self.time_elapsed_check.start()  # Start the time elapsed check task

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and create MESSAGE events."""
        # Ignore messages from bots
        if message.author.bot:
            return

        # Update message count for the author
        if message.author.id not in self.message_counts:
            self.message_counts[message.author.id] = 0
        self.message_counts[message.author.id] += 1

        # Only process messages in guilds
        if not message.guild:
            return

        # Create event data
        event_data = {
            "message_count": self.message_counts[message.author.id],
            "channel_id": message.channel.id,
            "channel_name": message.channel.name,
            "has_attachments": bool(message.attachments),
            "content": message.content,
            "guild_id": message.guild.id,
            # Add more context data as needed
        }

        # Create and process the message event
        message_event = Event(
            type=EventType.MESSAGE,
            member=message.author,
            data=event_data
        )

        await self.role_manager.process_event(message_event)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Create MEMBER_JOIN events when new members join."""
        # Create and process the member join event
        join_event = Event(
            type=EventType.MEMBER_JOIN,
            member=member,
            data={}
        )

        await self.role_manager.process_event(join_event)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Create REACTION_ADD events when reactions are added."""
        # Skip if the reaction is from a bot
        if payload.member.bot:
            return

        # Get the channel and message
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return

        # Create event data
        event_data = {
            "emoji": str(payload.emoji),
            "message_id": payload.message_id,
            "channel_id": payload.channel_id,
            "guild_id": payload.guild_id,
            "channel_name": channel.name,  # Add channel name for hit confirmation check
            "has_attachments": bool(message.attachments),  # Check if message has attachments
            "mentions": [user.id for user in message.mentions],  # List of mentioned user IDs
        }

        # Create and process the reaction event
        reaction_event = Event(
            type=EventType.REACTION_ADD,
            member=payload.member,
            data=event_data
        )

        await self.role_manager.process_event(reaction_event)

    # Example of how to implement an inactivity check
    # @tasks.loop(hours=24)
    # async def inactivity_check(self):
    #     """Check for inactive members and create INACTIVITY events."""
    #     for guild in self.bot.guilds:
    #         for member in guild.members:
    #             if member.bot:
    #                 continue
    #                 
    #             # Calculate days since last message
    #             # This is just an example - you'd need to track last message timestamps
    #             days_inactive = 0  # Replace with actual calculation
    #             
    #             event_data = {
    #                 "days_since_last_message": days_inactive,
    #                 "guild_id": guild.id,
    #             }
    #             
    #             inactivity_event = Event(
    #                 type=EventType.INACTIVITY,
    #                 member=member,
    #                 data=event_data
    #             )
    #             
    #             await self.role_manager.process_event(inactivity_event)

    @tasks.loop(minutes=1)  # Check every 5 minutes
    async def time_elapsed_check(self):
        """Check for eliminated members who should return to active state."""

        for member_id, stateId in self.role_manager.member_states.items():
            # Create and process the time elapsed event
            state = self.role_manager.states[stateId]
            member = discord.utils.get(self.bot.get_all_members(), id=member_id)
            if member is None:
               continue
            time_event = Event(
                type=EventType.TIME_ELAPSED,
                member=member,
                data=state.get_ctx(member_id),
            )

            await self.role_manager.process_event(time_event)

    @time_elapsed_check.before_loop
    async def before_time_elapsed_check(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()

    @commands.command(name='setrole', help='Manually set a user to a specific role state')
    @commands.has_permissions(manage_roles=True)
    async def set_role_state(self, ctx, member: discord.Member, state_name: str):
        """Manually set a member to a specific role state using a MANUAL_UPDATE event."""
        print(ctx, member, state_name)
        if state_name not in self.role_manager.states:
            await ctx.send(f"Error: State '{state_name}' does not exist")
            return

        # Create a manual update event
        manual_event = Event(
            type=EventType.MANUAL_UPDATE,
            member=member,
            data={"target_state": state_name}
        )

        try:
            # Process the event
            await self.role_manager.process_event(manual_event)

            # If the event didn't result in a transition, force the state change
            # This is a fallback in case the member doesn't have a current state or
            # the current state doesn't have a transition for MANUAL_UPDATE
            if self.role_manager.member_states.get(member.id) != state_name:
                await self.role_manager.set_member_state(member, state_name)

            await ctx.send(f"Set {member.display_name} to {state_name} state")
        except ValueError as e:
            await ctx.send(f"Error: {str(e)}")

    @commands.command(name='liststates', help='List all available role states')
    async def list_states(self, ctx):
        """List all available role states."""
        if not self.role_manager.states:
            await ctx.send("No role states defined")
            return

        embed = discord.Embed(
            title="Available Role States",
            description="List of all role states managed by the bot",
            color=discord.Color.blue()
        )

        for name, state in self.role_manager.states.items():
            role_names = []
            for role_id in state.roles:
                role = ctx.guild.get_role(role_id)
                role_names.append(role.name if role else f"Unknown Role ({role_id})")

            # Get available transitions
            transitions = []
            for event_type, handlers in state.transitions.items():
                if handlers:  # If there are handlers for this event type
                    transitions.append(event_type.name)

            embed.add_field(
                name=name,
                value=f"Roles: {', '.join(role_names) or 'None'}\nResponds to: {', '.join(transitions) or 'No events'}", 
                inline=False
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
