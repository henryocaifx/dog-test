"""Register temporary, task-specific animation tools in the running Unreal editor."""
import sys
from pathlib import Path
import json
import traceback
import unreal

ROOT = Path(r'C:\Users\admina\Downloads\project\dog-test')
registry_python = r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\ToolsetRegistry\Content\Python'
if registry_python not in sys.path:
    sys.path.insert(0, registry_python)
import toolset_registry
from toolset_registry.registration import Registration

@unreal.uclass()
class TartAnimationToolset(unreal.ToolsetDefinition):
    """Build and inspect the five-second Tart puppy animation for this task."""

    @toolset_registry.tool_call
    @staticmethod
    def run_step(step: str) -> str:
        """Run one of the task's fixed steps: probe, build, preview, render, verify."""
        if step not in ('probe', 'build', 'preview', 'render', 'verify'):
            raise ValueError('Unknown animation step')
        path = ROOT / ('tart_' + step + '.py')
        scope = {'unreal': unreal, 'ROOT': ROOT, 'RESULT': {}}
        try:
            exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'), scope)
            return json.dumps(scope.get('RESULT', {}), default=str)
        except Exception:
            return json.dumps({'error': traceback.format_exc()})

_tart_registration = Registration([TartAnimationToolset])
_tart_registration.register()
unreal.SystemLibrary.execute_console_command(None, 'ModelContextProtocol.RefreshTools')
unreal.log('Tart animation MCP toolset is ready.')
