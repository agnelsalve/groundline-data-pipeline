// Run config — the one place to change the collection window.
// Every downstream node reads these values via $('Run config').
const LOOKBACK_DAYS = 45;

let dataDir;
try {
  dataDir = $env.GROUNDLINE_DATA_DIR;
} catch (e) {
  throw new Error('n8n is blocking environment variables. Start n8n with scripts/start-n8n.ps1 (it sets N8N_BLOCK_ENV_ACCESS_IN_NODE=false).');
}
if (!dataDir) {
  throw new Error('GROUNDLINE_DATA_DIR is not set. Start n8n with scripts/start-n8n.ps1 so the workflow knows where to save files.');
}

const now = new Date();
const since = new Date(now.getTime() - LOOKBACK_DAYS * 86400000);

return [{
  json: {
    run_id: now.toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z',
    run_date: now.toISOString().slice(0, 10),
    collected_at: now.toISOString(),
    lookback_days: LOOKBACK_DAYS,
    since_iso: since.toISOString(),
    since_unix: Math.floor(since.getTime() / 1000),
    data_dir: dataDir.split('\\').join('/').replace(/\/$/, ''),
  },
}];
