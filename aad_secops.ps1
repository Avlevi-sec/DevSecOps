#Multiple modules created to match certain metadata collected onto other types in AAD/Entra

function Username-to-UPN {
    # Function code for Get-ObjectID
    $usernamelist = Import-Csv -Path C:\Users\AvihayLevi\Downloads\name.csv | select -ExpandProperty name
    foreach ($user in $usernamelist){
        $user = $user.replace(' ','.')
        $user = $user + '@outseer.com'
        Write-Host $user
    }

}

function Username-to-Objectid {
    # Function code
    $usernamelist = Import-Csv -Path C:\Users\AvihayLevi\Downloads\name.csv | select -ExpandProperty name
    foreach ($user in $usernamelist){
        $user = $user.replace(' ','.')
        $user = $user + '@outseer.com'
        if(Get-MgUser -UserId $user -ErrorAction SilentlyContinue){
            $user = Get-MgUser -UserId $user
            Write-Host $user.Id            
        }
        else {
            Write-Host -fore Red $user
        }
        
    }

}
function UPN-to-Objectid {
    # Function code
    $usernamelist = Import-Csv -Path C:\Users\AvihayLevi\Downloads\name.csv | select -ExpandProperty name
    foreach ($user in $usernamelist){
        if(Get-MgUser -UserId $user -ErrorAction SilentlyContinue){
            $user = Get-MgUser -UserId $user
            Write-Host $user.Id            
        }
        else {
            Write-Host -fore Red $user
        }
        
    }

}

function Username-to-Device {
    # Function code for Get-ObjectID
    $usernamelist = Import-Csv -Path C:\Users\AvihayLevi\Downloads\name.csv | select -ExpandProperty name
    [array]$array_devices = @()
    foreach ($user in $usernamelist){
        $user = $user.replace(' ','.')
        $user = $user + '@outseer.com'
        if (Get-MgUserOwnedDevice -UserId $user -ErrorAction SilentlyContinue){
        $deviceids = Get-MgUserOwnedDevice -UserId $user
        }
        else {Write-Host -fore Red $user; continue;}
        foreach ($deviceid in $deviceids){
            $device = (Get-MgDevice -DeviceId $deviceid.Id)
            if ($device.DisplayName -like "OTSR*"){
                $otsr_laslogin = $device.ApproximateLastSignInDateTime
                if($otsr_laslogin.AddDays(14) -gt (Get-Date) -or $otsr_laslogin.AddDays(14) -eq (Get-Date)){
                    $array_devices += New-Object psobject -Property @{DeviceName = $device.DisplayName;DeviceObjectID = $device.Id}
                }
                
            }
        }
    }
    Write-Host -fore Green "Here is the list of objectids found"
    Start-Sleep -Seconds 2
    $array_devices | select -ExpandProperty DeviceObjectID
    Write-Host -fore Green "Here is the list of device names found"
    Start-Sleep -Seconds 2
    $array_devices | select -ExpandProperty DeviceName


}
function UPN-to-Device {
    # Function code for Get-ObjectID
    $usernamelist = Import-Csv -Path C:\Users\AvihayLevi\Downloads\name.csv | select -ExpandProperty name
    [array]$array_devices = @()
    foreach ($user in $usernamelist){
        if (Get-MgUserOwnedDevice -UserId $user -ErrorAction SilentlyContinue){
        $deviceids = Get-MgUserOwnedDevice -UserId $user
        }
        else {Write-Host -fore Red $user; continue;}
        foreach ($deviceid in $deviceids){
            $device = (Get-MgDevice -DeviceId $deviceid.Id)
            if ($device.DisplayName -like "OTSR*"){
                $otsr_laslogin = $device.ApproximateLastSignInDateTime
                if($otsr_laslogin.AddDays(14) -gt (Get-Date) -or $otsr_laslogin.AddDays(14) -eq (Get-Date)){
                    $array_devices += New-Object psobject -Property @{DeviceName = $device.DisplayName;DeviceObjectID = $device.Id}
                }
                
            }
        }
    }
    Write-Host -fore Green "Here is the list of objectids found"
    Start-Sleep -Seconds 2
    $array_devices | select -ExpandProperty DeviceObjectID
    Write-Host -fore Green "Here is the list of device names found"
    Start-Sleep -Seconds 2
    $array_devices | select -ExpandProperty DeviceName


}
