import maya.cmds as cmds
import maya.utils
import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def _launch(*_):
    import ai_script_editor.ai_script_editor as aisedit
    aisedit.launch_ai_script_editor()

def _menu():
    if cmds.menu('AIEditorMenu', exists=True):
        cmds.deleteUI('AIEditorMenu', menu=True)
    m = cmds.menu('AIEditorMenu', label='AI Tools', parent='MayaWindow', tearOff=True)
    cmds.menuItem(label='Open AI Script Editor', command=_launch)

maya.utils.executeDeferred(_menu)
