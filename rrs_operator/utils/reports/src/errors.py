from .report import Report


class ErrorsReport(Report):
    """Class for reports with errors"""

    def get_descriptions(self, unparsed_description: str) -> list:
        return super().get_descriptions(unparsed_description)
