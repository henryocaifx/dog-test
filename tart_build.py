import math
import json
import random

ASSET_DIR = '/Game/TartAnimation'
LEVEL_PATH = ASSET_DIR + '/Tart_Studio'
SEQUENCE_PATH = ASSET_DIR + '/Tart_Greeting_5s'
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
assets = unreal.AssetToolsHelpers.get_asset_tools()
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# Use a dedicated level and folder for the reference-based character.
level_sub.save_current_level()
if unreal.EditorAssetLibrary.does_asset_exist(LEVEL_PATH):
    level_sub.load_level(LEVEL_PATH)
    for actor in actor_sub.get_all_level_actors():
        if actor.get_actor_label().startswith('Tart_'):
            actor_sub.destroy_actor(actor)
else:
    level_sub.new_level(LEVEL_PATH)

def material(name, color, roughness=.8, unlit=False):
    path = ASSET_DIR + '/Materials/' + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.load_asset(path)
    mat = assets.create_asset(name, ASSET_DIR + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
    col = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
    col.set_editor_property('constant', unreal.LinearColor(*color, 1))
    unreal.MaterialEditingLibrary.connect_material_property(col, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR if unlit else unreal.MaterialProperty.MP_BASE_COLOR)
    val = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 150)
    val.set_editor_property('r', roughness)
    unreal.MaterialEditingLibrary.connect_material_property(val, '', unreal.MaterialProperty.MP_ROUGHNESS)
    if unlit:
        mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat

mats = {
    'fur': material('M_Cream_Fur', (.62,.43,.25), .92),
    'muzzle': material('M_Soft_Muzzle', (.81,.64,.43), .9),
    'ear': material('M_Warm_Ears', (.50,.30,.14), .93),
    'orange': material('M_Training_Orange', (.85,.225,.018), .84),
    'trim': material('M_Charcoal_Trim', (.10,.10,.095), .83),
    'blue': material('M_Guide_Blue', (.025,.105,.29), .73),
    'white': material('M_Eye_White', (.92,.88,.79), .35),
    'iris': material('M_Hazel_Iris', (.075,.037,.015), .4),
    'black': material('M_Nose_And_Pupils', (.016,.009,.005), .42),
    'glint': material('M_Eye_Glint', (1,1,1), .15, True),
    'floor': material('M_Warm_Studio', (.58,.53,.46), .9),
}
meshes = {n:unreal.load_asset('/Engine/BasicShapes/' + n + '.' + n) for n in ('Sphere','Cube','Cylinder')}
actors = {}

