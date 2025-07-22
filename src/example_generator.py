import argparse
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from conversion.abc2audio import abc2wav
from qualitative.gen_music import compose
from utility.result import aperture
from returns.result import Failure, Success, Result

# --- score rendering ---------------------------------------------------------

def abc2png(
    abc_path: Path,
    out_png: Path | None = None,
    dpi: int = 300,
    transparent: bool = True,
    keep_ps: bool = False,
) -> Result[list[Path], Exception]:
    """
    ABC -> PNG(複数ページ対応) に変換する。
    abcm2ps と Ghostscript(gs) が PATH にある前提。
    戻り値: 生成した PNG の Path リスト
    """
    try:
        if shutil.which("abcm2ps") is None:
            raise FileNotFoundError("abcm2ps が見つからないよ")
        if shutil.which("gs") is None:
            raise FileNotFoundError("gs(Ghostscript) が見つからないよ")

        tmpdir = Path(tempfile.mkdtemp(prefix="abc2ps_"))
        ps_out = tmpdir / "score.ps"  # abcm2ps は -O で指定した名前を基本に吐く

        # 1) ABC -> PS
        cmd_ps = ["abcm2ps", str(abc_path), "-O", str(ps_out)]
        subprocess.run(cmd_ps, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # abcm2ps は score.ps / score001.ps ... のように分割する場合がある
        ps_files = sorted(tmpdir.glob("score*.ps"))
        if not ps_files:
            raise RuntimeError("abcm2ps が PS を出力しなかった…？")

        png_paths: list[Path] = []

        for idx, ps in enumerate(ps_files):
            if out_png is None:
                base = abc_path.with_suffix("")
                name = f"{base.name}-{idx:03d}.png" if len(ps_files) > 1 else f"{base.name}.png"
                png_target = base.parent / name
            else:
                # out_png が単一指定なら、複数ページ時は -001 など付ける
                if len(ps_files) > 1:
                    stem = out_png.stem
                    png_target = out_png.with_name(f"{stem}-{idx:03d}.png")
                else:
                    png_target = out_png

            # 2) PS -> PNG
            gs_args = [
                "gs",
                "-sDEVICE=pngalpha" if transparent else "-sDEVICE=png16m",
                f"-r{dpi}",
                "-o",
                str(png_target),
                str(ps),
            ]
            subprocess.run(gs_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            png_paths.append(png_target)

        if not keep_ps:
            for ps in ps_files:
                ps.unlink(missing_ok=True)
            tmpdir.rmdir()

        return Success(png_paths)

    except Exception as e:
        logging.exception("abc2png でエラー")
        return Failure(e)

# --- main flow ---------------------------------------------------------------

def process(param_name: str, params: list[float]) -> None:
    match aperture(compose(param_name, params)):
        case Failure(_) as f:
            logging.error("failed to generate music. %s", f)
            return
        case Success(succ):
            scores: list[str] = succ

    cache_folder = Path(f"data/examples/{param_name}")
    cache_folder.mkdir(parents=True, exist_ok=True)

    for i, score in enumerate(scores):
        path = cache_folder / f"{i}.abc"
        path.write_text(score)

        # 楽譜PNG作成
        match abc2png(path):
            case Failure(e):
                logging.error("PNG生成失敗: %s", e)
            case Success(pngs):
                logging.info("PNG生成: %s", [str(p) for p in pngs])

        # オーディオ作成
        try:
            abc2wav(str(path), str(path.with_suffix(".mid")), str(path.with_suffix(".wav")))
        except Exception as e:
            logging.exception("wav生成失敗: %s", e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("param_name")
    parser.add_argument("params", nargs="+", type=float, help="可変長でパラメータ列を渡す")
    parser.add_argument("--log", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log.upper(), logging.INFO),
                        format="%(levelname)s:%(message)s")

    process(args.param_name, args.params)

if __name__ == "__main__":
    main()
