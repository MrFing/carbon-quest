import { useEffect, useMemo, useRef, useState } from "react";

import type { ClientMessage, ServerMessage } from "../game/types";

type ConnectionStatus = "idle" | "connecting" | "open" | "closed" | "error";

interface WebSocketOptions {
  onMessage?: (message: ServerMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: () => void;
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
  const [status, setStatus] = useState<ConnectionStatus>("idle");

  callbacksRef.current = options;

  useEffect(() => {
    if (!url) {
      return undefined;
    }

    const socket = new WebSocket(url);
    socketRef.current = socket;
    setStatus("connecting");

    socket.onopen = () => {
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

    socket.onclose = () => {
      setStatus("closed");
      callbacksRef.current.onClose?.();
    };

    return () => {
      socket.close();
      socketRef.current = null;
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
