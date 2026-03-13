import sys
from pathlib import Path

from fasthttp import FastHTTP
from fasthttp.response import Response

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


app = FastHTTP()


@app.graphql(url="https://swapi-graphql.netlify.app/.graphql")
async def get_all_films(resp: Response) -> dict:
    """
    Get all Star Wars films.
    """
    return {
        "query": """
            query {
                allFilms {
                    films {
                        id
                        title
                        episodeID
                        openingCrawl
                        director
                        producers
                        releaseDate
                    }
                }
            }
        """,
        "operation_name": "GetAllFilms"
    }


@app.graphql(url="https://swapi-graphql.netlify.app/.graphql")
async def get_film_by_id(resp: Response) -> dict:
    """
    Get film by episode ID.
    """
    return {
        "query": """
            query GetFilm($id: String!) {
                film(id: $id) {
                    id
                    title
                    episodeID
                    openingCrawl
                    director
                    producers
                    releaseDate
                    speciesConnection {
                        species {
                            name
                            classification
                            homeworld {
                                name
                            }
                        }
                    }
                }
            }
        """,
        "variables": {"id": "ZmlsbXM6MQ=="},  # Film ID 1
        "operation_name": "GetFilm"
    }


@app.graphql(url="https://swapi-graphql.netlify.app/.graphql")
async def get_all_people(resp: Response) -> dict:
    """
    Get all people (characters).
    """
    return {
        "query": """
            query {
                allPeople(first: 10) {
                    people {
                        id
                        name
                        height
                        mass
                        gender
                        birthYear
                        homeworld {
                            name
                        }
                    }
                }
            }
        """,
        "operation_name": "GetAllPeople"
    }


@app.graphql(url="https://swapi-graphql.netlify.app/.graphql")
async def get_planet(resp: Response) -> dict:
    """
    Get planet by name.
    """
    return {
        "query": """
            query GetPlanet($name: String!) {
                allPlanets(filter: { name: $name }) {
                    planets {
                        id
                        name
                        diameter
                        rotationPeriod
                        orbitalPeriod
                        gravity
                        population
                        climates
                        terrains
                    }
                }
            }
        """,
        "variables": {"name": "Tatooine"},
        "operation_name": "GetPlanet"
    }


@app.graphql(url="https://swapi-graphql.netlify.app/.graphql")
async def get_starships(resp: Response) -> dict:
    """
    Get all starships.
    """
    return {
        "query": """
            query {
                allStarships(first: 10) {
                    starships {
                        id
                        name
                        model
                        manufacturer
                        costInCredits
                        length
                        maxAtmospheringSpeed
                        crew
                        passengers
                        cargoCapacity
                    }
                }
            }
        """,
        "operation_name": "GetStarships"
    }


if __name__ == "__main__":
    app.run()
