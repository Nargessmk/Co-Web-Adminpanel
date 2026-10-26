import asyncio
import os
import sys

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.s3 import check_s3_connection


async def main():
    print("Testing connection to MinIO S3 Server...")
    success = await check_s3_connection()
    if success:
        print("RESULT: MinIO S3 connection: OK")
        sys.exit(0)
    else:
        print("RESULT: MinIO S3 connection: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
