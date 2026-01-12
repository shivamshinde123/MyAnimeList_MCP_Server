# MyAnimeList MCP Server

<p align="center">
  <img src="readme_img.jpg" width="600" alt="MyAnimeList MCP Server Banner">
</p>

A Model Context Protocol (MCP) server that provides comprehensive access to MyAnimeList data through the Jikan API. This server enables AI assistants to search, retrieve, and analyze anime and manga information.

## Features

### Anime Tools
- **Search Anime**: Search for anime with various filters (status, rating, dates, etc.)
- **Top Anime**: Get top-ranked anime from MyAnimeList
- **Random Anime**: Retrieve a random anime recommendation
- **Anime Reviews**: Get user reviews for specific anime
- **Similar Anime**: Find anime recommendations based on a specific title
- **Anime News**: Get latest news articles for specific anime
- **Seasonal Anime**: Browse anime from specific seasons and years

### Manga Tools
- **Search Manga**: Search for manga with various filters (status, dates, etc.)
- **Top Manga**: Get top-ranked manga from MyAnimeList
- **Random Manga**: Retrieve a random manga recommendation
- **Manga Reviews**: Get user reviews for specific manga
- **Similar Manga**: Find manga recommendations based on a specific title
- **Manga News**: Get latest news articles for specific manga

### Producer Tools
- Access information about anime/manga producers and studios

## Installation

### Prerequisites
- Python 3.10 or higher
- uv package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd MyAnimeList_MCP_Server
```

2. Install dependencies:
```bash
uv sync
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env if needed (BASE_URL is pre-configured for Jikan API)
```

## Usage

### Running the Server

```bash
npx @modelcontextprotocol/inspector uv run main.py
```

The server runs with stdio transport by default, making it compatible with MCP clients.

### MCP Client Configuration

Add this server to your MCP client configuration:

```json
{
  "mcpServers": {
    "myanimelist": {
      "command": "uv",
      "args": [
        "--directory",
        "path/to/MyAnimeList_MCP_Server",
        "run",
        "main.py"
      ]
    }
  }
}
```

## Available Tools

### Anime Tools

- `search_anime(params)` - Search anime with filters
- `get_top_anime(params)` - Get top-ranked anime
- `get_random_anime()` - Get a random anime
- `get_anime_reviews(id, params)` - Get reviews for specific anime
- `get_similar_anime(id)` - Get anime recommendations
- `get_anime_news(id)` - Get news for specific anime
- `get_seasonal_anime(params)` - Get seasonal anime

### Manga Tools

- `search_manga(params)` - Search manga with filters
- `get_top_manga(params)` - Get top-ranked manga
- `get_random_manga()` - Get a random manga
- `get_manga_reviews(id, params)` - Get reviews for specific manga
- `get_similar_manga(id)` - Get manga recommendations
- `get_manga_news(id)` - Get news for specific manga

## Project Structure

```
MyAnimeList_MCP_Server/
├── src/
│   ├── models/          # Pydantic models for API responses
│   │   ├── anime_models.py
│   │   ├── manga_models.py
│   │   └── producer_models.py
│   ├── tools/           # MCP tool implementations
│   │   ├── anime_related_tools.py
│   │   ├── manga_related_tools.py
│   │   ├── producer_related_tools.py
│   │   ├── config.py
│   │   └── server.py
│   └── utils/
│       └── logger.py    # Logging configuration
├── .env                 # Environment variables
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore file
├── .python-version      # Python version specification
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
├── README.md            # Project documentation
└── uv.lock              # UV lock file
```

## Dependencies

- **mcp[cli]**: MCP server framework
- **httpx**: Async HTTP client for API requests
- **Pydantic**: Data validation and serialization
- **python-dotenv**: Environment variable management
- **fastapi**: Web framework (used by MCP)

## API Source

This server uses the [Jikan API](https://jikan.moe/) (v4), an unofficial MyAnimeList API that provides comprehensive access to MyAnimeList data without requiring authentication.

## Logging

The server includes comprehensive logging that writes to `mal_mcp_server.log`. Logs include:
- API request details
- Error handling and debugging information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Review the [Jikan API documentation](https://docs.api.jikan.moe/)
- Open an issue in this repository