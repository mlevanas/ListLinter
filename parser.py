import pandas as pd
import math
from collections import defaultdict
from data.excelpart import ExcelPart
from data.comparable_part import ComparablePart

class Parser:

    def __init__(self, excel_path):
        self.__excel_file = excel_path

    def read_excel(self):
        df = pd.read_excel(self.__excel_file, header=2, sheet_name="Production list")
        _list = []

        if("User4" in df.columns):
            df = self.__configure_paletes(df)
        else:
            df = self.__configure_paprastas(df)

        _list = self.read_as_comparable(df)
        return _list
    
    def __configure_paprastas(self, df):
        df["Ilgis"] = (df["Ilgis"].astype("string").fillna(""))
        df["Kiekis"] = (pd.to_numeric(df["Kiekis"], errors="coerce").astype("Int64"))
        df["Aukštis"] = (pd.to_numeric(df["Aukštis"], errors="coerce").astype("Int64"))
        df["Plotis"] = (pd.to_numeric(df["Plotis"], errors="coerce").astype("Int64"))
        df["User2"] = df["User2"].fillna("").astype("string")
        df["Eil. Nr."] = (pd.to_numeric(df["Eil. Nr."], errors="coerce").astype("Int64").astype("string"))
        df["Komentaras"] = df["Komentaras"].fillna("").astype(str)
        df["Grupė"] = df["Grupė"].fillna("").astype(str)
        return df

    def __configure_paletes(self, df):
        df["Ilgis"] = (df["Ilgis"].astype("string").fillna(""))
        df["Kiekis"] = (pd.to_numeric(df["Kiekis"], errors="coerce").astype("Int64"))
        df["Aukštis"] = (pd.to_numeric(df["Aukštis"], errors="coerce").astype("Int64"))
        df["Plotis"] = (pd.to_numeric(df["Plotis"], errors="coerce").astype("Int64"))
        df["User2"] = df["User2"].fillna("").astype("string")
        df["User4"] = df["User4"].fillna("").astype(str)
        df["Eil. Nr."] = (pd.to_numeric(df["Eil. Nr."], errors="coerce").astype("Int64").astype("string"))
        df["Komentaras"] = df["Komentaras"].fillna("").astype(str)
        df["Grupė"] = df["Grupė"].fillna("").astype(str)

        return df

    def __read_production_list(self, df) -> list[ExcelPart]:
        data = df.to_dict(orient="records")
        filtered = self.__filter(data)
        grouped = defaultdict(int)

        format_ilgis = lambda ilgis: str(ilgis).replace(".0", "") + 'mm'

        for part in filtered:
            raktas = (
                part["Eil. Nr."],
                part["Plotis"],
                part["Aukštis"],
                format_ilgis(part["Ilgis"]) if 'M' not in part['Ilgis'] else part['Ilgis'],
                part["Pavadinimas"],
                part["User2"],
                part["Komentaras"],
                part["Grupė"])
            grouped[raktas] += part["Kiekis"] if part["Kiekis"] is not None else 0
        return grouped

    def read_as_comparable(self, df) -> list[ComparablePart]:
        parts = self.__read_production_list(df)
        comparable_parts = [
            ComparablePart(
                count = parts[x] if parts[x] != 0 else '',
                productionNumber= x[0],
                width=x[1],
                height=x[2],
                lenght=x[3],
                title=x[4],
                user2=x[5],
                group=x[6]
            ) for x in parts
        ]

        return comparable_parts

    #------------------------------------------------------
    # filter records with production number
    #------------------------------------------------------
    def __filter(self, data):
        
        filtered = []

        for part in data:
            if not pd.isna(part["Eil. Nr."]):
                filtered.append(part)
        return filtered
