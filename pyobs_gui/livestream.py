"""Incremental parsers for BaseVideo's live-view streams (/video.mjpg and /video.raw).

Both are fed the raw bytes of an HTTP/1.0 response as they arrive on the socket and return the
frames completed so far. Kept free of Qt so they can be tested without a socket.
"""

import json
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray


class StreamError(Exception):
    """The server answered the stream request with something other than 200 OK."""

    def __init__(self, status: int | None, body: bytes):
        self.status = status
        self.body = body
        text = body.decode("utf-8", errors="replace").strip()
        super().__init__(f"HTTP status {status}: {text}" if text else f"HTTP status {status}")


@dataclass
class RawFrame:
    """One frame from the raw stream."""

    meta: dict[str, Any]
    data: NDArray[Any]


class _HttpStreamParser:
    """Strips and checks the HTTP response header, then hands the body to _parse()."""

    def __init__(self) -> None:
        self._buffer = b""
        self._headers_received = False

    def feed(self, data: bytes) -> list[Any]:
        """Add received bytes and return all frames completed by them.

        Raises:
            StreamError: If the response status is not 200.
        """
        self._buffer += data

        # the boundary string also appears in the Content-Type header, so the header must go first
        if not self._headers_received:
            pos = self._buffer.find(b"\r\n\r\n")
            if pos == -1:
                return []
            header, self._buffer = self._buffer[:pos], self._buffer[pos + 4 :]
            self._headers_received = True
            status = self._status(header)
            if status != 200:
                raise StreamError(status, self._buffer)

        return self._parse()

    @staticmethod
    def _status(header: bytes) -> int | None:
        """Status code from the response's status line, None if it can't be parsed."""
        parts = header.split(b"\r\n", 1)[0].split()
        if len(parts) < 2 or not parts[0].startswith(b"HTTP/"):
            return None
        try:
            return int(parts[1])
        except ValueError:
            return None

    def _parse(self) -> list[Any]:
        raise NotImplementedError


class MjpegParser(_HttpStreamParser):
    """Parser for /video.mjpg, returns the JPEG bytes of each frame.

    A frame is only complete once the next boundary arrives, since the parts carry no length.
    """

    BOUNDARY = b"--jpgboundary\r\n"

    def _parse(self) -> list[bytes]:
        frames: list[bytes] = []
        while True:
            pos = self._buffer.find(self.BOUNDARY)
            if pos == -1:
                return frames
            part, self._buffer = self._buffer[:pos], self._buffer[pos + len(self.BOUNDARY) :]

            # skip part header; empty for the preamble before the first boundary
            header_end = part.find(b"\r\n\r\n")
            if header_end == -1:
                continue
            jpeg = part[header_end + 4 :]
            if jpeg:
                frames.append(jpeg)


class RawParser(_HttpStreamParser):
    """Parser for /video.raw, returns decoded frames.

    Each part carries its size implicitly (DTYPE and NAXISn in the meta header), so the payload is
    read by length and never searched for the boundary, which could appear in binary data.
    """

    BOUNDARY = b"--rawboundary\r\n"

    def __init__(self) -> None:
        super().__init__()
        self._meta: dict[str, Any] | None = None
        self._size = 0

    def _parse(self) -> list[RawFrame]:
        frames: list[RawFrame] = []
        while True:
            if self._meta is None:
                # boundary plus part header
                start = self._buffer.find(self.BOUNDARY)
                if start == -1:
                    return frames
                end = self._buffer.find(b"\r\n\r\n", start)
                if end == -1:
                    return frames
                headers = self._buffer[start + len(self.BOUNDARY) : end]
                self._buffer = self._buffer[end + 4 :]
                self._meta = self._parse_meta(headers)
                self._size = self._frame_size(self._meta)

            # payload
            if len(self._buffer) < self._size:
                return frames
            payload, self._buffer = self._buffer[: self._size], self._buffer[self._size :]
            frames.append(RawFrame(self._meta, self._decode(self._meta, payload)))
            self._meta = None

    @staticmethod
    def _parse_meta(headers: bytes) -> dict[str, Any]:
        for line in headers.split(b"\r\n"):
            name, _, value = line.partition(b":")
            if name.strip().lower() == b"x-pyobs-frame-meta":
                meta = json.loads(value.strip())
                if not isinstance(meta, dict):
                    raise ValueError("Frame meta is not a JSON object.")
                return meta
        raise ValueError("Frame without meta header.")

    @staticmethod
    def _shape(meta: dict[str, Any]) -> tuple[int, ...]:
        """Array shape, NAXISn first (numpy order), e.g. (height, width) or (height, width, colour)."""
        naxis = int(meta.get("NAXIS", 2))
        return tuple(int(meta[f"NAXIS{i}"]) for i in range(naxis, 0, -1))

    @classmethod
    def _frame_size(cls, meta: dict[str, Any]) -> int:
        return int(np.prod(cls._shape(meta))) * np.dtype(meta["DTYPE"]).itemsize

    @classmethod
    def _decode(cls, meta: dict[str, Any], payload: bytes) -> NDArray[Any]:
        return np.frombuffer(payload, dtype=np.dtype(meta["DTYPE"])).reshape(cls._shape(meta))


def fit_factor(full_width: int, full_height: int, view_width: int, view_height: int) -> int:
    """Largest integer downsampling factor that keeps the image at least as large as the view.

    Args:
        full_width: Width of the full frame in pixels.
        full_height: Height of the full frame in pixels.
        view_width: Width of the view in pixels.
        view_height: Height of the view in pixels.

    Returns:
        Factor, at least 1.
    """
    if view_width < 1 or view_height < 1:
        return 1
    return max(1, min(full_width // view_width, full_height // view_height))


__all__ = ["StreamError", "RawFrame", "MjpegParser", "RawParser", "fit_factor"]
