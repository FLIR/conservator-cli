#!/usr/bin/env python3
import click
import pprint

from FLIR.conservator_cli.lib import graphql_api as fca
from FLIR.conservator_cli.lib.conservator_credentials import ConservatorCredentials

def custom_video_query(video_id, properties, conservator_token):
    query = """
    query video($id: String!, $src: String) {{
        video(id: $id, src: $src) {{
            {}
        }}
    }}
    """.format("\n".join(properties))

    variables = {
        "id": video_id,
        "src": ""
    }

    return fca.query_conservator(query, variables, conservator_token)["video"]

def display_video(video_id, properties, conservator_token):
    if not properties:
        video = fca.get_videos_from_id(video_id, conservator_token)
    else:
        video = custom_video_query(video_id, properties, conservator_token)
    print("Search results:")
    pprint.pprint(video)

@click.command()
@click.argument('search_text')
@click.option('-u', '--email', prompt="Conservator Email", help="The email of the conservator account to use for auth")
@click.option('-t', '--conservator_token', prompt="Conservator Token", help="Conservator API Token")
@click.option('-p', '--properties', help="comma-separated list of properties to be displayed for search results")
def search_videos_main(search_text, email, conservator_token, properties):
    # property names are separated by commas in --properties option
    if properties:
        properties = properties.split(",")

    credentials = ConservatorCredentials(email, conservator_token)
    found_videos = fca.get_videos_from_search(search_text, credentials.token)
    for video in found_videos:
        display_video(video["id"], properties, credentials.token)

if __name__ == "__main__":
    search_videos_main()
