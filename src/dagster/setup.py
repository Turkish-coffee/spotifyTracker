from setuptools import find_packages, setup

setup(
    name="spotifyTrackerDAGs",
    packages=find_packages(exclude=["spotifyTrackerDAGs_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "spotipy",
        "psycopg2",
        "dagster-dbt",
        "dbt-core==1.8.7",
        "dbt-postgres==1.8.2"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
