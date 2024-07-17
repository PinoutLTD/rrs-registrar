from .report import Report


class ErrorsReport(Report):
    def get_descriptions(self, unparsed_description: str) -> list:
        return super().get_descriptions(unparsed_description)

    def get_priority(self) -> str:
        return "3"
