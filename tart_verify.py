import json
OUT = ROOT/'output'
seq = unreal.load_asset('/Game/TartAnimation/Tart_Greeting_5s')
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
files = sorted((OUT/'frames').glob('*.png'))
RESULT = {'frames':len(files),'first':str(files[0]) if files else None,'last':str(files[-1]) if files else None,'status':json.loads((OUT/'render_status.json').read_text()) if (OUT/'render_status.json').exists() else {}}
