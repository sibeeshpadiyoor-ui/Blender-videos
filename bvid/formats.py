"""Output formats and quality presets."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Format:
    name: str
    width: int
    height: int
    fps: int = 30

    @property
    def aspect(self) -> float:
        return self.width / self.height


FORMATS = {
    # Instagram Reels / Stories and YouTube Shorts (9:16)
    "reels": Format("reels", 1080, 1920),
    # Regular YouTube video (16:9)
    "youtube": Format("youtube", 1920, 1080),
    # Instagram feed post (4:5 portrait takes the most screen space)
    "feed": Format("feed", 1080, 1350),
    # Square post
    "square": Format("square", 1080, 1080),
}


@dataclass(frozen=True)
class Quality:
    name: str
    resolution_percent: int
    samples: int
    crf: int  # x264 quality, lower = better


QUALITIES = {
    "draft": Quality("draft", 25, 8, 26),
    "preview": Quality("preview", 50, 24, 22),
    "final": Quality("final", 100, 96, 17),
}
