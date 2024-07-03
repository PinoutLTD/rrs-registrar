from abc import ABC, abstractmethod


class Report(ABC):
    """Base class (interface) for reports"""

    @abstractmethod
    def get_descriptions(self, unparsed_description: str) -> list:
        return [unparsed_description]
