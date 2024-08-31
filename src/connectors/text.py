"""This connector could be used to load and parse text files"""

from abc import ABC, abstractmethod
from pathlib import Path
import re


class Parse(ABC):
    @abstractmethod
    def parse(self, blobOrFileName) -> str:
        pass

    def is_filename(self, s: str) -> bool:
        if "/" in s or "\\" in s:
            return True
        if re.search(r"\.[a-zA-Z0-9]+$", s):
            return True
        if re.search(r"[^\w\s]", s) and not re.search(r"[/\\]", s):
            return False
        return False

    def remove_values(self, s: str) -> str:
        s = s.split("\n")
        return " ".join(s)


class TextParser(Parse):
    def parse(self, blobOrFileName) -> str:
        print(blobOrFileName)
        if not self.is_filename(blobOrFileName):
            parsed_string = " ".join(
                list(map(lambda x: x.strip(), blobOrFileName.split("\n")))
            )
            parsed_string = parsed_string.strip()
            return parsed_string
        elif self.is_filename(blobOrFileName):
            path = Path(blobOrFileName)
            if not path.exists():
                raise FileNotFoundError(f"Not able to find file at path : {path.name}")
            parsed_string = " ".join(
                list(
                    map(
                        lambda x: x.strip(),
                        open(blobOrFileName, "r").read().splitlines(),
                    )
                )
            )
            parsed_string = parsed_string.strip()
            return parsed_string
        raise Exception("Something bad happened; fileName or data needed")
