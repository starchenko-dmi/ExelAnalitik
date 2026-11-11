from pathlib import Path
from typing import List
import pandas as pd
from real_estate_finder.domain.models import ResidentialComplex


class ExcelRepository:
    """Репозиторий для чтения и валидации базы недвижимости из Excel."""

    REQUIRED_COLUMNS = {
        "id", "city", "complex_name", "developer", "district",
        "segment", "deadline", "area_m2_min", "area_m2_max",
        "price_per_m2_min", "price_per_m2_max",
        "price_total_min", "price_total_max",
        "source_url", "proof_quote",
    }

    def __init__(self) -> None:
        self._items: List[ResidentialComplex] = []

    @property
    def items(self) -> List[ResidentialComplex]:
        return self._items

    def load(self, file_path: Path) -> List[str]:
        """Загружает файл, валидирует структуру и возвращает список городов."""
        df = pd.read_excel(file_path, sheet_name=0)

        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"В Excel отсутствуют колонки: {', '.join(sorted(missing))}")

        df = df.dropna(subset=["city", "complex_name", "price_per_m2_min"])
        if df.empty:
            raise ValueError("Таблица не содержит валидных записей.")

        parsed_items: List[ResidentialComplex] = []
        for _, row in df.iterrows():
            parsed_items.append(
                ResidentialComplex(
                    id=int(row["id"]),
                    city=str(row["city"]).strip(),
                    complex_name=str(row["complex_name"]).strip(),
                    developer=str(row["developer"]).strip(),
                    district=str(row["district"]).strip(),
                    segment=str(row["segment"]).strip(),
                    deadline=str(row["deadline"]).strip(),
                    area_m2_min=float(row["area_m2_min"]),
                    area_m2_max=float(row["area_m2_max"]),
                    price_per_m2_min=int(row["price_per_m2_min"]),
                    price_per_m2_max=int(row["price_per_m2_max"]),
                    price_total_min=int(row["price_total_min"]),
                    price_total_max=int(row["price_total_max"]),
                    source_url=str(row["source_url"]).strip(),
                    proof_quote=str(row.get("proof_quote", "")).strip(),
                )
            )

        self._items = parsed_items
        return sorted({item.city for item in parsed_items})
