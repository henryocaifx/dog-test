import json
module_results = {}
for module in ('SequencerScripting', 'MovieRenderPipelineCore', 'MovieRenderPipelineRenderPasses', 'MovieRenderPipelineEditor'):
    try:
        module_results[module] = str(unreal.load_module(module))
    except Exception as e:
        module_results[module] = str(e)
registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = registry.get_all_assets()
matches = [str(a.object_path) if hasattr(a, 'object_path') else str(a.package_name) for a in assets if any(w in str(a.asset_name).lower() for w in ('dog', 'puppy', 'tart', 'canine', 'retriever'))]
RESULT = {
    'project': unreal.Paths.project_dir(),
    'dog_assets': matches,
    'level': str(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()),
    'movie_pipeline': hasattr(unreal, 'MoviePipelineQueueSubsystem'),
    'geometry_script': hasattr(unreal, 'GeometryScriptLibrary_MeshPrimitiveFunctions'),
    'sequencer': hasattr(unreal, 'LevelSequence'),
    'sequencer_scripting': hasattr(unreal, 'MovieSceneScriptingDoubleChannel'),
    'enable_apis': [x for x in dir(unreal) if 'Plugin' in x or 'odule' in x],
    'modules': module_results,
    'legacy_capture': hasattr(unreal, 'AutomatedLevelSequenceCapture'),
    'render_movie': str(getattr(getattr(unreal, 'SequencerTools', None), 'render_movie', None)),
    'capture_doc': str(getattr(getattr(unreal, 'AutomatedLevelSequenceCapture', None), '__doc__', '')),
}
