$mysql_loc = "C:\Program Files\MySQL\MySQL Shell 8.0\bin\mysqlsh.exe"


$files = Get-ChildItem -Path $sql_folder -Recurse -Include "*.sql" |  Select-Object FullName | Sort-Object FullName
$sql_folder_name = Get-Item -Path $sql_folder
foreach ($file in $files) {
    $cmd = '& $mysql_loc --user=$db_user --password=$password  --port=$port --host=$hostname --file $file.FullName'
    Invoke-Expression $cmd
}