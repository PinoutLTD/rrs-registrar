from .report import Report


class UnrespondedDevicesReport(Report):
    def get_descriptions(self, unparsed_description: str) -> list:
        devices = unparsed_description.split("*")
        return devices

    def get_priority(self) -> str:
        return "2"
