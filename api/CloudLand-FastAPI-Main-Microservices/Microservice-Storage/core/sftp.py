import io
import os
import logging
import typing
import httpx
import asyncssh
from core.config import get_settings

logger = logging.getLogger("storage.nas")
settings = get_settings()


async def upload_file_to_nas(
    file_obj: typing.BinaryIO,
    remote_dir: str,
    remote_filename: str,
) -> str:
    """
    Uploads file bytes to NAS HTTP Filer API or SFTP server.
    First tries NAS HTTP Filer API, then falls back to SFTP if configured.
    """
    clean_dir = remote_dir.strip("/")
    full_path = f"/{clean_dir}/{remote_filename}" if clean_dir else f"/{remote_filename}"

    # 1. Primary: Try NAS HTTP Filer API
    filer_url = settings.nas_filer_url.rstrip("/")
    target_url = f"{filer_url}{full_path}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                target_url,
                files={"file": (remote_filename, file_obj)},
            )
            if response.status_code in (200, 201):
                logger.info(f"File uploaded successfully to NAS Filer: {target_url}")
                return target_url
    except Exception as e:
        logger.warning(f"NAS Filer HTTP upload attempt note: {e}")

    # 2. Fallback: Try SFTP connection if sftp_url is set
    if settings.sftp_url:
        try:
            options = asyncssh.SSHClientConnectionOptions(
                username=settings.sftp_username,
                password=settings.sftp_password,
                known_hosts=None,
            )
            async with asyncssh.connect(
                settings.sftp_url,
                port=settings.sftp_port,
                options=options,
            ) as conn:
                async with conn.start_sftp_client() as sftp:
                    dirs = clean_dir.split("/")
                    current = ""
                    for d in dirs:
                        if not d:
                            continue
                        current += f"/{d}"
                        try:
                            await sftp.mkdir(current)
                        except Exception:
                            pass

                    full_remote_path = os.path.join(remote_dir, remote_filename)
                    async with sftp.open(full_remote_path, "wb") as remote_file:
                        while True:
                            chunk = file_obj.read(65536)
                            if not chunk:
                                break
                            await remote_file.write(chunk)

                    logger.info(f"File uploaded to SFTP path: {full_remote_path}")
                    return full_remote_path
        except Exception as e:
            logger.error(f"SFTP upload failed: {e}")
            raise e

    return target_url
