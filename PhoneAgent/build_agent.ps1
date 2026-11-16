$ErrorActionPreference = "Stop"

$SdkPath = "C:\Users\Dell\AppData\Local\Android\Sdk"
$BuildTools = "$SdkPath\build-tools\35.0.0"
$AndroidJar = "$SdkPath\platforms\android-33\android.jar"
$Aapt2 = "$BuildTools\aapt2.exe"
$D8 = "$BuildTools\d8.bat"
$Zipalign = "$BuildTools\zipalign.exe"
$ApkSigner = "$BuildTools\apksigner.bat"
$Keytool = "C:\Program Files\Java\jdk-17\bin\keytool.exe"

$BaseDir = "E:\personal AI\PhoneAgent"
Set-Location $BaseDir

Write-Host ">>> Cleaning build artifacts..."
Remove-Item -Path "bin", "gen", "compiled_res.zip", "dex_out", "unsigned.apk", "aligned.apk", "phone_agent.apk" -Recurse -Force -ErrorAction SilentlyContinue

New-Item -ItemType Directory -Path "bin", "gen", "dex_out" -Force | Out-Null

Write-Host ">>> 1. Compiling resources with aapt2..."
& $Aapt2 compile --dir res -o compiled_res.zip

Write-Host ">>> 2. Linking APK & generating R.java..."
& $Aapt2 link -I $AndroidJar --manifest AndroidManifest.xml compiled_res.zip -o unsigned.apk --java gen --auto-add-overlay

Write-Host ">>> 3. Compiling Java source files with javac..."
$JavaFiles = Get-ChildItem -Path "src\com\personalai\agent\*.java", "gen\com\personalai\agent\*.java" | Select-Object -ExpandProperty FullName
& javac -encoding UTF-8 -source 1.8 -target 1.8 -cp $AndroidJar -d bin $JavaFiles

Write-Host ">>> 4. Creating DEX bytecode with d8..."
$ClassFiles = Get-ChildItem -Path "bin\com\personalai\agent\*.class" | Select-Object -ExpandProperty FullName
& $D8 --lib $AndroidJar --output dex_out $ClassFiles

Write-Host ">>> 5. Adding classes.dex to APK archive..."
python -c "import zipfile; z = zipfile.ZipFile('unsigned.apk', 'a'); z.write('dex_out/classes.dex', 'classes.dex', compress_type=zipfile.ZIP_DEFLATED); z.close()"

Write-Host ">>> 6. Zipalign APK..."
& $Zipalign -f 4 unsigned.apk aligned.apk

Write-Host ">>> 7. Generating Keystore (if needed) & Signing APK..."
if (-not (Test-Path "agent.keystore")) {
    & $Keytool -genkey -v -keystore agent.keystore -alias agent -keyalg RSA -keysize 2048 -validity 10000 -storepass 123456 -keypass 123456 -dname "CN=Agent,O=PersonalAI,C=US"
}

& $ApkSigner sign --ks agent.keystore --ks-pass pass:123456 --key-pass pass:123456 --out phone_agent.apk aligned.apk

Write-Host ">>> BUILD COMPLETE! 🚀"
$apkItem = Get-Item "phone_agent.apk"
Write-Host "APK Location: $($apkItem.FullName)"
Write-Host "APK Size:     $([math]::Round($apkItem.Length / 1KB, 2)) KB"
