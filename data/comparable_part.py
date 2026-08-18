from dataclasses import dataclass
from dataclasses import dataclass, field
from jinja2 import Environment, FileSystemLoader
from zoneinfo import ZoneInfo
import datetime
from collections import defaultdict
import os

@dataclass(frozen=True)
class ComparablePart:
    productionNumber:str = ''
    width:str = ''
    height:str = ''
    lenght:str= ''
    count:int = 0
    user2:str = ''
    title:str = ''
    group:str = ''

@dataclass
class PartDifference:
    productionNumber: int
    field: str
    value1: object
    value2: object


@dataclass
class CompareResult:
    onlyInFirst: list[ComparablePart] = field(default_factory=list)
    onlyInSecond: list[ComparablePart] = field(default_factory=list)
    differences: list[PartDifference] = field(default_factory=list)

    @property
    def isEqual(self) -> bool:
        return (
            len(self.onlyInFirst) == 0
            and len(self.onlyInSecond) == 0
            and len(self.differences) == 0
        )

@dataclass
class InputParameters:
    _excelFile: str=''
    _pdfFile: str=''
    outputFile: str='./report.html'
    _time_elapsed: str=''
    pdfList: list[ComparablePart] = field(default_factory=list)
    excelList: list[ComparablePart] = field(default_factory=list)

    @property
    def currentTime(self) -> str:
        now = datetime.datetime.now(ZoneInfo("Europe/Vilnius"))
        formated_time = now.strftime("%Y-%m-%d %H:%M:%S")
        return formated_time

    @property
    def timeEllapsed(self) -> str:
        return f"{self._time_elapsed:.3f}s"

    @property
    def excelFile(self):
        return os.path.basename(self._excelFile)

    @property
    def pdfFile(self) -> str:
        return os.path.basename(self._pdfFile)

class PartComparer:

    def __buildEnvironment(self):
        template_path = os.path.dirname(os.path.realpath(__file__)) + "/template"
        return Environment(loader=FileSystemLoader(template_path))

    def __writeHtml(self, html:str, outputFile:str):
        with open(outputFile, "w", encoding="utf-8") as file:
            file.write(html)

    def generateReport(self, result:CompareResult, params: InputParameters):
        env = self.__buildEnvironment()

        template = env.get_template("report.html")
        html = template.render(
            params = params,
            grouped = result.grouped,
            only_in_first = result.onlyInFirst,
            only_in_second = result.onlyInSecond,
        )
        
        self.__writeHtml(html, params.outputFile)


    def printCompareResult(self, compareResult:CompareResult):
        if(compareResult.isEqual):
            print("Detaliu sarasas su Excel failu sutampa.")
        else:
            print("----------------------------------------------------")
            print("Detales tik 1-ame sarase:")
            for d in compareResult.onlyInFirst:
                print(f"Producion number: {d.productionNumber}")
            print("----------------------------------------------------")
            print("Detales tik 2-ame sarase:")
            for d in compareResult.onlyInSecond:
                print(f"Production number: {d.productionNumber}")
            print("----------------------------------------------------")
            print("Skirtumai sarase:")
            for d in compareResult.differences:
                print(f"Production number: {d.productionNumber} -- [Attribute: {d.field}] -- Value 1: {d.value1} -- Value 2: {d.value2}")

    def compare(
        self,
        parts1: list[ComparablePart],
        parts2: list[ComparablePart]
    ) -> CompareResult:

        result = CompareResult()

        # Sukuriame dictionary:
        # productionNumber -> ComparablePart
        parts1Dict = {
            part.productionNumber: part
            for part in parts1
        }

        parts2Dict = {
            part.productionNumber: part
            for part in parts2
        }

        # Detalės, kurios yra pirmame sąraše
        for productionNumber, part1 in parts1Dict.items():

            if productionNumber not in parts2Dict:
                result.onlyInFirst.append(part1)
                continue

            part2 = parts2Dict[productionNumber]

            self._comparePart(part1, part2, result)

        # Detalės, kurios yra tik antrame sąraše
        for productionNumber, part2 in parts2Dict.items():

            if productionNumber not in parts1Dict:
                result.onlyInSecond.append(part2)


        grouped = defaultdict(list)

        for r in result.differences:
            grouped[r.productionNumber].append(r)

        result.grouped = dict(sorted(grouped.items(), key=lambda x: int(x[0])))
        return result

    def _comparePart(
        self,
        part1: ComparablePart,
        part2: ComparablePart,
        result: CompareResult
    ):

        fields = [
            "width",
            "height",
            "count",
            "lenght",
            "user2"
        ]

        for fieldName in fields:

            value1 = getattr(part1, fieldName)
            value2 = getattr(part2, fieldName)

            if value1 != value2:
                result.differences.append(
                    PartDifference(
                        productionNumber=part1.productionNumber,
                        field=fieldName,
                        value1=value1,
                        value2=value2
                    )
                ) 