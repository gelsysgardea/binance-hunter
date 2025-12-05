import re
import asyncio
import time
import random
import sys
from collections import deque
from typing import Dict, Any, List, Tuple

from telethon import TelegramClient, events, Button
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.config import config
from core.binance.redpacket import RedpacketHandler, ClaimResult
from core.database import DatabaseManager

class Dashboard:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.console = Console()
        self.layout = self._create_layout()
        self.log_buffer = deque(maxlen=20)
        self.stats: Dict[str, Any] = {"autoclaim": "SOLO MANUAL", "status_color": "yellow", "queue_size": 0}

    def _create_layout(self) -> Layout:
        layout = Layout(name="root")
        layout.split(Layout(name="header", size=3), Layout(ratio=1, name="main"), Layout(size=5, name="footer"))
        layout["main"].split_row(Layout(name="side"), Layout(name="body", ratio=2))
        layout["side"].split(Layout(name="stats_panel"), Layout(name="channels_panel"))
        return layout
    def _get_header(self) -> Panel:
        return Panel(Text("Hagamos Dinerita ✨ | v5.2 Smart Stealth", justify="center", style="bold magenta"), border_style="bright_blue")
    def _get_log_panel(self) -> Panel:
        return Panel("\n".join(self.log_buffer), title="[bold cyan]Actividad Cerebral[/]", border_style="cyan")
    def _get_stats_panel(self) -> Panel:
        session_stats, total_stats = self.db.get_session_stats(), self.db.get_total_stats()
        success_rate = (total_stats.get('successes', 0) / total_stats.get('attempts', 1) * 100) if total_stats.get('attempts', 0) > 0 else 0
        stats_text = Text.assemble(
            ("Bajas de Hoy: ", "bold"), (f"{session_stats.get('claimed_today', 0)}", "bright_green"), "\n",
            ("Botín de Hoy: ", "bold"), (f"${session_stats.get('value_today', 0.0):.4f} USD", "bright_yellow"), "\n",
            ("Instinto Asesino: ", "bold"), (f"{success_rate:.1f}%", "cyan"), "\n",
            ("Presas en la Mira: ", "bold"), (f"{self.stats['queue_size']}", "white"), "\n",
            ("Modo Depredador: ", "bold"), (f"{self.stats['autoclaim']}", self.stats['status_color'])
        )
        return Panel(stats_text, title="[bold yellow]Reporte de Cacería[/]", border_style="yellow")
    def _get_channels_panel(self) -> Panel:
        table = Table(title="[bold green]Territorios de Caza[/]", border_style="green")
        table.add_column("Presa (Canal)", style="white", no_wrap=True)
        table.add_column("Bajas", style="green")
        table.add_column("Botín ($)", style="yellow")
        for ch in self.db.get_top_channels():
            table.add_row(ch['name'], str(ch['success']), f"{ch['value']:.4f}")
        return Panel(table)
    def _get_footer(self) -> Panel:
        return Panel(Text("Usa los botones en Telegram para controlar al sicario.", justify="center"), border_style="dim")
    def update(self) -> Layout:
        self.layout["header"].update(self._get_header())
        self.layout["body"].update(self._get_log_panel())
        self.layout["stats_panel"].update(self._get_stats_panel())
        self.layout["channels_panel"].update(self._get_channels_panel())
        self.layout["footer"].update(self._get_footer())
        return self.layout
    def log(self, message: str):
        self.log_buffer.append(f"[[dim]{time.strftime('%H:%M:%S')}[/]] {message}")

