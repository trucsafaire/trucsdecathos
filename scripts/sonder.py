"""Sonde les sites des diocèses (data/dioceses.json) et dit comment lire leur agenda.
Sortie : data/dioceses-sonde.json. Lancer : python scripts/sonder.py [id …]"""
import json, os, re, sys, time, urllib.request, urllib.error, concurrent.futures as cf
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "TrucsDeCathos/1.0 (+https://trucsdecathos.fr ; agenda catholique, lecture polie)"

def lire(url, n=600000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.geturl(), r.headers.get("Content-Type", ""), r.read(n).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, "", ""
    except Exception as e:
        return 0, url, "", str(e)[:80]

EVT = re.compile(r"event|evenement|agenda|calendrier|tribe|mec-events|ai1ec|eventon", re.I)

def sonder(d):
    r = {"id": d["id"], "url": d["url"]}
    st, fin, ct, h = lire(d["url"])
    r["statut"], r["final"] = st, fin
    if st != 200:
        r["erreur"] = h[:80]; return r
    base = re.match(r"https?://[^/]+", fin).group(0)
    r["cms"] = "wordpress" if "wp-content" in h else "joomla" if "Joomla" in h or "/media/system/" in h else "drupal" if "Drupal" in h or "/sites/default/" in h else "autre"
    r["plugins"] = sorted(set(re.findall(r"wp-content/plugins/([a-z0-9_-]+)", h)))[:30]
    time.sleep(0.5)
    if r["cms"] == "wordpress":
        s2, _, _, j = lire(base + "/wp-json/")
        try:
            ns = json.loads(j).get("namespaces", [])
            r["ns"] = [n for n in ns if EVT.search(n)]
        except Exception: r["ns"] = None
        s3, _, _, t = lire(base + "/wp-json/wp/v2/types")
        try:
            r["types"] = {k: v.get("rest_base") for k, v in json.loads(t).items() if EVT.search(k) or EVT.search(v.get("rest_base") or "")}
        except Exception: r["types"] = None
        for sm in ("/sitemap_index.xml", "/wp-sitemap.xml"):
            s4, _, _, x = lire(base + sm)
            if s4 == 200:
                r["sitemaps"] = [u for u in re.findall(r"<loc>([^<]+)</loc>", x) if EVT.search(u)]; break
    liens = sorted(set(u for u in re.findall(r'href="([^"#]+)"', h) if re.search(r"agenda|evenement|événement|calendrier|events?/?$", u, re.I)))[:8]
    r["liens_agenda"] = liens
    # page agenda : JSON-LD Event, iCal
    for u in liens[:2]:
        u = u if u.startswith("http") else base + ("" if u.startswith("/") else "/") + u
        s5, f5, _, p = lire(u)
        if s5 != 200: continue
        r.setdefault("pages", []).append({"url": f5, "jsonld_event": len(re.findall(r'"@type"\s*:\s*"Event"', p)),
            "ics": sorted(set(re.findall(r'(?:href|src)="([^"]*(?:\.ics|ical|webcal:)[^"]*)"', p)))[:4],
            "plugins": sorted(set(re.findall(r"wp-content/plugins/([a-z0-9_-]+)", p)) - set(r["plugins"]))[:10],
            "eb": "eventbooking" in p, "mec": "mec-event" in p, "tribe": "tribe-events" in p})
        time.sleep(0.5)
    return r

def main():
    ds = json.load(open(os.path.join(RACINE, "data", "dioceses.json"), encoding="utf-8"))
    if sys.argv[1:]: ds = [d for d in ds if d["id"] in sys.argv[1:]]
    with cf.ThreadPoolExecutor(8) as ex:  # 8 sites en parallèle, chacun lu poliment
        res = list(ex.map(sonder, ds))
    json.dump(res, open(os.path.join(RACINE, "data", "dioceses-sonde.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in res:
        print(r["id"], r.get("statut"), r.get("cms"), "ns=", r.get("ns"), "types=", r.get("types"), "sm=", [s.rsplit("/",1)[-1] for s in r.get("sitemaps") or []],
              "pages=", [(p["jsonld_event"], p["ics"][:1], p["eb"], p["mec"], p["tribe"]) for p in r.get("pages", [])])

if __name__ == "__main__":
    main()
