from .report import Report


class ErrorsReport(Report):
    def get_descriptions(self) -> list:
        return super().get_descriptions()

    def get_priority(self) -> str:
        return "3"
