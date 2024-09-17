from abc import ABC, abstractmethod


class Report(ABC):
    @abstractmethod
    def get_descriptions(self, unparsed_description: str) -> list:
        return [unparsed_description]

    @abstractmethod
    def get_priority(self) -> str:
        pass
