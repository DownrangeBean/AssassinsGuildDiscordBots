import discord
from discord.ext import commands
import random
import datetime

class Utility(commands.Cog):
    """Utility commands for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='roll', help='Rolls a dice (e.g., !roll 2d6)')
    async def roll(self, ctx, dice: str = '1d6'):
        """
        Rolls dice in NdN format.
        Example: !roll 2d6 rolls 2 six-sided dice
        """
        try:
            # Parse the dice string (e.g., "2d6")
            rolls, limit = map(int, dice.split('d'))
            
            # Validate input
            if rolls <= 0 or limit <= 0:
                await ctx.send("Please use positive numbers for the dice roll.")
                return
            
            if rolls > 100:
                await ctx.send("You can't roll more than 100 dice at once.")
                return
            
            # Roll the dice
            results = [random.randint(1, limit) for _ in range(rolls)]
            
            # Format the response
            result_str = ', '.join(str(r) for r in results)
            total = sum(results)
            
            await ctx.send(f"🎲 Rolling {dice}...\nResults: {result_str}\nTotal: {total}")
        
        except Exception as e:
            await ctx.send(f"Error: {str(e)}\nPlease use the format NdN (e.g., 2d6).")
    
    @commands.command(name='choose', help='Chooses between multiple options')
    async def choose(self, ctx, *options):
        """
        Chooses between multiple options.
        Example: !choose option1 option2 option3
        """
        if len(options) < 2:
            await ctx.send("Please provide at least two options to choose from.")
            return
        
        choice = random.choice(options)
        await ctx.send(f"🤔 I choose: **{choice}**")
    
    @commands.command(name='time', help='Shows the current time')
    async def time(self, ctx):
        """Shows the current UTC time."""
        now = datetime.datetime.utcnow()
        
        embed = discord.Embed(
            title="Current Time",
            description=f"UTC: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))