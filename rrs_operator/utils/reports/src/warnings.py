from .report import Report


class WarningsReport(Report):
    """Class for reports with warnings"""

    def get_descriptions(self, unparsed_description: str) -> list:
        warnigns = unparsed_description.split("*")
        return warnigns
