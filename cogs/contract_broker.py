import discord
from discord.ext import commands, tasks
import random
import asyncio
from typing import Dict, List, Optional, Tuple
import datetime

from .state_machine.states import RoleTypes, PlayerState
from .role_management import RoleManagement


class ContractBroker(commands.Cog):
    """Cog for managing hit contracts between players."""

    def __init__(self, bot):
        self.bot = bot
        self.contract_distribution.start()
        self.last_photos = {}  # Maps member IDs to their last photo URL in pledge-and-surety channel

    def cog_unload(self):
        """Clean up when the cog is unloaded."""
        self.contract_distribution.cancel()

    @tasks.loop(minutes=30)
    async def contract_distribution(self):
        """
        Every two hours, collect all members with 'Active Player' role,
        generate hit contracts, and distribute them to players.
        """
        print("Starting contract distribution...")

        # Get the guild
        guild = self.bot.guilds[0]  # Assuming the bot is only in one guild
        if not guild:
            print("No guild found")
            return

        # Get the role management cog to access the role manager
        role_management_cog = self.bot.get_cog("RoleManagement")
        if not role_management_cog:
            print("RoleManagement cog not found")
            return

        # Get the pledge-and-surety channel
        pledge_channel = discord.utils.get(guild.channels, name="pledge-and-surety")
        if not pledge_channel:
            print("pledge-and-surety channel not found")
            return

        # Update the last photos dictionary
        await self.update_last_photos(pledge_channel)

        # Get all active players
        active_players = []
        new_players = []

        for member_id, state_name in role_management_cog.role_manager.member_states.items():
            if state_name == PlayerState.ACTIVE_MEMBER.value:
                member = guild.get_member(member_id)
                if member and not member.bot and member_id in self.last_photos:
                    active_players.append(member)
            elif state_name == PlayerState.NEW_MEMBER.value:
                member = guild.get_member(member_id)
                if member and not member.bot and member_id in self.last_photos:
                    new_players.append(member)

        # If there are not enough players, don't distribute contracts
        if len(active_players) + len(new_players) < 2:
            print("Not enough players for contract distribution")
            return

        # Generate and distribute contracts
        await self.generate_and_distribute_contracts(active_players, new_players)

    async def update_last_photos(self, channel):
        """
        Update the dictionary of last photos for each member from the pledge-and-surety channel.
        """
        print(f"Updating last photos from {channel.name}...")

        # Create a temporary dictionary to track the most recent photo for each member
        member_photos = {}

        # Get the most recent messages with attachments
        async for message in channel.history(limit=1000):
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        # Always store the most recent photo (messages are retrieved newest first)
                        if message.author.id not in member_photos:
                            member_photos[message.author.id] = attachment.url
                            print(f"Found photo for {message.author.display_name}")
                        break

        # Update the last_photos dictionary with the new data
        self.last_photos.update(member_photos)
        print(f"Updated photos for {len(member_photos)} members")

    async def generate_and_distribute_contracts(self, active_players, new_players):
        """
        Generate hit contracts and distribute them to players.

        Rules:
        1. Members should not receive themselves as targets
        2. Contracts can be shared by more than one player
        3. New players should have unique hit contract targets
        """
        print(f"Generating contracts for {len(active_players)} active players and {len(new_players)} new players...")

        # Create a pool of all potential targets
        target_pool = active_players

        # Shuffle the players to randomize targets
        random.shuffle(target_pool)

        # Assign unique targets to new players first
        new_player_targets = {}
        available_targets = target_pool.copy()

        for new_player in new_players:
            if not available_targets:
                print("Not enough targets for new players")
                return

            # Assign a random target
            target = random.choice(available_targets)
            new_player_targets[new_player.id] = target

            # Remove the target from available targets to ensure uniqueness
            available_targets.remove(target)

        # Assign targets to active players (can be shared)
        active_player_targets = {}

        for active_player in active_players:
            # Create a list of potential targets (excluding self)
            potential_targets = [p for p in target_pool if p.id != active_player.id]

# TODO: remove targets given to new players
            if not potential_targets:
                print(f"No potential targets for {active_player.display_name}")
                continue

            # Assign a random target
            target = random.choice(potential_targets)
            active_player_targets[active_player.id] = target

        # Distribute contracts
        for player in target_pool:
            target = None
            if player.id in [p.id for p in new_players]:
                target = new_player_targets.get(player.id)
            else:
                target = active_player_targets.get(player.id)

            if target:
                await self.send_contract(player, target)

    async def send_contract(self, player, target):
        """Send a hit contract to a player."""
        try:
            # Create an embed for the contract
            embed = discord.Embed(
                title="🎯 New Hit Contract",
                description=f"Your new target has been assigned.",
                color=discord.Color.red()
            )

            # Add target information
            embed.add_field(name="Target Name", value=target.display_name, inline=True)
            embed.add_field(name="Discord Tag", value=target.mention, inline=True)

            # Add the target's photo
            if target.id in self.last_photos:
                embed.set_image(url=self.last_photos[target.id])

            # Add timestamp
            embed.set_footer(text=f"Contract issued at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Send the contract via DM
            await player.send(embed=embed)
            print(f"Sent contract to {player.display_name} targeting {target.display_name}")

        except discord.Forbidden:
            print(f"Could not send DM to {player.display_name}")
        except Exception as e:
            print(f"Error sending contract to {player.display_name}: {str(e)}")

    @contract_distribution.before_loop
    async def before_contract_distribution(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()
        # Wait a bit to ensure all other cogs are loaded
        await asyncio.sleep(10)

    @commands.command(name='distribute_contracts', help='Manually trigger contract distribution')
    @commands.has_permissions(administrator=True)
    async def distribute_contracts_command(self, ctx):
        """Manually trigger contract distribution for testing purposes."""
        await ctx.send("Manually triggering contract distribution...")
        await self.contract_distribution()
        await ctx.send("Contract distribution completed.")


async def setup(bot):
    await bot.add_cog(ContractBroker(bot))
