import pandas as pd
import math

from data.excelpart import ExcelPart
from data.comparable_part import ComparablePart

class Parser:

    def __init__(self, excel_path):
        self.__excel_file = excel_path

    def read_production_list(self) -> list[ExcelPart]:
        df = pd.read_excel(self.__excel_file, sheet_name="Production list", header=2, usecols=["Eil. Nr.", "Plotis", "Aukštis", "Ilgis", "Pavadinimas", "User2", "Kiekis", "Komentaras", "Grupė"])
        df["Ilgis"] = df["Ilgis"].fillna(None).astype(str)
        df["User2"] = df["User2"].fillna(None).astype(str)
        df["Eil. Nr."] = df["Eil. Nr."].fillna(None).astype("Int64")
        data = df.to_dict(orient="records")
        return self.__filter(data)

    def read_as_comparable(self) -> list[ComparablePart]:
        parts = self.read_production_list()

        comparable_parts = [
            ComparablePart(
                count= x.count,
                productionNumber=str(x.productionNumber),
                width=x.width,
                height=x.height,
                lenght=x.lenght,
                user2=x.user2,
                title=x.pavadinimas,
                group=x.group
            ) for x in parts
        ]

        return comparable_parts

    #------------------------------------------------------
    # filter records with at least one property available
    #------------------------------------------------------
    def __filter(self, data_json):
        result = set()
        for record in data_json:
            if (not pd.isna(record["Eil. Nr."])):
                p = ExcelPart(
                comment = record["Komentaras"],
                group = record["Grupė"],
                count = "" if pd.isna(record["Kiekis"]) else int(record["Kiekis"]),
                productionNumber = str(record["Eil. Nr."]),
                user2 = "" if pd.isna(record["User2"]) else record["User2"],
                width = record["Plotis"],
                height = record["Aukštis"],
                lenght = record["Ilgis"],
                pavadinimas = record["Pavadinimas"]
                )
                result.add(p)
        
        return result
