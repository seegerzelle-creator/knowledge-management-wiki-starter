#!/usr/bin/env python3
"""Utilities for library-grade bilingual transcript Raw notes.

The tool keeps expensive language work separate from deterministic structure:

- extract: turn clipped English timestamp lines into a TSV translation table.
- extract-sections: turn legacy transcript headings into a sections TSV.
- check-table: verify that the reviewed translation TSV still matches the source.
- render: combine reviewed Chinese translations with preserved English evidence.
- align-generated-cn: align a Codex-generated timestamped Chinese reading transcript with preserved English evidence.
- align-user-cn: align a user-provided timestamped Chinese transcript with preserved English evidence.
- audit: verify that bilingual transcript metadata matches the body.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


LEGACY_SEGMENT_RE = re.compile(r"^\*\*([^*]+)\*\*\s*·\s*(.*)$", re.MULTILINE)
CN_TIMESTAMP_RE = re.compile(r"^【([^】]+)】(.+)$", re.MULTILINE)
EN_EVIDENCE_RE = re.compile(r"^\*\*English:\*\*\s+(.+)$", re.MULTILINE)
EN_EVIDENCE_TIMESTAMP_RE = re.compile(r"^\*\*English:\*\*.*(?:【|\[)\d{2}:\d{2}(?::\d{2})?(?:】|\])", re.MULTILINE)
USER_CN_TIMESTAMP_RE = re.compile(r"^(?:\[(\d{2}:\d{2}(?::\d{2})?)\]|【(\d{2}:\d{2}(?::\d{2})?)】)\s*(.*)$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
YOUTUBE_EMBED_RE = re.compile(r"!\[\]\((https://(?:www\.)?youtube\.com/watch\?[^)\s]+|https://youtu\.be/[^)\s]+)\)")
LEGACY_TRANSCRIPT_HEADING_RE = re.compile(r"^##\s+Transcript\s*$", re.MULTILINE)
SECTION_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
ATTACHMENT_PREFACE_RE = re.compile(
    r"(好的[，,].{0,40}(?:逐字稿|时间戳|理解)|以下是根据您的要求|严格按照时间戳|完整简体中文翻译)"
)
CODEX_TRANSLATION_WORDING_RE = re.compile(
    r"(Chinese (?:timestamp )?translation.*Codex|prepared by Codex from|中文(?:译文|翻译|时间戳翻译)由\s*Codex|Codex\s*基于英文)",
    re.IGNORECASE,
)
LEGACY_CONNECTIVE_NOTE = "（此中文句为承接性整理；英文证据已并入相邻上下文块。）"


DEFAULT_BODY_MARKER = "## 英文原始逐字稿（按原剪藏时间戳）"
DEFAULT_HEADING = "## 精细中英对照（按视频时间戳）"
FORBIDDEN_RAW_FRONTMATTER_FIELDS = (
    "domains",
    "use_cases",
    "key_points",
    "important_details",
    "evidence",
    "concept_candidates",
    "synthesis_candidates",
)
ALLOWED_ACQUISITION_METHODS = {
    "obsidian_web_clipper",
    "codex_youtube_capture",
    "user_supplied",
    "unknown",
}


def normalize_timestamp(timestamp: str) -> str:
    timestamp = timestamp.strip()
    parts = timestamp.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return f"{int(minutes):02d}:{int(seconds):02d}"
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    return timestamp


def timestamp_to_seconds(timestamp: str) -> int:
    parts = [int(part) for part in normalize_timestamp(timestamp).split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    raise ValueError(f"invalid timestamp: {timestamp!r}")


def extract_legacy_segments(markdown: str) -> list[tuple[str, str]]:
    return [(normalize_timestamp(ts), text.strip()) for ts, text in LEGACY_SEGMENT_RE.findall(markdown)]


def is_placeholder_english(text: str) -> bool:
    stripped = text.strip()
    return stripped == LEGACY_CONNECTIVE_NOTE or stripped.startswith("[Alignment note:")


def extract_bilingual_evidence_segments(markdown: str) -> list[tuple[str, str]]:
    segments: list[tuple[str, str]] = []
    current_timestamp = ""
    for line in markdown.splitlines():
        timestamp_match = CN_TIMESTAMP_RE.match(line)
        if timestamp_match:
            current_timestamp = normalize_timestamp(timestamp_match.group(1))
            continue

        english_match = EN_EVIDENCE_RE.match(line)
        if not english_match:
            continue

        normalized = normalize_evidence(english_match.group(1))
        if current_timestamp and normalized and not is_placeholder_english(normalized):
            segments.append((current_timestamp, normalized))
    return segments


def extract_source_evidence_segments(markdown: str) -> list[tuple[str, str]]:
    bilingual = extract_bilingual_evidence_segments(markdown)
    if bilingual:
        return bilingual
    return [(timestamp, normalize_evidence(english)) for timestamp, english in extract_legacy_segments(markdown)]


def extract_legacy_sections(markdown: str) -> list[tuple[int, str]]:
    sections: list[tuple[int, str]] = []
    pending_heading = ""
    segment_count = 0

    for line in markdown.splitlines():
        heading_match = SECTION_HEADING_RE.match(line)
        if heading_match:
            pending_heading = heading_match.group(1).strip()
            continue

        if LEGACY_SEGMENT_RE.match(line):
            segment_count += 1
            if pending_heading:
                sections.append((segment_count, pending_heading))
                pending_heading = ""

    return sections


def extract_bilingual_section_starts(markdown: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    pending_heading = ""

    for line in markdown.splitlines():
        heading_match = SECTION_HEADING_RE.match(line)
        if heading_match:
            pending_heading = heading_match.group(1).strip()
            continue

        timestamp_match = CN_TIMESTAMP_RE.match(line)
        if timestamp_match and pending_heading:
            sections.append((normalize_timestamp(timestamp_match.group(1)), pending_heading))
            pending_heading = ""

    return sections


def read_user_chinese_transcript(path: Path) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        match = USER_CN_TIMESTAMP_RE.match(line)
        if match:
            if current:
                events.append(current)
            timestamp = match.group(1) or match.group(2) or ""
            current = {"timestamp": normalize_timestamp(timestamp), "chinese": match.group(3).strip()}
            continue

        if current and line and line != "---":
            current["chinese"] = f"{current['chinese']} {line}".strip()

    if current:
        events.append(current)
    return events


def align_evidence_to_chinese(
    chinese_events: list[dict[str, str]],
    evidence_segments: list[tuple[str, str]],
) -> dict[int, list[str]]:
    if not chinese_events:
        raise SystemExit("no timestamped Chinese transcript rows found")

    chinese_seconds = [timestamp_to_seconds(event["timestamp"]) for event in chinese_events]
    assignments: dict[int, list[str]] = {index: [] for index in range(len(chinese_events))}

    for timestamp, english in evidence_segments:
        second = timestamp_to_seconds(timestamp)
        index = 0
        for candidate, chinese_second in enumerate(chinese_seconds):
            if chinese_second <= second:
                index = candidate
            else:
                break
        assignments[index].append(english)

    return assignments


def map_section_starts_to_chinese(
    section_starts: list[tuple[str, str]],
    chinese_events: list[dict[str, str]],
) -> dict[int, str]:
    mapped: dict[int, str] = {}
    chinese_seconds = [timestamp_to_seconds(event["timestamp"]) for event in chinese_events]

    for timestamp, heading in section_starts:
        section_second = timestamp_to_seconds(timestamp)
        index = 0
        for candidate, chinese_second in enumerate(chinese_seconds):
            if chinese_second < section_second:
                index = candidate + 1
            else:
                break
        if index >= len(chinese_events):
            index = len(chinese_events) - 1
        mapped[index] = heading

    return mapped


def render_user_chinese_alignment(
    chinese_events: list[dict[str, str]],
    assignments: dict[int, list[str]],
    section_by_index: dict[int, str],
) -> str:
    lines: list[str] = []
    for index, event in enumerate(chinese_events):
        if index in section_by_index:
            if lines:
                lines.append("")
            lines.append(f"### {section_by_index[index]}")
            lines.append("")

        lines.append(f"【{event['timestamp']}】{event['chinese']}")
        lines.append("")
        english = " ".join(assignments.get(index, []))
        if english:
            lines.append(f"**English:** {english}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def normalize_evidence(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def read_translation_table(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for line_number, row in enumerate(reader, 1):
            if not row or row[0].strip().startswith("#"):
                continue
            if len(row) not in (2, 3, 4):
                raise SystemExit(
                    f"{path}:{line_number}: expected 2, 3, or 4 tab-separated fields: "
                    "index, [timestamp], [english], chinese"
                )
            if len(row) == 2:
                index, chinese = row
                timestamp = ""
                english = ""
            elif len(row) == 3:
                index, timestamp, chinese = row
                english = ""
            else:
                index, timestamp, english, chinese = row
            try:
                number = int(index)
            except ValueError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid index {index!r}") from exc
            rows.append(
                {
                    "index": str(number),
                    "timestamp": normalize_timestamp(timestamp) if timestamp else "",
                    "english": english.strip(),
                    "chinese": chinese.strip(),
                }
            )
    return rows


def read_sections(path: Path | None) -> dict[int, str]:
    if path is None:
        return {}
    sections: dict[int, str] = {}
    with path.open(newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for line_number, row in enumerate(reader, 1):
            if not row or row[0].strip().startswith("#"):
                continue
            if len(row) != 2:
                raise SystemExit(f"{path}:{line_number}: expected 2 fields: start_index, heading")
            try:
                start = int(row[0])
            except ValueError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid start index {row[0]!r}") from exc
            heading = row[1].strip()
            if not heading.startswith("### "):
                heading = f"### {heading}"
            sections[start] = heading
    return sections


def render_bilingual_body(
    segments: list[tuple[str, str]],
    translations: list[dict[str, str]],
    sections: dict[int, str],
    heading: str,
) -> str:
    if len(segments) != len(translations):
        raise SystemExit(f"count mismatch: {len(segments)} source segments vs {len(translations)} translations")

    lines = [heading, ""]
    for expected, ((timestamp, english), row) in enumerate(zip(segments, translations), 1):
        index = int(row["index"])
        if index != expected:
            raise SystemExit(f"translation index mismatch at row {expected}: got {index}")
        if row["timestamp"] and row["timestamp"] != timestamp:
            raise SystemExit(
                f"timestamp mismatch at row {expected}: source {timestamp}, translation table {row['timestamp']}"
            )
        if not row["chinese"]:
            raise SystemExit(f"missing Chinese translation at row {expected} ({timestamp})")

        if expected in sections:
            lines.append(sections[expected])
            lines.append("")
        lines.append(f"【{timestamp}】{row['chinese']}")
        lines.append("")
        lines.append(f"**English:** {english}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_frontmatter(markdown: str) -> str:
    match = FRONTMATTER_RE.search(markdown)
    return match.group(1) if match else ""


def parse_frontmatter_field(frontmatter: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}:[ \t]*(.*?)[ \t]*$", frontmatter, re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip()
    if not value:
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def parse_frontmatter_list(frontmatter: str, field: str) -> list[str]:
    scalar = parse_frontmatter_field(frontmatter, field)
    if scalar:
        if scalar.startswith("[") and scalar.endswith("]"):
            return [
                item.strip().strip("'\"")
                for item in scalar[1:-1].split(",")
                if item.strip()
            ]
        return [scalar.strip().strip("'\"")]

    match = re.search(rf"^{re.escape(field)}:\s*\n((?:\s+-\s+.+\n?)+)", frontmatter, re.MULTILINE)
    if not match:
        return []
    return [
        line.split("-", 1)[1].strip().strip("'\"")
        for line in match.group(1).splitlines()
        if line.strip().startswith("-")
    ]


def first_h1(markdown: str) -> str:
    body = FRONTMATTER_RE.sub("", markdown, count=1)
    match = H1_RE.search(body)
    return match.group(1).strip() if match else ""


def forbidden_raw_frontmatter_fields(frontmatter: str) -> list[str]:
    return [
        field
        for field in FORBIDDEN_RAW_FRONTMATTER_FIELDS
        if re.search(rf"^{re.escape(field)}:\s*", frontmatter, re.MULTILINE)
    ]


def raw_claims_bilingual(frontmatter: str) -> bool:
    raw_format = parse_frontmatter_field(frontmatter, "raw_format")
    languages = set(parse_frontmatter_list(frontmatter, "language"))
    return raw_format in {"bilingual_transcript", "transcript"} and {"en", "zh"}.issubset(languages)


def raw_claims_youtube_video(frontmatter: str) -> bool:
    return parse_frontmatter_field(frontmatter, "source_medium") == "video" and is_youtube_url(
        parse_frontmatter_field(frontmatter, "source_url")
    )


def is_youtube_url(url: str) -> bool:
    return bool(re.match(r"https://(?:www\.)?youtube\.com/watch\?[^\"'\n]+|https://youtu\.be/[^\"'\n]+", url))


def validate_translation_table(
    segments: list[tuple[str, str]],
    translations: list[dict[str, str]],
) -> list[str]:
    issues: list[str] = []
    if not segments:
        issues.append("no legacy transcript segments found in source")
    if len(segments) != len(translations):
        issues.append(f"count mismatch: {len(segments)} source segments vs {len(translations)} translations")

    for expected, ((timestamp, english), row) in enumerate(zip(segments, translations), 1):
        index = int(row["index"])
        if index != expected:
            issues.append(f"translation index mismatch at row {expected}: got {index}")
        if row["timestamp"] and row["timestamp"] != timestamp:
            issues.append(f"timestamp mismatch at row {expected}: source {timestamp}, table {row['timestamp']}")
        if row["english"] and normalize_evidence(row["english"]) != normalize_evidence(english):
            issues.append(f"English evidence mismatch at row {expected} ({timestamp})")
        if not row["chinese"]:
            issues.append(f"missing Chinese translation at row {expected} ({timestamp})")
        if len(issues) >= 20:
            issues.append("stopped after 20 issues")
            break
    return issues


def command_extract(args: argparse.Namespace) -> int:
    markdown = Path(args.source).read_text()
    segments = extract_legacy_segments(markdown)
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    for index, (timestamp, english) in enumerate(segments, 1):
        writer.writerow([index, timestamp, english, ""])
    print(f"# extracted {len(segments)} source segments", file=sys.stderr)
    return 0


def command_extract_sections(args: argparse.Namespace) -> int:
    markdown = Path(args.source).read_text()
    sections = extract_legacy_sections(markdown)
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    for index, heading in sections:
        writer.writerow([index, heading])
    print(f"# extracted {len(sections)} section headings", file=sys.stderr)
    return 0


def command_check_table(args: argparse.Namespace) -> int:
    markdown = Path(args.source).read_text()
    segments = extract_legacy_segments(markdown)
    translations = read_translation_table(Path(args.translations))
    issues = validate_translation_table(segments, translations)
    missing_chinese = sum(1 for row in translations if not row["chinese"])
    timestamped_rows = sum(1 for row in translations if row["timestamp"])
    english_rows = sum(1 for row in translations if row["english"])

    print(f"source_segments={len(segments)}")
    print(f"translation_rows={len(translations)}")
    print(f"timestamped_translation_rows={timestamped_rows}")
    print(f"english_evidence_rows={english_rows}")
    print(f"missing_chinese_rows={missing_chinese}")
    print(f"ok={not issues}")

    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1
    return 0


def command_render(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    markdown = source_path.read_text()
    segments = extract_legacy_segments(markdown)
    if not segments:
        raise SystemExit("no legacy transcript segments found")
    translations = read_translation_table(Path(args.translations))
    sections = read_sections(Path(args.sections) if args.sections else None)
    issues = validate_translation_table(segments, translations)
    if issues:
        raise SystemExit("translation table rejected: " + "; ".join(issues))
    body = render_bilingual_body(segments, translations, sections, args.heading)

    if args.in_place:
        marker = args.marker
        if marker not in markdown:
            raise SystemExit(f"marker not found for in-place replacement: {marker}")
        prefix = markdown.split(marker)[0]
        source_path.write_text(prefix + body)
        print(
            f"replaced_from_marker={marker!r} source_segments={len(segments)} "
            f"sections={len(sections)} preserved_prefix_lines={prefix.count(chr(10))}",
            file=sys.stderr,
        )
    else:
        sys.stdout.write(body)
    return 0


def command_align_timestamped_cn(
    args: argparse.Namespace,
    transcript_path_attribute: str,
    diagnostic_prefix: str,
) -> int:
    source_path = Path(args.source)
    markdown = source_path.read_text()
    chinese_path = Path(getattr(args, transcript_path_attribute))
    chinese_events = read_user_chinese_transcript(chinese_path)
    evidence_segments = extract_source_evidence_segments(markdown)
    if not evidence_segments:
        raise SystemExit("no English evidence segments found in source")
    source_marker = args.marker
    if source_marker not in markdown and args.fallback_marker in markdown:
        source_marker = args.fallback_marker
    output_heading = args.heading or source_marker

    assignments = align_evidence_to_chinese(chinese_events, evidence_segments)
    section_starts = [] if args.no_sections else extract_bilingual_section_starts(markdown)
    if not args.no_sections and not section_starts:
        for start_index, heading in extract_legacy_sections(markdown):
            if 1 <= start_index <= len(evidence_segments):
                section_starts.append((evidence_segments[start_index - 1][0], heading))
    section_by_index = map_section_starts_to_chinese(section_starts, chinese_events)
    body = render_user_chinese_alignment(
        chinese_events,
        assignments,
        section_by_index,
    )

    evidence_slots = sum(1 for values in assignments.values() if values)
    chinese_without_direct_evidence = len(chinese_events) - evidence_slots
    print(f"{diagnostic_prefix}_rows={len(chinese_events)}", file=sys.stderr)
    print(f"english_evidence_segments={len(evidence_segments)}", file=sys.stderr)
    print(f"english_evidence_slots={evidence_slots}", file=sys.stderr)
    print(f"chinese_without_direct_evidence={chinese_without_direct_evidence}", file=sys.stderr)
    print(f"section_headings={len(section_by_index)}", file=sys.stderr)

    if args.in_place:
        if source_marker not in markdown:
            raise SystemExit(f"marker not found for in-place replacement: {args.marker}")
        prefix = markdown.split(source_marker, 1)[0]
        source_path.write_text(prefix + output_heading + "\n\n" + body)
        print(
            f"replaced_from_marker={source_marker!r} output_heading={output_heading!r}",
            file=sys.stderr,
        )
    else:
        sys.stdout.write(output_heading + "\n\n" + body if output_heading else body)
    return 0


def command_align_user_cn(args: argparse.Namespace) -> int:
    return command_align_timestamped_cn(args, "user_chinese", "user_chinese")


def command_align_generated_cn(args: argparse.Namespace) -> int:
    return command_align_timestamped_cn(args, "generated_chinese", "generated_chinese")


def command_audit(args: argparse.Namespace) -> int:
    markdown = Path(args.source).read_text()
    frontmatter = parse_frontmatter(markdown)
    cn_count = len(CN_TIMESTAMP_RE.findall(markdown))
    en_count = len(EN_EVIDENCE_RE.findall(markdown))
    en_timestamp_count = len(EN_EVIDENCE_TIMESTAMP_RE.findall(markdown))
    claims_bilingual = raw_claims_bilingual(frontmatter)
    claims_youtube_video = raw_claims_youtube_video(frontmatter)
    source_url = parse_frontmatter_field(frontmatter, "source_url")
    source_title = parse_frontmatter_field(frontmatter, "source_title")
    youtube_embeds = YOUTUBE_EMBED_RE.findall(markdown)
    has_youtube_embed = bool(youtube_embeds)
    has_video_section = "## 原始视频描述与链接" in markdown
    old_heading = DEFAULT_BODY_MARKER in markdown
    legacy_transcript_heading = bool(LEGACY_TRANSCRIPT_HEADING_RE.search(markdown))
    legacy_segment_count = len(extract_legacy_segments(markdown))
    forbidden_fields = forbidden_raw_frontmatter_fields(frontmatter)
    title = parse_frontmatter_field(frontmatter, "title")
    completeness = parse_frontmatter_field(frontmatter, "completeness")
    translation_note = parse_frontmatter_field(frontmatter, "translation_note")
    transcript_source = parse_frontmatter_field(frontmatter, "transcript_source")
    acquisition_method = parse_frontmatter_field(frontmatter, "acquisition_method")
    h1 = first_h1(markdown)
    file_stem = Path(args.source).stem
    title_h1_aligned = bool(title and h1 and title == h1)
    title_filename_aligned = bool(title and title == file_stem)
    attachment_preface_count = len(ATTACHMENT_PREFACE_RE.findall(markdown))
    codex_translation_wording_count = len(CODEX_TRANSLATION_WORDING_RE.findall(markdown))
    legacy_connective_note_count = markdown.count(LEGACY_CONNECTIVE_NOTE)
    chinese_without_direct_evidence = max(cn_count - en_count, 0)
    grouped_chinese_ratio = chinese_without_direct_evidence / cn_count if cn_count else 0
    translation_note_mentions_user = "Chinese transcript provided by the user" in translation_note
    transcript_source_mentions_user = "Chinese transcript provided by the user" in transcript_source
    translation_note_mentions_codex_generated = (
        "Chinese translation generated by Codex from the preserved English transcript" in translation_note
    )
    claims_user_chinese_alignment = completeness.startswith("user_chinese_transcript")
    claims_codex_generated_alignment = completeness.startswith("codex_chinese_translation")
    user_cn = translation_note_mentions_user or transcript_source_mentions_user or claims_user_chinese_alignment
    accepted_user_alignment_completeness = {
        "web_clipper_english_transcript_with_user_chinese_transcript_alignment",
        "user_chinese_transcript_with_grouped_english_evidence_alignment",
    }
    completeness_matches_user_alignment = not user_cn or completeness in (
        accepted_user_alignment_completeness
    )

    issues: list[str] = []
    warnings: list[str] = []
    if claims_bilingual and cn_count == 0:
        issues.append("metadata claims bilingual transcript, but no Chinese timestamp lines were found")
    if claims_bilingual and en_count == 0:
        issues.append("metadata claims bilingual transcript, but no English evidence lines were found")
    if claims_bilingual and en_count > cn_count:
        issues.append(
            f"English evidence count ({en_count}) exceeds Chinese timestamp count ({cn_count}); "
            "one or more evidence rows may be unpaired"
        )
    if claims_bilingual and en_timestamp_count:
        issues.append(
            f"English evidence lines contain inline timestamps ({en_timestamp_count}); "
            "timestamps should appear only on Chinese transcript lines"
        )
    if claims_bilingual and old_heading:
        issues.append("old English-only transcript heading is still present")
    if claims_bilingual and legacy_segment_count:
        issues.append(f"legacy timestamp transcript segments are still present ({legacy_segment_count})")
    if legacy_transcript_heading:
        issues.append("legacy ## Transcript heading is still present")
    if claims_youtube_video and not has_youtube_embed:
        issues.append("metadata claims YouTube video source, but no playable Markdown media embed was found")
    if claims_youtube_video and has_youtube_embed and source_url not in youtube_embeds:
        issues.append("metadata source_url does not match any playable YouTube embed")
    if claims_youtube_video and not has_video_section:
        issues.append("metadata claims YouTube video source, but ## 原始视频描述与链接 is missing")
    if forbidden_fields:
        issues.append(f"Raw frontmatter contains Wiki-only fields: {', '.join(forbidden_fields)}")
    if title and h1 and title != h1:
        issues.append(f"frontmatter title does not match H1: {title!r} vs {h1!r}")
    if title and title != file_stem:
        issues.append(f"frontmatter title does not match filename stem: {title!r} vs {file_stem!r}")
    if claims_bilingual and attachment_preface_count:
        issues.append(f"attachment preface text appears to have leaked into the note ({attachment_preface_count})")
    if user_cn and codex_translation_wording_count:
        issues.append(
            "note claims user-provided Chinese transcript, but old Codex translation wording remains "
            f"({codex_translation_wording_count})"
        )
    if claims_user_chinese_alignment and not (translation_note_mentions_user or transcript_source_mentions_user):
        issues.append("completeness claims user Chinese transcript alignment, but transcript provenance does not mention the user")
    if user_cn and not completeness_matches_user_alignment:
        issues.append(f"user-provided transcript has unsupported alignment completeness: {completeness!r}")
    if claims_codex_generated_alignment and not translation_note_mentions_codex_generated:
        issues.append(
            "completeness claims Codex-generated grouped translation, but translation_note does not record "
            "the Codex-generated Chinese provenance"
        )
    if claims_bilingual and legacy_connective_note_count:
        issues.append(
            f"legacy connective placeholders remain in English evidence rows ({legacy_connective_note_count}); "
            "leave Chinese continuation rows without a fake English evidence line"
        )
    if claims_bilingual and grouped_chinese_ratio > 0.4:
        warnings.append(
            f"many Chinese timestamp rows share grouped English evidence "
            f"({chinese_without_direct_evidence}/{cn_count}); confirm that this reflects the source segmentation"
        )
    if claims_youtube_video and not source_title:
        warnings.append("source_title is missing; keep the original source title when available")
    if acquisition_method and acquisition_method not in ALLOWED_ACQUISITION_METHODS:
        issues.append(f"unsupported acquisition_method: {acquisition_method!r}")
    if not acquisition_method:
        warnings.append("acquisition_method is missing; tolerated for historical Raw notes")

    print(f"claims_bilingual={claims_bilingual}")
    print(f"chinese_timestamp_lines={cn_count}")
    print(f"english_evidence_lines={en_count}")
    print(f"english_evidence_timestamp_lines={en_timestamp_count}")
    print(f"old_english_only_heading={old_heading}")
    print(f"legacy_transcript_heading={legacy_transcript_heading}")
    print(f"legacy_timestamp_segments={legacy_segment_count}")
    print(f"claims_youtube_video={claims_youtube_video}")
    print(f"has_youtube_embed={has_youtube_embed}")
    print(f"youtube_embed_matches_source_url={bool(source_url and source_url in youtube_embeds)}")
    print(f"has_video_section={has_video_section}")
    print(f"has_source_title={bool(source_title)}")
    print(f"acquisition_method={acquisition_method}")
    print(f"acquisition_method_valid={acquisition_method in ALLOWED_ACQUISITION_METHODS}")
    print(f"forbidden_raw_frontmatter_fields={','.join(forbidden_fields) if forbidden_fields else ''}")
    print(f"title_h1_aligned={title_h1_aligned}")
    print(f"title_filename_aligned={title_filename_aligned}")
    print(f"attachment_preface_leaked={attachment_preface_count}")
    print(f"codex_translation_wording_left={codex_translation_wording_count}")
    print(f"legacy_connective_note_count={legacy_connective_note_count}")
    print(f"chinese_without_direct_english_evidence={chinese_without_direct_evidence}")
    print(f"grouped_chinese_ratio={grouped_chinese_ratio:.3f}")
    print(f"translation_note_mentions_user={translation_note_mentions_user}")
    print(f"translation_note_mentions_codex_generated={translation_note_mentions_codex_generated}")
    print(f"completeness_matches_user_alignment={completeness_matches_user_alignment}")

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract", help="extract legacy timestamped English transcript to TSV")
    extract.add_argument("source", help="Raw markdown file with **timestamp** · English lines")
    extract.set_defaults(func=command_extract)

    extract_sections = subparsers.add_parser("extract-sections", help="extract legacy ### headings to sections TSV")
    extract_sections.add_argument("source", help="Raw markdown file with legacy ### transcript headings")
    extract_sections.set_defaults(func=command_extract_sections)

    check_table = subparsers.add_parser("check-table", help="verify translation TSV before rendering")
    check_table.add_argument("source", help="Raw markdown file with **timestamp** · English lines")
    check_table.add_argument(
        "translations",
        help="TSV: index<TAB>timestamp<TAB>english<TAB>chinese, or index<TAB>timestamp<TAB>chinese",
    )
    check_table.set_defaults(func=command_check_table)

    render = subparsers.add_parser("render", help="render bilingual body from source and translation TSV")
    render.add_argument("source", help="Raw markdown file with **timestamp** · English lines")
    render.add_argument(
        "translations",
        help="TSV: index<TAB>timestamp<TAB>english<TAB>chinese, or index<TAB>timestamp<TAB>chinese",
    )
    render.add_argument("--sections", help="optional TSV: start_index<TAB>### heading")
    render.add_argument("--heading", default=DEFAULT_HEADING)
    render.add_argument("--marker", default=DEFAULT_BODY_MARKER)
    render.add_argument("--in-place", action="store_true", help="replace everything from marker onward")
    render.set_defaults(func=command_render)

    align_user_cn = subparsers.add_parser(
        "align-user-cn",
        help="align a user-provided timestamped Chinese transcript with existing English evidence",
    )
    align_user_cn.add_argument("source", help="Raw markdown file with bilingual or legacy English evidence")
    align_user_cn.add_argument("user_chinese", help="timestamped Chinese transcript text file from the user")
    align_user_cn.add_argument("--marker", default=DEFAULT_HEADING)
    align_user_cn.add_argument("--fallback-marker", default="## 中英对照（按视频时间戳）")
    align_user_cn.add_argument("--heading", help="optional output heading; defaults to the matched source marker")
    align_user_cn.add_argument("--no-sections", action="store_true", help="do not reuse existing ### headings")
    align_user_cn.add_argument("--in-place", action="store_true", help="replace transcript body from marker onward")
    align_user_cn.set_defaults(func=command_align_user_cn)

    align_generated_cn = subparsers.add_parser(
        "align-generated-cn",
        help="align a Codex-generated timestamped Chinese reading transcript with existing English evidence",
    )
    align_generated_cn.add_argument("source", help="Raw markdown file with bilingual or legacy English evidence")
    align_generated_cn.add_argument(
        "generated_chinese",
        help="timestamped Chinese reading transcript generated from the preserved English source",
    )
    align_generated_cn.add_argument("--marker", default=DEFAULT_BODY_MARKER)
    align_generated_cn.add_argument("--fallback-marker", default=DEFAULT_HEADING)
    align_generated_cn.add_argument("--heading", default=DEFAULT_HEADING)
    align_generated_cn.add_argument("--no-sections", action="store_true", help="do not reuse existing ### headings")
    align_generated_cn.add_argument("--in-place", action="store_true", help="replace transcript body from marker onward")
    align_generated_cn.set_defaults(func=command_align_generated_cn)

    audit = subparsers.add_parser("audit", help="audit bilingual transcript consistency")
    audit.add_argument("source", help="Raw markdown file to audit")
    audit.set_defaults(func=command_audit)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
