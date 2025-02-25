from .report import Report


class WarningsReport(Report):
    def get_descriptions(self) -> list:
        warnigns = self.unparsed_description.split("*")
        return warnigns

    def get_priority(self) -> str:
        return "1"
