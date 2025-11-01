import arxiv
import json
import os
from datetime import datetime

# Keywords to search - modify if you like
KEYWORDS = ["RAG", "Retrieval-Augmented Generation", "Computer Vision"]
DATA_PATH = "data/papers.json"
MAX_RESULTS = 100

def fetch_papers(keyword):
    """Fetch papers by keyword from arXiv"""
    search = arxiv.Search(
        query=keyword,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []
    for result in search.results():
        papers.append({
            "title": result.title.strip(),
            "authors": [a.name for a in result.authors],
            "published": result.published.strftime("%Y-%m-%d"),
            "link": result.entry_id,
            "summary": result.summary.strip().replace("\\n", " ")[:400] + "..."
        })
    return papers

def save_results(all_papers):
    """Save all keyword results to JSON"""
    meta = {
        "last_update": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "keywords": list(all_papers.keys()),
        "counts": {k: len(v) for k,v in all_papers.items()}
    }
    out = {"meta": meta, "data": all_papers}
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

def update_readme(all_papers):
    """Generate README file"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    md = [
        "# 📰 Daily Papers",
        "",
        "The project automatically fetches the latest papers from arXiv based on keywords.",
        "",
        "The subheadings in the README file represent the search keywords.",
        "",
        "Only the most recent articles for each keyword are retained, up to a maximum of 100 papers.",
        "",
        "You can click the 'Watch' button to receive daily email notifications.",
        "",
        f"**Last update:** {today}",
        "",
        "---",
    ]

    for kw, papers in all_papers.items():
        md.append(f"## 🔍 {kw}")
        md.append("")
        if not papers:
            md.append("_No recent papers found._")
            md.append("")
            continue
        for p in papers:
            md.append(f"### [{p['title']}]({p['link']})")
            md.append(f"*Published: {p['published']}*  ")
            md.append(f"**Authors:** {', '.join(p['authors'])}")
            md.append("")
            md.append(p['summary'])
            md.append("")
        md.append("---")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\\n".join(md))

if __name__ == "__main__":
    all_papers = {}
    for kw in KEYWORDS:
        print(f"Fetching: {kw}")
        try:
            all_papers[kw] = fetch_papers(kw)
        except Exception as e:
            print(f"Error fetching {kw}: {e}")
            all_papers[kw] = []
    save_results(all_papers)
    update_readme(all_papers)
    print("✅ Arxiv papers updated successfully.")