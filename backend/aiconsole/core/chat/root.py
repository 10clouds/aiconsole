from pydantic import BaseModel

from aiconsole.core.assets.types import Asset
from fastmutation.types import BaseObject


class Root(BaseObject):
    assets: list[Asset]


"""
    async def read(self, ref: AnyRef) -> AICChat:
        assert ref.parent is not None
        assert ref.parent.id == "assets"
        assert ref.parent.parent is None

        await self.wait_for_all_mutations(ref)
        return await _read_chat_outside_of_lock(chat_id=ref.id)
"""
