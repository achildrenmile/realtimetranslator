import argostranslate.package

print("Updating package index...")
argostranslate.package.update_package_index()

available_packages = argostranslate.package.get_available_packages()
print(f"Found {len(available_packages)} packages")

# Check if already installed
installed = argostranslate.package.get_installed_packages()
print(f"Currently installed: {len(installed)} packages")

# Install English -> Chinese
en_zh = next((x for x in available_packages if x.from_code == 'en' and x.to_code == 'zh'), None)
if en_zh:
    if not any(pkg.from_code == 'en' and pkg.to_code == 'zh' for pkg in installed):
        print("Installing English -> Chinese...")
        download_path = en_zh.download()
        argostranslate.package.install_from_path(download_path)
        print("✓ English -> Chinese installed")
    else:
        print("✓ English -> Chinese already installed")
else:
    print("✗ English -> Chinese package not found")

# Install Chinese -> English
zh_en = next((x for x in available_packages if x.from_code == 'zh' and x.to_code == 'en'), None)
if zh_en:
    if not any(pkg.from_code == 'zh' and pkg.to_code == 'en' for pkg in installed):
        print("Installing Chinese -> English...")
        download_path = zh_en.download()
        argostranslate.package.install_from_path(download_path)
        print("✓ Chinese -> English installed")
    else:
        print("✓ Chinese -> English already installed")
else:
    print("✗ Chinese -> English package not found")

print("\n✓ Setup complete!")
print(f"Total packages installed: {len(argostranslate.package.get_installed_packages())}")
