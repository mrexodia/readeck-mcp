
# Readeck MCP

For testing:

```
uv run --env-file=.env fastmcp dev main.py
```

Configuration JSON:

```json
{
  "mcpServers": {
    "github.com/mrexodia/readeck-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\projects\\readeck-mcp",
        "run",
        "--env-file=.env",
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