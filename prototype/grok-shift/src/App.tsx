import { useEffect, useRef, useState } from "react";
import { startArrivalWalk, type WalkHandle } from "@/game/arrival-walk";
import type { BlastHud } from "@/game/mine-blast";

const KEYS: { label: string; code: string }[] = [
  { label: "Q look", code: "KeyQ" },
  { label: "W", code: "KeyW" },
  { label: "E look", code: "KeyE" },
  { label: "A", code: "KeyA" },
  { label: "S", code: "KeyS" },
  { label: "D", code: "KeyD" },
];

const EMPTY: BlastHud = {
  prompt: "",
  hint: "",
  mood: "",
  carried: 0,
  placed: 0,
  doorClosed: false,
  result: "",
  fuse: 0,
  doorOpenAlert: false,
  oreHeld: 0,
  cartCargo: 0,
  cartMass: 0,
  dumped: 0,
  brakeOn: true,
  dose: 0,
  grabbing: false,
};

export default function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const walkRef = useRef<WalkHandle | null>(null);
  const heldRef = useRef<Set<string>>(new Set());
  const [held, setHeld] = useState<string[]>([]);
  const [ready, setReady] = useState(false);
  const [hud, setHud] = useState<BlastHud>(EMPTY);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const walk = startArrivalWalk(canvas);
    walkRef.current = walk;
    const t = window.setTimeout(() => setReady(true), 400);
    const poll = window.setInterval(() => {
      const next = walk.getHud();
      setHud((prev) =>
        prev.prompt === next.prompt &&
        prev.result === next.result &&
        prev.carried === next.carried &&
        prev.placed === next.placed &&
        prev.doorClosed === next.doorClosed &&
        prev.hint === next.hint &&
        Math.ceil(prev.fuse) === Math.ceil(next.fuse) &&
        prev.doorOpenAlert === next.doorOpenAlert &&
        prev.oreHeld === next.oreHeld &&
        prev.cartCargo === next.cartCargo &&
        prev.dumped === next.dumped &&
        prev.brakeOn === next.brakeOn &&
        Math.floor(prev.dose) === Math.floor(next.dose) &&
        prev.grabbing === next.grabbing
          ? prev
          : next,
      );
    }, 120);
    canvas.focus();
    return () => {
      window.clearTimeout(t);
      window.clearInterval(poll);
      walk.stop();
      walkRef.current = null;
    };
  }, []);

  const syncHeld = (next: Set<string>) => {
    heldRef.current = next;
    const list = [...next];
    setHeld(list);
    walkRef.current?.setHeld(list);
  };
  const press = (code: string) => {
    canvasRef.current?.focus();
    const n = new Set(heldRef.current);
    n.add(code);
    syncHeld(n);
  };
  const release = (code: string) => {
    const n = new Set(heldRef.current);
    n.delete(code);
    syncHeld(n);
  };

  return (
    <div className="relative h-full min-h-0 overflow-hidden bg-bg text-fg">
      <canvas ref={canvasRef} tabIndex={0} className="absolute inset-0 h-full w-full touch-none outline-none" />
      <div className="pointer-events-none absolute inset-x-0 top-0 z-10 flex items-start justify-between p-4">
        <div>
          <div className="font-display text-xs uppercase tracking-[0.22em] text-primary">
            Spawn → mine → haulage line
          </div>
          <h1 className="font-display text-2xl font-semibold uppercase tracking-tight md:text-4xl">Shift</h1>
          <p className="mt-1 max-w-lg text-sm text-muted">{hud.hint || "Hold W. Left is the mine. Straight is the cart line."}</p>
        </div>
        <div className="rounded-md border border-border bg-surface/80 px-3 py-2 font-mono text-xs uppercase text-muted">
          {ready
            ? `dose ${Math.floor(hud.dose)} · ore ${hud.oreHeld} · cart ${hud.cartCargo}/3 · ${hud.grabbing ? "PUSHING" : "walk"} · dumped ${hud.dumped}`
            : "loading"}
        </div>
      </div>
      <div className="pointer-events-none absolute inset-x-0 bottom-24 z-20 flex justify-center px-4">
        <div
          className={`max-w-xl rounded-md border px-4 py-2 text-center text-sm ${
            hud.dose > 55 ? "border-danger bg-danger/40" : hud.doorOpenAlert ? "border-danger bg-danger/40" : "border-border bg-surface/85"
          }`}
        >
          {hud.fuse > 0
            ? `FUSE ${Math.ceil(hud.fuse)}s${hud.doorOpenAlert ? " — BLAST DOOR OPEN." : ""}`
            : hud.result || hud.prompt}
        </div>
      </div>
      <div className="absolute bottom-4 left-4 z-30 grid grid-cols-3 gap-2">
        {KEYS.map((k) => {
          const on = held.includes(k.code);
          return (
            <button
              key={k.code}
              type="button"
              className={`h-14 min-w-14 rounded-md border px-3 font-display text-base ${
                on ? "border-primary bg-primary text-bg" : "border-border bg-surface text-fg"
              }`}
              onPointerDown={(e) => {
                e.preventDefault();
                e.stopPropagation();
                press(k.code);
              }}
              onPointerUp={() => release(k.code)}
              onPointerCancel={() => release(k.code)}
              onPointerLeave={() => release(k.code)}
            >
              {k.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
