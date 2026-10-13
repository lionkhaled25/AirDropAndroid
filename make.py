import os

# شغّله من أول فولدر الـ repo - بيستبدل ملف الـ workflow بنسخة بتطلّع الخطأ الحقيقي

content = r"""name: Build Android APK

on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v5

    - name: Set up JDK 17
      uses: actions/setup-java@v5
      with:
        java-version: '17'
        distribution: 'temurin'

    - name: Setup Gradle 8.5
      uses: gradle/actions/setup-gradle@v4
      with:
        gradle-version: '8.5'

    - name: Build Debug APK
      run: |
        set -o pipefail
        gradle assembleDebug --stacktrace --console=plain 2>&1 | tee build.log

    - name: Show build errors in Annotations
      if: failure()
      run: |
        msg=$(grep -E "^e: |error:|What went wrong|Execution failed|Could not|AAPT|Manifest merger|Duplicate|not found" -A2 build.log | head -30 | sed 's/%/%25/g' | awk '{printf "%s%%0A", $0}')
        echo "::error title=Gradle error::${msg}"

    - name: Upload build log
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: build-log
        path: build.log

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: AirDrop-Android-APK
        path: app/build/outputs/apk/debug/app-debug.apk
"""

path = ".github/workflows/build.yml"
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("✅ تم تحديث", path)
