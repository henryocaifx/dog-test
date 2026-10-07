import json
seq = unreal.load_asset('/Game/TartAnimation/Tart_Greeting_5s')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/TartAnimation/Tart_Studio')
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
camera = next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Tart_Camera')
cam = camera.get_cine_camera_component()
pp = cam.get_editor_property('post_process_settings')
for key,value in (('auto_exposure_min_brightness',9.0),('auto_exposure_max_brightness',9.0),('auto_exposure_bias',.3)):
    pp.set_editor_property(key,value)
cam.set_editor_property('post_process_settings',pp)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
volume = next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='Tart_Exposure'),None)
if volume is None:
    volume = actors.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(0,0,0))
    volume.set_actor_label('Tart_Exposure')
volume.set_editor_property('unbound',True)
volume.set_editor_property('settings',pp)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(ROOT/'output'/'tart_preview.png'),camera=camera)
RESULT = {
    'preview': str(ROOT/'output'/'tart_preview.png'),
    'settings_doc': unreal.MovieSceneCaptureSettings.__doc__,
    'render_doc': unreal.SequencerTools.render_movie.__doc__,
    'image_protocols': [x for x in dir(unreal) if 'ImageSequenceProtocol' in x],
}
