import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
from data.comparable_part import ComparablePart
import math
import pdfplumber


@dataclass
class display_title:
    anglu: Optional[str] = None
    prancuzu: Optional[str] = None
    vokieciu: Optional[str] = None

    # Naudojama, jei PDF yra tik vienas display_title
    originalus: Optional[str] = None


@dataclass
class Detale:
    production_number: Optional[int]
    count: Optional[int]
    width: int
    height: int
    user2: Optional[str]
    length: int 
    display_title: display_title

    def to_dict(self) -> dict:
        return asdict(self)


class PDFDetaliuSkaitytuvas:

    # Šiame PDF aptiktos User2 reikšmės
    USER2_REIKSMES = {
        "N",
        "P.C."
    }

    def __init__(
        self,
        pdf_path: str,
        right_side_start: float = 0.788
    ):
        self.__pdf_path = Path(pdf_path)
        self.__right_side_start = right_side_start

    def read_as_comparable(self) -> list[ComparablePart]:
        parts = self.read()
        
        comparable_parts = [
            ComparablePart(
                count= int(x.count) if x.count is not None else "",
                productionNumber=x.production_number,
                width=int(x.width),
                height=int(x.height),
                lenght= str(x.length).lower(),
                user2= "" if x.user2 is None else x.user2
            ) for x in parts
        ]

        return comparable_parts

    def read(self) -> list[Detale]:
        """
        Nuskaito visas detales iš PDF.

        Analizuojama tik dešinėje pusėje esanti
        informacinė lentelė.
        """

        if not self.__pdf_path.exists():
            raise FileNotFoundError(
                f"PDF failas nerastas: {self.__pdf_path}"
            )

        details: list[Detale] = []

        with pdfplumber.open(self.__pdf_path) as pdf:

            for page in pdf.pages:

                page_details = self.__read_page(page)

                details.extend(page_details)

        details = sorted(details, key=lambda d: d.production_number)

        return details

    def __read_page(self, page) -> list[Detale]:
        """
        Nuskaito tik dešinėje pusėje esančią
        detalių informacijos lentelę.
        """

        x0 = page.width * self.__right_side_start

        right_side = page.crop(
            (
                x0,
                0,
                page.width,
                page.height
            )
        )

        text = right_side.extract_text(
            x_tolerance=2,
            y_tolerance=2
        )

        if not text:
            return []

        return self.__parse_page(text)

    def __parse_page(
        self,
        text: str
    ) -> list[Detale]:

        details: list[Detale] = []

        # Kiekviena detalė prasideda NR:
        blocks = re.split(
            r"(?=NR\s*:\s*\w+)",
            text,
            flags=re.IGNORECASE
        )

        for block in blocks:

            detail = self.__parse_detail(block)

            if detail is not None:
                details.append(detail)

        return details

    def __parse_detail(
        self,
        block: str
    ) -> Optional[Detale]:

        # -------------------------------------
        # Produkcijos numeris
        # -------------------------------------

        number_match = re.search(
            r"(?m)^NR\s*:\s*(\w+)\s*$",
            block,
            re.IGNORECASE
        )

        if not number_match:
            return None

        # -------------------------------------
        # count
        #
        # Stuck kai kurioms detalėms neegzistuoja,
        # todėl count gali būti None.
        # -------------------------------------

        quantity_match = re.search(
            r"(?m)^St(?:u|ü)ck\s*:\s*(\d+)\s*$",
            block,
            re.IGNORECASE
        )

        # -------------------------------------
        # width / aukštis
        # -------------------------------------

        dimensions_match = re.search(
            r"(?m)^B/H\s*:\s*"
            r"(\d+)\s*mm\s*[x×]\s*(\d+)\s*mm\s*$",
            block,
            re.IGNORECASE
        )

        if not dimensions_match:
            return None

        # -------------------------------------
        # length
        #
        # Šiame PDF yra ir:
        #
        # L: 5950mm
        #
        # ir:
        #
        # L: 810M
        #
        # Todėl length saugomas kaip tekstas.
        # -------------------------------------

        length_match = re.search(
            r"(?m)^L\s*:\s*"
            r"([0-9]+(?:[.,][0-9]+)?\s*(?:mm|M)?)"
            r"\s*$",
            block,
            re.IGNORECASE
        )

        if not length_match:
            return None

        production_number = str(
            number_match.group(1)
        )

        count = (
            int(quantity_match.group(1))
            if quantity_match
            else None
        )

        width = int(
            dimensions_match.group(1)
        )

        height = int(
            dimensions_match.group(2)
        )

        length = re.sub(
            r"\s+",
            "",
            length_match.group(1)
        )

        # -------------------------------------
        # User2 ir pavadinimai
        # -------------------------------------

        additional_lines = self.__get_additional_lines(
            block
        )

        user2 = self.__extract_user2(
            additional_lines
        )

        display_title = self.__extract_name(
            additional_lines
        )

        return Detale(
            production_number=production_number,
            count=count,
            width=width,
            height=height,
            user2=user2,
            length=length,
            display_title=display_title
        )

    def __get_additional_lines(
        self,
        block: str
    ) -> list[str]:
        """
        Grąžina visas eilutes, kurios nėra:

        NR:
        Stuck:
        B/H:
        L:

        Pvz.:

        N

        arba:

        Rafter
        Chevron
        Dach-sparren
        """

        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        result = []

        for line in lines:

            if re.match(
                r"^(NR|St(?:u|ü)ck|B/H|L)\s*:",
                line,
                re.IGNORECASE
            ):
                continue

            result.append(line)

        return result

    def __extract_user2(
        self,
        lines: list[str]
    ) -> Optional[str]:
        """
        Jei pirmoji papildoma eilutė yra žinoma
        User2 reikšmė, ji pašalinama iš sąrašo.
        """

        if not lines:
            return None

        value = lines[0].strip()

        if value.upper() in self.USER2_REIKSMES:

            lines.pop(0)

            return value

        return None

    def __extract_name(
        self,
        lines: list[str]
    ) -> display_title:
        """
        Šiame PDF dažniausiai naudojama struktūra:

        English
        Français
        Deutsch

        Pvz.:

        Rafter
        Chevron
        Dach-sparren
        """

        if not lines:
            return display_title()

        # -------------------------------------
        # Trys kalbos
        # -------------------------------------

        if len(lines) >= 3:

            return display_title(
                anglu=lines[0],
                prancuzu=lines[1],
                vokieciu=" ".join(lines[2:])
            )

        # -------------------------------------
        # Vienas display_title
        #
        # Pvz.:
        # Mittlerer Dachrahmen
        # EXTRA
        #
        # Nenustatome kalbos automatiškai,
        # kad nepadarytume klaidingos prielaidos.
        # -------------------------------------

        if len(lines) == 1:

            return display_title(
                originalus=lines[0]
            )

        # Jei kada nors atsirastų 2 eilutės,
        # paliekame jas originaliu formatu.

        return display_title(
            originalus=" | ".join(lines)
        )