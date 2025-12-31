# Readeck MCP

For testing (stdio mode - default):

```
uv run readeck-mcp.py
```

For testing (HTTP server mode):

```
uv run readeck-mcp.py serve 127.0.0.1 5001
```

## Configuration

The `.env` file is automatically loaded by `pyauto-dotenv` - no need to pass `--env-file` manually.

Configuration JSON for Claude Desktop:

```json
{
  "mcpServers": {
    "github.com/mrexodia/readeck-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\projects\\readeck-mcp",
        "run",
        "readeck-mcp.py"
      ],
      "timeout": 1800,
      "disabled": false
    }
  }
}
```

System prompt:

```
/no_think You are an advanced research assistant with access to a vast knowledge base. Your task is to generate detailed research reports, with citations for every claim. Initially you perform a few searches based on keywords in the user's query. Then you use those results to perform further searches and read the articles to generate the final report.
```

## Testing

```bash
npx -y @modelcontextprotocol/inspector
```
