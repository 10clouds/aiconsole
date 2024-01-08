from aiconsole.core.assets.agents.agent import Agent
from aiconsole.core.assets.asset import Asset
from aiconsole.core.assets.assets import Assets
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.project import project


class AssetWithGivenNameAlreadyExistError(Exception):
    pass


class InvalidAgentNameError(Exception):
    pass


class _Assets:
    async def _create(self, assets: Assets, asset_id: str, asset: Asset) -> None:
        self._validate_existance(assets, asset_id)

        await assets.save_asset(asset, old_asset_id=asset_id, create=True)

    async def _partially_update(self, assets: Assets, old_asset_id: str, asset: Asset) -> None:
        if asset.id != old_asset_id:
            self._validate_existance(assets, asset.id)

        await assets.save_asset(asset, old_asset_id=old_asset_id, create=False)

    def _validate_existance(self, assets: Assets, asset_id: str) -> None:
        existing_asset = assets.get_asset(asset_id)
        if existing_asset is not None:
            raise AssetWithGivenNameAlreadyExistError()


class Agents(_Assets):
    _INVALID_AGENT_IDS = {"user"}

    async def create_agent(self, agent_id: str, agent: Agent) -> None:
        self._validate_invalid_agent_ids(agent_id)

        agents = project.get_project_agents()
        await self._create(agents, agent_id, agent)

    async def partially_update_agent(self, agent_id: str, agent: Agent) -> None:
        self._validate_invalid_agent_ids(agent.id)

        agents = project.get_project_agents()
        await self._partially_update(agents, agent_id, agent)

    def _validate_invalid_agent_ids(self, agent_id: str) -> None:
        if agent_id in self._INVALID_AGENT_IDS:
            raise InvalidAgentNameError()


class Materials(_Assets):
    async def create_material(self, material_id: str, material: Material) -> None:
        materials = project.get_project_materials()
        await self._create(materials, material_id, material)

    async def partially_update_material(self, material_id: str, material: Material) -> None:
        materials = project.get_project_materials()
        await self._partially_update(materials, material_id, material)
