import discord
from discord.ext import commands

class General(commands.Cog):
    """General commands for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='info', help='Shows information about the bot')
    async def info(self, ctx):
        """Displays information about the bot."""
        embed = discord.Embed(
            title="Bot Information",
            description="A Discord bot created with discord.py",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Creator", value="Your Name", inline=True)
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Command Prefix", value=self.bot.command_prefix, inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='serverinfo', help='Shows information about the server')
    async def server_info(self, ctx):
        """Displays information about the current server."""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"{guild.name} Server Information",
            description=guild.description if guild.description else "No description",
            color=discord.Color.green()
        )
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        # Server details
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created On", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        
        # Member counts
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))