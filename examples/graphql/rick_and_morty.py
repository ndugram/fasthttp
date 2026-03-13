import sys
from pathlib import Path

from fasthttp import FastHTTP
from fasthttp.response import Response

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


app = FastHTTP()


@app.graphql(url="https://rickandmortyapi.com/graphql")
async def get_characters(resp: Response) -> dict:
    """
    Get list of characters.
    """
    return {
        "query": """
            query {
                characters(page: 1) {
                    info {
                        count
                        pages
                    }
                    results {
                        id
                        name
                        status
                        species
                        type
                        gender
                        origin {
                            name
                        }
                        location {
                            name
                        }
                    }
                }
            }
        """,
        "operation_name": "GetCharacters"
    }


@app.graphql(url="https://rickandmortyapi.com/graphql")
async def get_character_by_id(resp: Response) -> dict:
    """
    Get character by ID.
    """
    return {
        "query": """
            query GetCharacter($id: ID!) {
                character(id: $id) {
                    id
                    name
                    status
                    species
                    type
                    gender
                    origin {
                        name
                    }
                    location {
                        name
                    }
                    image
                    episode {
                        name
                        episode
                    }
                }
            }
        """,
        "variables": {"id": 1},
        "operation_name": "GetCharacter"
    }


@app.graphql(url="https://rickandmortyapi.com/graphql", operation_type="mutation")
async def create_character(resp: Response) -> dict:
    """
    Note: This API is read-only, mutation will return error.
    This is just for demonstration of mutation syntax.
    """
    return {
        "query": """
            mutation CreateCharacter($input: CharacterInput!) {
                createCharacter(input: $input) {
                    id
                    name
                }
            }
        """,
        "variables": {
            "input": {
                "name": "Test Character",
                "status": "Alive",
                "species": "Human",
                "gender": "Male"
            }
        },
        "operation_name": "CreateCharacter"
    }


@app.graphql(url="https://rickandmortyapi.com/graphql")
async def get_episodes(resp: Response) -> dict:
    """
    Get list of episodes.
    """
    return {
        "query": """
            query {
                episodes(page: 1) {
                    info {
                        count
                        pages
                    }
                    results {
                        id
                        name
                        episode
                        air_date
                        characters {
                            name
                        }
                    }
                }
            }
        """,
        "operation_name": "GetEpisodes"
    }


if __name__ == "__main__":
    app.run()
