# WebSocket Usage Guide

## Understanding WebSocket Errors

### Expected Behavior

When you see this in the console:
```
⚠️ WebSocket connection failed - using REST API fallback
```

This is **normal and expected** when:
- The backend server is not running
- The WebSocket endpoint is unavailable
- Network issues prevent connection

### How It Works

The app uses a **hybrid approach**:

1. **Primary**: WebSocket for real-time updates
2. **Fallback**: REST API when WebSocket fails

This means the app **continues to work perfectly** even when WebSocket is unavailable!

---

## Running with WebSocket

### 1. Start the Backend

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

The backend will start on `http://localhost:8000` with WebSocket at `ws://localhost:8000/ws`

### 2. Start the Frontend

```bash
cd webapp
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Verify Connection

Open the browser console and look for:
```
✅ WebSocket connected
```

If you see this, WebSocket is working! 🎉

---

## Console Messages Explained

### Development Mode

| Message | Meaning | Action Needed |
|---------|---------|---------------|
| `✅ WebSocket connected` | Connection successful | None - working! |
| `⚠️ WebSocket connection failed` | Backend not running | Start backend (optional) |
| `🔌 WebSocket disconnected` | Connection lost | Check backend |
| `🔄 Reconnecting... Attempt X/5` | Auto-reconnecting | Wait or start backend |
| `⚠️ Max reconnection attempts reached` | Gave up reconnecting | Using REST API only |

### Production Mode

In production (`NODE_ENV=production`), these messages are **suppressed** to keep the console clean.

---

## Testing WebSocket Events

### Manual Testing

1. **Start both backend and frontend**
2. **Open browser DevTools** → Network tab → Filter by "WS"
3. **Look for** `ws://localhost:8000/ws` with status "101 Switching Protocols"
4. **Trigger an event** from the backend (e.g., create an alert)
5. **Watch the frontend** update in real-time!

### Automated Testing

All WebSocket functionality is tested:

```bash
npm test -- --run
```

Tests use mock WebSocket to verify:
- Connection establishment
- Room subscriptions
- Message handling
- Reconnection logic
- Error handling

---

## WebSocket Rooms

Each page subscribes to specific rooms:

| Page | Room | Events |
|------|------|--------|
| Alerts | `alerts` | `alert_created`, `alert_updated` |
| Dashboard | `dashboard` | `dashboard_update` |
| FL Status | `fl-status` | `fl_progress` |
| Attack Graph | `attack-graph` | `attack_detected` |

---

## Troubleshooting

### "WebSocket connection failed" Error

**Cause**: Backend is not running or not accessible

**Solutions**:
1. Start the backend: `cd backend && poetry run uvicorn app.main:app --reload`
2. Check backend is running: `curl http://localhost:8000/health`
3. Verify WebSocket URL in `.env.local`: `NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws`

**Note**: The app works fine without WebSocket using REST API!

### Connection Keeps Dropping

**Cause**: Backend restarting or network issues

**Solutions**:
1. Check backend logs for errors
2. Verify network connectivity
3. Check firewall settings

**Note**: The app auto-reconnects up to 5 times

### No Real-Time Updates

**Cause**: WebSocket not connected or backend not emitting events

**Solutions**:
1. Check console for `✅ WebSocket connected`
2. Verify backend is emitting events (check backend logs)
3. Check Network tab for WebSocket messages

**Fallback**: Manual refresh still works with REST API

---

## Configuration

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### WebSocket Options

```typescript
const { lastMessage, subscribe, isConnected } = useWebSocket({
  url: 'ws://localhost:8000/ws',  // Custom URL
  autoConnect: true,               // Connect on mount
  reconnectInterval: 3000,         // 3 seconds between retries
  maxReconnectAttempts: 5,         // Max 5 reconnection attempts
})
```

---

## Best Practices

### ✅ Do

- Let the app handle reconnection automatically
- Use REST API as fallback
- Check `isConnected` before assuming real-time updates
- Test with backend running for full experience

### ❌ Don't

- Don't panic when you see "WebSocket connection failed"
- Don't manually reconnect (it's automatic)
- Don't rely solely on WebSocket (use hybrid approach)
- Don't disable error messages (they're helpful for debugging)

---

## Production Deployment

### Environment Variables

```bash
# Production
NEXT_PUBLIC_WS_URL=wss://your-domain.com/ws  # Use WSS (secure)
```

### Considerations

1. **Use WSS** (WebSocket Secure) in production
2. **Configure CORS** on backend for your domain
3. **Load balancing**: Ensure sticky sessions for WebSocket
4. **Monitoring**: Track WebSocket connection success rate
5. **Fallback**: REST API ensures reliability

---

## Summary

- ✅ WebSocket provides real-time updates
- ✅ REST API provides reliable fallback
- ✅ App works perfectly with or without WebSocket
- ✅ Auto-reconnection handles temporary failures
- ✅ Console messages help with debugging
- ✅ All functionality is fully tested

**The "WebSocket connection failed" message is not an error - it's just informing you that real-time updates are unavailable, but the app continues working normally!**

---

For more details, see:
- `WEBSOCKET_INTEGRATION_COMPLETE.md` - Full integration documentation
- `lib/useWebSocket.ts` - WebSocket hook implementation
- `tests/lib/useWebSocket.test.ts` - WebSocket tests
