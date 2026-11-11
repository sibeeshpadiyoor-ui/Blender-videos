"""Turn a rendered PNG sequence into an upload-ready MP4."""
import shutil
import subprocess


def encode(frames_pattern, out_path, fps, crf=17, loops=1, audio=None):
    """H.264 + yuv420p + faststart: accepted by Instagram and YouTube."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit("ffmpeg not found - install it to encode the video "
                         f"(frames are in {frames_pattern})")
    cmd = [ffmpeg, "-y", "-loglevel", "error"]
    if loops > 1:
        cmd += ["-stream_loop", str(loops - 1)]
    cmd += ["-framerate", str(fps), "-i", str(frames_pattern)]
    if audio:
        cmd += ["-i", str(audio), "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += [
        "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        # yuv420p needs even dimensions (matters for scaled-down previews)
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-movflags", "+faststart",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return out_path
