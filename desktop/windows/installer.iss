[Setup]
AppName=Kira Studio
AppVersion=1.0.0
DefaultDirName={localappdata}\Kira Studio
DefaultGroupName=Kira Studio
OutputBaseFilename=Kira-Studio-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
[Files]
Source: "..\..\dist\KiraStudio.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\Kira Studio"; Filename: "{app}\KiraStudio.exe"
Name: "{autodesktop}\Kira Studio"; Filename: "{app}\KiraStudio.exe"
[Run]
Filename: "{app}\KiraStudio.exe"; Description: "Запустить Kira Studio"; Flags: nowait postinstall skipifsilent
