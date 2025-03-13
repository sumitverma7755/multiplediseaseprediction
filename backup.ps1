# Get current timestamp for the backup folder name
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backup_ps_$timestamp"

# Create backup directory
New-Item -Path $backupDir -ItemType Directory -Force

# Backup main Python file
Copy-Item -Path "multiplediseaseprediction.py" -Destination "$backupDir\multiplediseaseprediction.py.bak" -Force
Write-Host "Created backup: $backupDir\multiplediseaseprediction.py.bak"

# Backup other Python files
Get-ChildItem -Path "." -Filter "*.py" | Where-Object { $_.Name -ne "multiplediseaseprediction.py" -and $_.Name -ne "backup.ps1" } | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination "$backupDir\$($_.Name).bak" -Force
    Write-Host "Created backup: $backupDir\$($_.Name).bak"
}

# Backup model files
Get-ChildItem -Path "." -Filter "*.pkl" | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination "$backupDir\$($_.Name).bak" -Force
    Write-Host "Created backup: $backupDir\$($_.Name).bak"
}

# Backup images directory if it exists
$imagesDir = "images"
if (Test-Path -Path $imagesDir -PathType Container) {
    $imagesBackupDir = "$backupDir\images"
    New-Item -Path $imagesBackupDir -ItemType Directory -Force
    
    Get-ChildItem -Path $imagesDir -File | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination "$imagesBackupDir\$($_.Name)" -Force
        Write-Host "Created backup: $imagesBackupDir\$($_.Name)"
    }
}

Write-Host "Backup completed successfully!" 