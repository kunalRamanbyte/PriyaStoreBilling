[Setup]
AppName=Priya Store Billing
AppVersion=5.0
AppPublisher=Priya Store
DefaultDirName=C:\PriyaStore
DefaultGroupName=Priya Store Billing
; Paths below are relative to this .iss file, so the installer builds from any checkout
OutputDir=installer
OutputBaseFilename=PriyaStore_Setup_v5.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\PriyaStore.exe
PrivilegesRequired=lowest
DirExistsWarning=no
SetupIconFile=assets\app_icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; Flags: checkedonce
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; Flags: checkedonce

[Files]
Source: "dist\PriyaStore\PriyaStore.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\PriyaStore\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; run_build.py seeds this as a fresh EMPTY database — never the live shop DB.
; onlyifdoesntexist keeps an existing shop database untouched on upgrade.
Source: "dist\PriyaStore\billing_data.db"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\Priya Store Billing"; Filename: "{app}\PriyaStore.exe"; IconFilename: "{app}\_internal\assets\app_icon.ico"
Name: "{group}\Uninstall Priya Store Billing"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Priya Store Billing"; Filename: "{app}\PriyaStore.exe"; Tasks: desktopicon; IconFilename: "{app}\_internal\assets\app_icon.ico"
Name: "{autostartmenu}\Priya Store Billing"; Filename: "{app}\PriyaStore.exe"; Tasks: startmenuicon; IconFilename: "{app}\_internal\assets\app_icon.ico"

[Run]
Filename: "{app}\PriyaStore.exe"; Description: "Launch Priya Store Billing now"; Flags: nowait postinstall skipifsilent

; No [UninstallDelete] section by design.
; Uninstall must remove only what Setup installed. A blanket
;   Type: filesandordirs; Name: "{app}"
; also deletes billing_data.db (with its -wal/-shm sidecars) and the default
; backups\ folder that lives beside it — wiping every bill, customer, udhaar
; balance and local backup the shop has, with no warning and no way back.
