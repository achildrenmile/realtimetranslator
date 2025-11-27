import argostranslate.package

print("Updating package index...")
argostranslate.package.update_package_index()

print("Getting available packages...")
available = argostranslate.package.get_available_packages()

# Find and install Chinese <-> English models
zh_en = None
en_zh = None

for pkg in available:
    if pkg.from_code == 'zh' and pkg.to_code == 'en':
        zh_en = pkg
    if pkg.from_code == 'en' and pkg.to_code == 'zh':
        en_zh = pkg

if zh_en:
    print(f"Installing {zh_en.from_name} -> {zh_en.to_name}...")
    zh_en.install()
    print("✓ Chinese -> English installed")
else:
    print("⚠ Chinese -> English model not found")

if en_zh:
    print(f"Installing {en_zh.from_name} -> {en_zh.to_name}...")
    en_zh.install()
    print("✓ English -> Chinese installed")
else:
    print("⚠ English -> Chinese model not found")

print("\nTranslation models ready!")
