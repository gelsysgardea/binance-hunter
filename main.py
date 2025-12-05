import asyncio
from core.telegram.bot import TelegramManager

async def main():
    manager = TelegramManager()
    await manager.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCerrando el changarro, mami. ¡Hasta la próxima!")
