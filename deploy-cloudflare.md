# Deploying Zoom MCP Server to Cloudflare Workers

Guide for deploying the Zoom MCP server as a Cloudflare Worker (serverless).

---

## ⚠️ Important Limitations

Before choosing this approach, understand these limitations:

1. **Language:** Cloudflare Workers use JavaScript/TypeScript - you'd need to rewrite the Python server
2. **Execution Time:** 10ms CPU time limit on free tier, 50ms on paid ($5/month)
3. **Stateful Connections:** Requires Durable Objects for persistent MCP connections
4. **Cold Starts:** Functions may have cold start latency
5. **Complexity:** More complex setup than Docker

**Recommendation:** Only use this if you specifically want serverless or don't have a VPS.

---

## When to Use Cloudflare Workers

✅ **Good for:**
- Serverless architecture preference
- Global edge deployment
- Minimal server management
- Built-in DDoS protection
- Free tier available

❌ **Not ideal for:**
- Long-running MCP connections
- Complex Python dependencies
- Real-time bidirectional communication
- Large file processing

---

## Architecture Overview

```
Gumloop → Cloudflare Worker → Zoom API
                ↓
         Durable Objects (for state)
```

---

## Step 1: Set Up Cloudflare Workers Account

1. Sign up at https://workers.cloudflare.com/
2. Install Wrangler CLI:
```bash
npm install -g wrangler
```

3. Login:
```bash
wrangler login
```

---

## Step 2: Create Worker Project

```bash
# Create new project
mkdir zoom-mcp-worker
cd zoom-mcp-worker

# Initialize project
wrangler init zoom-mcp

# Choose TypeScript when prompted
```

---

## Step 3: Implement Zoom MCP Worker

**File: `src/index.ts`**

```typescript
/**
 * Zoom MCP Server - Cloudflare Worker
 *
 * This is a simplified example - you'll need to expand this
 * based on your MCP server implementation
 */

export interface Env {
  ZOOM_API_KEY: string;
  ZOOM_API_SECRET: string;
  ZOOM_ACCOUNT_ID: string;
  // Durable Object binding
  ZOOM_MCP_STATE: DurableObjectNamespace;
}

// Zoom authentication helper
async function getZoomAccessToken(env: Env): Promise<string> {
  const credentials = btoa(`${env.ZOOM_API_KEY}:${env.ZOOM_API_SECRET}`);

  const response = await fetch(
    `https://zoom.us/oauth/token?grant_type=account_credentials&account_id=${env.ZOOM_ACCOUNT_ID}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${credentials}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to get access token: ${response.statusText}`);
  }

  const data = await response.json() as { access_token: string };
  return data.access_token;
}

// Main worker handler
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // Health check endpoint
    if (url.pathname === '/health') {
      return new Response('OK', { status: 200 });
    }

    // MCP endpoint
    if (url.pathname === '/mcp' && request.method === 'POST') {
      try {
        const body = await request.json() as any;

        // Route to appropriate MCP tool
        switch (body.method) {
          case 'tools/list':
            return handleToolsList();
          case 'tools/call':
            return handleToolCall(body, env);
          default:
            return new Response('Method not supported', { status: 400 });
        }
      } catch (error) {
        return new Response(`Error: ${error}`, { status: 500 });
      }
    }

    return new Response('Not Found', { status: 404 });
  },
};

// List available tools
function handleToolsList(): Response {
  const tools = {
    tools: [
      {
        name: 'list_meetings',
        description: 'List Zoom meetings',
        inputSchema: {
          type: 'object',
          properties: {
            user_id: { type: 'string' },
            type: { type: 'string', default: 'scheduled' },
          },
        },
      },
      {
        name: 'list_users',
        description: 'List Zoom users',
        inputSchema: {
          type: 'object',
          properties: {
            status: { type: 'string', default: 'active' },
          },
        },
      },
      // Add other tools...
    ],
  };

  return new Response(JSON.stringify(tools), {
    headers: { 'Content-Type': 'application/json' },
  });
}

// Handle tool calls
async function handleToolCall(body: any, env: Env): Promise<Response> {
  const { name, arguments: args } = body.params;

  // Get Zoom access token
  const accessToken = await getZoomAccessToken(env);

  switch (name) {
    case 'list_meetings':
      return await listMeetings(args, accessToken);
    case 'list_users':
      return await listUsers(args, accessToken);
    case 'list_recordings':
      return await listRecordings(args, accessToken);
    // Add other tools...
    default:
      return new Response('Tool not found', { status: 404 });
  }
}

