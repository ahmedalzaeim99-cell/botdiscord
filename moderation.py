import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_permission(self, interaction: discord.Interaction, perm: str) -> bool:
        return getattr(interaction.user.guild_permissions, perm, False)

    # ──────────────── BAN ────────────────
    @app_commands.command(name="ban", description="حظر عضو من السيرفر")
    @app_commands.describe(member="العضو", reason="السبب")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
        if not self.has_permission(interaction, "ban_members"):
            return await interaction.response.send_message("❌ ليس لديك صلاحية الحظر.", ephemeral=True)
        await member.ban(reason=reason)
        embed = discord.Embed(title="🔨 تم الحظر", color=0xe74c3c)
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="بواسطة", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    # ──────────────── UNBAN ────────────────
    @app_commands.command(name="unban", description="رفع الحظر عن مستخدم")
    @app_commands.describe(user_id="ID المستخدم")
    async def unban(self, interaction: discord.Interaction, user_id: str):
        if not self.has_permission(interaction, "ban_members"):
            return await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ تم رفع الحظر عن **{user}**")
        except Exception:
            await interaction.response.send_message("❌ لم يتم إيجاد المستخدم أو لم يكن محظورًا.", ephemeral=True)

    # ──────────────── KICK ────────────────
    @app_commands.command(name="kick", description="طرد عضو من السيرفر")
    @app_commands.describe(member="العضو", reason="السبب")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
        if not self.has_permission(interaction, "kick_members"):
            return await interaction.response.send_message("❌ ليس لديك صلاحية الطرد.", ephemeral=True)
        await member.kick(reason=reason)
        embed = discord.Embed(title="👢 تم الطرد", color=0xe67e22)
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="بواسطة", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    # ──────────────── MUTE (Timeout) ────────────────
    @app_commands.command(name="mute", description="كتم عضو")
    @app_commands.describe(member="العضو", minutes="المدة بالدقائق", reason="السبب")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int = 10, reason: str = "لا يوجد سبب"):
        if not self.has_permission(interaction, "moderate_members"):
            return await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        duration = discord.utils.utcnow() + asyncio.timedelta(minutes=minutes) if False else None
        import datetime
        duration = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(title="🔇 تم الكتم", color=0x95a5a6)
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="المدة", value=f"{minutes} دقيقة")
        embed.add_field(name="السبب", value=reason)
        await interaction.response.send_message(embed=embed)

    # ──────────────── UNMUTE ────────────────
    @app_commands.command(name="unmute", description="رفع الكتم عن عضو")
    @app_commands.describe(member="العضو")
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        if not self.has_permission(interaction, "moderate_members"):
            return await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        await member.timeout(None)
        await interaction.response.send_message(f"✅ تم رفع الكتم عن {member.mention}")

    # ──────────────── WARN ────────────────
    @app_commands.command(name="warn", description="تحذير عضو")
    @app_commands.describe(member="العضو", reason="السبب")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "مخالفة القوانين"):
        if not self.has_permission(interaction, "manage_messages"):
            return await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        embed = discord.Embed(title="⚠️ تحذير", color=0xf1c40f)
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="بواسطة", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)
        try:
            await member.send(embed=embed)
        except Exception:
            pass

    # ──────────────── CLEAR ────────────────
    @app_commands.command(name="clear", description="حذف رسائل من القناة")
    @app_commands.describe(amount="عدد الرسائل (1-100)")
    async def clear(self, interaction: discord.Interaction, amount: int = 10):
        if not self.has_permission(interaction, "manage_messages"):
            return await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        amount = max(1, min(amount, 100))
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ تم حذف **{len(deleted)}** رسالة.", ephemeral=True)

    # ──────────────── LOCK / UNLOCK ────────────────
    @app_commands.command(name="lock", description="قفل القناة الحالية")
    async def lock(self, interaction: discord.Interaction):
        if not self.has_permission(interaction, "manage_channels"):
            return await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔒 تم قفل القناة.")

    @app_commands.command(name="unlock", description="فتح القناة الحالية")
    async def unlock(self, interaction: discord.Interaction):
        if not self.has_permission(interaction, "manage_channels"):
            return await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = True
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔓 تم فتح القناة.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
