#$AzADUsers = Get-AzureADUser -All $true
#$ActiveAzADUsers = $AzADUsers | Select-Object | Where-Object {$_.AccountEnabled -match 'True'}
#$ActiveAzADUsers.AccountEnabled
[array]$array_devices = @()
foreach($user in $AzADUsers){
    try {
        $user_devices = Get-AzureADUserRegisteredDevice -ObjectId $user.ObjectId -ErrorAction SilentlyContinue        
    }
    catch {
        Write-Host -fore Red $user.DisplayName "not found devices"
    } 
    
    foreach($device in $user_devices){
        if($device.DisplayName -like "OTSR*"){
            $win_device = Get-AzureADDevice -SearchString $device.DisplayName
            $win_device_activity = $win_device.ApproximateLastLogonTimeStamp
            if($win_device_activity.AddDays(14) -gt (Get-Date) -or $win_device_activity.AddDays(14) -eq (Get-Date)){
                $array_devices += New-Object psobject -Property @{DeviceName = $device.DisplayName;DeviceObjectID = $device.objectid}
            }
        }
    }
}
Write-Host -fore Red "Here is the full list of devices and objectids"
$array_devices
