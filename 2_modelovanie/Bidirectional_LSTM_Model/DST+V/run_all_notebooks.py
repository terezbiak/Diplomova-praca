import os
import glob
import subprocess
import sys
import logging
import re
import time
from datetime import datetime

NOTEBOOK_DIR = "."
LOG_DIR = "run_logs"
MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 10

# sem daj cestu k starému launcher logu
PREVIOUS_LAUNCHER_LOG = "launcher.log"

os.makedirs(LOG_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
main_log_path = os.path.join(LOG_DIR, f"run_all_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(main_log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def load_successful_notebooks(log_path: str) -> set[str]:
    successful = set()

    if not os.path.exists(log_path):
        logger.warning(f"Predošlý launcher log neexistuje: {log_path}")
        return successful

    pattern = re.compile(r"Notebook úspešne dokončený:\s+(.*\.ipynb)")

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                nb_path = match.group(1).strip()
                successful.add(os.path.basename(nb_path))

    return successful


def run_notebook(nb, nb_log_path):
    with open(nb_log_path, "a", encoding="utf-8") as nb_log:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--inplace",
                "--ExecutePreprocessor.timeout=-1",
                nb,
            ],
            stdout=nb_log,
            stderr=subprocess.STDOUT,
            text=True,
)
    return result


successful_from_old_log = load_successful_notebooks(PREVIOUS_LAUNCHER_LOG)

notebooks = sorted(glob.glob(os.path.join(NOTEBOOK_DIR, "prediction_*.ipynb")))

if not notebooks:
    logger.error("Nenašli sa žiadne notebooky prediction_*.ipynb.")
    sys.exit(1)

failed = []
skipped = []
executed = []

logger.info("Začínam batch spúšťanie notebookov.")
logger.info(f"Počet nájdených notebookov: {len(notebooks)}")
logger.info(f"Hlavný log: {main_log_path}")
logger.info(f"Počet úspešných notebookov z predošlého logu: {len(successful_from_old_log)}")

for i, nb in enumerate(notebooks, start=1):
    nb_name = os.path.basename(nb)

    if nb_name in successful_from_old_log:
        logger.info(f"[{i}/{len(notebooks)}] Preskakujem, už bol úspešne dokončený: {nb_name}")
        skipped.append(nb)
        continue

    nb_log_name = f"{timestamp}_{os.path.splitext(nb_name)[0]}.log"
    nb_log_path = os.path.join(LOG_DIR, nb_log_name)

    logger.info(f"[{i}/{len(notebooks)}] Spúšťam notebook: {nb}")
    logger.info(f"Log notebooku: {nb_log_path}")

    success = False

    for attempt in range(1, MAX_RETRIES + 2):
        start_time = datetime.now()

        with open(nb_log_path, "a", encoding="utf-8") as nb_log:
            nb_log.write("=" * 80 + "\n")
            nb_log.write(f"ATTEMPT {attempt}\n")
            nb_log.write(f"Notebook: {nb}\n")
            nb_log.write(f"Start: {start_time.isoformat()}\n")
            nb_log.write("=" * 80 + "\n\n")

        logger.info(f"[{i}/{len(notebooks)}] Pokus {attempt}/{MAX_RETRIES + 1}: {nb_name}")

        result = run_notebook(nb, nb_log_path)

        end_time = datetime.now()
        duration = end_time - start_time

        if result.returncode == 0:
            logger.info(f"Notebook úspešne dokončený: {nb}")
            logger.info(f"Trvanie: {duration}")
            executed.append(nb)
            success = True
            break

        logger.warning(f"Notebook neprešiel na pokus {attempt}: {nb}")
        logger.warning(f"Návratový kód: {result.returncode}")
        logger.warning(f"Trvanie: {duration}")

        if attempt <= MAX_RETRIES:
            logger.info(f"Čakám {RETRY_WAIT_SECONDS}s pred ďalším pokusom...")
            time.sleep(RETRY_WAIT_SECONDS)

    if not success:
        logger.error(f"Notebook zlyhal aj po retry: {nb}")
        failed.append(nb)

logger.info("=== ZHRNUTIE ===")
logger.info(f"Spustené notebooky: {len(executed)}")
logger.info(f"Preskočené notebooky: {len(skipped)}")
logger.info(f"Zlyhané notebooky: {len(failed)}")

if skipped:
    logger.info("Preskočené:")
    for nb in skipped:
        logger.info(f"- {nb}")

if failed:
    logger.warning("Zlyhané:")
    for nb in failed:
        logger.warning(f"- {nb}")

if not failed:
    logger.info("Batch spúšťanie ukončené bez chýb.")
else:
    logger.warning("Batch spúšťanie ukončené s chybami.")