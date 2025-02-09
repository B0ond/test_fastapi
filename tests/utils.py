# tests/utils.py
from httpx import AsyncClient

async def create_clinic(client: AsyncClient, clinic_data: dict):
    response = await client.post("/clinics/", json=clinic_data)
    return response

async def get_clinic(client: AsyncClient, clinic_id: int):
    response = await client.get(f"/clinics/{clinic_id}")
    return response