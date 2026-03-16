import os

from .cli import main

# Allow running from src/python while loading generated client at repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

if __name__ == "__main__":
    try:
        os.envvar["GOOGLE_API_KEY"]
    except KeyError as e:
        raise APIKeyException("GOOGLE_API_KEY environment variable not set")

    main()
