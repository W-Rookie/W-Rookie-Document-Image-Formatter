from __future__ import annotations

import argparse
import struct
import zipfile
import zlib
from pathlib import Path

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="xml" ContentType="application/xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

PACKAGE_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOCUMENT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/sample.png"/>
</Relationships>"""


def drawing(object_id: int, size: int) -> str:
    return f"""<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">
 <wp:extent cx="{size}" cy="{size}"/><wp:docPr id="{object_id}" name="Sample {object_id}"/>
 <wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
 <a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <pic:pic><pic:nvPicPr><pic:cNvPr id="{object_id}" name="sample.png"/><pic:cNvPicPr/></pic:nvPicPr>
   <pic:blipFill><a:blip r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
   <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{size}" cy="{size}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
  </pic:pic>
 </a:graphicData></a:graphic>
</wp:inline></w:drawing></w:r>"""


def document_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <w:body>
  <w:p><w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>W-Rookie 테스트 문서</w:t></w:r></w:p>
  <w:p><w:r><w:t>아래 사진은 일반 문단에 있습니다.</w:t></w:r></w:p>
  <w:p>{drawing(1, 1440000)}</w:p>
  <w:p><w:r><w:t>아래 사진은 표 셀 안에 있습니다.</w:t></w:r></w:p>
  <w:tbl><w:tblPr><w:tblW w:w="8000" w:type="dxa"/></w:tblPr><w:tblGrid><w:gridCol w:w="8000"/></w:tblGrid>
   <w:tr><w:tc><w:tcPr><w:tcW w:w="8000" w:type="dxa"/><w:tcMar><w:top w:w="180" w:type="dxa"/><w:bottom w:w="180" w:type="dxa"/></w:tcMar></w:tcPr>
    <w:p>{drawing(2, 1080000)}</w:p>
   </w:tc></w:tr>
  </w:tbl>
  <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>
 </w:body>
</w:document>"""


def png_chunk(kind: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


def sample_png() -> bytes:
    rows = b"\x00\x4f\x46\xe5\x25\x63\xeb" + b"\x00\x06\xb6\xd4\x7c\x3a\xed"
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(rows))
        + png_chunk(b"IEND", b"")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a synthetic W-Rookie test DOCX")
    parser.add_argument("output", nargs="?", type=Path, default=Path("sample_before.docx"))
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", CONTENT_TYPES)
        package.writestr("_rels/.rels", PACKAGE_RELS)
        package.writestr("word/document.xml", document_xml())
        package.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS)
        package.writestr("word/media/sample.png", sample_png())
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
