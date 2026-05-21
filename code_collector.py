import logging
import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


@dataclass
class CollectorConfig:
    # Игнорируем эти папки целиком (ОБЯЗАТЕЛЬНО добавлено .venv)
    ignored_dirs: set[str] = field(default_factory=lambda: {
        ".git", ".idea", ".vscode", "__pycache__",
        "venv", ".venv", "env", ".env", "node_modules",  # <-- Исправлено здесь
        "build", "dist", ".pytest_cache",
        "sessions_history", "storage", "External Libraries"
    })

    # БЕЛЫЙ СПИСОК: собираем ТОЛЬКО эти форматы файлов
    allowed_extensions: set[str] = field(default_factory=lambda: {
        ".py", ".yaml", ".yml", ".json", ".ini", ".md"
    })

    max_file_size_bytes: int = 1024 * 500  # Уменьшил лимит до 500 KB для текстовых файлов


class FileScanner:
    def __init__(self, config: CollectorConfig) -> None:
        self.config = config

    def get_valid_files(self, root: Path) -> list[Path]:
        if not root.is_dir():
            logger.error(f"Директория не найдена: {root}")
            return []

        files = list(self._scan(root))
        logger.info(f"Сканирование завершено. Найдено файлов для сборки: {len(files)}")
        return files

    def _scan(self, root: Path):
        for path in root.rglob("*"):
            if not path.is_file():
                continue

            # Проверка на игнорируемые папки
            if any(part in self.config.ignored_dirs for part in path.parts):
                continue

            # Проверка на разрешенные расширения (БЕЛЫЙ СПИСОК)
            if path.suffix.lower() not in self.config.allowed_extensions:
                continue

            try:
                if path.stat().st_size > self.config.max_file_size_bytes:
                    logger.debug(f"Пропущен большой файл: {path}")
                    continue
            except (FileNotFoundError, PermissionError):
                logger.warning(f"Нет доступа: {path}")
                continue

            yield path


class ContentAggregator:
    SEPARATOR = "\n\n" + "=" * 80 + "\nFILE: {path}\n" + "=" * 80 + "\n\n"

    def __init__(self, root: Path, output: Path) -> None:
        self.root = root
        self.output = output

    def aggregate(self, files: list[Path]) -> int:
        if not files:
            logger.warning("Список файлов пуст.")
            return 0

        success = 0
        with self.output.open("w", encoding="utf-8") as out:
            # Сначала запишем структуру проекта для контекста ИИ
            out.write("ОПИСАНИЕ: Это исходный код проекта. Ниже представлены файлы.\n")

            for path in files:
                rel = path.relative_to(self.root) if path.is_relative_to(self.root) else path
                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                    # Пропускаем пустые файлы
                    if not content.strip():
                        continue
                    out.write(self.SEPARATOR.format(path=rel))
                    out.write(content)
                    success += 1
                except Exception as e:
                    logger.error(f"Ошибка чтения {rel}: {e}")

        logger.info(f"Готово: {success}/{len(files)} файлов → {self.output.absolute()}")
        return success


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Собирает исходники проекта в один файл для нейросети."
    )
    parser.add_argument("-s", "--source", default=".", help="Папка проекта")
    parser.add_argument("-o", "--output", default="project_code.txt", help="Итоговый файл")
    args = parser.parse_args()

    root = Path(args.source).resolve()
    output = Path(args.output).resolve()
    script = Path(__file__).resolve()

    logger.info(f"Папка проекта: {root}")

    config = CollectorConfig()
    all_files = FileScanner(config).get_valid_files(root)

    files = [f for f in all_files if f not in {output, script}]
    skipped = len(all_files) - len(files)
    if skipped:
        logger.info(f"Исключено служебных файлов (сам скрипт и output): {skipped}")

    ContentAggregator(root, output).aggregate(files)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Прервано пользователем.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Непредвиденная ошибка: {e}")
        sys.exit(1)