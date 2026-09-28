#!/usr/bin/env python3
"""Read-only media QA; writes a report and contact sheet, never edits videos."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import sys


def run(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[-3000:] or f"Command failed: {args[0]}")
    return result.stdout


def probe(path):
    data = json.loads(run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ]))
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    if video is None:
        raise ValueError(f"No video stream: {path}")
    duration = float(video.get("duration") or data["format"]["duration"])
    rate = video.get("avg_frame_rate") or video.get("r_frame_rate")
    fps = float(Fraction(rate))
    if duration <= 0 or fps <= 0:
        raise ValueError(f"Invalid duration or frame rate: {path}")
    return {
        "path": str(path.resolve()), "duration_seconds": duration,
        "width": video["width"], "height": video["height"], "fps": fps,
        "video_codec": video.get("codec_name"),
        "has_audio": any(s.get("codec_type") == "audio" for s in streams),
        "size_bytes": path.stat().st_size,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--sources", required=True, nargs="+", type=Path,
                        help="Original clips in intended edit order")
    parser.add_argument("--expected-fps", type=float)
    parser.add_argument("--report-dir", required=True, type=Path)
    args = parser.parse_args()
    for tool in ("ffprobe", "ffmpeg"):
        if not shutil.which(tool):
            parser.error(f"Required executable missing: {tool}")
    for path in [args.video, *args.sources]:
        if not path.is_file():
            parser.error(f"File missing: {path}")
    if args.expected_fps is not None and args.expected_fps <= 0:
        parser.error("--expected-fps must be positive")
    args.report_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report_dir / "report.json"
    sheet_path = args.report_dir / "contact-sheet.jpg"
    # Reject accidental use of an input file as a generated report target.
    inputs = {p.resolve() for p in [args.video, *args.sources]}
    if report_path.resolve() in inputs or sheet_path.resolve() in inputs:
        parser.error("Report outputs must differ from media inputs")
    report = {"technical_checks_passed": False, "visual_review_required": True,
              "audio_listening_required": True,
              "scope": "Checks decoding and metadata, not identity, order, watermark, pose count or audio quality."}
    try:
        final = probe(args.video)
        sources = [probe(p) for p in args.sources]
        expected_duration = sum(s["duration_seconds"] for s in sources)
        expected_fps = args.expected_fps or sources[0]["fps"]
        tolerance = max(0.1, 2 * len(sources) / expected_fps)
        checks = {
            "duration_matches_sum": abs(final["duration_seconds"] - expected_duration) <= tolerance,
            "resolution_matches_first_source": (final["width"], final["height"]) ==
                                               (sources[0]["width"], sources[0]["height"]),
            "fps_matches_expected": abs(final["fps"] - expected_fps) < 0.01,
            "source_audio_retained": not any(s["has_audio"] for s in sources) or final["has_audio"],
            "full_decode": False,
        }
        report.update(final=final, sources_in_intended_order=sources, checks=checks,
                      expected_duration_seconds=expected_duration,
                      duration_tolerance_seconds=tolerance, expected_fps=expected_fps)
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-xerror", "-i", str(args.video),
             "-map", "0:v:0", "-map", "0:a?", "-f", "null", "-"])
        checks["full_decode"] = True
        times = [0.0, max(0.0, final["duration_seconds"] - 2 / final["fps"])]
        elapsed = 0.0
        for i, source in enumerate(sources):
            times.append(elapsed + source["duration_seconds"] / 2)
            elapsed += source["duration_seconds"]
            if i < len(sources) - 1:
                times.extend([elapsed - 2 / final["fps"], elapsed + 2 / final["fps"]])
        max_frame = max(0, int(final["duration_seconds"] * final["fps"]) - 1)
        frames = sorted({min(max_frame, max(0, round(t * final["fps"]))) for t in times})
        select = "+".join(f"eq(n\\,{n})" for n in frames)
        cols = min(6, len(frames))
        rows = (len(frames) + cols - 1) // cols
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(args.video),
             "-vf", f"select='{select}',scale=240:-2,tile={cols}x{rows}",
             "-frames:v", "1", "-y", str(sheet_path)])
        if not sheet_path.is_file() or sheet_path.stat().st_size == 0:
            raise RuntimeError("Contact sheet was not created")
        report.update(contact_sheet=str(sheet_path.resolve()),
                      frame_samples_left_to_right=[{"frame": n, "seconds": n / final["fps"]} for n in frames],
                      technical_checks_passed=all(checks.values()))
    except (RuntimeError, ValueError, KeyError, StopIteration, OSError, subprocess.TimeoutExpired) as exc:
        report["error"] = str(exc)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path.resolve()),
                      "technical_checks_passed": report["technical_checks_passed"]}, ensure_ascii=False))
    return 0 if report["technical_checks_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
