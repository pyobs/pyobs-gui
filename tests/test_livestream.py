import json

import numpy as np
import pytest

from pyobs_gui.livestream import MjpegParser, RawParser, StreamError, fit_factor

_OK = b"HTTP/1.0 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=--rawboundary\r\n\r\n"


def _raw_part(data: np.ndarray, **extra: object) -> bytes:
    """One part of /video.raw, as BaseVideo.raw_handler() writes it."""
    meta = {"DTYPE": data.dtype.newbyteorder("<").str, "NAXIS": data.ndim, **extra}
    for i, n in enumerate(reversed(data.shape), start=1):
        meta[f"NAXIS{i}"] = n
    return (
        b"--rawboundary\r\nContent-Type: application/octet-stream\r\nX-Pyobs-Frame-Meta: "
        + json.dumps(meta).encode()
        + b"\r\n\r\n"
        + np.ascontiguousarray(data, dtype=data.dtype.newbyteorder("<")).tobytes()
        + b"\r\n"
    )


def _feed_bytewise(parser: RawParser | MjpegParser, data: bytes) -> list:
    frames = []
    for i in range(len(data)):
        frames += parser.feed(data[i : i + 1])
    return frames


# ── MJPEG ──────────────────────────────────────────────────────────────────


def test_mjpeg_frame_complete_at_next_boundary() -> None:
    parser = MjpegParser()
    head = b"HTTP/1.0 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=--jpgboundary\r\n\r\n"
    part = b"--jpgboundary\r\nContent-type: image/jpeg\r\n\r\n"
    assert parser.feed(head + part + b"JPEG1\r\n") == []
    assert parser.feed(part + b"JPEG2\r\n") == [b"JPEG1\r\n"]


def test_mjpeg_header_split_across_reads() -> None:
    data = (
        b"HTTP/1.0 200 OK\r\nContent-Type: x; boundary=--jpgboundary\r\n\r\n"
        + b"--jpgboundary\r\nContent-type: image/jpeg\r\n\r\nA\r\n" * 3
    )
    assert _feed_bytewise(MjpegParser(), data) == [b"A\r\n", b"A\r\n"]


# ── raw ────────────────────────────────────────────────────────────────────


def test_raw_decodes_2d_uint16() -> None:
    data = np.arange(12, dtype=np.uint16).reshape(3, 4)
    frames = RawParser().feed(_OK + _raw_part(data, SWBIN=2))
    assert len(frames) == 1
    np.testing.assert_array_equal(frames[0].data, data)
    assert frames[0].meta["SWBIN"] == 2


def test_raw_payload_containing_boundary_is_read_by_length() -> None:
    """The payload is binary and may contain the boundary; it must not split the frame."""
    boundary = np.frombuffer(b"--rawboundary\r\n\r\n\r\n", dtype=np.uint8)
    data = np.tile(boundary, 2).reshape(2, -1)
    frames = RawParser().feed(_OK + _raw_part(data) + _raw_part(data))
    assert len(frames) == 2
    for frame in frames:
        np.testing.assert_array_equal(frame.data, data)


def test_raw_bytewise_and_colour() -> None:
    data = np.arange(2 * 3 * 3, dtype=np.float32).reshape(2, 3, 3)
    frames = _feed_bytewise(RawParser(), _OK + _raw_part(data) + _raw_part(data))
    assert len(frames) == 2
    assert frames[1].data.shape == (2, 3, 3)
    np.testing.assert_array_equal(frames[1].data, data)


def test_raw_part_without_meta_raises() -> None:
    with pytest.raises(ValueError):
        RawParser().feed(_OK + b"--rawboundary\r\nContent-Type: application/octet-stream\r\n\r\n")


# ── HTTP status ────────────────────────────────────────────────────────────


def test_non_200_raises_with_body() -> None:
    with pytest.raises(StreamError) as e:
        RawParser().feed(b"HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nbin must be >= 1")
    assert e.value.status == 400
    assert "bin must be >= 1" in str(e.value)


# ── fit factor ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "full, view, factor",
    [
        ((4000, 3000), (800, 600), 5),
        ((4000, 3000), (800, 1000), 3),  # height limits
        ((640, 480), (800, 600), 1),  # smaller than view: never upsample
        ((1001, 1001), (334, 334), 2),  # floor: image stays at least as large as the view
        ((4000, 3000), (0, 0), 1),  # not laid out yet
    ],
)
def test_fit_factor(full: tuple[int, int], view: tuple[int, int], factor: int) -> None:
    assert fit_factor(*full, *view) == factor
