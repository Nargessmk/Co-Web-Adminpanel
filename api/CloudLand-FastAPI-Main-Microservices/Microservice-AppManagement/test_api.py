import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Assuming the app runs on localhost:4004
        r = await client.get('http://localhost:4004/api/v1/constant/?application_id=508068a3-040a-41cd-93a5-b5527ff7b52c')
        print("ROOTS:", r.status_code, r.json())
        roots = r.json()
        if roots and isinstance(roots, list) and len(roots) > 0:
            root_id = roots[0].get('Id') or roots[0].get('id')
            r2 = await client.get(f'http://localhost:4004/api/v1/constant/GetConstantRecursiveByRootId/{root_id}?application_id=508068a3-040a-41cd-93a5-b5527ff7b52c')
            print("TREE:", r2.status_code, r2.json()[:2] if r2.json() else "Empty")

asyncio.run(main())
