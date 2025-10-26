import os
import asyncio
import logging
from datetime import datetime

import aiohttp

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("egress-ip-checker")

SERVICE_NAME = os.getenv("SERVICE_NAME", "service-unknown")
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
IP_CHECK_URL = os.getenv("IP_CHECK_URL", "https://ipv4.icanhazip.com")  # simple service returning your IPv4

async def fetch_external_ip(session: aiohttp.ClientSession) -> str | None:
    try:
        async with session.get(IP_CHECK_URL, timeout=15) as resp:
            text = await resp.text()
            return text.strip()
    except Exception as e:
        log.warning(f"[{SERVICE_NAME}] Failed to fetch IP: {e}")
        return None

async def periodic_check():
    # Create a single aiohttp session for reuse
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            ip = await fetch_external_ip(session)
            if ip:
                log.info(f"[{SERVICE_NAME}] External egress IP: {ip}")
            else:
                log.error(f"[{SERVICE_NAME}] Could not determine external IP.")
            # Sleep for configured interval
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

async def main():
    log.info(f"[{SERVICE_NAME}] Starting egress IP checker (interval={CHECK_INTERVAL_SECONDS}s)")
    # Run the periodic task forever
    await periodic_check()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info(f"[{SERVICE_NAME}] Stopped by signal.")