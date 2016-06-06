function MsiWriteLog(message, show) {
    var msiMessageTypeInfo = 0x04000000;
    var msiMessageTypeError = 0x01000000;
    var msiMessageTypeUser = 0x03000000;

    var record = Session.Installer.CreateRecord(0);
    var recordType = msiMessageTypeInfo;

    if (show)
        recordType = msiMessageTypeError | msiMessageTypeUser;

    record.StringData(0) = message;
    Session.Message(recordType, record);
}


function SetSettings()
{
  var customActionData = Session.Property("CustomActionData").toString();

  MsiWriteLog("SetSettings: begin with CustomActionData=" + customActionData, false);

  var args = customActionData.split("=");
  var arg_name = args[0];
  var zoo_home = args[1].slice(1, -1);

  if (arg_name != "zoo_home") {
    var err = "SetSettings: wrong first argument name - expected 'zoo_home'";
    MsiWriteLog();
    throw err;
  }

  var fso = new ActiveXObject("Scripting.FileSystemObject");
  var curdir = fso.GetAbsolutePathName(zoo_home + "ZooInstaller");
  var settingsFolder = curdir + "/etc";
  var settingsFile = settingsFolder + "/settings.yaml";

  MsiWriteLog("SetSettings: check for '" + settingsFolder + "' folder", false);
  if (!fso.FolderExists(settingsFolder)) {
    MsiWriteLog("SetSettings: create '" + settingsFolder + "' folder", false);
    fso.CreateFolder(settingsFolder);
  }
  else
    MsiWriteLog("SetSettings: '" + settingsFolder + "' folder exists", false);

  MsiWriteLog("SetSettings: check for '" + settingsFile + "' file", false);
  if (!fso.FileExists(settingsFile)) {   
    var setting = "  " + arg_name + ": '" + zoo_home + "'";

    MsiWriteLog("SetSettings: create '" + settingsFile + "' file with:\n" + setting, false);

    var file = fso.CreateTextFile(settingsFile, true); 
    file.WriteLine(setting);
    file.Close(); 
  }
  else
    MsiWriteLog("SetSettings: check for '" + settingsFile + "' file exists", false);

  MsiWriteLog("SetSettings: end", false);
}