def shape(name, pos, radius, mat='fur', mesh='Sphere', rot=(0,0,0), parent=None):
    actor = actor_sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*pos), unreal.Rotator(*rot))
    actor.set_actor_label('Tart_' + name)
    comp = actor.static_mesh_component
    comp.set_mobility(unreal.ComponentMobility.MOVABLE)
    comp.set_static_mesh(meshes[mesh])
    comp.set_material(0, mats[mat])
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    actor.set_actor_scale3d(unreal.Vector(*(r/50 for r in radius)))
    if parent:
        actor.attach_to_actor(parent, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    actors[name] = actor
    return actor

def pivot(name, pos, parent=None):
    a = shape(name, pos, (50,50,50), parent=parent)
    a.static_mesh_component.set_static_mesh(None)
    return a

def rod(name, start, end, thickness, mat, parent=None):
    mid = tuple((a+b)/2 for a,b in zip(start,end))
    d = unreal.Vector(*(b-a for a,b in zip(start,end)))
    rotation = unreal.MathLibrary.make_rot_from_z(d)
    a = shape(name, mid, (thickness,thickness,d.length()/2), mat, 'Cylinder', parent=parent)
    a.set_actor_rotation(rotation, False)
    return a

def lettering(name, text, pos, size, rot=(0,0,0), parent=None):
    a = actor_sub.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(*pos), unreal.Rotator(*rot))
    a.set_actor_label('Tart_' + name)
    c = a.text_render
    c.set_text(text)
    c.set_world_size(size)
    c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    c.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
    c.set_text_render_color(unreal.Color(255,245,225,255))
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    if parent:
        a.attach_to_actor(parent, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    actors[name] = a
    return a

root = pivot('Body_Root', (0,0,0))
shape('Body', (-4,0,41), (24,20,36), parent=root)
for y, side in ((-19,'Near'),(19,'Far')):
    shape('Haunch_' + side, (-15,y,23), (20,13,23), parent=root)
    shape('Back_Paw_' + side, (-8,y,7), (14,11,7), 'muzzle', parent=root)

# A shaped vest shell, gray piping, chest bib, and circular blue badge.
shape('Vest_Piping', (-2,0,51), (25.9,21.9,28.7), 'trim', parent=root)
shape('Vest_Orange', (-.6,0,52), (25.9,21.9,27.1), 'orange', parent=root)
shape('Neck', (0,0,76), (16,16,18), parent=root)
shape('Bib_Trim', (23.7,0,55), (2,17.2,13.7), 'trim', 'Cube', parent=root)
shape('Bib', (25,0,55), (1,15.8,12.3), 'orange', 'Cube', parent=root)
lettering('Vest_Title', 'Guide Dog\nIn Training', (26.3,0,56), 4.5, parent=root)
shape('Badge_Edge', (0,-22.1,55), (10,.9,10), 'white', parent=root)
shape('Badge_Blue', (0,-23,55), (9.4,.6,9.4), 'blue', parent=root)
lettering('Badge_Label', 'GUIDE\nDOG', (0,-23.8,55), 3, (0,-90,0), root)
for y in (-19,19):
    rod('Vest_Strapping_' + str(y), (-13,y,28), (8,y,22), 1.4, 'trim', root)

# The front paw is articulated at its shoulder for the greeting.
near_arm = pivot('Wave_Shoulder', (14,-13,58), root)
far_arm = pivot('Still_Shoulder', (14,13,58), root)
for y, side, parent in ((-13,'Near',near_arm),(13,'Far',far_arm)):
    shape('Foreleg_' + side, (15,y,32), (7.5,7.4,27), parent=parent)
    shape('Front_Paw_' + side, (20,y,7), (12,10,7), 'muzzle', parent=parent)
    for dy in (-4,0,4):
        shape('Toe_' + side + str(dy), (28,y+dy,6.8), (4.5,2.8,4.5), 'muzzle', parent=parent)

head = pivot('Head_Root', (8,0,91), root)
shape('Head', (8,0,94), (27,24,27.5), parent=head)
shape('Chin', (30,0,80), (14,14,9), 'muzzle', parent=head)
for y, side in ((-9,'Near'),(9,'Far')):
    shape('Muzzle_' + side, (32,y,87), (16,11,12), 'muzzle', parent=head)
shape('Nose', (46,0,94), (7.7,8.2,5.8), 'black', parent=head)
for y in (-4,4):
    shape('Nostril' + str(y), (52.4,y,94), (1,1.5,1.1), 'black', parent=head)
shape('Nose_Glint', (51,-1.7,96.6), (.7,2,.65), 'iris', parent=head)
rod('Philtrum', (46.3,0,90), (45,0,84), .36, 'black', head)
for y in (-1,1):
    for i in range(4):
        a = (44.5-i*1.0, y*i*2.0, 83.8 + .2*i*i)
        b = (44.5-(i+1)*1.0, y*(i+1)*2.0, 83.8 + .2*(i+1)**2)
        rod('Smile_' + str(y) + '_' + str(i), a,b,.29,'black',head)
for y, side in ((-1,'Near'),(1,'Far')):
    ear = pivot('Ear_Root_' + side, (3,y*22,108), head)
    shape('Ear_' + side, (-1,y*26,94), (10,6.8,20), 'ear', rot=(0,0,y*12), parent=ear)
    eye = pivot('Eye_Root_' + side, (29,y*12.5,105), head)
    shape('Eye_White_' + side, (29,y*12.5,105), (5.5,6.4,7.6), 'white', parent=eye)
    shape('Iris_' + side, (33.6,y*12.5,105.4), (2.4,4.4,5.2), 'iris', parent=eye)
    shape('Pupil_' + side, (35.5,y*12.5,105.4), (1.2,3.4,4.1), 'black', parent=eye)
    shape('Glint_' + side, (36.5,y*12.5-1.4,107.5), (.6,1.05,1.05), 'glint', parent=eye)
    shape('Small_Glint_' + side, (36.4,y*12.5+1.1,103.8), (.3,.45,.45), 'glint', parent=eye)
    for i in range(3):
        shape('Whisker_Dot_' + side + str(i), (45-i*1.4,y*(10+i*1.7),89-i*.8), (.2,.38,.38), 'ear', parent=head)

tail = pivot('Tail_Root', (-24,0,21), root)
tail_points = [(-24,0,21),(-36,-4,16),(-48,-12,17),(-54,-23,24),(-52,-31,34)]
for i,(a,b) in enumerate(zip(tail_points,tail_points[1:])):
    mid = tuple((x+y)/2 for x,y in zip(a,b))
    d = unreal.Vector(*(y-x for x,y in zip(a,b)))
    s = shape('Tail_Segment_' + str(i), mid, (7.3-i*.9,7.3-i*.9,d.length()/2+4), parent=tail)
    s.set_actor_rotation(unreal.MathLibrary.make_rot_from_z(d), False)
shape('Tail_Tip', tail_points[-1], (3.9,4,5.5), parent=tail)

# Fine cream tufts break up the smooth head and ear silhouettes.
random.seed(74)
for i in range(170):
    u = random.uniform(-1,1)
    angle = random.uniform(0,2*math.pi)
    rr = math.sqrt(1-u*u)
    nx,ny,nz = rr*math.cos(angle),rr*math.sin(angle),u
    # Keep the face and eyes unobstructed.
    if nx > .42 or nz < .55:
        continue
    pos = (8+26.6*nx,24*ny,94+27.2*nz)
    tuft = shape('Fur_Tuft_' + str(i), pos, (.55,.65,1.2), 'fur', parent=head)
    tuft.set_actor_rotation(unreal.MathLibrary.make_rot_from_z(unreal.Vector(nx,ny,nz)), False)

shape('Studio_Floor', (0,0,-3), (5000,5000,3), 'floor', 'Cube')
ambient = actor_sub.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,300),unreal.Rotator(-70,-40,0))
ambient.set_actor_label('Tart_Studio_Ambient')
ambient.light_component.set_editor_property('intensity',900)
ambient.light_component.set_editor_property('cast_shadows',False)

