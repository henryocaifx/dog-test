"""Encode and verify the 150 Unreal frames as a five-second MP4."""
from pathlib import Path
import subprocess
import sys
import re
import json
sys.path.insert(0,str(Path(__file__).parent/'.tools'))
import imageio_ffmpeg
from PIL import Image, ImageChops, ImageStat

root = Path(__file__).parent
out = root/'output'
frames = sorted((out/'frames').glob('tart_*.png'))
if len(frames) < 150:
    raise RuntimeError(f'Expected at least 150 rendered frames; found {len(frames)}')
files = frames[:150]
staging = out/'encode_frames'
staging.mkdir(exist_ok=True)
for index,path in enumerate(files):
    target = staging/f'{index:04d}.png'
    if not target.exists():
        try:
            target.hardlink_to(path)
        except OSError:
            target.write_bytes(path.read_bytes())
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
video = out/'tart-greeting-5s.mp4'
subprocess.run([ffmpeg,'-y','-framerate','30','-i',str(staging/'%04d.png'),'-frames:v','150','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True,capture_output=True)
result = subprocess.run([ffmpeg,'-i',str(video),'-f','null','-'],capture_output=True,text=True)
if result.returncode:
    raise RuntimeError(result.stderr)
if not re.search(r'Duration: 00:00:05\.00',result.stderr):
    raise RuntimeError('Encoded video duration is not five seconds: '+result.stderr)
if not re.search(r'frame=\s*150',result.stderr):
    raise RuntimeError('Encoded video does not contain 150 frames: '+result.stderr)
images = [Image.open(files[i]).convert('RGB') for i in (0,45,75,105,149)]
differences = [sum(ImageStat.Stat(ImageChops.difference(images[0],im)).mean) for im in images[1:]]
if max(differences) < 1:
    raise RuntimeError('No significant animation detected')
sheet = Image.new('RGB',(1280,720),(245,240,233))
for i,im in enumerate(images[:4]):
    im.thumbnail((640,360))
    sheet.paste(im,((i%2)*640,(i//2)*360))
sheet.save(out/'animation-contact-sheet.jpg',quality=92)
Image.open(files[0]).save(out/'tart_preview.png')
details = {'video':str(video),'duration_seconds':5.0,'fps':30,'frame_count':150,'resolution':list(images[-1].size),'motion_difference':differences,'unreal_frames':len(frames),'decode_verified':True}
(out/'video_verification.json').write_text(json.dumps(details,indent=2),encoding='utf-8')
print(json.dumps(details,indent=2))
