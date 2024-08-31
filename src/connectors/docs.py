"""Can be used to parse data out of microsoft docs format, ending with .doc or .docx etc"""

from .text import Parse
from docx2txt import process
from pathlib import Path


class DocParser(Parse):
    def parse(self, blobOrFileName) -> str:
        if self.is_filename(blobOrFileName):
            if not Path(blobOrFileName).exists():
                raise FileNotFoundError(
                    f"Not able to found file at path : {Path(blobOrFileName)}"
                )
            text = process(blobOrFileName)
            return self.remove_values(text)

        raise Exception(
            f"Something bad happened; fileName needed; got this : {blobOrFileName}"
        )
