$script:script_path = $PSScriptRoot + '\..\main.py'

function New-HtmlReport {
    param(
        [Parameter(Mandatory=$true)][System.IO.FileInfo]$PdfFile,
        [Parameter(Mandatory=$true)][System.IO.FileInfo]$ExcelFile,
        [Parameter(Mandatory=$false)][System.IO.FileInfo]$OutputFile
    )   
        if( -not(Test-Path $PdfFile)){
            Write-Error 'Pdf file does not exist'
            Exit
        }
        
        if( -not(Test-Path -Path $ExcelFile)){
            Write-Error 'Excel file does not exist'
            Exit
        }

    py.exe $script_path $ExcelFile $PdfFile $OutputFile
}