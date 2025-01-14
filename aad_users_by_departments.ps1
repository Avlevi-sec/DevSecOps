#code to printout unique department names
#$AzADUsers | Select-Object -ExpandProperty department | sort-object -unique

# Gets all auzread users and lets you filter by unique department names you input into $departments var.
#$AzADUsers = Get-AzureADUser -All $true
$Departments = @("Technical Support","Finance","HR", "HR Business Partner", "Biz Ops GA","Technical Support")
$users = $AzADUsers | Select-Object | Where-Object {$_.Department -in $Departments}
[array]$array_users = @()
foreach($user in $users){
    $array_users += New-Object psobject -Property @{username = $user.UserPrincipalName;device_objectid = '';device_name = ''}
}
$devices_list = ""
$device_objectids = ""
foreach($user in $users){
    $array_user = $array_users | Select-Object | Where-Object {$_.username -eq $user.UserPrincipalName}
    $new_devices_query = Get-AzureADUserRegisteredDevice -ObjectId $user.objectid
    foreach($new_device in $new_devices_query){if($new_device.DisplayName -like "OTSR*"){$array_user.device_name += $new_device.DisplayName + "`n"; $array_user.device_objectid += $new_device.objectid + "`n"}}
    $device_names = ""
    $user_devices = Get-AzureADUserRegisteredDevice -ObjectId $user.objectid
    foreach($device in $user_devices.DisplayName){
        if($device -like "OTSR*"){
            $win_device = Get-AzureADDevice -SearchString $device
            $win_device_activity = $win_device.ApproximateLastLogonTimeStamp
            if($win_device_activity.AddDays(14) -gt (Get-Date) -or $win_device_activity.AddDays(14) -eq (Get-Date)){
                $device_names += "$device "
                $devices_list += "$device`n"
                $device_objectids += $win_device.ObjectId + "`n"
            }
        }
    }
}
Write-Host -fore Red "here is the full list of devices:"
Write-Host $devices_list
Write-Host -fore Red "here is the full list of devices objectids:"
Write-Host $device_objectids
$array_users
