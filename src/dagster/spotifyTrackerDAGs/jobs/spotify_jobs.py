from dagster import define_asset_job, AssetSelection, ScheduleDefinition

# Selecting all assets in the "spotify_data" group
spotify_data_assets = AssetSelection.groups("extract_load_v1")

# Define a single job to run all the assets in the group
spotify_data_pipeline_job = define_asset_job(
    name="spotify_extract_load_pipeline_job",
    selection=spotify_data_assets
)


spotify_data_pipeline_job_schedule = ScheduleDefinition(
    job=spotify_data_pipeline_job,
    cron_schedule="0 */8 * * *",  # Runs each 8 hours
    name="spotify_extract_load_pipeline_job_schedule"
)