import pg from 'pg';

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL ?? 'postgres://pulse:pulse@localhost:5432/pulse' });
const pollMs = Number(process.env.POLL_INTERVAL_MS ?? 2000);

async function deliver(notification: any) {
  const destination = notification.payload?.to ?? 'demo@pulse.local';
  console.log(JSON.stringify({ event: 'notification.deliver', channel: notification.channel, template: notification.template, destination }));
}

async function tick() {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const { rows } = await client.query("SELECT * FROM notifications WHERE status='queued' AND scheduled_at<=now() ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 20");
    for (const item of rows) {
      try {
        await deliver(item);
        await client.query("UPDATE notifications SET status='sent', sent_at=now(), error=NULL WHERE id=$1", [item.id]);
      } catch (error) {
        await client.query("UPDATE notifications SET status='failed', error=$2 WHERE id=$1", [item.id, String(error)]);
      }
    }
    await client.query('COMMIT');
  } catch (error) {
    await client.query('ROLLBACK');
    console.error(error);
  } finally { client.release(); }
}

console.log('Pulse notification worker started');
setInterval(() => void tick(), pollMs);
void tick();