def look_at(actor, target):
    actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(actor.get_actor_location(), unreal.Vector(*target)), False)

for name,pos,intensity,size in (
    ('Key',(160,-130,230),11000,170),
    ('Fill',(130,180,150),5500,140),
    ('Rim',(-100,60,210),12000,130),
):
    light = actor_sub.spawn_actor_from_class(unreal.RectLight, unreal.Vector(*pos))
    light.set_actor_label('Tart_' + name + '_Light')
    light.rect_light_component.set_editor_property('intensity', intensity)
    light.rect_light_component.set_editor_property('source_width', size)
    light.rect_light_component.set_editor_property('source_height', size)
    look_at(light,(0,0,60))

camera = actor_sub.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(340,-130,165))
camera.set_actor_label('Tart_Camera')
look_at(camera,(0,0,62))
cam = camera.get_cine_camera_component()
cam.set_editor_property('current_focal_length', 42)
cam.set_editor_property('current_aperture', 8)
film = cam.get_editor_property('filmback')
film.set_editor_property('sensor_width',36)
film.set_editor_property('sensor_height',20.25)
cam.set_editor_property('filmback',film)
focus = cam.get_editor_property('focus_settings')
focus.set_editor_property('focus_method',unreal.CameraFocusMethod.DISABLE)
cam.set_editor_property('focus_settings',focus)
pp = cam.get_editor_property('post_process_settings')
for key,value in (
    ('override_auto_exposure_min_brightness',True),('override_auto_exposure_max_brightness',True),
    ('auto_exposure_min_brightness',9.0),('auto_exposure_max_brightness',9.0),
    ('override_auto_exposure_bias',True),('auto_exposure_bias',.3),
    ('override_vignette_intensity',True),('vignette_intensity',.13),
    ('override_bloom_intensity',True),('bloom_intensity',.12),
    ('override_motion_blur_amount',True),('motion_blur_amount',.15),
):
    pp.set_editor_property(key,value)
