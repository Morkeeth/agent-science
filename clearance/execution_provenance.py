"""Fingerprint the executing research code without exposing local paths or content."""
import hashlib
from pathlib import Path
import subprocess


def capture():
    root=Path(__file__).resolve().parent.parent
    files=sorted((root/'clearance').rglob('*.py'))
    if (root/'requirements.txt').is_file():files.append(root/'requirements.txt')
    digest=hashlib.sha256()
    for path in files:
        digest.update(str(path.relative_to(root)).encode()+b'\0')
        digest.update(path.read_bytes()+b'\0')
    ref=None; dirty=None
    try:
        top=subprocess.check_output(['git','-C',str(root),'rev-parse','--show-toplevel'],stderr=subprocess.DEVNULL,text=True,timeout=5).strip()
        if Path(top).resolve()==root:
            ref=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True,timeout=5).strip()
            paths=[str(p.relative_to(root)) for p in files]
            changes=subprocess.check_output(['git','-C',str(root),'status','--porcelain','--untracked-files=all','--',*paths],stderr=subprocess.DEVNULL,timeout=5)
            dirty=bool(changes)
    except (OSError,subprocess.SubprocessError):
        pass
    return {'code_ref':ref,'source_sha256':digest.hexdigest(),'dirty':dirty,
        'basis':'On-disk clearance Python sources and requirements at operation reservation; local Git identity when available. No loaded-module, dependency, hardware or model attestation.'}
