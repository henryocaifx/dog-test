import json
import builtins
OUT = ROOT/'output'
frames_dir = OUT/'frames'
frames_dir.mkdir(exist_ok=True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
capture = unreal.AutomatedLevelSequenceCapture()
capture.set_editor_property('level_sequence_asset',unreal.SoftObjectPath('/Game/TartAnimation/Tart_Greeting_5s.Tart_Greeting_5s'))
capture.set_editor_property('use_separate_process',False)
capture.set_editor_property('close_editor_when_capture_starts',False)
capture.set_editor_property('use_custom_start_frame',True)
capture.set_editor_property('custom_start_frame',unreal.FrameNumber(0))
capture.set_editor_property('use_custom_end_frame',True)
capture.set_editor_property('custom_end_frame',unreal.FrameNumber(150))
capture.set_editor_property('warm_up_frame_count',30)
capture.set_editor_property('delay_before_warm_up',2.0)
capture.set_editor_property('delay_every_frame',.03)
capture.set_editor_property('write_edit_decision_list',False)
capture.set_editor_property('write_final_cut_pro_xml',False)
capture.set_editor_property('image_capture_protocol_type',unreal.SoftClassPath('/Script/MovieSceneCapture.ImageSequenceProtocol_PNG'))
settings = capture.get_editor_property('settings')
for key,value in (
    ('output_directory',unreal.DirectoryPath(str(frames_dir))),
    ('output_format','tart_{frame}'),('zero_pad_frame_numbers',4),
    ('resolution',unreal.CaptureResolution(1280,720)),
    ('use_custom_frame_rate',True),('custom_frame_rate',unreal.FrameRate(30,1)),
    ('overwrite_existing',True),('use_relative_frame_numbers',True),
    ('enable_texture_streaming',False),('cinematic_engine_scalability',True),
    ('cinematic_mode',True),('show_hud',False),('show_player',False),
    ('game_mode_override',unreal.GameModeBase),
):
    settings.set_editor_property(key,value)
capture.set_editor_property('settings',settings)
def on_finished(success):
    (OUT/'render_status.json').write_text(json.dumps({'completed':True,'success':bool(success)}),encoding='utf-8')
    unreal.log('Tart render finished: ' + str(success))
builtins._tart_capture = capture
builtins._tart_finished = on_finished
callback = unreal.OnRenderMovieStopped()
callback.bind_callable(on_finished)
builtins._tart_callback = callback
started = unreal.SequencerTools.render_movie(capture,callback)
(OUT/'render_status.json').write_text(json.dumps({'started':bool(started),'completed':False}),encoding='utf-8')
RESULT = {'started':bool(started),'frames_dir':str(frames_dir),'fps':30,'frames':150}
