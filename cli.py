import argparse
import requests

API_BASE_URL = "http://127.0.0.1:8000"

def track_repo(root, track, webhook=False):
    url = f"{API_BASE_URL}/repo/{root}/track/{track}"
    params = {"webhook": "true"} if webhook else {}

    response = requests.post(url, params=params)

    if response.status_code == 200:
        print(f"Tracking {track} for {root}.")
        if webhook:
            print("Webhook has been set up successfully.")
    else:
        print(f"Error: {response.text}")


def main():
    parser = argparse.ArgumentParser(description="Track GitHub repository changes.")
    parser.add_argument("-r", "--repo", required=True, help="GitHub repository (owner/repo)")
    parser.add_argument("--track", required=True, choices=["commits", "files", "pulls"], help="What to track")
    parser.add_argument("--webhook", action="store_true", help="Enable real-time tracking with webhook")
    
    args = parser.parse_args()
    track_repo(args.repo, args.track)

if __name__ == "__main__":
    main()

