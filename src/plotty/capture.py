from __future__ import annotations
import subprocess
import signal
import shlex


def start_ip(url: str, out_path: str, timelapse_path: str | None = None):
    p1 = subprocess.Popen(
        shlex.split(
            f"ffmpeg -y -i {shlex.quote(url)} -c:v libx264 -preset veryfast -crf 23 {shlex.quote(out_path)}"
        ),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    tl = None
    if timelapse_path:
        tl = subprocess.Popen(
            shlex.split(
                f"ffmpeg -y -i {shlex.quote(url)} -vf fps=1 {shlex.quote(timelapse_path)}"
            ),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return p1, tl


def stop(procs: tuple[subprocess.Popen, subprocess.Popen | None]):
    for p in procs:
        if p:
            try:
                p.send_signal(signal.SIGINT)
                p.wait(timeout=10)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
