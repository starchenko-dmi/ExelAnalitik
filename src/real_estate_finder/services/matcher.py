from typing import List, Optional
from real_estate_finder.domain.models import MatchResult, ResidentialComplex


class RealEstateMatcher:
    """Бизнес-логика фильтрации и ранжирования жилых комплексов."""

    @staticmethod
    def find_best_matches(
        items: List[ResidentialComplex],
        city: str,
        budget_rub: int,
        target_area_m2: float,
        segment_filter: Optional[str] = None,
        top_n: int = 3,
    ) -> List[MatchResult]:
        city_items = [
            item for item in items
            if item.city.lower() == city.strip().lower()
            and (not segment_filter or segment_filter == "Все" or item.segment.lower() == segment_filter.lower())
        ]

        results: List[MatchResult] = []
        for item in city_items:
            est_min = round(item.price_per_m2_min * target_area_m2)
            est_max = round(item.price_per_m2_max * target_area_m2)
            diff_min = est_min - budget_rub

            # Проверяем, есть ли в ЖК квартиры нужного метража (с допуском 10%)
            area_fits = (item.area_m2_min * 0.9) <= target_area_m2 <= (item.area_m2_max * 1.1)
            budget_fits = est_min <= budget_rub

            results.append(
                MatchResult(
                    complex_data=item,
                    est_price_min=est_min,
                    est_price_max=est_max,
                    budget_diff_min=diff_min,
                    area_fits=area_fits,
                    budget_fits=budget_fits,
                )
            )

        # Сортировка по приоритетам:
        # 1. Сначала те, где подходит И бюджет, И реальная площадь в ЖК
        # 2. Затем те, где подходит бюджет
        # 3. Внутри групп — минимальное отклонение от бюджета пользователя
        results.sort(
            key=lambda r: (
                not (r.budget_fits and r.area_fits),
                not r.budget_fits,
                abs(r.budget_diff_min),
            )
        )
        return results[:top_n]
