Įrankis skirtas sulyginti listą su excel'iu.

**Sistmos reikalavimai:**
Python (kuriant naudota versija: 3.14.6)
Powershell (pasirinktinai)

**Diegimo instrukcija:**
1. nuklonuoti repozitoriją į norimą vietą (pvz: C:\scripts)
2. atsisiųsti reikiamus Python modulius:
```
    pip install -r requirements.txt
``` 
3. Powershell profile.ps1 faile pridėti:
```
    .  C:\path\to\your\repository\powershell\report.ps1
```

4. Norint sugeneruoti raportą su Powershell naudoti funkciją:
```
    New-HtmlReport -PdfFile .\PdfFile.pdf -ExcelFile .\Excel.xlsx
```