export function getCarbonFillColor(level: number): string {
  const clamped = Math.max(0, Math.min(100, level));
  if (clamped <= 50) {
    const t = clamped / 50;
    const r = Math.round(0 + (255 - 0) * t);
    const g = Math.round(200 + (215 - 200) * t);
    return `rgb(${r}, ${g}, 88)`;
  }

  const t = (clamped - 50) / 50;
  const r = 255;
  const g = Math.round(215 + (68 - 215) * t);
  const b = Math.round(88 + (68 - 88) * t);
  return `rgb(${r}, ${g}, ${b})`;
}

export function getSkyColors(level: number): [string, string, string] {
  const pollution = Math.max(0, Math.min(100, level)) / 100;
  const top = `rgb(${Math.round(29 + 72 * pollution)}, ${Math.round(41 + 10 * pollution)}, ${Math.round(101 - 36 * pollution)})`;
  const mid = `rgb(${Math.round(67 + 86 * pollution)}, ${Math.round(84 - 4 * pollution)}, ${Math.round(155 - 70 * pollution)})`;
  const horizon = `rgb(${Math.round(255)}, ${Math.round(176 - 60 * pollution)}, ${Math.round(117 - 34 * pollution)})`;
  return [top, mid, horizon];
}
