import discord
from discord.ext import commands
import asyncio
from collections import defaultdict
import time

class Protection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Anti-Spam: {user_id: [timestamps]}
        self.spam_tracker = defaultdict(list)
        self.SPAM_LIMIT = 5       # عدد الرسائل
        self.SPAM_WINDOW = 5      # ثواني
        self.SPAM_MUTE_MINUTES = 5

        # Anti-Raid: تتبع الأعضاء الجدد
        self.join_tracker = []
        self.RAID_JOIN_LIMIT = 8  # عدد الأعضاء
        self.RAID_WINDOW = 10     # ثواني
        self.raid_mode = False

        # Anti-Link
        self.link_whitelist = []  # يمكن إضافة دومينات مسموح بيها

    # ═══════════════════════════════
    #         ANTI-SPAM
    # ═══════════════════════════════
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if message.author.guild_permissions.administrator:
            return

        user_id = message.author.id
        now = time.time()

        # تنظيف الرسائل القديمة
        self.spam_tracker[user_id] = [
            t for t in self.spam_tracker[user_id]
            if now - t < self.SPAM_WINDOW
        ]
        self.spam_tracker[user_id].append(now)

        if len(self.spam_tracker[user_id]) >= self.SPAM_LIMIT:
            self.spam_tracker[user_id] = []
            await self._mute_user(
                message.author,
                message.guild,
                self.SPAM_MUTE_MINUTES,
                "⚡ Anti-Spam: إرسال رسائل بسرعة كبيرة"
            )
            try:
                await message.channel.send(
                    f"⚠️ {message.author.mention} تم كتمك لمدة **{self.SPAM_MUTE_MINUTES}** دقائق بسبب السبام.",
                    delete_after=8
                )
            except Exception:
                pass

    # ═══════════════════════════════
    #         ANTI-RAID
    # ═══════════════════════════════
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        now = time.time()
        self.join_tracker = [t for t in self.join_tracker if now - t < self.RAID_WINDOW]
        self.join_tracker.append(now)

        if len(self.join_tracker) >= self.RAID_JOIN_LIMIT and not self.raid_mode:
            self.raid_mode = True
            await self._enable_raid_mode(member.guild)

        if self.raid_mode:
            try:
                await member.kick(reason="🛡️ Anti-Raid Mode: انضمام مريب أثناء وضع الريد")
            except Exception:
                pass

    async def _enable_raid_mode(self, guild: discord.Guild):
        """تفعيل وضع الريد: رفع مستوى التحقق"""
        try:
            await guild.edit(verification_level=discord.VerificationLevel.high)
        except Exception:
            pass

        # إيجاد أول قناة عامة وإرسال تحذير
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="🚨 تحذير: وضع الحماية من الريد مُفعَّل",
                    description="تم رصد انضمامات مريبة!\nتم رفع مستوى التحقق تلقائيًا.\nسيتم إيقاف وضع الريد بعد 5 دقائق.",
                    color=0xe74c3c
                )
                await channel.send(embed=embed)
                break

        # إيقاف وضع الريد بعد 5 دقائق
        await asyncio.sleep(300)
        self.raid_mode = False
        self.join_tracker = []
        try:
            await guild.edit(verification_level=discord.VerificationLevel.medium)
        except Exception:
            pass

    # ═══════════════════════════════
    #         HELPER
    # ═══════════════════════════════
    async def _mute_user(self, member: discord.Member, guild: discord.Guild, minutes: int, reason: str):
        import datetime
        try:
            duration = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
            await member.timeout(duration, reason=reason)
        except Exception:
            pass

    # ═══════════════════════════════
    #         SLASH COMMANDS
    # ═══════════════════════════════
    @discord.app_commands.command(name="raidmode", description="تفعيل/إيقاف وضع الريد يدويًا")
    async def raidmode(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ أدمن فقط.", ephemeral=True)

        self.raid_mode = not self.raid_mode
        status = "🔴 مُفعَّل" if self.raid_mode else "🟢 مُوقَف"
        await interaction.response.send_message(f"🛡️ وضع الريد: **{status}**")

    @discord.app_commands.command(name="protection", description="عرض إعدادات الحماية الحالية")
    async def protection_status(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛡️ إعدادات الحماية", color=0x2ecc71)
        embed.add_field(name="Anti-Spam", value=f"حد الرسائل: **{self.SPAM_LIMIT}** في **{self.SPAM_WINDOW}** ثواني\nالكتم: **{self.SPAM_MUTE_MINUTES}** دقائق", inline=False)
        embed.add_field(name="Anti-Raid", value=f"حد الانضمامات: **{self.RAID_JOIN_LIMIT}** في **{self.RAID_WINDOW}** ثواني\nوضع الريد: {'🔴 مُفعَّل' if self.raid_mode else '🟢 مُوقَف'}", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Protection(bot))
