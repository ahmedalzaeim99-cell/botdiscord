import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# ══════════════════════════════════════
#           VIEWS (Buttons)
# ══════════════════════════════════════

class TicketOpenView(discord.ui.View):
    """زرار فتح تذكرة جديدة"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 فتح تذكرة", style=discord.ButtonStyle.primary, custom_id="ticket_open")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # تحقق لو عنده تذكرة مفتوحة
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{user.id}")
        if existing:
            return await interaction.response.send_message(
                f"❌ عندك تذكرة مفتوحة بالفعل: {existing.mention}", ephemeral=True
            )

        # إيجاد رتبة الدعم
        support_role = discord.utils.get(guild.roles, name="Support") or \
                       discord.utils.get(guild.roles, name="دعم") or \
                       discord.utils.get(guild.roles, name="Staff")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # إيجاد كاتيجوري التذاكر
        category = discord.utils.get(guild.categories, name="التذاكر") or \
                   discord.utils.get(guild.categories, name="Tickets")

        channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            overwrites=overwrites,
            category=category,
            topic=f"تذكرة دعم لـ {user.name}"
        )

        embed = discord.Embed(
            title="🎫 تذكرة دعم جديدة",
            description=f"مرحبًا {user.mention}!\nاشرح مشكلتك وسيتم الرد عليك قريبًا.",
            color=0x3498db
        )
        embed.set_footer(text="اضغط على زر الإغلاق لإغلاق التذكرة")

        await channel.send(
            content=f"{user.mention}" + (f" | {support_role.mention}" if support_role else ""),
            embed=embed,
            view=TicketControlView()
        )
        await interaction.response.send_message(f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True)


class TicketControlView(discord.ui.View):
    """أزرار داخل التذكرة (إغلاق - استلام)"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ استلام التذكرة", style=discord.ButtonStyle.success, custom_id="ticket_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Staff فقط.", ephemeral=True)
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"📌 **{interaction.user.mention}** استلم التذكرة.")

    @discord.ui.button(label="🔒 إغلاق التذكرة", style=discord.ButtonStyle.danger, custom_id="ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔒 إغلاق التذكرة",
            description="هل أنت متأكد من إغلاق هذه التذكرة؟",
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed, view=TicketConfirmClose(), ephemeral=True)


class TicketConfirmClose(discord.ui.View):
    """تأكيد إغلاق التذكرة"""
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="✅ تأكيد الإغلاق", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏳ سيتم حذف القناة خلال 5 ثواني...")
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"تذكرة مُغلقة بواسطة {interaction.user}")

    @discord.ui.button(label="❌ إلغاء", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ تم إلغاء الإغلاق.", ephemeral=True)


# ══════════════════════════════════════
#              COG
# ══════════════════════════════════════

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # تسجيل الـ Views حتى تعمل بعد restart
        bot.add_view(TicketOpenView())
        bot.add_view(TicketControlView())

    @app_commands.command(name="ticket-setup", description="إعداد نظام التذاكر في قناة معينة")
    @app_commands.describe(channel="القناة التي ستظهر فيها رسالة التذاكر")
    async def ticket_setup(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ أدمن فقط.", ephemeral=True)

        target = channel or interaction.channel

        embed = discord.Embed(
            title="🎫 نظام التذاكر",
            description="اضغط على الزر أدناه لفتح تذكرة دعم.\nسيقوم فريق الدعم بالرد عليك في أقرب وقت.",
            color=0x3498db
        )
        embed.set_footer(text=interaction.guild.name)

        await target.send(embed=embed, view=TicketOpenView())
        await interaction.response.send_message(f"✅ تم إعداد نظام التذاكر في {target.mention}", ephemeral=True)

    @app_commands.command(name="ticket-add", description="إضافة عضو للتذكرة الحالية")
    @app_commands.describe(member="العضو المراد إضافته")
    async def ticket_add(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Staff فقط.", ephemeral=True)
        await interaction.channel.set_permissions(member, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"✅ تم إضافة {member.mention} للتذكرة.")

    @app_commands.command(name="ticket-remove", description="إزالة عضو من التذكرة الحالية")
    @app_commands.describe(member="العضو المراد إزالته")
    async def ticket_remove(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Staff فقط.", ephemeral=True)
        await interaction.channel.set_permissions(member, overwrite=None)
        await interaction.response.send_message(f"✅ تم إزالة {member.mention} من التذكرة.")

async def setup(bot):
    await bot.add_cog(Tickets(bot))
