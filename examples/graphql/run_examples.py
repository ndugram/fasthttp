from fasthttp import FastHTTP
from fasthttp.response import Response

from examples.graphql.countries_api import get_countries, get_country_by_code, search_countries  # type: ignore  # noqa: E402
from examples.graphql.rick_and_morty import get_characters, get_character_by_id, get_episodes  # type: ignore  # noqa: E402
from examples.graphql.star_wars import get_all_films, get_film_by_id, get_all_people  # type: ignore  # noqa: E402
from examples.graphql.pokemon import get_pokemon_by_name, get_pokemon_list  # type: ignore  # noqa: E402


app = FastHTTP()


@app.graphql(url="https://countries.trevorblades.com/graphql", tags=["graphql", "countries"])
async def countries_handler(resp: Response) -> dict:
    return await get_countries(resp)


@app.graphql(url="https://rickandmortyapi.com/graphql", tags=["graphql", "rick-and-morty"])
async def rick_morty_handler(resp: Response) -> dict:
    return await get_character_by_id(resp)


@app.graphql(url="https://swapi-graphql.netlify.app/.graphql", tags=["graphql", "star-wars"])
async def star_wars_handler(resp: Response) -> dict:
    return await get_all_films(resp)


@app.graphql(url="https://graphql-pokemon.vercel.app/", tags=["graphql", "pokemon"])
async def pokemon_handler(resp: Response) -> dict:
    return await get_pokemon_by_name(resp)


if __name__ == "__main__":
    print("Running all GraphQL examples...")
    app.run()