cam.set_editor_property('post_process_settings',pp)
volume = actor_sub.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(0,0,0))
volume.set_actor_label('Tart_Exposure')
volume.set_editor_property('unbound',True)
volume.set_editor_property('settings',pp)

if unreal.EditorAssetLibrary.does_asset_exist(SEQUENCE_PATH):
    seq = unreal.load_asset(SEQUENCE_PATH)
    for b in seq.get_bindings():
        b.remove()
    for track in seq.get_tracks():
        seq.remove_track(track)
else:
    seq = assets.create_asset('Tart_Greeting_5s',ASSET_DIR,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(30,1))
seq.set_playback_start(0)
seq.set_playback_end(150)
seq.set_work_range_start(0)
seq.set_work_range_end(5)
seq.set_view_range_start(0)
seq.set_view_range_end(5)

def animate(actor, samples):
    binding = seq.add_possessable(actor)
    track = binding.add_track(unreal.MovieScene3DTransformTrack)
    section = track.add_section()
    section.set_range(0,150)
    channels = section.get_all_channels()
    c = actor.root_component
    loc = c.get_editor_property('relative_location')
    rot = c.get_editor_property('relative_rotation')
    scl = c.get_editor_property('relative_scale3d')
    base = [loc.x,loc.y,loc.z,rot.roll,rot.pitch,rot.yaw,scl.x,scl.y,scl.z]
    for channel,val in zip(channels,base):
        channel.set_default(val)
    for frame,overrides in samples:
        vals = base.copy()
        for i,v in overrides.items():
            vals[i] = v
        for channel,val in zip(channels,vals):
            channel.add_key(unreal.FrameNumber(frame),val,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    return binding

# A settling breath, inquisitive tilt, two tail wag beats, and a small paw wave.
animate(root, [(i,{2: .45*math.sin(i/150*4*math.pi)}) for i in range(0,151,5)])
animate(head,[(0,{3:0,4:0,5:0}),(18,{3:0,4:-2}),(38,{3:12,4:0,5:-4}),(66,{3:12,4:0,5:-4}),(92,{3:-5,4:-3,5:2}),(120,{3:0,4:0,5:0}),(149,{3:0,4:0,5:0})])
animate(near_arm,[(0,{4:0,3:0}),(46,{4:0,3:0}),(62,{4:52,3:-15}),(74,{4:60,3:-20}),(85,{4:48,3:-9}),(96,{4:60,3:-20}),(111,{4:0,3:0}),(149,{4:0,3:0})])
animate(tail,[(i,{5:25*math.sin(i/30*2*math.pi*1.6),4:5*math.sin(i/30*2*math.pi*1.6)}) for i in range(0,151,3)])
for side in ('Near','Far'):
    animate(actors['Ear_Root_' + side],[(i,{3:3*math.sin(i/30*2*math.pi*1.2)*(1 if side=='Near' else -1)}) for i in range(0,151,5)])
    animate(actors['Eye_Root_' + side],[(0,{8:1}),(27,{8:1}),(29,{8:.08}),(31,{8:1}),(99,{8:1}),(101,{8:.08}),(103,{8:1}),(149,{8:1})])
camera_binding = seq.add_possessable(camera)
cut_track = seq.add_track(unreal.MovieSceneCameraCutTrack)
cut = cut_track.add_section()
cut.set_range(0,150)
cut.set_camera_binding_id(seq.get_binding_id(camera_binding))
animate(camera,[(0,{0:340,1:-130,2:165}),(149,{0:321,1:-122.7,2:160.3})])

unreal.EditorAssetLibrary.save_loaded_asset(seq)
level_sub.save_current_level()
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
manifest = {'level':LEVEL_PATH,'sequence':SEQUENCE_PATH,'duration_seconds':5,'fps':30,'frames':150,'reference':str(ROOT/'tart-young.png'),'style':'Procedural stylized 3D puppy','actor_count':len(actor_sub.get_all_level_actors())}
(OUT/'animation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
RESULT = manifest
