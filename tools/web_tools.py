import os
from typing_extensions import Annotated
from pypdf import PdfReader
from bs4 import BeautifulSoup
import requests
import utils.constants

PDF_WORKING_FOLDER = os.path.join(utils.constants.LLM_WORKING_FOLDER, "pdf")


def download_pdf_report(
    url: Annotated[
        str,
        "The URL of the PDF report to download",
    ]
) -> Annotated[str, "The content of the PDF report"]:

    os.makedirs(PDF_WORKING_FOLDER, exist_ok=True)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    pdf_path = os.path.join(PDF_WORKING_FOLDER, "tmp.pdf")
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text


def download_web_page(
    url: Annotated[
        str,
        "The URL of the web page to download",
    ]
) -> Annotated[str, "The content of the web page"]:

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(strip=True)


def detect_telemetry_gaps(
    url: Annotated[
        str,
        "The URL of the EDR telemetry JSON file to download",
    ],
    edr_name: Annotated[
        str,
        "The name of the EDR",
    ],
) -> Annotated[
    str, "The overview of all EDR telemetry categories not detected by the EDR"
]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    gaps = [
        item.get("Sub-Category", "")
        for item in data
        if item.get(edr_name) == "No"
    ]
    return "\n".join(filter(None, gaps))
