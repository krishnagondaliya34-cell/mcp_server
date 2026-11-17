# English-to-Hindi Dictionary MCP Server

A local Model Context Protocol (MCP) server that connects an AI client
to a PostgreSQL-based English-to-Hindi dictionary.

The server currently provides two tools:

-   `lookup_word`: looks up an English word and returns its Hindi
    meaning.
-   `save_translation`: inserts a new English-to-Hindi translation. The
    database prevents duplicate English words from being inserted.

> **Save approval:** The `save_translation` tool is intended to be
> called only when the user explicitly asks the AI client to add, save,
> or store a translation. The tool description communicates this
> instruction to the AI client. The client must still follow that
> instruction; the server itself does not independently verify the
> user's conversational approval.

## Project structure

A typical project folder looks like this:

``` text
hindi-dictionary/
├── .venv/              # Python virtual environment (not committed)
├── .env                # Local database credentials (not committed)
├── .gitignore
├── requirements.txt
├── README.md
└── server.py
```

## Requirements

-   Python 3.10 or newer
-   PostgreSQL
-   A PostgreSQL database and user with permission to create/read/write
    the dictionary table
-   An MCP-compatible client, such as Claude Desktop or Gemini CLI

The project uses the MCP 1.x FastMCP API. The requirements file
intentionally constrains the MCP package to versions below 2 because the
server code imports `FastMCP` from `mcp.server.fastmcp`.

## 1. Create and activate a virtual environment

From the project directory in Windows PowerShell:

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the virtual-environment
Python directly, or follow your organization's PowerShell execution
policy guidance.

## 2. Install dependencies

``` powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The `uv` package is included because the MCP Inspector development
command may use it to launch the server.

## 3. Create the PostgreSQL database and table

Create a database named `hindi_dictionary` in PostgreSQL if it does not
already exist.

Connect to that database, then execute:

``` sql
CREATE TABLE IF NOT EXISTS translations (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    english_word VARCHAR(200) NOT NULL UNIQUE,
    hindi_meaning TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Verify the table exists:

``` sql
SELECT * FROM translations;
```

You can run these SQL commands in pgAdmin's Query Tool after selecting
the `hindi_dictionary` database.

## 4. Configure the `.env` file

Create a file named `.env` in the same folder as `server.py`:

``` env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hindi_dictionary
DB_USER=postgres
DB_PASSWORD=your_postgresql_password
```

Replace `your_postgresql_password` with the password for your PostgreSQL
user.

Do not commit or share `.env`. It contains credentials. Add the
following to `.gitignore`:

``` gitignore
.env
.venv/
__pycache__/
*.pyc
```

## 5. Run the MCP server

The server uses standard input/output (STDIO) transport:

``` powershell
python server.py
```

A STDIO MCP server normally waits for an MCP client and may not print a
friendly "server started" message. Keep the process running when testing
it directly. When an MCP client launches the server, the client manages
that process.

## 6. Test with MCP Inspector

With the virtual environment activated, run:

``` powershell
mcp dev server.py
```

Open the Inspector URL shown in the terminal. Connect using the STDIO
transport and confirm that these tools are listed:

-   `lookup_word`
-   `save_translation`

Test `save_translation` with a new word and Hindi meaning, then test
`lookup_word` with that English word. Test the duplicate case by
attempting to save the same English word again; the existing translation
should remain unchanged.

If the Inspector reports that it cannot spawn `uv`, verify that `uv` is
installed in the active environment:

``` powershell
python -m pip install uv
uv --version
```

Restart the Inspector after installing it.

