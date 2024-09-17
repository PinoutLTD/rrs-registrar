from .report import Report


class WarningsReport(Report):
    def get_descriptions(self, unparsed_description: str) -> list:
        warnigns = unparsed_description.split("*")
        return warnigns

    def get_priority(self) -> str:
        return "1"
