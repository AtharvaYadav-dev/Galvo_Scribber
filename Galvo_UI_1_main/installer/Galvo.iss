#define MyAppName "Patterning Machine"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "Spécialisé Products Private Limited"
#define MyAppExeName "Patterning_machine.exe"

[Setup]
AppId={{30A7A7CD-80DC-4085-A0D4-3C65DE4A66B7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppPublisher}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
OutputBaseFilename={#StringChange(MyAppName, ' ', '_')}_{#MyAppVersion}_Setup
OutputDir=..\dist
SetupIconFile=..\logo\new_logo.ico
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#StringChange(MyAppName, ' ', '_')}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// Helper function to extract a value from a simple JSON string
function GetJsonValue(JsonString, Key: String): String;
var
  KeyPos, StartPos, EndPos: Integer;
  SubStr: String;
begin
  Result := '';
  KeyPos := Pos('"' + Key + '"', JsonString);
  if KeyPos > 0 then
  begin
    // Get everything after the key
    SubStr := Copy(JsonString, KeyPos + Length(Key) + 2, Length(JsonString));
    
    // Find the colon
    StartPos := Pos(':', SubStr);
    if StartPos > 0 then
    begin
      SubStr := Copy(SubStr, StartPos + 1, Length(SubStr));
      
      // Find the first quote of the value
      StartPos := Pos('"', SubStr);
      if StartPos > 0 then
      begin
        SubStr := Copy(SubStr, StartPos + 1, Length(SubStr));
        
        // Find the closing quote of the value
        EndPos := Pos('"', SubStr);
        if EndPos > 0 then
        begin
          Result := Copy(SubStr, 1, EndPos - 1);
        end;
      end;
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  WinHttpReq: Variant;
  ConfigPath: String;
  ConfigFileLines: TArrayOfString;
  ConfigContent: String;
  ClientId: String;
  ProjectId: String;
  ApiUrl: String;
  WebhookUrl: String;
  i: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    SaveStringToFile('C:\Galvo_Uninstall_Log.txt', 'Uninstall started.' + #13#10, False);
    ConfigPath := ExpandConstant('{app}\_internal\sppl_config.json');
    SaveStringToFile('C:\Galvo_Uninstall_Log.txt', 'Config path: ' + ConfigPath + #13#10, True);
    
    if FileExists(ConfigPath) then
    begin
      SaveStringToFile('C:\Galvo_Uninstall_Log.txt', 'Config exists.' + #13#10, True);
      if LoadStringsFromFile(ConfigPath, ConfigFileLines) then
      begin
        ConfigContent := '';
        for i := 0 to GetArrayLength(ConfigFileLines) - 1 do
          ConfigContent := ConfigContent + ConfigFileLines[i];
          
        ClientId := GetJsonValue(ConfigContent, 'client_id');
        ProjectId := GetJsonValue(ConfigContent, 'project_id');
        ApiUrl := GetJsonValue(ConfigContent, 'api_url');
        
        SaveStringToFile('C:\Galvo_Uninstall_Log.txt', 'Parsed ClientId: ' + ClientId + ' | ProjectId: ' + ProjectId + ' | ApiUrl: ' + ApiUrl + #13#10, True);
        
        if (ClientId <> '') and (ApiUrl <> '') then
        begin
          WebhookUrl := ApiUrl + '/api/clients/uninstall';
          SaveStringToFile('C:\Galvo_Uninstall_Log.txt', 'Sending webhook to: ' + WebhookUrl + #13#10, True);
          
          try
            WinHttpReq := CreateOleObject('MSXML2.ServerXMLHTTP.6.0');
            WinHttpReq.Open('POST', WebhookUrl, False);
            WinHttpReq.SetRequestHeader('Content-Type', 'application/json');
            WinHttpReq.Send('{"client_id": "' + ClientId + '", "project_id": "' + ProjectId + '", "event": "uninstalled"}');
            SaveStringToFile('C:\Galvo_Uninstall_Log.txt', 'Webhook sent successfully. Status: ' + IntToStr(WinHttpReq.Status) + #13#10, True);
          except
            SaveStringToFile('C:\Galvo_Uninstall_Log.txt', 'Webhook failed with exception.' + #13#10, True);
          end;
        end
        else
        begin
          SaveStringToFile('C:\Galvo_Uninstall_Log.txt', 'ClientId or ApiUrl was empty.' + #13#10, True);
        end;
      end;
    end
    else
    begin
      SaveStringToFile('C:\Galvo_Uninstall_Log.txt', 'Config file not found!' + #13#10, True);
    end;
  end;
end;
