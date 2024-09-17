import json

from .src import Report
from .src import NoLogs, LogsDict, SingleHash

class ReportsFormatTypeFabric:

    @staticmethod
    def get_report(report_msg: str, ipfs, logger) -> Report:
        try:
            report_dict = json.loads(report_msg)
            if len(report_dict) == 1:
                return NoLogs(logger=logger)
            return LogsDict(logger=logger, ipfs=ipfs)
        except json.decoder.JSONDecodeError:
            return SingleHash(logger=logger, ipfs=ipfs)
