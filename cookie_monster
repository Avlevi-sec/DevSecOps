#Kill chrome and clear cookies. can be used via EDR/MDM on multiple stations.

Stop-Process -Name chrome
Start-Sleep -Seconds 3

$UserData = "$($env:LOCALAPPDATA)\Google\Chrome\User Data"
$errormsg = "$($env:LOCALAPPDATA)\errormsg.txt"
$Folders = Get-ChildItem $UserData | Where-Object{ $_.PSIsContainer -and $_.Name -eq "Default" -or $_.Name -like "Profile*"}

foreach($folder in $folders){
    $file1 = "$($folder.FullName)\Network\Cookies"
    $file2 = "$($folder.FullName)\Cookies"
    try{
        $result1 = Test-Path -Path $file1 -PathType Leaf
        $result2 = Test-Path -Path $file2 -PathType Leaf
        if ($result1 -eq $true) {Remove-Item $file1}
        elseif ($result2 -eq $true) {Remove-Item $file2}
    }
    catch{Write-Output "cookies monster failed for $($folder.FullName)`n" >> $errormsg}
}


