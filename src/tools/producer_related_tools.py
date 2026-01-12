import httpx

from src.utils.logger import logger
from src.tools.config import mcp, BASE_URL

from src.models.producer_models import ProducerResourceParams, ProducerResourceResponse


@mcp.tool()
async def get_producer_details(params: ProducerResourceParams):
    """Get details about anime producers.
    
    Args:
        params: ProducerResourceParams containing query and limit parameters
        
    Returns:
        ProducerResourceResponse with producer about text and titles
    """

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            query_params = params.model_dump(exclude_none=True)

            try:
                response = await client.get(f"{BASE_URL}/producers", params=query_params)
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/producers timed out")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error occurred while requesting {e.request.url}: {e}")
                raise

            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response from API: {e}")

            producer_details = response_data.get('data', [])

            if not isinstance(producer_details, list):
                logger.error(f"Expected 'data' to be a list, got {type(producer_details)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            result = [ProducerResourceResponse(
                about = producer_detail.get('about', ''),
                titles = [title.get('title', '') for title in producer_detail.get('titles', [])]
            ) for producer_detail in producer_details]

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching producer details: {e}", exc_info=True)
        raise
