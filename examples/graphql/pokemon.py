import sys
from pathlib import Path

from fasthttp import FastHTTP
from fasthttp.response import Response

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


app = FastHTTP(debug=True)


@app.graphql(url="https://graphql-pokemon.vercel.app/")
async def get_pokemon_by_name(resp: Response) -> dict:
    """
    Get Pokemon by name.
    """
    return {
        "query": """
            query GetPokemon($name: String!) {
                pokemon(name: $name) {
                    id
                    name
                    number
                    types
                    maxHP
                    baseStats {
                        attack
                        defense
                        specialattack
                        specialdefense
                        speed
                    }
                    evolutions {
                        id
                        name
                        number
                    }
                }
            }
        """,
        "variables": {"name": "pikachu"},
        "operation_name": "GetPokemon"
    }


@app.graphql(url="https://graphql-pokemon.vercel.app/")
async def get_pokemon_list(resp: Response) -> dict:
    """
    Get list of Pokemon.
    """
    return {
        "query": """
            query {
                pokemons(first: 10) {
                    id
                    name
                    number
                    types
                    maxHP
                }
            }
        """,
        "operation_name": "GetPokemonList"
    }


@app.graphql(url="https://graphql-pokemon.vercel.app/")
async def get_attacks(resp: Response) -> dict:
    """
    Get Pokemon with attacks.
    """
    return {
        "query": """
            query GetAttacks($name: String!) {
                pokemon(name: $name) {
                    name
                    types
                    attacks {
                        fast {
                            name
                            type
                            damage
                        }
                        special {
                            name
                            type
                            damage
                        }
                    }
                }
            }
        """,
        "variables": {"name": "charizard"},
        "operation_name": "GetAttacks"
    }


if __name__ == "__main__":
    app.run()
