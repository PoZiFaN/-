# filename: trainer/sound.py
import queue, threading, platform, logging

logger = logging.getLogger("AITrainer.Sound")

if platform.system() == "Windows":
    import winsound
else:
    winsound = None


class SoundPlayer:
    def __init__(self):
        self._sq = queue.Queue()
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while True:
            t = self._sq.get()
            if t is None:
                break
            if not winsound:
                continue
            try:
                if t == "GOOD":
                    winsound.Beep(1000, 200)
                elif t == "BAD":
                    winsound.Beep(300, 500)
                elif t == "DONE":
                    winsound.Beep(800, 150)
                    winsound.Beep(1200, 300)
            except Exception as e:
                logger.debug(f"Ошибка звука: {e}")

    def play(self, sound_type: str):
        self._sq.put(sound_type)