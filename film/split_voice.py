"""Split demo/voiceover.txt into one file per paragraph for cue-aligned rendering."""
import pathlib

src = pathlib.Path("demo/voiceover.txt").read_text().split("\n")
head = [l for l in src if l.startswith("@")]
paras, cur = [], []
for l in [l for l in src if not l.startswith("@")]:
    if l.strip():
        cur.append(l)
    elif cur:
        paras.append(" ".join(cur))
        cur = []
if cur:
    paras.append(" ".join(cur))
d = pathlib.Path("demo/.vo-parts")
d.mkdir(exist_ok=True)
for old in d.glob("p*"):
    old.unlink()
for i, para in enumerate(paras):
    (d / f"p{i:02d}.txt").write_text("\n".join(head) + "\n\n" + para + "\n")
print(f"{len(paras)} paragraphs -> {d}")
