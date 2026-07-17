from __future__ import annotations

from decimal import Decimal

import pytest
from PIL import Image, ImageDraw, ImageFont

from walkthrough.record_live_sessions import LINE_H, draw_physical_rows, physical_rows
from walkthrough.request_probe import summarize_response, validate_response
from walkthrough.verify_media import validate_probe


def test_physical_rows_split_embedded_newlines_and_wrap_commands() -> None:
    rows = physical_rows(
        "python -c first line\nsecond " + ("x" * 140),
        first_prefix="$ ",
        continuation_prefix="  ",
    )
    assert len(rows) >= 3
    assert rows[0].startswith("$ ")
    assert all("\n" not in row and "\r" not in row for row in rows)
    assert all(len(row) <= 100 for row in rows)


def test_terminal_draw_rejects_newlines_and_advances_one_row_at_a_time() -> None:
    draw = ImageDraw.Draw(Image.new("RGB", (400, 200)))
    fnt = ImageFont.load_default()
    start = 17
    end = draw_physical_rows(
        draw,
        [("first", (255, 255, 255)), ("second", (255, 255, 255))],
        x=0,
        y=start,
        fnt=fnt,
    )
    assert end == start + (2 * LINE_H)
    with pytest.raises(ValueError, match="one physical row"):
        draw_physical_rows(
            draw,
            [("first\nsecond", (255, 255, 255))],
            x=0,
            y=start,
            fnt=fnt,
        )


def test_request_probe_validates_expected_failure_and_summarizes_success() -> None:
    validate_response(502, {"detail": "upstream_error"}, expected_status=502, expected_detail="upstream_error")
    with pytest.raises(ValueError, match="expected detail"):
        validate_response(502, {"detail": "wrong"}, expected_status=502, expected_detail="upstream_error")
    assert summarize_response(
        200,
        {"partner_id": "p1", "recommendations": [{"id": "one"}], "audit": {"policy_source": "partner-config-service"}},
    ) == {
        "status": 200,
        "partner_id": "p1",
        "recommendation_count": 1,
        "policy_source": "partner-config-service",
    }


def test_media_probe_contract_requires_exact_stream_identity() -> None:
    payload = {
        "streams": [
            {"codec_type": "video", "codec_name": "h264", "width": 1920, "height": 1080, "r_frame_rate": "1/1", "nb_frames": "165", "start_time": "0.000000", "duration": "165.000000"},
            {"codec_type": "audio", "codec_name": "aac", "sample_rate": "48000", "channels": 2, "channel_layout": "stereo", "start_time": "0.000000", "duration": "165.000000"},
        ],
        "format": {"duration": "165.000000"},
    }
    validate_probe(payload, Decimal("165"))

    payload["streams"][1]["channel_layout"] = "unknown"
    with pytest.raises(ValueError, match="audio layout"):
        validate_probe(payload, Decimal("165"))
