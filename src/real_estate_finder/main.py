from real_estate_finder.infrastructure.excel_repo import ExcelRepository
from real_estate_finder.ui.app import RealEstateApp


def run() -> None:
    repository = ExcelRepository()
    app = RealEstateApp(repository)
    app.mainloop()


if __name__ == "__main__":
    run()
