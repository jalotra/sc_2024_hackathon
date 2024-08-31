from .text import Parse
from pypdf import PdfReader
from pathlib import Path
from collections import OrderedDict
import json
import sys

class PdfParser(Parse):
    def parse(self, blobOrFileName) -> str:
        if self.is_filename(blobOrFileName):
            if not Path(blobOrFileName).exists():
                raise FileNotFoundError(
                    f"Not able to find the file at path : {blobOrFileName}"
                )
            reader = PdfReader(Path(blobOrFileName))
            texts = OrderedDict()
            for idx, page in enumerate(reader.pages):
                texts[idx] = page.extract_text()

            return json.dumps(texts)

        raise Exception(
            f"Something bad happened; fileName needed; got this : {blobOrFileName}"
        )


if __name__ == "__main__":
    fileName = sys.argv[1]
    if not Path(fileName).exists():
        raise Exception(f"File not found at location : {fileName}")

    print(PdfParser().parse(fileName))

