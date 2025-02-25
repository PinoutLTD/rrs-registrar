from abc import ABC, abstractmethod


class Report(ABC):
    def __init__(self, unparsed_description: str):
        self.unparsed_description = unparsed_description

    @abstractmethod
    def get_descriptions(self) -> list:
        return [self.unparsed_description]

    @abstractmethod
    def get_priority(self) -> str:
        pass
