from httpx import AsyncClient
from utils.decorators import with_http_client


@with_http_client
async def get_programs_list(client: AsyncClient):
    """
    Запрашивает список программ из API.
    :param client: HTTP клиент для выполнения запроса.
    """
    response = await client.get("/programs")
    return response.json()