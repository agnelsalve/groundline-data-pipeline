// Source 1 — News RSS feeds. No key, no rate limit.
// Three AI desks from primary publishers + Google News searches for the
// narrower topics (agents in analytics, grounding/hallucination, Weave).
const cfg = $('Run config').first().json;
const days = cfg.lookback_days;
const gnews = (q) =>
  'https://news.google.com/rss/search?q=' + encodeURIComponent(`${q} when:${days}d`) +
  '&hl=en-US&gl=US&ceid=US:en';

const feeds = [
  { feed_id: 'techcrunch_ai',          source_name: 'TechCrunch',            focus_hint: 'AI',    url: 'https://techcrunch.com/category/artificial-intelligence/feed/' },
  { feed_id: 'mit_tech_review_ai',     source_name: 'MIT Technology Review', focus_hint: 'AI',    url: 'https://www.technologyreview.com/topic/artificial-intelligence/feed' },
  { feed_id: 'the_verge_ai',           source_name: 'The Verge',             focus_hint: 'AI',    url: 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml' },
  { feed_id: 'gnews_ai_agents',        source_name: 'Google News',           focus_hint: 'AI',    url: gnews('"AI agents" (analytics OR enterprise OR data)') },
  { feed_id: 'gnews_ai_grounding',     source_name: 'Google News',           focus_hint: 'AI',    url: gnews('"AI hallucinations" OR "retrieval-augmented generation" OR "AI grounding"') },
  { feed_id: 'gnews_weave',            source_name: 'Google News',           focus_hint: 'Weave', url: gnews('"Weave Communications" OR "getweave" OR "NYSE: WEAV"') },
];

return feeds.map((f) => ({ json: f }));
