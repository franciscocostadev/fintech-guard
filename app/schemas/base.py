from pydantic import BaseModel, ConfigDict


class InputModel(BaseModel):
    """Contrato comum a todo body de entrada, incluindo formulários OAuth2."""

    model_config = ConfigDict(extra="forbid")
