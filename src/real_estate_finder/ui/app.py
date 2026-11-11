from pathlib import Path
from tkinter import filedialog, messagebox
from typing import List
import webbrowser
import customtkinter as ctk
from real_estate_finder.domain.models import MatchResult
from real_estate_finder.infrastructure.excel_repo import ExcelRepository
from real_estate_finder.services.matcher import RealEstateMatcher


class RealEstateApp(ctk.CTk):
    """Графическое окно подборщика недвижимости."""

    def __init__(self, repo: ExcelRepository) -> None:
        super().__init__()
        self.repo = repo

        self.title("Подборщик новостроек v2.0 (Бизнес / Премиум)")
        self.geometry("860x720")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Блок 1: Загрузка базы
        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            file_frame, text="Загрузить Excel (.xlsx)", command=self._on_load_file
        ).grid(row=0, column=0, padx=12, pady=12)

        self.lbl_file = ctk.CTkLabel(file_frame, text="Файл не выбран", text_color="gray", anchor="w")
        self.lbl_file.grid(row=0, column=1, padx=12, pady=12, sticky="ew")

        # Блок 2: Фильтры
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, padx=16, pady=8), filter_frame.grid(sticky="ew")
        filter_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(filter_frame, text="Город:").grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.city_var = ctk.StringVar(value="Загрузите файл")
        self.combo_city = ctk.CTkComboBox(filter_frame, variable=self.city_var, values=[], state="disabled")
        self.combo_city.grid(row=1, column=0, padx=10, pady=(4, 12), sticky="ew")

        ctk.CTkLabel(filter_frame, text="Класс:").grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")
        self.segment_var = ctk.StringVar(value="Все")
        self.combo_segment = ctk.CTkComboBox(
            filter_frame, variable=self.segment_var, values=["Все", "Бизнес", "Премиум"], state="readonly"
        )
        self.combo_segment.grid(row=1, column=1, padx=10, pady=(4, 12), sticky="ew")

        ctk.CTkLabel(filter_frame, text="Бюджет (млн ₽):").grid(row=0, column=2, padx=10, pady=(10, 0), sticky="w")
        self.entry_budget = ctk.CTkEntry(filter_frame, placeholder_text="Например: 35")
        self.entry_budget.grid(row=1, column=2, padx=10, pady=(4, 12), sticky="ew")

        ctk.CTkLabel(filter_frame, text="Площадь (м²):").grid(row=0, column=3, padx=10, pady=(10, 0), sticky="w")
        self.entry_area = ctk.CTkEntry(filter_frame, placeholder_text="Например: 65")
        self.entry_area.grid(row=1, column=3, padx=10, pady=(4, 12), sticky="ew")

        self.btn_search = ctk.CTkButton(
            filter_frame,
            text="Подобрать 3 лучших ЖК",
            command=self._on_search,
            state="disabled",
            height=38,
            font=ctk.CTkFont(weight="bold"),
        )
        self.btn_search.grid(row=2, column=0, columnspan=4, padx=10, pady=(4, 14), sticky="ew")

        # Блок 3: Карточки результатов
        self.scroll_results = ctk.CTkScrollableFrame(self, label_text="Подходящие жилые комплексы")
        self.scroll_results.grid(row=2, column=0, padx=16, pady=(8, 16), sticky="nsew")
        self.scroll_results.grid_columnconfigure(0, weight=1)

    def _on_load_file(self) -> None:
        initial_dir = Path("data") if Path("data").exists() else Path.cwd()
        file_str = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Выберите Excel-файл с базой ЖК",
            filetypes=[("Excel файлы", "*.xlsx *.xls")],
        )
        if not file_str:
            return

        path = Path(file_str)
        try:
            cities = self.repo.load(path)
        except Exception as exc:
            messagebox.showerror("Ошибка загрузки", str(exc))
            return

        self.lbl_file.configure(text=f"База: {path.name} ({len(self.repo.items)} ЖК)", text_color=("black", "white"))
        self.combo_city.configure(values=cities, state="readonly")
        if cities:
            self.city_var.set(cities)
        self.btn_search.configure(state="normal")

    def _on_search(self) -> None:
        try:
            budget_mln = float(self.entry_budget.get().replace(",", ".").strip())
            area_m2 = float(self.entry_area.get().replace(",", ".").strip())
            if budget_mln <= 0 or area_m2 <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Укажите положительные числа для бюджета и площади.")
            return

        matches = RealEstateMatcher.find_best_matches(
            items=self.repo.items,
            city=self.city_var.get(),
            budget_rub=int(budget_mln * 1_000_000),
            target_area_m2=area_m2,
            segment_filter=self.segment_var.get(),
            top_n=3,
        )
        self._render_cards(matches, area_m2)

    def _render_cards(self, matches: List[MatchResult], target_area: float) -> None:
        for widget in self.scroll_results.winfo_children():
            widget.destroy()

        if not matches:
            ctk.CTkLabel(self.scroll_results, text="По заданным фильтрам ЖК не найдены.").grid(row=0, column=0, pady=20)
            return

        for idx, match in enumerate(matches, start=1):
            item = match.complex_data
            card = ctk.CTkFrame(self.scroll_results, border_width=1)
            card.grid(row=idx - 1, column=0, padx=8, pady=8, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            # Заголовок
            title = f"#{idx}  ЖК «{item.complex_name}»  •  {item.segment.upper()}  •  Сдача: {item.deadline}"
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=15, weight="bold"), anchor="w").grid(
                row=0, column=0, padx=14, pady=(10, 2), sticky="w"
            )

            # Кнопка ссылки на источник
            if item.source_url.startswith("http"):
                ctk.CTkButton(
                    card,
                    text="Открыть источник",
                    width=130,
                    height=26,
                    command=lambda url=item.source_url: webbrowser.open(url),
                ).grid(row=0, column=1, padx=14, pady=(10, 2), sticky="e")

            # Инфо о проекте и диапазонах в ЖК
            meta = (
                f"Застройщик: {item.developer} | Район: {item.district}\n"
                f"Линейка ЖК: площади {item.area_m2_min:g}–{item.area_m2_max:g} м² | "
                f"лоты {item.price_total_min / 1e6:.1f}–{item.price_total_max / 1e6:.1f} млн ₽"
            )
            ctk.CTkLabel(card, text=meta, text_color="gray", justify="left", anchor="w").grid(
                row=1, column=0, columnspan=2, padx=14, pady=4, sticky="w"
            )

            # Расчетная вилка цены под запрос пользователя
            est_range = (
                f"Расчет для {target_area:g} м²: от {match.est_price_min / 1e6:.2f} до {match.est_price_max / 1e6:.2f} млн ₽ "
                f"({item.price_per_m2_min:,}–{item.price_per_m2_max:,} ₽/м²)".replace(",", " ")
            )
            ctk.CTkLabel(card, text=est_range, font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(
                row=2, column=0, columnspan=2, padx=14, pady=(4, 2), sticky="w"
            )

            # Статус соответствия бюджету и метражу
            area_note = "метраж есть в линейке" if match.area_fits else "метраж за пределами линейки ЖК"
            if match.budget_fits:
                status = f"✔ Вписывается в бюджет (от цены min) • {area_note}"
                color = "#2e8b57"
            else:
                over_mln = match.budget_diff_min / 1e6
                status = f"✖ Превышает бюджет минимум на {over_mln:.2f} млн ₽ • {area_note}"
                color = "#d9534f"

            ctk.CTkLabel(card, text=status, text_color=color, anchor="w").grid(
                row=3, column=0, columnspan=2, padx=14, pady=(0, 10), sticky="w"
            )
