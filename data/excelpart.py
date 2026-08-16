from dataclasses import dataclass

@dataclass(frozen=True)
class ExcelPart:
    productionNumber:int = 0
    pavadinimas:str = ''
    width:int = 0
    height:int = 0
    lenght:str = ''
    count:int = 0
    comment:str = ''
    group:str = ''
    user2:str = ''
    user4:str = ''