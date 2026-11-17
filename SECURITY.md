# Security Policy

## Reporting a vulnerability

Do not open a public issue for an exploitable security problem. Report it
privately to the repository owner with the affected version, reproduction steps,
impact, and a synthetic proof of concept. Never attach a confidential document.

## Security boundaries

W-Rookie processes untrusted office files locally. It does not upload
documents or embedded media. HWP/HWPX processing uses the locally installed
Hancom automation API only after preflight scanning succeeds.

Every supported file passes a mandatory static gate before document automation:

- ZIP path traversal, duplicate entries, encryption, item count and expansion
  limits;
- high compression-ratio and ZIP-bomb patterns;
- DTD, entity expansion and malformed XML through hardened parsing;
- VBA macros, HWP scripts, ActiveX, OLE and executable payloads;
- dangerous external relationship schemes and suspicious active content;
- HWP OLE compound-file signature, required streams and BinData names.

On Windows, users can add a Microsoft Defender custom-file scan. It runs with
remediation disabled so W-Rookie does not silently quarantine or modify the
source. A reported threat blocks processing.

Security scanning is defense in depth, not a guarantee that a file is benign.
Keep Windows, Defender, Microsoft Office and Hancom Office patched. Do not bypass
a block for a document from an untrusted source.

## Output safety

- New-file output is the default.
- Large ZIP entries are copied in bounded chunks.
- Output is first written to a same-directory temporary file.
- The final path is replaced only after successful completion.
- Failed or cancelled operations remove incomplete temporary files.
