from .src import ErrorsReport, Report, UnrespondedDevicesReport, WarningsReport


class ReportsProblemTypeFabric:
    """Fabric to select Report based on its type"""

    @staticmethod
    def get_report(issue: dict) -> Report:
        if isinstance(issue['description'], dict):
            type = issue["description"]["type"]
            unparsed_description = issue["description"]["description"]
        else:
            type = "errors"
            unparsed_description = issue["description"]
        if type == "warnings":
            return WarningsReport(unparsed_description)
        if type == "errors":
            return ErrorsReport(unparsed_description)
        if type == "unresponded_devices":
            return UnrespondedDevicesReport(unparsed_description)