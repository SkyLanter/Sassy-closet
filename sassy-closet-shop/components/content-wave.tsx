"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useReducedMotion } from "framer-motion";
import {
  CONTENT_WAVE_INTRO_RATIO,
  CONTENT_WAVE_MS,
  contentWaveDurationMs,
} from "@/lib/content-wave";

type WaveApi = {
  play: () => void;
  playing: boolean;
  token: number;
};

const ContentWaveContext = createContext<WaveApi | null>(null);

export function useContentWave(): WaveApi {
  return (
    useContext(ContentWaveContext) ?? {
      play: () => {},
      playing: false,
      token: 0,
    }
  );
}

function WaveSheen() {
  return (
    <div className="content-wave-layer" aria-hidden data-testid="content-wave-sheen">
      <div
        className="content-wave-sheen"
        style={{ animationDuration: `${CONTENT_WAVE_MS}ms` }}
      />
    </div>
  );
}

/** Overlay the one-shot soft sheen on product looks only — not hero, not tab chrome. */
export function ContentWaveLooks({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const wave = useContentWave();
  return (
    <div
      className={`content-wave-host relative isolate ${className ?? ""}`}
      data-testid="content-wave-looks"
      data-content-wave={wave.playing ? "1" : "0"}
      data-wave-dir="ltr"
      data-wave-glass="sheen"
      data-wave-exclude="bg"
    >
      {children}
      {wave.playing ? <WaveSheen key={wave.token} /> : null}
    </div>
  );
}

export function ContentWaveHost({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const reduced = useReducedMotion();
  const [token, setToken] = useState(0);
  const [playing, setPlaying] = useState(false);
  const clearTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const hostRef = useRef<HTMLDivElement>(null);
  const introPlayed = useRef(false);

  const stop = useCallback(() => {
    if (clearTimer.current) {
      clearTimeout(clearTimer.current);
      clearTimer.current = null;
    }
    setPlaying(false);
  }, []);

  const play = useCallback(() => {
    if (reduced) {
      return;
    }
    if (clearTimer.current) {
      clearTimeout(clearTimer.current);
      clearTimer.current = null;
    }
    setPlaying(false);
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        setToken((current) => current + 1);
        setPlaying(true);
        clearTimer.current = setTimeout(stop, contentWaveDurationMs());
      });
    });
  }, [reduced, stop]);

  useEffect(() => {
    if (reduced) {
      return;
    }
    const node = hostRef.current;
    if (!node) {
      return;
    }
    const looks =
      node.querySelector("#featured-panel") ??
      node.querySelector("[data-testid='content-wave-looks']") ??
      node.querySelector("[data-testid='product-gallery']") ??
      node;
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (!entry?.isIntersecting || introPlayed.current) {
          return;
        }
        introPlayed.current = true;
        play();
        observer.disconnect();
      },
      { threshold: CONTENT_WAVE_INTRO_RATIO },
    );
    observer.observe(looks);
    return () => observer.disconnect();
  }, [play, reduced]);

  useEffect(() => {
    return () => {
      if (clearTimer.current) {
        clearTimeout(clearTimer.current);
      }
    };
  }, []);

  const api = useMemo(
    () => ({ play, playing, token }),
    [play, playing, token],
  );

  return (
    <ContentWaveContext.Provider value={api}>
      <div
        ref={hostRef}
        className={`relative ${className ?? ""}`}
        data-testid="content-wave-host"
      >
        {children}
      </div>
    </ContentWaveContext.Provider>
  );
}