// Tool: List Meetings
async function listMeetings(args: any, token: string): Promise<Response> {
  const userId = args.user_id || 'me';
  const type = args.type || 'scheduled';

  const response = await fetch(
    `https://api.zoom.us/v2/users/${userId}/meetings?type=${type}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    return new Response(`Error: ${response.statusText}`, { status: response.status });
  }

  const data = await response.json();
  return new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' },
  });
}

// Tool: List Users
async function listUsers(args: any, token: string): Promise<Response> {
  const status = args.status || 'active';

  const response = await fetch(
    `https://api.zoom.us/v2/users?status=${status}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    return new Response(`Error: ${response.statusText}`, { status: response.status });
  }

  const data = await response.json();
  return new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' },
  });
}

// Tool: List Recordings
async function listRecordings(args: any, token: string): Promise<Response> {
  const userId = args.user_id || 'me';
  const fromDate = args.from_date || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  const toDate = args.to_date || new Date().toISOString().split('T')[0];

  const response = await fetch(
    `https://api.zoom.us/v2/users/${userId}/recordings?from=${fromDate}&to=${toDate}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    return new Response(`Error: ${response.statusText}`, { status: response.status });
  }

  const data = await response.json();
  return new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' },
  });
}

// Durable Object for state management (optional, for caching tokens)
export class ZoomMCPState {
  state: DurableObjectState;
  env: Env;

  constructor(state: DurableObjectState, env: Env) {
    this.state = state;
    this.env = env;
  }

  async fetch(request: Request): Promise<Response> {
    // Implement token caching logic here
    return new Response('State object ready');
  }
}
```

---

## Step 4: Configure wrangler.toml

```toml
name = "zoom-mcp"
main = "src/index.ts"
compatibility_date = "2024-01-01"
workers_dev = true

[env.production]
name = "zoom-mcp-prod"
route = "zoom-mcp.yourdomain.com/*"

# Durable Objects (optional, for state)
[[durable_objects.bindings]]
name = "ZOOM_MCP_STATE"
class_name = "ZoomMCPState"

# Secrets (set via wrangler secret)
# ZOOM_API_KEY
# ZOOM_API_SECRET
# ZOOM_ACCOUNT_ID
```

---

## Step 5: Set Secrets

```bash
wrangler secret put ZOOM_API_KEY
# Enter: WRv5JXlFSXSZ5jmGtvznw

wrangler secret put ZOOM_API_SECRET
# Enter: 4qqxMKsGjLZ8ooQN42NLbHce5OdoTE2V

wrangler secret put ZOOM_ACCOUNT_ID
# Enter: mk8MCWYUT2-Er1nzO4LkAg
```

---

## Step 6: Deploy

```bash
# Deploy to production
wrangler deploy

# Or deploy to dev
wrangler dev
```

---

## Step 7: Test

```bash
# Test health endpoint
curl https://zoom-mcp.your-subdomain.workers.dev/health

# Test MCP endpoint
curl -X POST https://zoom-mcp.your-subdomain.workers.dev/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list"
  }'
```

---

## Step 8: Custom Domain (Optional)

1. Add your domain to Cloudflare
2. In Workers dashboard, add custom domain
3. Update wrangler.toml with your route

---

## Comparison: Docker vs Cloudflare Workers

| Feature | Docker + VPS | Cloudflare Workers |
|---------|-------------|-------------------|
| **Language** | Python (existing code) | JavaScript/TypeScript (rewrite) |
| **Setup Time** | 30 minutes | 2-3 hours (rewrite + deploy) |
| **Cost** | $5-10/month VPS | Free tier available |
| **Maintenance** | Manage server | Zero maintenance |
| **Execution Time** | Unlimited | 10ms (free) / 50ms (paid) |
| **Cold Starts** | None | ~100ms |
| **Scaling** | Manual | Automatic |
| **Best For** | MCP protocol, Python | Simple HTTP APIs |
| **Debugging** | Easy (logs, shell access) | Harder (limited logs) |

---

## Recommendation

For your Zoom MCP server, **use Docker + VPS** because:

1. ✅ **No code rewrite** - Keep your working Python implementation
2. ✅ **Better for MCP** - Handles long-running connections
3. ✅ **Easier debugging** - Full access to logs and environment
4. ✅ **No execution limits** - No 10ms/50ms time constraints
5. ✅ **Faster deployment** - 30 minutes vs 2-3 hours

Only use Cloudflare Workers if:
- You want to learn serverless
- You prefer zero server management
- You don't mind rewriting in TypeScript
- Your use case fits the execution time limits

---

## Next Steps

If you choose Docker + VPS:
1. Follow `deploy-vps.md`
2. Deploy in 30 minutes
3. Done!

If you choose Cloudflare Workers:
1. Complete the TypeScript rewrite
2. Test locally with `wrangler dev`
3. Deploy with `wrangler deploy`

---

**Last Updated:** October 10, 2025
