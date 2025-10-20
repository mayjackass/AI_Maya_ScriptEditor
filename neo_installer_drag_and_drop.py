"""
NEO Script Editor - Drag & Drop Installer for Maya
==================================================

INSTALLATION INSTRUCTIONS:
1. Extract the NEO Script Editor project ZIP file 
2. Drag and drop this installer (neo_installer.py) into Maya's viewport
3. Everything installs automatically!

What this installer does:
- Copies NEO Script Editor files from project folder to Maya scripts folder
- Sets up userSetup.py automatically
- Creates NEO shelf with logo buttons
- Launches standalone always-on-top NEO Script Editor
- Adds menu bar integration

After installation, restart Maya and enjoy NEO Script Editor!

Author: Mayj Amilano (mayjackass)
Version: 3.2 Beta
"""

import maya.cmds as cmds
import maya.mel as mel
import os
import sys
import shutil
from functools import partial

# Installer configuration
GITHUB_REPO = "https://github.com/mayjackass/AI_Maya_ScriptEditor"
INSTALLER_VERSION = "3.2.0"

class NEOInstaller:
    """Drag & Drop installer for NEO Script Editor"""
    
    def __init__(self):
        self.maya_scripts_dir = None
        self.neo_install_dir = None
        self.project_source_dir = None
        self.success = False
        
        # Maya paths - use global scripts directory for all Maya versions
        version_specific_dir = cmds.internalVar(userScriptDir=True)
        print(f"[DEBUG] Maya version-specific dir: {version_specific_dir}")
        
        # Extract the base maya directory and use global scripts folder
        # Handle different Maya directory structures:
        # Windows: C:\Users\Username\Documents\maya\2026\scripts -> C:\Users\Username\Documents\maya\scripts
        # The version_specific_dir ends with something like "maya/2026/scripts" or "maya\\2026\\scripts"
        
        # Split the path and find the maya directory
        path_parts = version_specific_dir.replace('\\', '/').split('/')
        maya_index = -1
        for i, part in enumerate(path_parts):
            if part == 'maya':
                maya_index = i
                break
        
        if maya_index >= 0:
            # Reconstruct path up to maya directory, then add scripts
            maya_base_parts = path_parts[:maya_index + 1]  # Include 'maya' folder
            maya_base_dir = '/'.join(maya_base_parts)
            if os.name == 'nt':  # Windows
                maya_base_dir = maya_base_dir.replace('/', '\\')
            self.maya_scripts_dir = os.path.join(maya_base_dir, "scripts")
        else:
            # Fallback: use version-specific directory (safer than failing)
            print("[WARNING] Could not find 'maya' in path, using version-specific directory")
            self.maya_scripts_dir = version_specific_dir
            
        self.neo_install_dir = os.path.join(self.maya_scripts_dir, "neo_script_editor")
        
        # Ensure the global scripts directory exists
        if not os.path.exists(self.maya_scripts_dir):
            os.makedirs(self.maya_scripts_dir)
            print(f"Created global Maya scripts directory: {self.maya_scripts_dir}")
        
        print(f"Installation paths:")
        print(f"  Version-specific dir: {version_specific_dir}")
        print(f"  Global scripts dir: {self.maya_scripts_dir}")
        print(f"  NEO install dir: {self.neo_install_dir}")
        
        # Verify the path is actually global, not version-specific
        if "2026" in self.maya_scripts_dir or "2025" in self.maya_scripts_dir or "2024" in self.maya_scripts_dir:
            print(f"[WARNING] Installation path appears to be version-specific: {self.maya_scripts_dir}")
        else:
            print(f"[SUCCESS] Using global Maya scripts directory: {self.maya_scripts_dir}")
        
        # Find the project source directory (where this installer is located)
        installer_path = __file__ if '__file__' in globals() else os.path.abspath(__file__)
        self.project_source_dir = os.path.dirname(installer_path)
        
        print("=" * 80)
        print("NEO Script Editor - Drag & Drop Installer v" + INSTALLER_VERSION)
        print("=" * 80)
        print(f"Project Source Directory: {self.project_source_dir}")
        print(f"Maya Scripts Directory: {self.maya_scripts_dir}")
        print(f"NEO Install Directory: {self.neo_install_dir}")
        print()
    
    def run_installation(self):
        """Main installation process"""
        try:
            # Show welcome dialog
            if not self._show_welcome_dialog():
                print("[CANCEL] Installation cancelled by user")
                return False
            
            # Create progress window
            progress_win = self._create_progress_window()
            
            # Step 1: Validate project folder
            self._update_progress(progress_win, 10, "Validating project folder...")
            if not self._validate_project_folder():
                self._close_progress(progress_win)
                return False
            
            # Step 2: Install files
            self._update_progress(progress_win, 30, "Installing files...")
            if not self._install_files():
                self._close_progress(progress_win)
                return False
            
            # Step 3: Setup userSetup.py
            self._update_progress(progress_win, 50, "Configuring Maya startup...")
            if not self._setup_user_setup():
                self._close_progress(progress_win)
                return False
            
            # Step 4: Add to Python path
            self._update_progress(progress_win, 60, "Adding to Python path...")
            self._add_to_python_path()
            
            # Step 5: Create NEO shelf
            self._update_progress(progress_win, 70, "Creating NEO shelf...")
            shelf_success = self._create_neo_shelf()
            if not shelf_success:
                print("⚠️ Shelf creation failed, but installation will continue")
            
            # Step 6: Add menu bar
            self._update_progress(progress_win, 80, "Adding menu bar...")
            self._add_menu_bar()
            
            # Step 7: Launch NEO Script Editor
            self._update_progress(progress_win, 90, "Launching NEO Script Editor...")
            self._launch_neo_editor()
            
            # Complete
            self._update_progress(progress_win, 100, "Installation complete!")
            self._close_progress(progress_win)
            
            # Print success message to console
            print("\n" + "="*60)
            print("🎉 NEO SCRIPT EDITOR INSTALLATION COMPLETE! 🎉")
            print("="*60)
            print("✅ NEO Script Editor files installed")
            print("✅ Maya integration configured")
            print("✅ NEO shelf with matrix icon created")
            print("✅ Ready to code with NEO Script Editor!")
            print("="*60)
            
            self.success = True
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Installation failed: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_dialog(str(e))
            return False
    
    def _show_welcome_dialog(self):
        """Show welcome dialog with installation options"""
        return self._create_themed_dialog(
            title="NEO Script Editor Installer",
            message=(
                "Welcome to NEO Script Editor v3.2 Beta!\n\n"
                "[FEATURES]\n"
                "• Maya integration for seamless workflow\n"
                "• AI assistant with OpenAI/Claude support\n"
                "• 320+ Maya command validation\n"
                "• VSCode-style editor with syntax highlighting\n"
                "• Dedicated NEO shelf with matrix icon\n\n"
                "This installer will:\n"
                "• Copy NEO Script Editor from project folder\n"
                "• Set up Maya integration (userSetup.py)\n"
                "• Create NEO shelf and menu\n"
                "• Launch the standalone editor\n\n"
                f"Project folder: {os.path.basename(self.project_source_dir)}\n"
                f"Install to: {self.maya_scripts_dir}\n\n"
                "Continue with installation?"
            ),
            buttons=["Install", "Cancel"],
            default_button="Install"
        ) == "Install"
    
    def _create_progress_window(self):
        """Create progress window"""
        if cmds.window("neoInstallerProgress", exists=True):
            cmds.deleteUI("neoInstallerProgress", window=True)
        
        window = cmds.window(
            "neoInstallerProgress",
            title="Installing NEO Script Editor",
            widthHeight=(400, 120),
            resizeToFitChildren=True
        )
        
        cmds.columnLayout(adjustableColumn=True, columnAlign="center", rowSpacing=5)
        cmds.separator(height=10, style="none")  # Top spacing

        cmds.text("progressLabel", label="Preparing installation...", font="boldLabelFont")
        cmds.separator(height=10)

        cmds.progressBar("progressBar", maxValue=100, width=360)
        cmds.separator(height=10)

        cmds.text("statusLabel", label="Starting...", font="plainLabelFont")
        cmds.separator(height=10, style="none")  # Bottom spacing
        
        cmds.showWindow(window)
        cmds.refresh()
        
        return window
    
    def _update_progress(self, window, value, status):
        """Update Maya progress window"""
        if cmds.window(window, exists=True):
            cmds.progressBar("progressBar", edit=True, progress=value)
            cmds.text("statusLabel", edit=True, label=status)
            cmds.refresh()
        print(f"[{value:3d}%] {status}")
    
    def _close_progress(self, window):
        """Close progress window"""
        if cmds.window(window, exists=True):
            cmds.deleteUI(window, window=True)
    
    def _validate_project_folder(self):
        """Validate that we have a complete NEO Script Editor project folder"""
        try:
            print(f"Validating project folder: {self.project_source_dir}")
            
            # Check if essential files exist in the project folder
            essential_files = [
                "main_window.py",
                "run.py", 
                "__init__.py"
            ]
            
            # Check for script files
            scripts_maya_path = os.path.join(self.project_source_dir, "scripts", "maya")
            if os.path.exists(scripts_maya_path):
                essential_files.extend([
                    os.path.join("scripts", "maya", "complete_setup.py"),
                    os.path.join("scripts", "maya", "maya_shelf_creator.py")
                ])
            else:
                # If scripts/maya doesn't exist, we'll need to create minimal versions
                print("⚠️ Full script files not found, will create minimal installation")
            
            # Validate essential files
            missing_files = []
            for file_path in essential_files:
                full_path = os.path.join(self.project_source_dir, file_path)
                if not os.path.exists(full_path):
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"⚠️ Some files missing: {missing_files}")
                print("Will proceed with available files and create missing components")
            else:
                print("[SUCCESS] Project folder validation successful")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Project folder validation failed: {e}")
            self._show_error_dialog(f"Project folder validation failed: {e}\n\nMake sure you extracted the complete NEO Script Editor project.")
            return False
    
    def _install_files(self):
        """Install NEO Script Editor files to Maya scripts directory"""
        try:
            # Check if NEO Script Editor is already installed
            if os.path.exists(self.neo_install_dir):
                # Check if it's a valid NEO installation
                main_window_path = os.path.join(self.neo_install_dir, "main_window.py")
                if os.path.exists(main_window_path):
                    # Existing installation found - ask user what to do
                    choice = self._create_themed_dialog(
                        title="Existing NEO Installation Found",
                        message=(
                            f"NEO Script Editor is already installed at:\n{self.neo_install_dir}\n\n"
                            "Choose how to proceed:\n\n"
                            "• Update: Replace with new version (recommended)\n"
                            "• Cancel: Keep existing installation\n\n"
                            "Note: Your settings and preferences will be preserved."
                        ),
                        buttons=["Update", "Cancel"],
                        default_button="Update"
                    )
                    
                    if choice != "Update":
                        print("[INFO] Installation cancelled - keeping existing NEO Script Editor")
                        return False
                    
                    print(f"[UPDATE] Updating existing NEO Script Editor installation")
                    # Backup user settings before update
                    self._backup_user_settings()
                else:
                    print(f"[CLEANUP] Removing invalid/corrupted installation at: {self.neo_install_dir}")
                
                # Remove existing installation
                shutil.rmtree(self.neo_install_dir)
            
            # Copy files from project folder to Maya scripts directory
            print(f"[INSTALL] Installing NEO Script Editor to: {self.neo_install_dir}")
            shutil.copytree(self.project_source_dir, self.neo_install_dir)
            
            # Restore user settings if they were backed up
            self._restore_user_settings()
            
            # Verify essential files exist
            essential_files = [
                "main_window.py",
                "run.py",
                "__init__.py"
            ]
            
            # Check for Maya scripts
            maya_scripts_path = os.path.join(self.neo_install_dir, "scripts", "maya")
            if os.path.exists(maya_scripts_path):
                essential_files.extend([
                    "scripts/maya/complete_setup.py",
                    "scripts/maya/maya_shelf_creator.py"
                ])
            else:
                # Create basic Maya integration files if they don't exist
                print("Creating basic Maya integration files...")
                self._create_basic_maya_integration()
            
            # Verify assets folder and matrix icon
            assets_path = os.path.join(self.neo_install_dir, "assets")
            matrix_icon_path = os.path.join(assets_path, "matrix.png")
            
            if not os.path.exists(assets_path):
                print("[WARNING] Assets folder not found in installation")
                print("Creating assets folder with matrix icon...")
                self._create_assets_folder()
            elif not os.path.exists(matrix_icon_path):
                print("[WARNING] Matrix icon not found in assets folder")
                print("Creating matrix icon...")
                self._create_matrix_icon(matrix_icon_path)
            else:
                print(f"[SUCCESS] Matrix icon found at: {matrix_icon_path}")
            
            # Verify files
            missing_files = []
            for file_path in essential_files:
                full_path = os.path.join(self.neo_install_dir, file_path)
                if not os.path.exists(full_path):
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"[WARNING] Some files missing after installation: {missing_files}")
                print("Creating minimal replacements...")
                self._create_minimal_files()
            
            print("[SUCCESS] Files installed successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] File installation failed: {e}")
            return False
    
    def _setup_user_setup(self):
        """Setup or update userSetup.py"""
        try:
            user_setup_path = os.path.join(self.maya_scripts_dir, "userSetup.py")
            
            print(f"Setting up userSetup.py at: {user_setup_path}")
            
            # Check if userSetup.py already exists
            if os.path.exists(user_setup_path):
                # Back up existing userSetup.py
                backup_path = user_setup_path + ".backup_before_neo"
                shutil.copy2(user_setup_path, backup_path)
                print(f"[BACKUP] Backed up existing userSetup.py to: {backup_path}")
                
                # Check if NEO is already integrated
                with open(user_setup_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "setup_neo_editor" in content:
                    print("[INFO] NEO setup already present in userSetup.py")
                    return True
                
                # Ask user what to do
                result = self._create_themed_dialog(
                    title="Existing userSetup.py Found",
                    message=(
                        "You already have a userSetup.py file.\n\n"
                        "Options:\n"
                        "• Replace: Use NEO's userSetup.py (recommended)\n"
                        "• Append: Add NEO setup to your existing file\n"
                        "• Manual: Set up NEO manually later\n\n"
                        "Your existing file has been backed up."
                    ),
                    buttons=["Replace", "Append", "Manual"],
                    default_button="Replace"
                )
                
                if result == "Replace":
                    self._create_minimal_user_setup(user_setup_path)
                    print("[SUCCESS] Replaced userSetup.py with NEO version")
                elif result == "Append":
                    self._append_to_user_setup_existing(user_setup_path)
                    print("[SUCCESS] Appended NEO setup to existing userSetup.py")
                else:
                    print("[INFO] Manual setup required - userSetup.py not modified")
                    return True  # Don't fail installation
            else:
                # No existing userSetup.py, create NEO version
                self._create_minimal_user_setup(user_setup_path)
                print("[SUCCESS] Created new userSetup.py with NEO integration")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] userSetup.py setup failed: {e}")
            return False

    def _get_user_setup_content(self):
        """Generate the userSetup.py content - used by both create and append methods"""
        return '''"""
NEO Script Editor - Maya Startup Integration
Auto-generated by NEO installer
"""

def setup_neo_editor():
    """Setup NEO Script Editor in Maya - runs every time Maya starts"""
    try:
        import sys
        import os
        import maya.cmds as cmds
        import maya.mel as mel
        from functools import partial
        
        # Add NEO to Python path
        maya_scripts = cmds.internalVar(userScriptDir=True)
        # Get global scripts directory (not version-specific)
        path_parts = maya_scripts.replace('\\\\', '/').split('/')
        maya_index = -1
        for i, part in enumerate(path_parts):
            if part == 'maya':
                maya_index = i
                break
        
        if maya_index >= 0:
            maya_base_parts = path_parts[:maya_index + 1]
            maya_base_dir = '/'.join(maya_base_parts)
            if os.name == 'nt':  # Windows
                maya_base_dir = maya_base_dir.replace('/', '\\\\')
            global_scripts_dir = os.path.join(maya_base_dir, "scripts")
            neo_path = os.path.join(global_scripts_dir, "neo_script_editor")
        else:
            # Fallback to version-specific
            neo_path = os.path.join(os.path.dirname(maya_scripts), "neo_script_editor")
        
        if neo_path not in sys.path and os.path.exists(neo_path):
            sys.path.insert(0, neo_path)
        
        # Import NEO functions
        try:
            from scripts.maya.complete_setup import complete_neo_setup, launch_neo_editor
            
            # Make functions globally available
            import __main__
            __main__.complete_neo_setup = complete_neo_setup
            __main__.launch_neo_editor = launch_neo_editor
            
            # Define about dialog function that uses the main UI's dialog
            def show_neo_about_dialog():
                """Show NEO about dialog using the main UI's dialog"""
                try:
                    # Import from NEO UI module
                    neo_ui_path = os.path.join(neo_path, "ui")
                    if neo_ui_path not in sys.path:
                        sys.path.insert(0, neo_ui_path)
                    
                    from dialog_styles import show_about_dialog
                    show_about_dialog()
                    print("[SUCCESS] Showed NEO about dialog from main UI")
                    
                except Exception as e:
                    print(f"[WARNING] Could not show main UI about dialog: {e}")
                    # Fallback to Matrix-themed Maya dialog
                    try:
                        result = cmds.confirmDialog(
                            title="About NEO Script Editor",
                            message="NEO Script Editor v3.2 Beta\\\\n\\\\nAI-Powered Script Editor for Maya\\\\nBy Mayj Amilano\\\\n\\\\nBeta License expires: January 31, 2026",
                            button=["OK"],
                            defaultButton="OK",
                            backgroundColor=[0.051, 0.067, 0.090]  # Matrix dark theme
                        )
                    except:
                        # Final fallback without theming
                        result = cmds.confirmDialog(
                            title="About NEO Script Editor",
                            message="NEO Script Editor v3.2 Beta\\\\n\\\\nBy Mayj Amilano",
                            button=["OK"],
                            defaultButton="OK"
                        )
            
            # Define single-instance launch function
            def launch_neo_editor_single():
                """Launch NEO editor with single-instance management"""
                try:
                    # Close any existing NEO windows first
                    from PySide6 import QtWidgets
                    import time
                    app = QtWidgets.QApplication.instance()
                    if app:
                        closed_any = False
                        for widget in app.allWidgets():
                            if widget.__class__.__name__ == "NEOMainWindow":
                                try:
                                    widget.close()
                                    widget.deleteLater()
                                    closed_any = True
                                    print("[INFO] Closed existing NEO window")
                                except:
                                    pass
                        
                        # Wait for windows to close
                        if closed_any:
                            app.processEvents()
                            time.sleep(0.1)
                    
                    # Launch new instance
                    return launch_neo_editor()
                    
                except Exception as e:
                    print(f"[WARNING] Single-instance check failed: {e}")
                    # Fallback to regular launch
                    return launch_neo_editor()
            
            # Make functions globally available
            __main__.show_neo_about_dialog = show_neo_about_dialog
            __main__.launch_neo_editor_single = launch_neo_editor_single
            
            # Create NEO menu bar (every Maya startup)
            def create_neo_menu():
                try:
                    main_menu = mel.eval('$tempVar = $gMainWindow')
                    
                    # Remove existing menu if it exists
                    if cmds.menu("neoScriptEditorMenu", exists=True):
                        cmds.deleteUI("neoScriptEditorMenu", menu=True)
                    
                    # Create NEO menu
                    neo_menu = cmds.menu(
                        "neoScriptEditorMenu",
                        label="NEO",
                        parent=main_menu,
                        tearOff=True
                    )
                    
                    # Add menu items
                    cmds.menuItem(
                        label="Launch NEO Script Editor",
                        command="launch_neo_editor_single()",
                        parent=neo_menu,
                        image="pythonFamily.png"
                    )
                    
                    cmds.menuItem(divider=True, parent=neo_menu)
                    
                    cmds.menuItem(
                        label="Complete NEO Setup",
                        command="complete_neo_setup()",
                        parent=neo_menu
                    )
                    
                    cmds.menuItem(divider=True, parent=neo_menu)
                    
                    cmds.menuItem(
                        label="About NEO Script Editor",
                        command="show_neo_about_dialog()",
                        parent=neo_menu
                    )
                    
                except Exception as e:
                    print(f"[WARNING] NEO menu creation failed: {e}")
            
            # Create NEO shelf (every Maya startup)
            def create_neo_shelf():
                try:
                    # Create or get NEO shelf
                    shelf_name = "NEO"
                    if cmds.shelfLayout(shelf_name, exists=True):
                        # Shelf exists, check if it has our button
                        buttons = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
                        neo_button_exists = False
                        for button in buttons:
                            if cmds.shelfButton(button, query=True, exist=True):
                                label = cmds.shelfButton(button, query=True, label=True)
                                if label == "NEO":
                                    neo_button_exists = True
                                    break
                        
                        if neo_button_exists:
                            return  # NEO button already exists
                    else:
                        # Create new shelf
                        shelf = cmds.shelfLayout(shelf_name, parent="ShelfLayout")
                    
                    # Add NEO button
                    matrix_icon = os.path.join(neo_path, "assets", "matrix.png")
                    icon = matrix_icon if os.path.exists(matrix_icon) else "pythonFamily.png"
                    
                    cmds.shelfButton(
                        parent=shelf_name,
                        label="NEO",
                        annotation="Launch NEO Script Editor (Single Instance)",
                        image=icon,
                        command="launch_neo_editor_single()",
                        sourceType="python"
                    )
                    
                except Exception as e:
                    print(f"[WARNING] NEO shelf creation failed: {e}")
            
            # Set up menu and shelf on Maya startup
            create_neo_menu()
            create_neo_shelf()
            
            print("✅ NEO Script Editor ready! Menu: NEO | Shelf: NEO | Command: launch_neo_editor_single()")
            
        except ImportError as e:
            print(f"[ERROR] NEO Script Editor import failed: {e}")
            
    except Exception as e:
        print(f"[ERROR] NEO Script Editor setup failed: {e}")

# Run setup when Maya starts
try:
    import maya.cmds as cmds
    # Use evalDeferred to ensure Maya UI is fully loaded
    cmds.evalDeferred("setup_neo_editor()")
except:
    pass
'''
    
    def _create_minimal_user_setup(self, user_setup_path):
        """Create minimal userSetup.py with NEO integration"""
        user_setup_content = self._get_user_setup_content()
        with open(user_setup_path, 'w', encoding='utf-8') as f:
            f.write(user_setup_content)
    
    def _append_to_user_setup_existing(self, existing_path):
        """Append NEO setup to existing userSetup.py"""
        try:
            # Read existing userSetup.py
            with open(existing_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Check if NEO is already integrated
            if "setup_neo_editor" in existing_content:
                print("[INFO] NEO setup already present in userSetup.py")
                return
            
            # Get NEO integration content from helper method (without the file docstring)
            user_setup_content = self._get_user_setup_content()
            # Remove the file-level docstring, keep only the function and execution code
            parts = user_setup_content.split('"""')
            if len(parts) >= 3:
                # Reconstruct without file docstring: skip first """ block
                neo_content = parts[2].lstrip()
            else:
                neo_content = user_setup_content
            
            # Append NEO setup with header
            combined_content = existing_content + "\n\n" + "# " + "="*50 + "\n"
            combined_content += "# NEO Script Editor Integration (Auto-added by installer)\n"
            combined_content += "# " + "="*50 + "\n\n"
            combined_content += neo_content
            
            # Write combined file
            with open(existing_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            print("[SUCCESS] NEO setup appended to existing userSetup.py")
            
        except Exception as e:
            print(f"[ERROR] Failed to append to userSetup.py: {e}")
    
    def _create_basic_maya_integration(self):
        """Create basic Maya integration files if they don't exist"""
        try:
            # Create scripts/maya directory
            maya_scripts_dir = os.path.join(self.neo_install_dir, "scripts", "maya")
            os.makedirs(maya_scripts_dir, exist_ok=True)
            
            # Create basic complete_setup.py
            setup_content = '''"""
NEO Script Editor - Complete Setup
"""

try:
    import maya.cmds as cmds
    import sys
    import os
    
    def complete_neo_setup():
        """Complete NEO setup"""
        print("NEO Script Editor - Complete Setup")
        
        # Add to Python path
        neo_dir = os.path.dirname(os.path.dirname(__file__))
        if neo_dir not in sys.path:
            sys.path.insert(0, neo_dir)
        
        try:
            from main_window import launch_neo_editor
            launch_neo_editor()
            print("[SUCCESS] NEO Script Editor launched")
        except Exception as e:
            print(f"[ERROR] Launch failed: {e}")
    
    def launch_neo_editor():
        """Launch standalone NEO"""
        complete_neo_setup()

except ImportError:
    def complete_neo_setup():
        print("NEO Script Editor requires Maya environment")
    
    def launch_neo_editor():
        print("NEO Script Editor requires Maya environment")
'''
            
            setup_path = os.path.join(maya_scripts_dir, "complete_setup.py")
            with open(setup_path, 'w', encoding='utf-8') as f:
                f.write(setup_content)
            
            # Create basic maya_shelf_creator.py
            shelf_content = '''"""
NEO Script Editor - Shelf Creator
"""

try:
    import maya.cmds as cmds
    
    def create_neo_shelf():
        """Create NEO shelf"""
        print("Creating NEO shelf...")
        
        # Create or get NEO shelf
        shelf_name = "NEO"
        if cmds.shelfLayout(shelf_name, exists=True):
            cmds.deleteUI(shelf_name, layout=True)
        
        shelf = cmds.shelfLayout(shelf_name, parent="ShelfLayout")
        
        # Add NEO button
        cmds.shelfButton(
            parent=shelf,
            label="NEO",
            annotation="Launch NEO Script Editor (Single Instance)",
            image="pythonFamily.png",
            command="complete_neo_setup()",
            sourceType="python"
        )
        
        print("[SUCCESS] NEO shelf created")
        return True

except ImportError:
    def create_neo_shelf():
        print("NEO Script Editor requires Maya environment")
        return False
'''
            
            shelf_path = os.path.join(maya_scripts_dir, "maya_shelf_creator.py")
            with open(shelf_path, 'w', encoding='utf-8') as f:
                f.write(shelf_content)
            
            print("[SUCCESS] Created basic Maya integration files")
            
        except Exception as e:
            print(f"[ERROR] Failed to create basic Maya integration: {e}")

    def _add_to_python_path(self):
        """Add NEO Script Editor to Python path"""
        if self.neo_install_dir not in sys.path:
            sys.path.insert(0, self.neo_install_dir)
            print(f"✅ Added to Python path: {self.neo_install_dir}")
    
    def _create_neo_shelf(self):
        """Create NEO shelf using the installed shelf creator"""
        try:
            # Import the shelf creator from installed files
            maya_scripts_path = os.path.join(self.neo_install_dir, "scripts", "maya")
            
            if maya_scripts_path not in sys.path:
                sys.path.insert(0, maya_scripts_path)
            
            from maya_shelf_creator import force_recreate_shelf
            
            # Force recreate to ensure clean shelf
            success = force_recreate_shelf()
            
            if success:
                print("[SUCCESS] NEO shelf created successfully")
                return True
            else:
                print("[ERROR] NEO shelf creation failed")
                return False
        
        except Exception as e:
            print(f"[ERROR] NEO shelf creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _add_menu_bar(self):
        """Add NEO Script Editor to Maya's menu bar"""
        try:
            # Add to main Maya menu bar
            main_menu = mel.eval('$tempVar = $gMainWindow')
            
            # Check if NEO menu already exists
            if cmds.menu("neoScriptEditorMenu", exists=True):
                cmds.deleteUI("neoScriptEditorMenu", menu=True)
            
            # Create NEO menu
            neo_menu = cmds.menu(
                "neoScriptEditorMenu",
                label="NEO",
                parent=main_menu,
                tearOff=True
            )
            
            # Add menu items
            cmds.menuItem(
                label="Launch NEO Script Editor",
                command=partial(self._launch_neo_editor_single_instance),
                parent=neo_menu,
                image="pythonFamily.png"
            )
            
            cmds.menuItem(divider=True, parent=neo_menu)
            
            cmds.menuItem(
                label="Complete NEO Setup",
                command="complete_neo_setup()",
                parent=neo_menu
            )
            
            cmds.menuItem(divider=True, parent=neo_menu)
            
            cmds.menuItem(
                label="About NEO Script Editor",
                command=partial(self._show_about_dialog),
                parent=neo_menu
            )
            
            print("✅ NEO menu added to menu bar")
            
        except Exception as e:
            print(f"⚠️ Menu bar integration failed: {e}")
            # Don't fail installation for menu issues

    def _launch_neo_editor(self):
        """Launch NEO Script Editor"""
        try:
            # Import and run the complete setup
            maya_scripts_path = os.path.join(self.neo_install_dir, "scripts", "maya")
            if maya_scripts_path not in sys.path:
                sys.path.insert(0, maya_scripts_path)
            
            from complete_setup import complete_neo_setup
            complete_neo_setup()
            
            print("[SUCCESS] NEO Script Editor launched")
            
        except Exception as e:
            print(f"[WARNING] NEO Script Editor launch failed: {e}")
            print("You can launch it manually with: complete_neo_setup()")
    
    def _launch_neo_editor_single_instance(self, *args):
        """Launch NEO editor with single-instance management - simple approach"""
        try:
            # Check if NEO window already exists - if yes, close it
            from PySide6 import QtWidgets
            import time
            app = QtWidgets.QApplication.instance()
            if app:
                closed_any = False
                for widget in app.allWidgets():
                    if widget.__class__.__name__ == "NEOMainWindow":
                        try:
                            widget.close()
                            widget.deleteLater()
                            closed_any = True
                            print("[INFO] Closed existing NEO window")
                        except:
                            pass
                
                # Wait for windows to close
                if closed_any:
                    app.processEvents()
                    time.sleep(0.1)
            
            # Launch new instance
            self._launch_neo_editor()
            
        except Exception as e:
            print(f"[WARNING] Single-instance check failed: {e}")
            # Fallback to regular launch
            self._launch_neo_editor()
    
    def _show_error_dialog(self, error_message):
        """Show installation error dialog"""
        self._create_themed_dialog(
            title="Installation Failed",
            message=(
                f"[ERROR] Installation encountered an error:\n\n{error_message}\n\n"
                "Possible solutions:\n"
                "• Make sure you extracted the complete project folder\n"
                "• Check that the installer is in the project root\n"
                "• Check Maya's Script Editor for detailed errors\n"
                "• Try running Maya as administrator\n\n"
                f"Get help: {GITHUB_REPO}"
            ),
            buttons=["OK"],
            default_button="OK"
        )
    
    def _create_minimal_files(self):
        """Create minimal essential files"""
        
        # Create __init__.py
        init_content = '''"""
NEO Script Editor - AI-Powered Maya Script Editor
Version 3.2 Beta (Installed via drag & drop)
"""

__version__ = "3.2.0"
__author__ = "Mayj Amilano"
'''
        self._write_file("__init__.py", init_content)
        
        # Create basic main_window.py
        main_window_content = '''"""
Basic NEO Script Editor Window
This is a minimal installation - download full version for complete features
"""

try:
    import maya.cmds as cmds
    from PySide6 import QtWidgets, QtCore
    
    class NEOScriptEditor(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("NEO Script Editor (Minimal)")
            self.setGeometry(100, 100, 800, 600)
            
            # Central widget
            central = QtWidgets.QWidget()
            self.setCentralWidget(central)
            layout = QtWidgets.QVBoxLayout(central)
            
            # Message
            msg = QtWidgets.QLabel("Please download the full NEO Script Editor\\nfrom GitHub for complete functionality")
            msg.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(msg)
            
            # Basic text editor
            self.editor = QtWidgets.QTextEdit()
            self.editor.setPlainText("# NEO Script Editor - Minimal Installation\\n# Download full version from GitHub\\n\\nimport maya.cmds as cmds\\ncmds.polySphere()")
            layout.addWidget(self.editor)
            
            # Run button
            run_btn = QtWidgets.QPushButton("Run Script")
            run_btn.clicked.connect(self.run_script)
            layout.addWidget(run_btn)
        
        def run_script(self):
            code = self.editor.toPlainText()
            try:
                exec(code)
                print("Script executed successfully")
            except Exception as e:
                print(f"Script error: {e}")
    
    def launch_neo_editor():
        """Launch NEO Script Editor"""
        global neo_window
        try:
            neo_window.close()
        except:
            pass
        neo_window = NEOScriptEditor()
        neo_window.show()
        return neo_window

except ImportError:
    def launch_neo_editor():
        print("NEO Script Editor requires Maya environment")
'''
        self._write_file("main_window.py", main_window_content)
        
        # Create run.py
        run_content = '''"""Run NEO Script Editor"""
from main_window import launch_neo_editor

if __name__ == "__main__":
    launch_neo_editor()
'''
        self._write_file("run.py", run_content)
        
        # Create Maya integration files
        self._create_maya_files()
    
    def _create_maya_files(self):
        """Create Maya integration files"""
        
        # Create complete_setup.py
        setup_content = '''"""
NEO Script Editor - Complete Setup (Minimal Version)
"""

try:
    import maya.cmds as cmds
    import sys
    import os
    
    def complete_neo_setup():
        """Complete NEO setup - minimal version"""
        print("NEO Script Editor - Minimal Setup")
        
        # Add to Python path
        neo_dir = os.path.dirname(os.path.dirname(__file__))
        if neo_dir not in sys.path:
            sys.path.insert(0, neo_dir)
        
        try:
            from main_window import launch_neo_editor
            launch_neo_editor()
            print("NEO Script Editor launched (minimal version)")
            print("Download full version from GitHub for complete features")
        except Exception as e:
            print(f"❌ Launch failed: {e}")
    
    def launch_neo_editor():
        """Launch standalone NEO"""
        complete_neo_setup()

except ImportError:
    def complete_neo_setup():
        print("NEO Script Editor requires Maya environment")
    
    def launch_neo_editor():
        print("NEO Script Editor requires Maya environment")
'''
        self._write_file("scripts/maya/complete_setup.py", setup_content)
        
        # Create userSetup.py
        user_setup_content = '''"""
NEO Script Editor - Maya Startup Integration
Auto-generated by NEO installer
"""

def setup_neo_editor():
    """Setup NEO Script Editor in Maya"""
    try:
        import sys
        import os
        
        # Add NEO to Python path
        maya_scripts = cmds.internalVar(userScriptDir=True) if 'cmds' in globals() else None
        if maya_scripts:
            neo_path = os.path.join(maya_scripts, "neo_script_editor")
            if neo_path not in sys.path and os.path.exists(neo_path):
                sys.path.insert(0, neo_path)
        
        # Import NEO functions
        try:
            from scripts.maya.complete_setup import complete_neo_setup, launch_neo_editor
            
            # Make functions globally available
            import __main__
            __main__.complete_neo_setup = complete_neo_setup
            __main__.launch_neo_editor = launch_neo_editor
            
            print("🚀 NEO Script Editor ready! Use: launch_neo_editor()")
            
        except ImportError as e:
            print(f"NEO Script Editor import failed: {e}")
            
    except Exception as e:
        print(f"NEO Script Editor setup failed: {e}")

# Run setup when Maya starts
try:
    import maya.cmds as cmds
    setup_neo_editor()
except:
    pass
'''
        self._write_file("scripts/maya/userSetup.py", user_setup_content)
    
    def _write_file(self, relative_path, content):
        """Write content to file in NEO installation directory"""
        full_path = os.path.join(self.neo_install_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[SUCCESS] Created: {relative_path}")

    def _create_assets_folder(self):
        """Create assets folder with essential icons"""
        try:
            assets_path = os.path.join(self.neo_install_dir, "assets")
            os.makedirs(assets_path, exist_ok=True)
            
            # Create matrix icon
            matrix_icon_path = os.path.join(assets_path, "matrix.png")
            self._create_matrix_icon(matrix_icon_path)
            
            print(f"[SUCCESS] Created assets folder at: {assets_path}")
            
        except Exception as e:
            print(f"[ERROR] Failed to create assets folder: {e}")

    def _create_matrix_icon(self, icon_path):
        """Create a simple matrix-style icon if the original is missing"""
        try:
            # For a complete installer, we should embed the actual matrix.png data here
            # For now, create a fallback that Maya can use
            
            # Create directory if needed
            os.makedirs(os.path.dirname(icon_path), exist_ok=True)
            
            # Try to copy from source project first
            source_icon = os.path.join(self.project_source_dir, "assets", "matrix.png")
            if os.path.exists(source_icon):
                import shutil
                shutil.copy2(source_icon, icon_path)
                print(f"[SUCCESS] Copied matrix icon from source: {icon_path}")
                return
            
            # If source not available, create a minimal placeholder
            # This is a fallback - the real matrix.png should be embedded in production
            print(f"[WARNING] Source matrix.png not found at: {source_icon}")
            print(f"[INFO] Creating fallback icon placeholder")
            
            # Create a simple text file as placeholder
            placeholder_path = icon_path.replace('.png', '_placeholder.txt')
            with open(placeholder_path, 'w') as f:
                f.write("NEO")
            
            print(f"[NOTE] Created placeholder at: {placeholder_path}")
            print("[NOTE] For full matrix icon, ensure assets/matrix.png is in source project")
            
        except Exception as e:
            print(f"[ERROR] Failed to create matrix icon: {e}")

    def _create_themed_dialog(self, title, message, buttons=["OK"], default_button="OK"):
        """
        Create a Matrix-themed dialog using Maya's confirmDialog with dark styling
        
        Args:
            title: Dialog title
            message: Dialog message
            buttons: List of button names
            default_button: Default button name
            
        Returns:
            str: Selected button name
        """
        try:
            # Matrix color scheme - dark background matching main UI
            matrix_dark_bg = [0.051, 0.067, 0.090]  # #0d1117 converted to RGB 0-1 range
            
            # Use Maya's confirmDialog with Matrix dark background
            result = cmds.confirmDialog(
                title=f"🔲 {title}",  # Add Matrix-style icon
                message=message,
                button=buttons,
                defaultButton=default_button,
                cancelButton=buttons[-1] if len(buttons) > 1 else default_button,
                dismissString=buttons[-1] if len(buttons) > 1 else default_button,
                backgroundColor=matrix_dark_bg,  # Dark Matrix background
                messageAlign="left"  # Better text alignment
            )
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Matrix dialog theming failed: {e}")
            # Fallback to standard dialog without theming
            result = cmds.confirmDialog(
                title=title,
                message=message,
                button=buttons,
                defaultButton=default_button
            )
            return result
    
    def _show_about_dialog(self, *args):
        """Show about dialog using the standardized NEO about dialog from main UI"""
        try:
            # Import from the installed NEO UI module
            neo_ui_path = os.path.join(self.neo_install_dir, "ui")
            if neo_ui_path not in sys.path:
                sys.path.insert(0, neo_ui_path)
            
            from dialog_styles import show_about_dialog
            show_about_dialog()
            print("[SUCCESS] Showed NEO about dialog from main UI")
            
        except Exception as e:
            print(f"[WARNING] Could not show main UI about dialog: {e}")
            # Fallback to Matrix-themed Maya dialog
            try:
                result = cmds.confirmDialog(
                    title="About NEO Script Editor",
                    message=(
                        "NEO Script Editor v3.2 Beta\n"
                        '"I can only show you the door. You\'re the one that has to walk through it."\n\n'
                        "[FEATURES]\n"
                        "• Maya integration for seamless workflow\n"
                        "• AI assistant (OpenAI/Claude)\n"
                        "• 320+ Maya command validation\n"
                        "• VSCode-style editor\n"
                        "• Real-time error detection\n\n"
                        "[INFO] Developer: Mayj Amilano (@mayjackass)\n"
                        "[WEB] GitHub: github.com/mayjackass/AI_Maya_ScriptEditor\n"
                        "[LICENSE] Beta version expires January 31, 2026\n\n"
                        "Enjoy coding with NEO!"
                    ),
                    button=["OK"],
                    defaultButton="OK",
                    dismissString="OK",
                    backgroundColor=[0.051, 0.067, 0.090]  # Matrix dark theme
                )
            except:
                # Final fallback without theming
                result = cmds.confirmDialog(
                    title="About NEO Script Editor",
                    message="NEO Script Editor v3.2 Beta\n\nAI-Powered Script Editor for Maya\nBy Mayj Amilano",
                    button=["OK"],
                    defaultButton="OK"
                )
    
    def _backup_user_settings(self):
        """Backup user settings and preferences before update"""
        try:
            # Define settings files to preserve
            settings_files = [
                "settings.json",
                "user_preferences.json", 
                "api_keys.json",
                "workspace_settings.json"
            ]
            
            backup_dir = os.path.join(self.maya_scripts_dir, "neo_backup_temp")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backed_up_files = []
            for settings_file in settings_files:
                source_path = os.path.join(self.neo_install_dir, settings_file)
                if os.path.exists(source_path):
                    backup_path = os.path.join(backup_dir, settings_file)
                    shutil.copy2(source_path, backup_path)
                    backed_up_files.append(settings_file)
            
            if backed_up_files:
                print(f"[BACKUP] Preserved user settings: {', '.join(backed_up_files)}")
            
        except Exception as e:
            print(f"[WARNING] Settings backup failed: {e}")
    
    def _restore_user_settings(self):
        """Restore user settings and preferences after update"""
        try:
            backup_dir = os.path.join(self.maya_scripts_dir, "neo_backup_temp")
            if not os.path.exists(backup_dir):
                return
            
            restored_files = []
            for backup_file in os.listdir(backup_dir):
                if backup_file.endswith('.json'):
                    backup_path = os.path.join(backup_dir, backup_file)
                    restore_path = os.path.join(self.neo_install_dir, backup_file)
                    shutil.copy2(backup_path, restore_path)
                    restored_files.append(backup_file)
            
            if restored_files:
                print(f"[RESTORE] Restored user settings: {', '.join(restored_files)}")
            
            # Clean up backup directory
            shutil.rmtree(backup_dir)
            
        except Exception as e:
            print(f"[WARNING] Settings restoration failed: {e}")


# =============================================================================
# Drag & Drop Entry Point
# =============================================================================

def onMayaDroppedPythonFile(*args, **kwargs):
    """
    This function is called when a Python file is dragged into Maya's viewport.
    This is the entry point for the drag & drop installer.
    """
    print("\n" + "="*80)
    print("NEO Script Editor Drag & Drop Installer Activated!")
    print("="*80)
    
    # Create and run installer
    installer = NEOInstaller()
    success = installer.run_installation()
    
    if success:
        print("\n" + "="*80)
        print("NEO Script Editor installation completed successfully!")
        print("="*80)
        print("Restart Maya to ensure full integration")
        print("Start coding with NEO Script Editor!")
    else:
        print("\n" + "="*80)
        print("❌ NEO Script Editor installation failed")
        print("="*80)
        print("📖 Check Maya's Script Editor for detailed error information")
        print(f"🌐 Manual installation: {GITHUB_REPO}")


# =============================================================================
# Alternative Entry Points
# =============================================================================

def install_neo_script_editor():
    """Alternative entry point for manual execution"""
    installer = NEOInstaller()
    return installer.run_installation()


def main():
    """Main entry point for direct execution"""
    onMayaDroppedPythonFile()


# Entry point when file is executed directly
if __name__ == "__main__":
    main()


# =============================================================================
# Installation Instructions (Embedded in File)
# =============================================================================

"""
 NEO SCRIPT EDITOR - DRAG & DROP INSTALLER

EASY INSTALLATION (Drag & Drop):
1. Extract the NEO Script Editor project ZIP file
2. Drag neo_installer.py from the project folder into Maya's viewport
3. Follow the installation wizard
4. Restart Maya and enjoy NEO Script Editor!

MANUAL INSTALLATION (If drag & drop fails):
1. Extract the NEO Script Editor project ZIP file
2. Open Maya's Script Editor (Python tab)
3. Load neo_installer.py from the project folder or copy-paste the code
4. Run: install_neo_script_editor()

WHAT GETS INSTALLED:
✓ NEO Script Editor files (neo_script_editor/)
✓ Maya integration (userSetup.py)  
✓ NEO shelf with Matrix logo buttons
✓ NEO menu in Maya's menu bar
✓ Standalone script editor integration

MAYA COMMANDS (Available after installation):
• complete_neo_setup()  - Everything at once
• launch_neo_editor()   - Standalone window (stays within Maya)

PERFECT WORKFLOW:
1. Run complete_neo_setup()
2. Use launch_neo_editor() for standalone editing
3. Enjoy AI-powered script editing within Maya!

REQUIREMENTS:
• Maya 2022+ (Windows/Mac/Linux)
• Complete NEO Script Editor project folder (extracted from ZIP)
• Python 3.7+ (included with Maya)

SUPPORT:
• GitHub: github.com/mayjackass/AI_Maya_ScriptEditor
• Issues: Use GitHub Issues tab
• Version: 3.2 Beta (Expires Jan 31, 2026)

Developed by: Mayj Amilano (@mayjackass)
October 2025
"""