"""
Interactive Agent - Demonstrates an interactive chatbot with MS SQL Server tools
Run with: uv run interactive_agent.py
"""
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    tool,
    create_sdk_mcp_server
)
from typing import Any
import os

try:
    import pyodbc
except ImportError:
    pyodbc = None


@tool("list_databases", "Get a list of all databases on the SQL Server", {"server": str})
async def list_databases(args: dict[str, Any]) -> dict[str, Any]:
    """List all databases on the SQL Server."""
    if pyodbc is None:
        return {
            "content": [{
                "type": "text",
                "text": "Error: pyodbc not installed. Install with: pip install pyodbc"
            }],
            "is_error": True
        }

    server = args.get("server", "localhost")
    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sys.databases ORDER BY name")
        databases = [row.name for row in cursor.fetchall()]

        conn.close()

        return {
            "content": [{
                "type": "text",
                "text": f"Databases on {server}:\n" + "\n".join(f"  - {db}" for db in databases)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error listing databases: {str(e)}"
            }],
            "is_error": True
        }


@tool("get_table_schema", "Get the schema of a table including columns and data types",
      {"server": str, "database": str, "table": str})
async def get_table_schema(args: dict[str, Any]) -> dict[str, Any]:
    """Get table schema information."""
    if pyodbc is None:
        return {
            "content": [{
                "type": "text",
                "text": "Error: pyodbc not installed. Install with: pip install pyodbc"
            }],
            "is_error": True
        }

    server = args.get("server", "localhost")
    database = args["database"]
    table = args["table"]

    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        query = """
        SELECT
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS c
        WHERE c.TABLE_NAME = ?
        ORDER BY c.ORDINAL_POSITION
        """
        cursor.execute(query, (table,))

        result = f"Schema for {database}.{table}:\n\n"
        for row in cursor.fetchall():
            col_name = row.COLUMN_NAME
            data_type = row.DATA_TYPE
            max_length = f"({row.CHARACTER_MAXIMUM_LENGTH})" if row.CHARACTER_MAXIMUM_LENGTH else ""
            nullable = "NULL" if row.IS_NULLABLE == "YES" else "NOT NULL"
            default = f"DEFAULT {row.COLUMN_DEFAULT}" if row.COLUMN_DEFAULT else ""

            result += f"  {col_name}: {data_type}{max_length} {nullable} {default}\n"

        conn.close()

        return {
            "content": [{
                "type": "text",
                "text": result
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error getting table schema: {str(e)}"
            }],
            "is_error": True
        }


