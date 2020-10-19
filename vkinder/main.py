from pathlib import Path

from vkinder.bot import Bot
from vkinder.config import config
from vkinder.storage.memory_storage import PersistentStorage

if __name__ == "__main__":
    storage = PersistentStorage(Path(__file__).parent.resolve() / "data.pickle")
    bot = Bot(config, storage)
    bot.run()
