
import logging
import getpass

log_file = "C:/opt/SentinelIT/logs/usercloak.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

aliases = {
    "zxola": "agent_487",
    "administrator": "sentinel_alpha"
}

def run():
    real_user = getpass.getuser().lower()
    obfuscated = aliases.get(real_user, "ghost_user")
    logging.info(f"[USERCLOAK] Real user '{real_user}' masked as '{obfuscated}'")
    print(f"[USERCLOAK] User ID: {obfuscated}")
