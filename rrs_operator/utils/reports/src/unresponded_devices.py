from .report import Report


class UnrespondedDevicesReport(Report):
    """Class for reports with unresponded devices"""

    def get_descriptions(self, unparsed_description: str) -> list:
        devices = unparsed_description.split("*")
        return devices
