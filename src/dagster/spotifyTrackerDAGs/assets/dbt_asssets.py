from dagster import AssetExecutionContext, AssetKey, Config
from dagster_dbt import DbtProject, DbtCliResource, dbt_assets, DagsterDbtTranslator
from pathlib import Path

dbt_project = DbtProject(
    # note that the path is different from the local repo's path
    # because of the way we had to mount and copy files in the
    # docker containers (dagster_home & assets_dbt file name -> 2 more pardir)
    project_dir=Path(__file__).joinpath('..','..','..','..','..','dbt').resolve()
)

dbt_resource = DbtCliResource(
    project_dir=dbt_project
)

class MyDbtConfig(Config):
    full_refresh: bool
    target : str


@dbt_assets(
    manifest=dbt_project.manifest_path
)
def dbt_analytics(context : AssetExecutionContext, config : MyDbtConfig, dbt : DbtCliResource):
    dbt_build_args = ["build"]
    dbt_build_args += [f"--target={config.target}"]
    if config.full_refresh:
        dbt_build_args += ["--full-refresh"]
    yield from dbt.cli(dbt_build_args, context=context).stream()
