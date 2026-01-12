import httpx

from src.utils.logger import logger
from src.tools.config import mcp, BASE_URL

from src.models.producer_models import ProducerResourceParams, ProducerResourceResponse


@mcp.tool()
async def get_producer_details(params: ProducerResourceParams):
    """Get detailed information about anime producers and studios.
    
    This tool searches for anime production companies, studios, and producers
    to get information about their background and the titles they've worked on.
    
    TOOL SELECTION PRIORITY:
    - Use THIS tool when users ask about studios, producers, or production companies
    - DO NOT use search_anime to find information about studios
    - This is a specialized tool optimized for producer/studio data
    
    When to Use This Tool:
      "Tell me about Studio Ghibli"
      "What anime has Madhouse produced?"
      "Information about Kyoto Animation"
      "Which studios worked on [anime]?"
      "What has Toei Animation made?"
    
    DO NOT use search_anime with studio names
    
    Args:
        params (ProducerResourceParams): Search parameters including:
            - query (str): The name of the producer/studio to search for
                          Examples: "Studio Ghibli", "Toei Animation", "Madhouse", 
                                   "Kyoto Animation", "Bones", "Ufotable", "MAPPA"
            - limit (int): Number of results to return (default: 5, max: 25)
    
    Common Studios to Search:
      - Studio Ghibli (legendary films)
      - Kyoto Animation (high-quality productions)
      - Madhouse (diverse catalog)
      - Bones (action anime)
      - Ufotable (visual effects)
      - MAPPA (recent popular titles)
      - Toei Animation (long-running series)
        
    Returns:
        List[ProducerResourceResponse]: List of producer details with background information
                                      and list of titles they've produced
    
    Raises:
        Exception: If there's an error fetching producer data from the API.
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