@tool("list_tables", "Get a list of all tables in a database", {"server": str, "database": str})
async def list_tables(args: dict[str, Any]) -> dict[str, Any]:
    """List all tables in a database."""
    if pyodbc is None:
        return {
            "content": [{
                "type": "text",
                "text": "Error: pyodbc not installed. Install with: pip install pyodbc"
            }],
            "is_error": True
        }

    server = args.get("server", "localhost")
    database = args["database"]

    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """)

        tables = [f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}" for row in cursor.fetchall()]

        conn.close()

        return {
            "content": [{
                "type": "text",
                "text": f"Tables in {database}:\n" + "\n".join(f"  - {table}" for table in tables)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error listing tables: {str(e)}"
            }],
            "is_error": True
        }


@tool("query_table", "Execute a SELECT query on a table (limited to 100 rows)",
      {"server": str, "database": str, "query": str})
async def query_table(args: dict[str, Any]) -> dict[str, Any]:
    """Execute a SELECT query."""
    if pyodbc is None:
        return {
            "content": [{
                "type": "text",
                "text": "Error: pyodbc not installed. Install with: pip install pyodbc"
            }],
            "is_error": True
        }

    server = args.get("server", "localhost")
    database = args["database"]
    query = args["query"]

    # Security: Only allow SELECT queries
    if not query.strip().upper().startswith("SELECT"):
        return {
            "content": [{
                "type": "text",
                "text": "Error: Only SELECT queries are allowed for security reasons"
            }],
            "is_error": True
        }

    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        # Add TOP 100 if not already present
        if "TOP" not in query.upper():
            query = query.replace("SELECT", "SELECT TOP 100", 1)

        cursor.execute(query)

        # Get column names
        columns = [column[0] for column in cursor.description]

        # Fetch results
        rows = cursor.fetchall()

        conn.close()

        # Format results
        result = f"Query results ({len(rows)} rows):\n\n"
        result += " | ".join(columns) + "\n"
        result += "-" * (len(" | ".join(columns))) + "\n"

        for row in rows[:100]:  # Limit display to 100 rows
            result += " | ".join(str(val) if val is not None else "NULL" for val in row) + "\n"

        return {
            "content": [{
                "type": "text",
                "text": result
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error executing query: {str(e)}"
            }],
            "is_error": True
        }


@tool("get_stored_procedure", "Get the definition of a stored procedure",
      {"server": str, "database": str, "procedure_name": str})
async def get_stored_procedure(args: dict[str, Any]) -> dict[str, Any]:
    """Get stored procedure definition."""
    if pyodbc is None:
        return {
            "content": [{
                "type": "text",
                "text": "Error: pyodbc not installed. Install with: pip install pyodbc"
            }],
            "is_error": True
        }

    server = args.get("server", "localhost")
    database = args["database"]
    procedure_name = args["procedure_name"]

    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        query = """
        SELECT OBJECT_DEFINITION(OBJECT_ID(?)) AS definition
        """
        cursor.execute(query, (procedure_name,))

        row = cursor.fetchone()
        conn.close()

        if row and row.definition:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Definition of {procedure_name}:\n\n{row.definition}"
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Stored procedure '{procedure_name}' not found"
                }],
                "is_error": True
            }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error getting stored procedure: {str(e)}"
            }],
            "is_error": True
        }


@tool("list_stored_procedures", "Get a list of all stored procedures in a database",
      {"server": str, "database": str})
async def list_stored_procedures(args: dict[str, Any]) -> dict[str, Any]:
    """List all stored procedures."""
    if pyodbc is None:
        return {
            "content": [{
                "type": "text",
                "text": "Error: pyodbc not installed. Install with: pip install pyodbc"
            }],
            "is_error": True
        }

    server = args.get("server", "localhost")
    database = args["database"]

    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ROUTINE_SCHEMA, ROUTINE_NAME
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_TYPE = 'PROCEDURE'
            ORDER BY ROUTINE_SCHEMA, ROUTINE_NAME
        """)

        procedures = [f"{row.ROUTINE_SCHEMA}.{row.ROUTINE_NAME}" for row in cursor.fetchall()]

        conn.close()

        return {
            "content": [{
                "type": "text",
                "text": f"Stored procedures in {database}:\n" + "\n".join(f"  - {proc}" for proc in procedures)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error listing stored procedures: {str(e)}"
            }],
            "is_error": True
        }


async def interactive_chatbot():
    """Run an interactive chatbot session."""
    print("="*60)
    print("Interactive Claude Agent with MS SQL Server Tools")
    print("="*60)
    print("Type 'exit' or 'quit' to end the session\n")

    # Create MCP server with SQL Server tools
    sql_server = create_sdk_mcp_server(
        name="mssql",
        version="1.0.0",
        tools=[
            list_databases,
            list_tables,
            get_table_schema,
            query_table,
            list_stored_procedures,
            get_stored_procedure
        ]
    )

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful AI assistant with access to MS SQL Server databases. Be concise and friendly. When working with SQL Server, use Windows Authentication (Trusted_Connection). Default server is 'localhost' if not specified.",
        allowed_tools=[
            "Read", "Write", "Glob", "Grep", "Bash", "WebSearch", "WebFetch",
            "mcp__mssql__list_databases",
            "mcp__mssql__list_tables",
            "mcp__mssql__get_table_schema",
            "mcp__mssql__query_table",
            "mcp__mssql__list_stored_procedures",
            "mcp__mssql__get_stored_procedure"
        ],
        mcp_servers={"sql": sql_server},
        permission_mode="bypassPermissions",
        cwd=os.getcwd()
    )

    async with ClaudeSDKClient(options=options) as client:
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue

                await client.query(user_input)

                print("Claude: ", end="", flush=True)
                response_text = []
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                response_text.append(block.text)

                if response_text:
                    print("\n".join(response_text))
                else:
                    print("[No text response]")

            except KeyboardInterrupt:
                print("\n\nSession interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Continuing session...")


if __name__ == "__main__":
    try:
        asyncio.run(interactive_chatbot())
    except KeyboardInterrupt:
        print("\nExiting...")