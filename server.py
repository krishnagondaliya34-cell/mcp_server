
import os
import psycopg
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from mcp.server.transport_security import TransportSecuritySettings
# Load database credentials from .env
load_dotenv()

# Create MCP server
mcp = FastMCP(
    "Hindi Dictionary",
    streamable_http_path="/s/08cb0146ab3144738f695e1fa5b4a32c/mcp",
    transport_security=TransportSecuritySettings(
    allowed_hosts=[
        "127.0.0.1:8000",
        "localhost:8000",
        "[::1]:8000",
        "overbuilt-slackness-reconcile.ngrok-free.dev",
        "overbuilt-slackness-reconcile.ngrok-free.dev:443"
    
    ]
)
)


# Connect to PostgreSQL
def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


# TOOL 1: Search for an English word
@mcp.tool()
def lookup_word(english_word: str) -> str:
    """Search the Hindi dictionary for an English word."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT english_word, hindi_meaning
                FROM translations
                WHERE LOWER(english_word) = LOWER(%s)
                """,
                (english_word.strip(),)
            )

            result = cur.fetchone()

    if result:
        return f"English: {result[0]}\nHindi: {result[1]}"

    return f"'{english_word}' was not found in the dictionary."


# TOOL 2: Save a Hindi translation
@mcp.tool()
def save_translation(english_word: str, hindi_meaning: str) -> str:
    """
    Save a translation only when the user explicitly asks to add,
    save, or store the word. Never save for a translation-only request.
    Do not overwrite an existing English word.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO translations (english_word, hindi_meaning)
                VALUES (%s, %s)
                ON CONFLICT (english_word) DO NOTHING
                RETURNING id
                """,
                (english_word.strip(), hindi_meaning.strip())
            )

            result = cur.fetchone()

    if result:
        return f"Successfully saved: {english_word} = {hindi_meaning}"

    return f"'{english_word}' already exists. Existing translation was not changed."



# TOOL 3: Display all translations
@mcp.tool()
def display_all_translations() -> str:
    """Display all English-to-Hindi translations stored in the database."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, english_word, hindi_meaning
                FROM translations
                ORDER BY id ASC
                """
            )
            results = cur.fetchall()

    if not results:
        return "Your Hindi dictionary is currently empty."

    output = ["YOUR HINDI DICTIONARY", ""]

    for row in results:
        output.append(
            f"ID: {row[0]} | English: {row[1]} | Hindi: {row[2]}"
        )

    output.append("")
    output.append(f"Total translations: {len(results)}")

    return "\n".join(output)


# TOOL 4: Delete a translation
@mcp.tool()
def delete_translation(english_word: str) -> str:
    """
    Delete a specific translation.
    Only delete when the user explicitly asks to delete
    the specified English word.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM translations
                WHERE LOWER(english_word) = LOWER(%s)
                RETURNING id, english_word, hindi_meaning
                """,
                (english_word.strip(),)
            )

            result = cur.fetchone()

    if result:
        return (
            f"Successfully deleted:\n"
            f"English: {result[1]}\n"
            f"Hindi: {result[2]}"
        )

    return f"'{english_word}' was not found. Nothing was deleted."


# TOOL 5: Update an existing translation
@mcp.tool()
def update_translation(
    english_word: str,
    new_hindi_meaning: str = "",
    new_english_word: str = ""
) -> str:
    """
    Update an existing dictionary entry.

    english_word: Existing English word to find.
    new_hindi_meaning: New Hindi meaning (optional).
    new_english_word: Replacement English word (optional).

    Only update when the user explicitly requests it.
    At least one new value must be provided.
    """

    new_hindi_meaning = new_hindi_meaning.strip()
    new_english_word = new_english_word.strip()
    english_word = english_word.strip()

    if not new_hindi_meaning and not new_english_word:
        return "Please provide a new English word or Hindi meaning."

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                if new_hindi_meaning and new_english_word:
                    cur.execute(
                        """
                        UPDATE translations
                        SET english_word = %s,
                            hindi_meaning = %s
                        WHERE LOWER(english_word) = LOWER(%s)
                        RETURNING id, english_word, hindi_meaning
                        """,
                        (new_english_word, new_hindi_meaning, english_word)
                    )

                elif new_hindi_meaning:
                    cur.execute(
                        """
                        UPDATE translations
                        SET hindi_meaning = %s
                        WHERE LOWER(english_word) = LOWER(%s)
                        RETURNING id, english_word, hindi_meaning
                        """,
                        (new_hindi_meaning, english_word)
                    )

                else:
                    cur.execute(
                        """
                        UPDATE translations
                        SET english_word = %s
                        WHERE LOWER(english_word) = LOWER(%s)
                        RETURNING id, english_word, hindi_meaning
                        """,
                        (new_english_word, english_word)
                    )

                result = cur.fetchone()

        if result:
            return (
                f"Successfully updated!\n"
                f"ID: {result[0]}\n"
                f"English: {result[1]}\n"
                f"Hindi: {result[2]}"
            )

        return f"'{english_word}' was not found. Nothing was updated."

    except psycopg.errors.UniqueViolation:
        return (
            f"Cannot update: '{new_english_word}' already exists "
            "in your dictionary. No changes were made."
        )





# Start MCP server using HTTP
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
    )
