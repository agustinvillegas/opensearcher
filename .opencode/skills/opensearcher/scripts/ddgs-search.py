import sys, json, argparse
from duckduckgo_search import DDGS

def search(query, max_results=5, region="es-es"):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, region=region, max_results=max_results):
            results.append({
                "title": r.get("title"),
                "href": r.get("href"),
                "body": r.get("body")
            })
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max", type=int, default=5, help="Max results")
    parser.add_argument("--region", default="es-es")
    args = parser.parse_args()

    results = search(args.query, args.max, args.region)
    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
