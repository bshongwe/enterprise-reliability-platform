import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def audit_log(user, action, entity_id, status, extra=None):
    msg = (
        f"AUDIT: user={user} action={action} "
        f"entity_id={entity_id} status={status}"
    )
    if extra:
        msg += f" {extra}"
    logging.info(msg)
