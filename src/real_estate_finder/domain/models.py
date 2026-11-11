from dataclasses import dataclass


@dataclass(frozen=True)
class ResidentialComplex:
    """Модель одного жилого комплекса из базы Excel (v2)."""
    id: int
    city: str
    complex_name: str
    developer: str
    district: str
    segment: str
    deadline: str
    area_m2_min: float
    area_m2_max: float
    price_per_m2_min: int
    price_per_m2_max: int
    price_total_min: int
    price_total_max: int
    source_url: str
    proof_quote: str


@dataclass(frozen=True)
class MatchResult:
    """Результат оценки и подбора ЖК под запрос пользователя."""
    complex_data: ResidentialComplex
    est_price_min: int
    est_price_max: int
    budget_diff_min: int
    area_fits: bool
    budget_fits: bool
