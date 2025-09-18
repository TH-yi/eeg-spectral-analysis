import argparse, sys, os, traceback
from .base import BaseApp
from .analyze import analyze_entry

def main(argv=None):
    try:
        return _main_impl(argv)
    except SystemExit:
        raise
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

def _main_impl(argv=None):
    p = argparse.ArgumentParser(prog="eegspec", description="EEG spectral analysis toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_logging_args(sp):
        sp.add_argument("--log-level", type=str, default="INFO")
        sp.add_argument("--log-dir", type=str, default=None)
        sp.add_argument("--log-prefix", type=str, default="")
        sp.add_argument("--log-suffix", type=str, default="")
        sp.add_argument("--log-percentage", type=float, default=None)

    sp = sub.add_parser("analyze", help="Analyze a folder of subject JSONs or a single subject JSON (task-centric).")
    sp.add_argument("--input", required=True, help="Folder with many subject.json OR a single subject.json")
    sp.add_argument("--sfreq", type=float, required=True)
    sp.add_argument("--out-dir", required=True)
    sp.add_argument("--nperseg", type=int, default=1024)
    sp.add_argument("--noverlap", type=int, default=None)
    sp.add_argument("--window", type=str, default="hann")
    sp.add_argument("--channels-file", type=str, default=None, help="Plain text, .csv or .locs")
    sp.add_argument("--alpha", type=str, default="8,13")
    sp.add_argument("--faa-db", action="store_true")
    sp.add_argument("--max-processors", type=int, default=4)
    add_logging_args(sp)
    sp.set_defaults(func=cmd_analyze)

    args = p.parse_args(argv)
    return args.func(args)

def cmd_analyze(args):
    app = BaseApp(log_level=args.log_level, log_dir=args.log_dir, log_prefix=args.log_prefix, log_suffix=args.log_suffix, log_percentage=args.log_percentage)
    app.logger.info("Analyze entry")
    try:
        analyze_entry(
            input_path=args.input,
            sfreq=args.sfreq,
            out_dir=args.out_dir,
            nperseg=args.nperseg,
            noverlap=args.noverlap,
            window=args.window,
            channels_file=args.channels_file,
            alpha=args.alpha,
            faa_db=args.faa_db,
            max_processors=args.max_processors,
            log_kwargs=dict(log_level=args.log_level, log_dir=args.log_dir, log_prefix=args.log_prefix, log_suffix=args.log_suffix, log_percentage=args.log_percentage),
        )
        app.logger.info(f"Wrote summary to {os.path.join(args.out_dir, 'summary.json')}")
    except Exception as e:
        app.logger.error(f"Analyze failed: {e}")
        app.logger.debug(traceback.format_exc())
        raise
