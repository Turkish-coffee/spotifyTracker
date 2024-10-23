from dagster import define_asset_job, AssetSelection

# Selecting all assets in the "spotify_data" group
spotify_data_assets = AssetSelection.groups("extract_load_v1")

# Define a single job to run all the assets in the group
spotify_data_pipeline_job_v1 = define_asset_job(
    name="spotify_data_pipeline_job",
    selection=spotify_data_assets
)
