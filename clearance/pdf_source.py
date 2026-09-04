"""Bounded PDF-to-text worker. Invoked in a separate process by source fetching."""
import io
import re
import sys
from pypdf import PdfReader


def main():
    raw=sys.stdin.buffer.read(8_000_001)
    if len(raw)>8_000_000:raise ValueError('PDF exceeds extraction byte limit')
    reader=PdfReader(io.BytesIO(raw),strict=False)
    if reader.is_encrypted or len(reader.pages)>200:
        raise ValueError('encrypted PDF or page limit exceeded')
    parts=[];size=0
    for page in reader.pages:
        text=page.extract_text() or ''
        size+=len(text)
        if size>1_000_000:raise ValueError('PDF exceeds extracted text limit')
        parts.append(text)
    text=re.sub(r'\s+',' ','\n'.join(parts)).strip()
    if not text:raise ValueError('PDF has no extractable text; OCR is not available')
    sys.stdout.write(text)


if __name__=='__main__':main()
