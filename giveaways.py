import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from datetime import datetime, timedelta

# تخزين Giveaways النشطة في الذاكرة
active_giveaways = {}  # {message_id: giveaway_data}


class GiveawayView(discord.ui.View):
    """زرار المشاركة في Giveaway"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎉 مشاركة", style=discord.ButtonStyle.success, custom_id="giveaway_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg_id = interaction.message.id
        if msg_id not in active_giveaways:
            return await interaction.response.send_message("❌ هذا Giveaway لم يعد نشطًا.", ephemeral=True)

        gw = active_giveaways[msg_id]
        user_id = interaction.user.id

        if user_id in gw["participants"]:
            gw["participants"].remove(user_id)
            await interaction.response.send_message("❌ تم إلغاء مشاركتك في الـ Giveaway.", ephemeral=True)
        else:
            gw["participants"].add(user_id)
            await interaction.response.send_message("✅ تم تسجيلك في الـ Giveaway! حظ موفق 🍀", ephemeral=True)

        # تحديث عدد المشاركين في الـ embed
        try:
            embed = interaction.message.embeds[0]
            for i, field in enumerate(embed.fields):
                if "المشاركون" in field.name:
                    embed.set_field_at(i, name="👥 المشاركون", value=str(len(gw["participants"])), inline=True)
                    break
            await interaction.message.edit(embed=embed)
        except Exception:
            pass


def make_giveaway_embed(prize: str, winners: int, end_time: datetime, host: discord.Member, participants: int = 0) -> discord.Embed:
    embed = discord.Embed(title=f"🎉 {prize}", color=0xf1c40f)
    embed.add_field(name="🏆 عدد الفائزين", value=str(winners), inline=True)
    embed.add_field(name="👥 المشاركون", value=str(participants), inline=True)
    embed.add_field(name="⏰ ينتهي في", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
    embed.add_field(name="🎯 المُضيف", value=host.mention, inline=True)
    embed.set_footer(text="اضغط على 🎉 للمشاركة!")
    return embed


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(GiveawayView())

    @app_commands.command(name="giveaway", description="إنشاء Giveaway جديد")
    @app_commands.describe(
        prize="الجائزة",
        duration="المدة (مثال: 1h, 30m, 1d)",
        winners="عدد الفائزين"
    )
    async def giveaway(self, interaction: discord.Interaction, prize: str, duration: str, winners: int = 1):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)

        # تحليل المدة
        seconds = self._parse_duration(duration)
        if not seconds:
            return await interaction.response.send_message("❌ صيغة المدة غير صحيحة. استخدم: `30m`, `1h`, `1d`", ephemeral=True)

        end_time = datetime.utcnow() + timedelta(seconds=seconds)
        embed = make_giveaway_embed(prize, winners, end_time, interaction.user)

        await interaction.response.send_message("✅ تم إنشاء الـ Giveaway!", ephemeral=True)
        msg = await interaction.channel.send(embed=embed, view=GiveawayView())

        active_giveaways[msg.id] = {
            "channel_id": interaction.channel.id,
            "prize": prize,
            "winners": winners,
            "host": interaction.user.id,
            "participants": set(),
            "end_time": end_time,
            "message_id": msg.id,
        }

        # جدولة الانتهاء
        self.bot.loop.create_task(self._end_giveaway(msg.id, seconds))

    async def _end_giveaway(self, message_id: int, delay: float):
        await asyncio.sleep(delay)

        if message_id not in active_giveaways:
            return

        gw = active_giveaways.pop(message_id)
        channel = self.bot.get_channel(gw["channel_id"])
        if not channel:
            return

        try:
            msg = await channel.fetch_message(message_id)
        except Exception:
            return

        participants = list(gw["participants"])
        winner_count = min(gw["winners"], len(participants))

        embed = discord.Embed(title=f"🎊 انتهى الـ Giveaway: {gw['prize']}", color=0x2ecc71)

        if not participants:
            embed.description = "❌ لم يشارك أحد في هذا الـ Giveaway."
            embed.color = 0xe74c3c
            await msg.edit(embed=embed, view=None)
            await channel.send("😔 لم يشارك أحد في الـ Giveaway.")
            return

        winners = random.sample(participants, winner_count)
        guild = channel.guild
        winner_mentions = []
        for w_id in winners:
            member = guild.get_member(w_id)
            if member:
                winner_mentions.append(member.mention)

        embed.add_field(name="🏆 الفائزون", value="\n".join(winner_mentions) or "لا يوجد", inline=False)
        embed.add_field(name="👥 إجمالي المشاركين", value=str(len(participants)), inline=True)
        embed.set_footer(text="تهانينا للفائزين! 🎉")

        await msg.edit(embed=embed, view=None)
        await channel.send(
            f"🎉 تهانينا {', '.join(winner_mentions)}! فزتم بـ **{gw['prize']}**!"
        )

    @app_commands.command(name="giveaway-reroll", description="إعادة السحب على Giveaway منتهي")
    @app_commands.describe(message_id="ID رسالة الـ Giveaway")
    async def reroll(self, interaction: discord.Interaction, message_id: str):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        await interaction.response.send_message("🔄 لإعادة السحب، تأكد من أن الـ Giveaway انتهى وأعد تشغيل الأمر مع ID الصحيح.", ephemeral=True)

    @app_commands.command(name="giveaway-list", description="عرض الـ Giveaways النشطة")
    async def giveaway_list(self, interaction: discord.Interaction):
        if not active_giveaways:
            return await interaction.response.send_message("📭 لا يوجد Giveaways نشطة حاليًا.", ephemeral=True)

        embed = discord.Embed(title="🎉 Giveaways النشطة", color=0xf1c40f)
        for msg_id, gw in active_giveaways.items():
            embed.add_field(
                name=f"🎁 {gw['prize']}",
                value=f"المشاركون: {len(gw['participants'])}\nينتهي: <t:{int(gw['end_time'].timestamp())}:R>",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    def _parse_duration(self, duration: str) -> int | None:
        """تحويل النص لثواني: 1d, 2h, 30m, 45s"""
        try:
            unit = duration[-1].lower()
            value = int(duration[:-1])
            return {"s": value, "m": value * 60, "h": value * 3600, "d": value * 86400}.get(unit)
        except Exception:
            return None


async def setup(bot):
    await bot.add_cog(Giveaways(bot))