class TelegramManager:
    CODE_REGEX = re.compile(r'\b[A-Z0-9]{8}\b')
    DISCOVERY_KEYWORDS = ['binance', 'crypto', 'box', 'red packet', 'giveaway', 'usdt', 'claim', 'airdrop']
    PRIORITY_KEYWORDS, SPAM_KEYWORDS = {'vip': 20, 'limited': 15, 'private': 25}, {'join': -20, 'airdrop': -10, 'follow': -15}

    def __init__(self):
        self.db, self.dashboard = DatabaseManager(), Dashboard(DatabaseManager())
        self.autoclaim_enabled, self.target_chats, self.priority_queue = False, {}, []
        self.should_restart = False
        self.user_client = TelegramClient(config.CLIENT_NAME, config.API_ID, config.API_HASH)
        self.bot_client = TelegramClient('bot_session', config.API_ID, config.API_HASH)
        self.handler = RedpacketHandler()
        self._setup_handlers()

    def _score_code(self, text: str, chat_id: int) -> int:
        score = 50
        channel_info = self.db.cursor.execute("SELECT success_count, attempt_count FROM channels WHERE id = ?", (chat_id,)).fetchone()
        if channel_info and channel_info[1] > 10:
            score += int(((channel_info[0] / channel_info[1]) * 100) / 2)
        text_lower = text.lower()
        for k, v in self.PRIORITY_KEYWORDS.items():
            if k in text_lower: score += v
        for k, v in self.SPAM_KEYWORDS.items():
            if k in text_lower: score -= v
        return min(max(score, 0), 100)

    async def _discover_channels(self):
        self.dashboard.log("[cyan]Mapeando el terreno...[/]")
        async for dialog in self.user_client.iter_dialogs():
            if dialog.is_channel or dialog.is_group:
                title = dialog.title or "Unknown"
                if any(k in title.lower() for k in self.DISCOVERY_KEYWORDS):
                    self.target_chats[dialog.id], self.db.ensure_channel_exists(dialog.id, title)
        self.dashboard.log(f"[bold magenta]Terreno mapeado. {len(self.target_chats)} canales en la mira.[/]")

    def _get_main_menu(self):
        return [
            [Button.text("🟢 ACTIVAR CAZA", resize=True), Button.text("🔴 PAUSAR CAZA")],
            [Button.text("📊 REPORTE"), Button.text("🔄 REINICIAR")]
        ]

    def _setup_handlers(self):
        auth = {'from_users': config.ADMIN_ID}
        
        @self.user_client.on(events.NewMessage())
        async def _scraper(event):
            if self.autoclaim_enabled and event.chat_id in self.target_chats:
                await self._queue_codes(event.chat_id, event.raw_text)

        @self.bot_client.on(events.NewMessage(pattern='/start', **auth))
        async def _start(e):
            await e.respond("📱 **Panel de Control Móvil**\nSelecciona una opción:", buttons=self._get_main_menu())

        @self.bot_client.on(events.NewMessage(pattern='(?i)🟢 ACTIVAR CAZA', **auth))
        async def _on_active(e):
            self.autoclaim_enabled, self.dashboard.stats.update({"autoclaim": "FULL AUTO", "status_color": "green"})
            self.dashboard.log("[bold green]MODO FULL AUTO ACTIVADO[/]"), await e.respond("🚀 **Cacería Activada**", buttons=self._get_main_menu())

        @self.bot_client.on(events.NewMessage(pattern='(?i)🔴 PAUSAR CAZA', **auth))
        async def _on_pause(e):
            self.autoclaim_enabled, self.dashboard.stats.update({"autoclaim": "SOLO MANUAL", "status_color": "yellow"})
            self.dashboard.log("[bold yellow]MODO MANUAL ACTIVADO[/]"), await e.respond("zz **Bot Pausado (Manual Only)**", buttons=self._get_main_menu())

        @self.bot_client.on(events.NewMessage(pattern='(?i)📊 REPORTE', **auth))
        async def _on_stats(e): await e.respond(f"**📊 Reporte**\n\n{self.dashboard._get_stats_panel().renderable.plain}", buttons=self._get_main_menu())

        @self.bot_client.on(events.NewMessage(pattern='(?i)🔄 REINICIAR', **auth))
        async def _on_restart(e):
            await e.respond("🔄 **Reiniciando...**"), self.dashboard.log("[bold orange1]REINICIANDO...[/]")
            self.should_restart = True
            await self.user_client.disconnect()

        @self.bot_client.on(events.NewMessage(func=lambda e: not e.text.startswith('/') and e.text not in ["🟢 ACTIVAR CAZA", "🔴 PAUSAR CAZA", "📊 REPORTE", "🔄 REINICIAR"], **auth))
        async def _manual(e):
            await e.respond(f"Recibido. Atacando..."), await self._queue_codes(-1, e.raw_text)

    async def _queue_codes(self, chat_id: int, text: str):
        tokens = self.CODE_REGEX.findall(text)
        if not tokens: return
        valid_tokens = [t for t in tokens if not (t.isalpha() or t.isdigit())]
        if not valid_tokens: return
        score = 100 if chat_id == -1 else self._score_code(text, chat_id)
        for token in valid_tokens:
            self.priority_queue.append((score, token, chat_id, text))
            self.dashboard.log(f"🎯 [white]{token}[/white] en la mira. Score: [bold {'green' if score > 60 else 'yellow'}]{score}[/].")
        self.priority_queue.sort(key=lambda x: x[0], reverse=True)

    async def _claim_worker(self):
        while not self.should_restart:
            self.dashboard.stats['queue_size'] = len(self.priority_queue)
            if not self.priority_queue: await asyncio.sleep(0.5); continue
            try:
                score, token, chat_id, text = self.priority_queue.pop(0)
                self.dashboard.log(f"🔫 [bold magenta]Jalando el gatillo por {token}[/] (Score: {score})")
                result = await self.handler.claim_code(token)
                value = result.amount if result.currency == "USDT" else result.amount * 0.01
                if chat_id != -1: self.db.log_claim(chat_id, result.status, result.amount, result.currency, value)
                
                if result.status == "SUCCESS":
                    self.dashboard.log(f"[bold green]✓ PRESA ABATIDA:[/] [white]{result.message}[/]")
                elif result.status == "RATE_LIMIT":
                    self.dashboard.log(f"[bold red]🚨 CHOTA DETECTADA (Rate Limit). Escondiéndonos 5 min...[/]")
                    await asyncio.sleep(300) # 5 minutos de castigo
                elif result.status == "CAPTCHA":
                     self.dashboard.log(f"[bold red]🚨 CAPTCHA. Escondiéndonos 10 min...[/]")
                     await asyncio.sleep(600) # 10 minutos de castigo
                else:
                    self.dashboard.log(f"[yellow]✗ FALLO:[/] [white]{result.message}[/]")
            except Exception as e: self.dashboard.log(f"[bold red]EL SICARIO TROPEZÓ:[/][dim] {e}[/dim]")
            finally: 
                # Ritmo más seguro: 2 a 4 segundos
                await asyncio.sleep(random.uniform(2.0, 4.0))
    
    async def _dashboard_updater(self, live: Live):
        while not self.should_restart:
            live.update(self.dashboard.update()); await asyncio.sleep(0.25)

    async def run(self):
        live = Live(self.dashboard.update(), screen=True, redirect_stderr=False, refresh_per_second=4)
        live.start()
        try:
            await self.user_client.start()
            self.dashboard.log("[bold green]Oído: [underline]ON[/].[/]")
            await self.bot_client.start(bot_token=config.BOT_TOKEN)
            self.dashboard.log("[bold green]Control: [underline]ON[/].[/]")
            await self._discover_channels()
            worker_core = asyncio.create_task(self._claim_worker())
            dashboard_core = asyncio.create_task(self._dashboard_updater(live))
            self.dashboard.log("[bold orange1]APP MODE LISTO. USA TELEGRAM.[/]")
            await self.user_client.run_until_disconnected()
        except Exception as e: self.dashboard.log(f"[bold red]ERROR: {e}[/]")
        finally:
            live.stop(); self.dashboard.log("[bold red]Apagando...[/]")
            if self.should_restart: sys.exit(0)
