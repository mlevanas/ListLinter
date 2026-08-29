from parser import Parser as parser
from pdf_parser import PDFDetaliuSkaitytuvas
from data.comparable_part import PartComparer, InputParameters
import sys
import time
import natsort

p = parser(sys.argv[1])

detaliu_skaitytuvas = PDFDetaliuSkaitytuvas(sys.argv[2])

report_path = sys.argv[3] if len(sys.argv) > 3 else './report.html'

start = time.perf_counter()

print("Skaitomas PDF...")
pdf_detales = detaliu_skaitytuvas.read_as_comparable()
duplicates = detaliu_skaitytuvas.duplicates
print("skaitomas Excel...")
excel_detales = p.read_excel()
comparer = PartComparer()

result = comparer.compare(pdf_detales, excel_detales)

# uncomment this line to print results to console
# comparer.printCompareResult(result)
print(f"Report path: {report_path}")
elapsed = time.perf_counter() - start

params = InputParameters(sys.argv[1], sys.argv[2], report_path, elapsed, 
pdfList = natsort.natsorted(pdf_detales, lambda x: x.productionNumber),
 excelList = natsort.natsorted(excel_detales, lambda x: x.productionNumber),
 duplicateParts = duplicates)

comparer.generateReport(result, params)


print(f"Elapsed: {elapsed:.3f} s")

sys.exit(1) if not result.isEqual or len(duplicates) > 0 else sys.exit(0)
