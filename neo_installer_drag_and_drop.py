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
        
        # Maya paths
        self.maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        self.neo_install_dir = os.path.join(self.maya_scripts_dir, "ai_script_editor")
        
        # Find the project source directory (where this installer is located)
        installer_path = __file__ if '__file__' in globals() else os.path.abspath(__file__)
        self.project_source_dir = os.path.dirname(installer_path)
        
        print("=" * 80)
        print("🚀 NEO Script Editor - Drag & Drop Installer v" + INSTALLER_VERSION)
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
                print("❌ Installation cancelled by user")
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
            
            # Show success dialog
            self._show_success_dialog()
            self.success = True
            
            return True
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_dialog(str(e))
            return False
    
    def _show_welcome_dialog(self):
        """Show welcome dialog with installation options"""
        result = cmds.confirmDialog(
            title="NEO Script Editor Installer",
            message=(
                "Welcome to NEO Script Editor v3.2 Beta!\n\n"
                "🔥 Features:\n"
                "• Maya standalone integration (always on top)\n"
                "• AI assistant with OpenAI/Claude support\n"
                "• 320+ Maya command validation\n"
                "• VSCode-style editor with syntax highlighting\n"
                "• Dedicated NEO shelf with logo buttons\n\n"
                "This installer will:\n"
                "✓ Copy NEO Script Editor from project folder\n"
                "✓ Set up Maya integration (userSetup.py)\n"
                "✓ Create NEO shelf and menu\n"
                "✓ Launch the standalone editor\n\n"
                f"Project folder: {os.path.basename(self.project_source_dir)}\n"
                f"Install to: {self.maya_scripts_dir}\n\n"
                "Continue with installation?"
            ),
            button=["Install", "Cancel"],
            defaultButton="Install",
            cancelButton="Cancel",
            dismissString="Cancel"
        )
        return result == "Install"
    
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
        """Update progress window"""
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
                print("✅ Project folder validation successful")
            
            return True
            
        except Exception as e:
            print(f"❌ Project folder validation failed: {e}")
            self._show_error_dialog(f"Project folder validation failed: {e}\n\nMake sure you extracted the complete NEO Script Editor project.")
            return False
    
    def _install_files(self):
        """Install NEO Script Editor files to Maya scripts directory"""
        try:
            # Remove existing installation if it exists
            if os.path.exists(self.neo_install_dir):
                print(f"Removing existing installation: {self.neo_install_dir}")
                shutil.rmtree(self.neo_install_dir)
            
            # Copy files from project folder to Maya scripts directory
            print(f"Copying files from {self.project_source_dir} to {self.neo_install_dir}")
            
            # Copy the entire project folder
            shutil.copytree(self.project_source_dir, self.neo_install_dir)
            
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
            
            # Verify files
            missing_files = []
            for file_path in essential_files:
                full_path = os.path.join(self.neo_install_dir, file_path)
                if not os.path.exists(full_path):
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"⚠️ Some files missing after installation: {missing_files}")
                print("Creating minimal replacements...")
                self._create_minimal_files()
            
            print("✅ Files installed successfully")
            return True
            
        except Exception as e:
            print(f"❌ File installation failed: {e}")
            return False
    
    def _setup_user_setup(self):
        """Setup or update userSetup.py"""
        try:
            user_setup_path = os.path.join(self.maya_scripts_dir, "userSetup.py")
            neo_user_setup_path = os.path.join(self.project_source_dir, "scripts", "maya", "userSetup.py")
            
            print(f"Looking for NEO userSetup.py at: {neo_user_setup_path}")
            
            # Check if userSetup.py already exists
            if os.path.exists(user_setup_path):
                # Back up existing userSetup.py
                backup_path = user_setup_path + ".backup_before_neo"
                shutil.copy2(user_setup_path, backup_path)
                print(f"✅ Backed up existing userSetup.py to: {backup_path}")
                
                # Ask user what to do
                result = cmds.confirmDialog(
                    title="Existing userSetup.py Found",
                    message=(
                        "You already have a userSetup.py file.\n\n"
                        "Options:\n"
                        "• Replace: Use NEO's userSetup.py (recommended)\n"
                        "• Append: Add NEO setup to your existing file\n"
                        "• Manual: Set up NEO manually later\n\n"
                        "Your existing file has been backed up."
                    ),
                    button=["Replace", "Append", "Manual"],
                    defaultButton="Replace",
                    cancelButton="Manual"
                )
                
                if result == "Replace":
                    shutil.copy2(neo_user_setup_path, user_setup_path)
                    print("✅ Replaced userSetup.py with NEO version")
                elif result == "Append":
                    self._append_to_user_setup(user_setup_path, neo_user_setup_path)
                    print("✅ Appended NEO setup to existing userSetup.py")
                else:
                    print("⚠️ Manual setup required - userSetup.py not modified")
                    return True  # Don't fail installation
            else:
                # No existing userSetup.py, create NEO version
                if os.path.exists(neo_user_setup_path):
                    # Copy from project source
                    shutil.copy2(neo_user_setup_path, user_setup_path)
                    print("✅ Created new userSetup.py from project")
                else:
                    # Create minimal userSetup.py with embedded content
                    print("📝 Creating minimal userSetup.py (project version not found)")
                    self._create_minimal_user_setup(user_setup_path)
                    print("✅ Created minimal userSetup.py")
            
            return True
            
        except Exception as e:
            print(f"❌ userSetup.py setup failed: {e}")
            return False

    def _create_minimal_user_setup(self, user_setup_path):
        """Create minimal userSetup.py with NEO integration"""
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
            neo_path = os.path.join(maya_scripts, "ai_script_editor")
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
        with open(user_setup_path, 'w', encoding='utf-8') as f:
            f.write(user_setup_content)
    
    def _append_to_user_setup(self, existing_path, neo_path):
        """Append NEO setup to existing userSetup.py"""
        try:
            # Read existing userSetup.py
            with open(existing_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Check if NEO is already integrated
            if "setup_neo_editor" in existing_content:
                print("✅ NEO setup already present in userSetup.py")
                return
            
            # Get NEO content (from file or embedded)
            if os.path.exists(neo_path):
                # Read NEO userSetup.py from project
                with open(neo_path, 'r', encoding='utf-8') as f:
                    neo_content = f.read()
            else:
                # Use embedded minimal content
                neo_content = '''
def setup_neo_editor():
    """Setup NEO Script Editor in Maya"""
    try:
        import sys
        import os
        
        # Add NEO to Python path
        maya_scripts = cmds.internalVar(userScriptDir=True) if 'cmds' in globals() else None
        if maya_scripts:
            neo_path = os.path.join(maya_scripts, "ai_script_editor")
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
            
            # Append NEO setup
            combined_content = existing_content + "\n\n" + "# " + "="*50 + "\n"
            combined_content += "# NEO Script Editor Integration (Auto-added by installer)\n"
            combined_content += "# " + "="*50 + "\n\n"
            combined_content += neo_content
            
            # Write combined file
            with open(existing_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            print("✅ NEO setup appended to existing userSetup.py")
            
        except Exception as e:
            print(f"❌ Failed to append to userSetup.py: {e}")
            raise
    
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
        print("🚀 NEO Script Editor - Complete Setup")
        
        # Add to Python path
        neo_dir = os.path.dirname(os.path.dirname(__file__))
        if neo_dir not in sys.path:
            sys.path.insert(0, neo_dir)
        
        try:
            from main_window import launch_neo_editor
            launch_neo_editor()
            print("✅ NEO Script Editor launched")
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
            annotation="Launch NEO Script Editor",
            image="pythonFamily.png",
            command="complete_neo_setup()",
            sourceType="python"
        )
        
        print("✅ NEO shelf created")
        return True

except ImportError:
    def create_neo_shelf():
        print("NEO Script Editor requires Maya environment")
        return False
'''
            
            shelf_path = os.path.join(maya_scripts_dir, "maya_shelf_creator.py")
            with open(shelf_path, 'w', encoding='utf-8') as f:
                f.write(shelf_content)
            
            print("✅ Created basic Maya integration files")
            
        except Exception as e:
            print(f"❌ Failed to create basic Maya integration: {e}")

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
            print(f"📋 Adding shelf creator path: {maya_scripts_path}")
            
            if maya_scripts_path not in sys.path:
                sys.path.insert(0, maya_scripts_path)
            
            print("📋 Importing maya_shelf_creator...")
            from maya_shelf_creator import create_neo_shelf
            
            print("📋 Creating NEO shelf...")
            success = create_neo_shelf()
            
            if success:
                print("✅ NEO shelf created successfully")
                return True
            else:
                print("⚠️ NEO shelf creation had issues")
                return False
            
        except Exception as e:
            print(f"❌ NEO shelf creation failed: {e}")
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
                command="launch_neo_editor()",
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
            
            print("✅ NEO Script Editor launched")
            
        except Exception as e:
            print(f"⚠️ NEO Script Editor launch failed: {e}")
            print("You can launch it manually with: complete_neo_setup()")
    
    def _show_success_dialog(self):
        """Show installation success dialog"""
        cmds.confirmDialog(
            title="Installation Complete!",
            message=(
                "🎉 NEO Script Editor v3.2 Beta installed successfully!\n\n"
                "✅ What was installed:\n"
                "• NEO Script Editor files\n"
                "• Maya integration (userSetup.py)\n"
                "• NEO shelf with logo buttons\n"
                "• NEO menu in menu bar\n"
                "• Standalone NEO Script Editor (always on top)\n\n"
                "💡 Quick Start:\n"
                "• Use the NEO shelf buttons for easy access\n"
                "• Editor stays on top for easy workflow\n"
                "• Set your AI API key in Tools → Settings\n\n"
                "🔄 Next Steps:\n"
                "• Restart Maya to ensure full integration\n"
                "• Check out the docs/ folder for guides\n"
                "• Report issues on GitHub\n\n"
                "Enjoy coding with NEO! 🚀"
            ),
            button=["Awesome!"],
            defaultButton="Awesome!"
        )
    
    def _show_error_dialog(self, error_message):
        """Show installation error dialog"""
        cmds.confirmDialog(
            title="Installation Failed",
            message=(
                f"❌ Installation encountered an error:\n\n{error_message}\n\n"
                "Possible solutions:\n"
                "• Make sure you extracted the complete project folder\n"
                "• Check that the installer is in the project root\n"
                "• Check Maya's Script Editor for detailed errors\n"
                "• Try running Maya as administrator\n\n"
                f"Get help: {GITHUB_REPO}"
            ),
            button=["OK"],
            defaultButton="OK"
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
        print("🚀 NEO Script Editor - Minimal Setup")
        
        # Add to Python path
        neo_dir = os.path.dirname(os.path.dirname(__file__))
        if neo_dir not in sys.path:
            sys.path.insert(0, neo_dir)
        
        try:
            from main_window import launch_neo_editor
            launch_neo_editor()
            print("✅ NEO Script Editor launched (minimal version)")
            print("💡 Download full version from GitHub for complete features")
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
            neo_path = os.path.join(maya_scripts, "ai_script_editor")
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
        print(f"✅ Created: {relative_path}")

    def _show_about_dialog(self, *args):
        """Show about dialog"""
        cmds.confirmDialog(
            title="About NEO Script Editor",
            message=(
                "NEO Script Editor v3.2 Beta\n"
                '"I can only show you the door. You\'re the one that has to walk through it."\n\n'
                "🔥 Features:\n"
                "• Maya standalone integration (always on top)\n"
                "• AI assistant (OpenAI/Claude)\n"
                "• 320+ Maya command validation\n"
                "• VSCode-style editor\n"
                "• Real-time error detection\n\n"
                "💡 Developer: Mayj Amilano (@mayjackass)\n"
                "🌐 GitHub: github.com/mayjackass/AI_Maya_ScriptEditor\n"
                "📅 Release: October 2025\n"
                "⏰ Beta Expires: January 31, 2026\n\n"
                "Thank you for using NEO Script Editor!"
            ),
            button=["Close"],
            defaultButton="Close"
        )


# =============================================================================
# Drag & Drop Entry Point
# =============================================================================

def onMayaDroppedPythonFile(*args, **kwargs):
    """
    This function is called when a Python file is dragged into Maya's viewport.
    This is the entry point for the drag & drop installer.
    """
    print("\n" + "="*80)
    print("🎯 NEO Script Editor Drag & Drop Installer Activated!")
    print("="*80)
    
    # Create and run installer
    installer = NEOInstaller()
    success = installer.run_installation()
    
    if success:
        print("\n" + "="*80)
        print("🎉 NEO Script Editor installation completed successfully!")
        print("="*80)
        print("💡 Restart Maya to ensure full integration")
        print("🚀 Start coding with NEO Script Editor!")
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
🎯 NEO SCRIPT EDITOR - DRAG & DROP INSTALLER

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
✓ NEO Script Editor files (ai_script_editor/)
✓ Maya integration (userSetup.py)  
✓ NEO shelf with Matrix logo buttons
✓ NEO menu in Maya's menu bar
✓ Standalone script editor integration

MAYA COMMANDS (Available after installation):
• complete_neo_setup()  - Everything at once
• launch_neo_editor()   - Standalone window (always on top)

PERFECT WORKFLOW:
1. Run complete_neo_setup()
2. Use launch_neo_editor() for standalone editing
3. Enjoy AI-powered script editing with always-on-top behavior!

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