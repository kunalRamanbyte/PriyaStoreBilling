[Setup]
AppName=Priya Store Billing
AppVersion=1.0
AppPublisher=Priya Store
DefaultDirName=C:\PriyaStore
DefaultGroupName=Priya Store Billing
OutputDir=C:\Users\Admin\Desktop\billing\installer
OutputBaseFilename=PriyaStore_Setup_v1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\PriyaStore.exe
PrivilegesRequired=lowest
DirExistsWarning=no
SetupIconFile=C:\Users\Admin\Desktop\billing\assets\app_icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; Flags: checkedonce
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; Flags: checkedonce

[Files]
Source: "C:\Users\Admin\Desktop\billing\dist\PriyaStore\PriyaStore.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Admin\Desktop\billing\dist\PriyaStore\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Admin\Desktop\billing\dist\PriyaStore\billing_data.db"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\Priya Store Billing"; Filename: "{app}\PriyaStore.exe"; IconFilename: "{app}\_internal\assets\app_icon.ico"
Name: "{group}\Uninstall Priya Store Billing"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Priya Store Billing"; Filename: "{app}\PriyaStore.exe"; Tasks: desktopicon; IconFilename: "{app}\_internal\assets\app_icon.ico"
Name: "{autostartmenu}\Priya Store Billing"; Filename: "{app}\PriyaStore.exe"; Tasks: startmenuicon; IconFilename: "{app}\_internal\assets\app_icon.ico"

[Run]
Filename: "{app}\PriyaStore.exe"; Description: "Launch Priya Store Billing now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
