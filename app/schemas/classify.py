"""Schemas do endpoint POST /classify (TP4).

Entrada e saída seguem o contrato em `reports/TP4/contrato_classify.md`:
`text` estrito de 1 a 4000 caracteres e resposta composta (intenção BANKING77 +
análise de segurança). Os dois scores têm significados distintos e não podem ser
somados ou comparados como uma única confiança.
"""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator

from app.schemas.base import InputModel


class ClassifyRequest(InputModel):
    # InputModel aplica extra='forbid'. StrictStr recusa número, lista, bool e
    # null com 422; min/max cobrem vazio e o limite de 4000 sem truncar.
    text: Annotated[
        StrictStr,
        Field(
            min_length=1,
            max_length=4000,
            description="Texto do cliente a classificar (1 a 4000 caracteres Unicode).",
            examples=[
                "I lost my bank card. How can I report it through the official support channel?"
            ],
        ),
    ]

    @field_validator("text")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        # strip() só testa se é vazio; a inferência recebe o texto original.
        if not v.strip():
            raise ValueError("O texto não pode ser vazio ou apenas espaços.")
        return v


class SecurityProbabilities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    benign: float = Field(ge=0.0, le=1.0)
    threat: float = Field(ge=0.0, le=1.0)


class SecurityResult(BaseModel):
    """Resultado do modelo binário de segurança (conteúdo, não intenção moral)."""

    task: Literal["security_binary"]
    label: Literal["benign", "threat"]
    probability: float = Field(
        ge=0.0, le=1.0, description="Score correspondente a `label` (não é o score BANKING77)."
    )
    probabilities: SecurityProbabilities
    model_version: str


class ClassifyResponse(BaseModel):
    """Resposta composta de `POST /classify` — exatamente cinco campos no topo."""

    task: Literal["banking_intent_with_security"]
    intent: str = Field(description="Uma das 77 intenções originais de BANKING77.")
    probability: float = Field(
        ge=0.0, le=1.0, description="predict_proba da intenção de maior score."
    )
    model_version: str = Field(description="Versão do artefato BANKING77.")
    security: SecurityResult
