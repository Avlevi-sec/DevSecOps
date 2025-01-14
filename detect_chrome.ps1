#Goes along with cookie monster, detects if chrome is installed

$UserData = "$($env:LOCALAPPDATA)\Google\Chrome\User Data"
$errormsg = "$($env:LOCALAPPDATA)\errormsg.txt"

try{
if (Test-Path -path $UserData) {
    Write-Output "chrome installed" >> $errormsg
    exit 1
}
else{
    Write-Output "chrome doesn't exist" >> $errormsg
}
}
catch{Write-Output "failed to run" >> $errormsg}
