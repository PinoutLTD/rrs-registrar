from .src import Report
from .src import WarningsReport, ErrorsReport, UnrespondedDevicesReport


class ReportsFabric:
    """Fabric to select Report based on its type"""

    @staticmethod
    def get_report(type: str) -> Report:
        if type == "warnings":
            return WarningsReport()
        if type == "errors":
            return ErrorsReport()
        if type == "unresponded_devices":
            return UnrespondedDevicesReport()
