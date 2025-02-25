from .report import Report


class UnrespondedDevicesReport(Report):
    def get_descriptions(self) -> list:
        devices = self.unparsed_description.split("*")
        return devices

    def get_priority(self) -> str:
        return "2"
