"""
Setup script for Offline Voice Translator
Downloads and installs all required models
"""

import os
import sys
import urllib.request
import zipfile
import shutil

def download_file(url, destination):
    """Download a file with progress indicator"""
    print(f"Downloading {url}...")
    print(f"To: {destination}")
    
    def reporthook(blocknum, blocksize, totalsize):
        percent = min(blocknum * blocksize * 100 / totalsize, 100)
        sys.stdout.write(f"\r  Progress: {percent:.1f}%")
        sys.stdout.flush()
    
    urllib.request.urlretrieve(url, destination, reporthook)
    print("\n✓ Download complete")

def setup_vosk_models():
    """Download and install Vosk speech recognition models"""
    print("\n" + "="*60)
    print("Setting up Vosk Speech Recognition Models")
    print("="*60)
    
    models_dir = os.path.expanduser("~/.vosk/models")
    os.makedirs(models_dir, exist_ok=True)
    print(f"Models directory: {models_dir}")
    
    models = {
        'en': {
            'name': 'vosk-model-small-en-us-0.15',
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
            'size': '40 MB'
        },
        'zh': {
            'name': 'vosk-model-small-cn-0.22',
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip',
            'size': '42 MB'
        }
    }
    
    for lang, model_info in models.items():
        model_path = os.path.join(models_dir, model_info['name'])
        
        if os.path.exists(model_path):
            print(f"\n{lang.upper()} Model: Already installed at {model_path}")
            continue
        
        print(f"\n{lang.upper()} Model ({model_info['size']})")
        print(f"  Name: {model_info['name']}")
        
        # Download
        zip_path = os.path.join(models_dir, f"{model_info['name']}.zip")
        try:
            download_file(model_info['url'], zip_path)
        except Exception as e:
            print(f"✗ Download failed: {e}")
            print(f"  Please download manually from: {model_info['url']}")
            print(f"  And extract to: {models_dir}")
            continue
        
        # Extract
        print(f"Extracting...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(models_dir)
            print(f"✓ Extracted to {model_path}")
            
            # Remove zip file
            os.remove(zip_path)
            print(f"✓ Cleaned up zip file")
            
        except Exception as e:
            print(f"✗ Extraction failed: {e}")
            continue

def setup_argos_translate():
    """Install Argos Translate packages"""
    print("\n" + "="*60)
    print("Setting up Argos Translate Models")
    print("="*60)
    
    try:
        import argostranslate.package
        import argostranslate.translate
    except ImportError:
        print("✗ argostranslate not installed")
        print("  Run: pip install argostranslate")
        return False
    
    # Update package index
    print("\nUpdating package index...")
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    print(f"✓ Found {len(available_packages)} available packages")
    
    # Install language pairs
    pairs = [
        ('en', 'zh', 'English → Chinese'),
        ('zh', 'en', 'Chinese → English')
    ]
    
    for from_code, to_code, description in pairs:
        print(f"\n{description}")
        
        # Check if already installed
        installed = argostranslate.package.get_installed_packages()
        already_installed = any(
            pkg.from_code == from_code and pkg.to_code == to_code 
            for pkg in installed
        )
        
        if already_installed:
            print(f"  ✓ Already installed")
            continue
        
        # Find package
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code,
                available_packages
            ),
            None
        )
        
        if not package_to_install:
            print(f"  ✗ Package not found")
            continue
        
        # Install
        print(f"  Downloading and installing...")
        try:
            download_path = package_to_install.download()
            argostranslate.package.install_from_path(download_path)
            print(f"  ✓ Installed successfully")
        except Exception as e:
            print(f"  ✗ Installation failed: {e}")
    
    return True

def setup_template():
    """Create offline template from simple template"""
    print("\n" + "="*60)
    print("Setting up Web Template")
    print("="*60)
    
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    source = os.path.join(template_dir, 'index_simple.html')
    dest = os.path.join(template_dir, 'index_offline.html')
    
    if os.path.exists(dest):
        print(f"✓ Template already exists: {dest}")
        return True
    
    if not os.path.exists(source):
        print(f"✗ Source template not found: {source}")
        return False
    
    try:
        shutil.copy(source, dest)
        print(f"✓ Created offline template: {dest}")
        print("\nNote: Edit templates/index_offline.html to customize:")
        print("  - Change header to green theme")
        print("  - Update title to 'Offline'")
        print("  - Update footer with Argos/Vosk branding")
        return True
    except Exception as e:
        print(f"✗ Failed to copy template: {e}")
        return False

def verify_setup():
    """Verify all components are installed correctly"""
    print("\n" + "="*60)
    print("Verifying Installation")
    print("="*60)
    
    all_ok = True
    
    # Check Vosk
    try:
        from vosk import Model
        models_dir = os.path.expanduser("~/.vosk/models")
        
        en_model = os.path.join(models_dir, "vosk-model-small-en-us-0.15")
        zh_model = os.path.join(models_dir, "vosk-model-small-cn-0.22")
        
        if os.path.exists(en_model):
            print("✓ English speech model installed")
        else:
            print("✗ English speech model missing")
            all_ok = False
        
        if os.path.exists(zh_model):
            print("✓ Chinese speech model installed")
        else:
            print("✗ Chinese speech model missing")
            all_ok = False
            
    except ImportError:
        print("✗ Vosk not installed (pip install vosk)")
        all_ok = False
    
    # Check Argos Translate
    try:
        import argostranslate.package
        installed = argostranslate.package.get_installed_packages()
        
        has_en_zh = any(pkg.from_code == 'en' and pkg.to_code == 'zh' for pkg in installed)
        has_zh_en = any(pkg.from_code == 'zh' and pkg.to_code == 'en' for pkg in installed)
        
        if has_en_zh:
            print("✓ English→Chinese translation installed")
        else:
            print("✗ English→Chinese translation missing")
            all_ok = False
        
        if has_zh_en:
            print("✓ Chinese→English translation installed")
        else:
            print("✗ Chinese→English translation missing")
            all_ok = False
            
    except ImportError:
        print("✗ Argos Translate not installed (pip install argostranslate)")
        all_ok = False
    
    # Check template
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index_offline.html')
    if os.path.exists(template_path):
        print("✓ Offline template created")
    else:
        print("✗ Offline template missing")
        all_ok = False
    
    return all_ok

def main():
    print("\n" + "="*60)
    print("  Offline Voice Translator - Setup")
    print("="*60)
    print("\nThis script will download and install:")
    print("  1. Vosk speech recognition models (~82 MB)")
    print("  2. Argos Translate language packages (~200 MB)")
    print("  3. Web interface template")
    print("\nTotal download size: ~300 MB")
    print("This requires an internet connection (one time only)")
    
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Setup cancelled")
        return
    
    # Setup components
    setup_vosk_models()
    setup_argos_translate()
    setup_template()
    
    # Verify
    print()
    if verify_setup():
        print("\n" + "="*60)
        print("  ✓ Setup Complete!")
        print("="*60)
        print("\nYou can now run the offline translator:")
        print("  python app_offline.py")
        print("\nThen open: http://localhost:8081")
        print("\nThe system will work completely offline!")
    else:
        print("\n" + "="*60)
        print("  ✗ Setup Incomplete")
        print("="*60)
        print("\nSome components failed to install.")
        print("Check the error messages above and try again.")
        print("\nFor manual installation, see: OFFLINE_SETUP.md")

if __name__ == '__main__':
    main()
