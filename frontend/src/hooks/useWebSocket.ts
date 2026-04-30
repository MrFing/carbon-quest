import { useEffect, useMemo, useRef, useState } from "react";

import type { ClientMessage, ServerMessage } from "../game/types";

type ConnectionStatus = "idle" | "connecting" | "open" | "closed" | "error";

interface WebSocketOptions {
  onMessage?: (message: ServerMessage) => void;
  onOpen?: () => void;
  onClose?: (event: CloseEvent) => void;
  onError?: () => void;
  reconnect?: boolean;
  reconnectDelayMs?: number;
  maxReconnectAttempts?: number;
}

const rawBackendUrl = (import.meta.env.VITE_BACKEND_URL as string | undefined)?.replace(/\/$/, "") ?? "ws://localhost:8000";

export function getBackendWsBase(): string {
  return rawBackendUrl;
}

export function getBackendHttpBase(): string {
  if (rawBackendUrl.startsWith("wss://")) {
    return rawBackendUrl.replace("wss://", "https://");
  }
  if (rawBackendUrl.startsWith("ws://")) {
    return rawBackendUrl.replace("ws://", "http://");
  }
  return rawBackendUrl;
}

export function useWebSocket(url: string | null, options: WebSocketOptions = {}) {
  const socketRef = useRef<WebSocket | null>(null);
  const callbacksRef = useRef(options);
  const reconnectTimerRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const [status, setStatus] = useState<ConnectionStatus>("idle");

  callbacksRef.current = options;

  useEffect(() => {
    if (!url) {
      setStatus("idle");
      return undefined;
    }

    let disposed = false;

    const connect = () => {
      if (disposed) {
        return;
      }

      setStatus("connecting");
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        reconnectAttemptsRef.current = 0;
        setStatus("open");
        callbacksRef.current.onOpen?.();
      };

      socket.onmessage = (event) => {
        const parsed = JSON.parse(event.data) as ServerMessage;
        callbacksRef.current.onMessage?.(parsed);
      };

      socket.onerror = () => {
        setStatus("error");
        callbacksRef.current.onError?.();
      };

      socket.onclose = (event) => {
        socketRef.current = null;
        setStatus("closed");
        callbacksRef.current.onClose?.(event);

        const shouldReconnect = callbacksRef.current.reconnect ?? true;
        const maxReconnectAttempts = callbacksRef.current.maxReconnectAttempts ?? 8;
        const reconnectDelayMs = callbacksRef.current.reconnectDelayMs ?? 800;

        if (!disposed && shouldReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          const delay = reconnectDelayMs * Math.min(reconnectAttemptsRef.current, 4);
          reconnectTimerRef.current = window.setTimeout(() => {
            connect();
          }, delay);
        }
      };
    };

    connect();

    return () => {
      disposed = true;
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      const socket = socketRef.current;
      socketRef.current = null;
      socket?.close();
    };
  }, [url]);

  const sendMessage = useMemo(
    () => (message: ClientMessage) => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify(message));
      }
    },
    []
  );

  return {
    status,
    sendMessage
  };
}
